import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as func
from pyspark.sql.types import StructType, StructField, StringType
from collections import namedtuple

# Schema for events data coming from Kafka
schema = StructType([
    StructField("type", StringType(), nullable=False),
    StructField("ip", StringType(), nullable=False),
    StructField("event_time", StringType(), nullable=False),
    StructField("url", StringType(), nullable=False)])

# Apache Spark session
spark = SparkSession \
    .builder \
    .appName("BotDetector") \
    .config("spark.redis.host", "redis")\
    .config("spark.redis.port", "6379")\
    .config("spark.cassandra.connection.host", "cassandra")\
    .config("spark.cassandra.connection.localDC", "datacenter1")\
    .master("spark://spark-master:7077") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Pulling data from Kafka
data = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:19092")) \
    .option("subscribe", "project-events") \
    .option("startingOffsets", "earliest") \
    .load()

# Parsing data using schema
df = data\
    .select(
        func.from_json(
            func.col("value").cast(StringType()), schema)
        .alias("event"))

# Getting events data from data stream
events = df.select(
    func.to_timestamp(func.from_unixtime(
        "event.event_time")).alias("event_time"),
    func.col("event.ip").alias("event_ip"),
    func.col("event.type").alias("event_type"),
    func.col("event.url").alias("event_url")
)


def batch_processor(events, _):
    events.persist()
    try:
        # Detecting bots and saving to Redis
        events \
            .withWatermark(
                "event_time",
                "10 minutes"
            ) \
            .groupBy(
                func.window("event_time", "10 seconds", "1 second"),
                "event_ip") \
            .agg(
                func.count(func.col("event_ip")).alias("request_count"),
                func.last(func.col("event_time")).alias("detected_at"),
                func.last(func.col("event_url")).alias("url")) \
            .where(func.col("request_count") > func.lit(20))\
            .write\
            .format("org.apache.spark.sql.redis")\
            .option("table", "bots")\
            .option("key.column", "event_ip")\
            .option("ttl", "600")\
            .mode("append")\
            .save()

        # Getting all bots
        bots_df = spark\
            .read\
            .format("org.apache.spark.sql.redis")\
            .option("table", "bots")\
            .option("key.column", "event_ip")\
            .load()\
            .drop("window")

        bot_ips = [bot["event_ip"] for bot in bots_df.collect()]

        # Saving events to Cassandra
        events.\
            withColumn("is_bot",
                       func.when(
                           func.col("event_ip")
                           .isin(bot_ips),
                           "true")
                       .otherwise("false"))\
            .write\
            .format("org.apache.spark.sql.cassandra")\
            .mode('append')\
            .options(table="events", keyspace="project")\
            .save()
    finally:
        events.unpersist()


output_stream = events\
    .writeStream\
    .outputMode("update")\
    .option("checkpointLocation", "/spark/checkpoints/")\
    .foreachBatch(batch_processor)\
    .start()\
    .awaitTermination()
