def test_detected_bot(events_data, spark_job_dstream, redis_bot):
    assert redis_bot.decode('utf-8') == "bots:172.8.0.1"
