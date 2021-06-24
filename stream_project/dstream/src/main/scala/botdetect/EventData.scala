package botdetect
import org.json4s._
import org.json4s.jackson.JsonMethods._
/**
  * Data model for the events
  */
case class EventData(
    event_type: String,
    event_ip: String,
    event_time: String,
    event_url: String,
    var is_bot: Boolean
) extends Serializable
/**
  * Event data model companion object
  */
object EventData {
  def apply(data: String): EventData = {
    implicit val formats: DefaultFormats = DefaultFormats
    val json = parse(data)
    val event_type = (json \\ "type").extract[String]
    val event_ip = (json \\ "ip").extract[String]
    val event_time = (json \\ "event_time").extract[String]
    val event_url = (json \\ "url").extract[String]
    new EventData(event_type, event_ip, event_time, event_url, false)
  }
}
