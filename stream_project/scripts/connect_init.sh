#!/bin/bash
/wait_for_it.sh connect:8083 --strict --timeout=300 -- sleep 15 && curl -X POST -H "Content-Type: application/json" --data '{
  "name": "JsonSpoolDir",
  "config":{
  "tasks.max": "1",
  "connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirSchemaLessJsonSourceConnector",
  "input.path": "/connect/data",
  "input.file.pattern": "^.+..json$",
  "error.path": "/connect/error",
  "finished.path": "/connect/finished",
  "halt.on.error": "false",
  "topic": "project-events",
  "schema.generation.enabled": "false",
  "value.schema": "{\"name\":\"value\",\"type\":\"STRUCT\",\"isOptional\":false,\"fieldSchemas\":{\"type\":{\"type\":\"STRING\",\"isOptional\":false},\"ip\":{\"type\":\"STRING\",\"isOptional\":false},\"event_time\":{\"type\":\"STRING\",\"isOptional\":false},\"url\":{\"type\":\"STRING\",\"isOptional\":false}}}"
}}' http://connect:8083/connectors