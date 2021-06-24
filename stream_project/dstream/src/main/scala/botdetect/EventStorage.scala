package botdetect
import scala.collection.mutable.ListBuffer
class EventStorage(
    var events: scala.collection.mutable.Map[String, ListBuffer[EventData]] =
      scala.collection.mutable.Map(),
    var windows: scala.collection.mutable.Map[String, ListBuffer[
      ListBuffer[EventData]
    ]] = scala.collection.mutable.Map(),
    var maxTimestamps: scala.collection.mutable.Map[String,Int] = scala.collection.mutable.Map()
) extends Serializable {
  /**
    * Adds event to event storage
    *
    * @param event The event data
    * @param recursive The flag for filling all windows that event belongs to
    */
  def add(event: EventData, recursive: Boolean = false): Unit = {
    if (!maxTimestamps.keys.exists(_ == event.event_ip)) {
      maxTimestamps = maxTimestamps + ((event.event_ip, event.event_time.toInt))
    }
    else {
      if(maxTimestamps(event.event_ip) < event.event_time.toInt){
        maxTimestamps(event.event_ip) = event.event_time.toInt
      }
    }
    if (!events.keys.exists(_ == event.event_ip)) {
      events = events + ((event.event_ip, ListBuffer()))
    }

    if (!events(event.event_ip).contains(event)) {
      events(event.event_ip) += event
    }

    if (!windows.keys.exists(_ == event.event_ip)) {
      windows = windows + ((event.event_ip, ListBuffer(ListBuffer())))
    }

    var belongsToExistingWindow = false

    windows(event.event_ip) = windows(event.event_ip).map(window => {
      var maxTimestamp = -1
      window.foreach(savedEvent => {
        if (savedEvent.event_time.toInt > maxTimestamp) {
          maxTimestamp = savedEvent.event_time.toInt
        }
      })

      if (maxTimestamp - event.event_time.toInt < 10) {
        if (!window.contains(event)) {
          window += event
          belongsToExistingWindow = true
        }
      }
      window
    })

    if (!belongsToExistingWindow) {
      windows(event.event_ip) += ListBuffer(event)
    }

    if (!recursive) {
      updateWindows(event.event_ip)
    }
  }
  /**
    * Fills all windows that events belongs to
    *
    * @param event_ip The IP for events to be updated
    */
  def updateWindows(event_ip: String): Unit = {
    events(event_ip).foreach(event => {
      add(event, recursive = true)
    })
  }
  /**
    *
    * @return All events from the storage
    */
  def getAllEvents: scala.collection.mutable.Map[String, ListBuffer[EventData]] = {
    events
  }
  /**
    *
    * @return All windows from the storage
    */
  def getWindows: scala.collection.mutable.Map[String, ListBuffer[ListBuffer[EventData]]] = {
    windows
  }
  /**
    *
    * @return All detected bots from the storage
    */
  def getBots: Seq[String] = {
    windows.values.flatMap(_.toList).filter(_.length > 20).map(_.last).map(_.event_ip).toList.distinct
  }
  /**
    * 
    * @param ip IP for max event timestamp to return
    * @return Max timestamp registered from new events for specified IP
    */
  def getMaxTimestamp(ip:String):Int = {
    if (maxTimestamps.keys.exists(_ == ip)) {
      maxTimestamps(ip)
    }
    -1
  }
}
