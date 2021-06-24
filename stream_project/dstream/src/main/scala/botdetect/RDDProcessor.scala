package botdetect
import com.redis._
import io.jvm.uuid._
import com.datastax.oss.driver.api.core.CqlSession
import java.net.InetSocketAddress


object RDDProcessor {
  /**
    * Processes events data from Kafka
    *
    * Process data, save bots to Redis and save events to Cassandra
    * 
    * @param data the event data
    */
  def process(data: org.apache.spark.rdd.RDD[EventData]): Unit = {
    data.foreachPartition(partitionOfRecords => {
      // Event storage
      val storage = new EventStorage

      // Add data to event storage
      partitionOfRecords.foreach(event => {
        storage.add(event)
      })

      // Connect to Redis
      val redisClient = new RedisClient("redis", 6379)

      // New events to save in Redis and Cassandra
      val newEvents = storage.getAllEvents

      // Saved events keys
      val savedEventsKeys = redisClient.keys("events:*")

      // Load saved events from Redis to event storage
      for (keyList <- savedEventsKeys) {
        for (key <- keyList) {
          // Load events only if timestamp is not older than 10 seconds than newest event
          val event:botdetect.EventData = EventData(redisClient.get(key.get).get)
          val maxTimestamp = storage.getMaxTimestamp(event.event_ip)
          if(maxTimestamp != -1 && maxTimestamp - event.event_time.toInt < 10)
            storage.add(event)
        }
      }

      // Save new events to Redis
      for (
        (ip: String, events: scala.collection.mutable.ListBuffer[EventData]) <-
          newEvents
      ) {
        for (event <- events) {
          // JSON String
          val data =
            "{\"type\":\"" + event.event_type + "\",\"ip\":\"" + event.event_ip + "\",\"event_time\":\"" + event.event_time + "\",\"url\":\"" + event.event_url + "\"}"
          val uuid = UUID.randomUUID()
          redisClient.set("events:" + ip + ":" + uuid, data)
          redisClient.expire("events:" + ip+ ":" + uuid, 600)
        }
      }

      // Detect bots using new and saved events
      val bots = storage.getBots

      // Save detected bots to Redis
      bots.foreach(bot => {
        redisClient.hmset("bots:" + bot, Map("is_bot" -> true))
        redisClient.expire("bots:" + bot, 600)
      })

      // Save events to Cassandra
      val session:CqlSession = CqlSession.builder().withLocalDatacenter("datacenter1").addContactPoint(new InetSocketAddress("cassandra",9042)).build()

      for ((_, events) <- newEvents) {
        val eventsToSave = events.map(event => {
          if (bots.contains(event.event_ip)) {
            event.is_bot = true
          }
          event
        })

        eventsToSave.foreach(eventToSave => {
          session.execute("INSERT INTO project.events (event_ip,event_time,event_type,event_url,is_bot) VALUES (\'"+eventToSave.event_ip+"\',\'"+eventToSave.event_time+"\',\'"+eventToSave.event_type+"\',\'"+eventToSave.event_url+"\',"+eventToSave.is_bot+");")
        })
      }
    })
  }
}
