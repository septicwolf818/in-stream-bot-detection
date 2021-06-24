#!/bin/bash
/wait_for_it.sh kafka:9092 --strict --timeout=300 -- /usr/bin/kafka-topics --zookeeper zookeeper:2181 --create --topic project-events --partitions 1 --replication-factor 1