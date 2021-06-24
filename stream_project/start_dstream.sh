#!/bin/bash
echo "Generate input data (10 users and 1 bot)"
RANDOM_SUFFIX=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
python3 generator.py --users 10 --bots 1 > container-data/connect/data/data_$RANDOM_SUFFIX.json 
echo "Start Spark jobs"
cd dstream/ && sbt clean assembly
cp target/scala-2.12/BotDetectDStream.jar ../container-data/spark/apps/
docker exec spark-master spark-submit --conf spark.jars.ivy=/spark/jars/ --class "botdetect.BotDetectDStream" /spark/apps/BotDetectDStream.jar
