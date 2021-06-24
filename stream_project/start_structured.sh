#!/bin/bash
echo "Generate input data (10 users and 1 bot)"
RANDOM_SUFFIX=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
python3 generator.py --users 10 --bots 1 > container-data/connect/data/data_$RANDOM_SUFFIX.json 
echo "Start Spark jobs"
cp structured/botdetect-structured.py container-data/spark/apps/
docker exec -it spark-master spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.2,com.redislabs:spark-redis_2.12:2.6.0,com.datastax.spark:spark-cassandra-connector_2.12:3.0.1 --conf spark.jars.ivy=/spark/jars/ /spark/apps/botdetect-structured.py
