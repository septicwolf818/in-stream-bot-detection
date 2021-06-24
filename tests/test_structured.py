def test_detected_bot(events_data, spark_job_structured, redis_bot):
    assert redis_bot.decode('utf-8') == "bots:172.8.0.1"
