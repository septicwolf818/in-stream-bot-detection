CREATE KEYSPACE IF NOT EXISTS project WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE project.events (event_ip text, event_time text, event_type text, event_url text, is_bot boolean, PRIMARY KEY (event_ip, event_time, event_url));
