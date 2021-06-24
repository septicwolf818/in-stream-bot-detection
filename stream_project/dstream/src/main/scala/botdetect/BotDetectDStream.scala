package botdetect
import org.apache.spark._
import org.apache.spark.streaming._
import org.apache.kafka.common.serialization.StringDeserializer
import org.apache.spark.streaming.kafka010._
import org.apache.spark.streaming.kafka010.LocationStrategies.PreferConsistent
import org.apache.spark.streaming.kafka010.ConsumerStrategies.Subscribe
/**
  * DStream bot detector
  */
object BotDetectDStream {
  /**
    * Main method to be run on Spark cluster
    *
    * @param args
    */
  def main(args: Array[String]): Unit = {
    val conf = new SparkConf()
      .setMaster("spark://spark-master:7077")
      .setAppName("BotDetectDStream")
    val ssc = new StreamingContext(conf, Seconds(10))
    ssc.checkpoint("/spark/checkpoints")
    val kafkaParams = Map[String, Object](
      "bootstrap.servers" -> "kafka:19092",
      "group.id" -> "BotDetectDStream",
      "key.deserializer" -> classOf[StringDeserializer],
      "value.deserializer" -> classOf[StringDeserializer],
      "auto.offset.reset" -> "earliest",
      "enable.auto.commit" -> (false: java.lang.Boolean)
    )
    val topics = Array("project-events")
    val stream = KafkaUtils.createDirectStream[String, String](
      ssc,
      PreferConsistent,
      Subscribe[String, String](topics, kafkaParams)
    )
    val dataStream = stream.map(record => EventData(record.value))
    dataStream.foreachRDD(RDDProcessor.process _)

    ssc.start()
    ssc.awaitTermination()
  }

}
