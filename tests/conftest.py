import os
import time
import shutil
import pytest
import requests
from kafka.admin import KafkaAdminClient, NewTopic
from cassandra.cluster import Cluster, NoHostAvailable
import redis
from pytest_docker import docker_ip, docker_services


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "..", "stream_project", "docker-compose.yaml")


def null_sink(*_):
    pass


@pytest.fixture(scope="session")
def docker_cleanup(pytestconfig):
    shutil.rmtree(os.path.join(str(pytestconfig.rootdir), "..",
                               "stream_project", "container-data"), onerror=null_sink)
    return "down -v"


@pytest.fixture(scope="session")
def events_data(docker_services):
    os.system("/bin/bash -c \"python3 ../stream_project/generator.py --users 10 --bots 1 > ../stream_project/container-data/connect/data/data.json\"")
    return True



@pytest.fixture(scope="session")
def spark_job_dstream():
    time.sleep(30)
    os.system(
        "/bin/bash -c \"cd ../stream_project/dstream/ && sbt clean assembly \"")
    os.system("/bin/bash -c \"cp ../stream_project/dstream/target/scala-2.12/BotDetectDStream.jar ../stream_project/container-data/spark/apps/ \"")
    os.system("/bin/bash -c \"docker exec spark-master spark-submit --conf spark.jars.ivy=/spark/jars/ --class \"botdetect.BotDetectDStream\" /spark/apps/BotDetectDStream.jar  \"&")
    return True


@pytest.fixture(scope="session")
def spark_job_structured():
    time.sleep(30)
    os.system("/bin/bash -c \"cp ../stream_project/structured/botdetect-structured.py ../stream_project/container-data/spark/apps/ \"")
    os.system("/bin/bash -c \"docker exec spark-master spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.2,com.redislabs:spark-redis_2.12:2.6.0,com.datastax.spark:spark-cassandra-connector_2.12:3.0.1 --conf spark.jars.ivy=/spark/jars/ /spark/apps/botdetect-structured.py  \"&")
    return True


@pytest.fixture(scope="session")
def redis_bot(docker_services, docker_ip):
    r = redis.StrictRedis(
        host=docker_ip, port=docker_services.port_for("redis", 6379))
    data = []
    while len(data) < 1:
        time.sleep(5)
        data = [key for key in r.scan_iter("bots:*")]
    return data[0]
