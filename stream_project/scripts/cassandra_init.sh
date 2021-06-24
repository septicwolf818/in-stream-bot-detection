#!/bin/bash
/wait_for_it.sh cassandra:9042 --strict --timeout=300 -- cqlsh -f /cassandra_init.cql cassandra 9042