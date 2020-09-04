--This file is run in Docker compose to set up the database:
\c escalation;
create table if not exists data_upload_metadata (upload_id int, table_name text, upload_time timestamp, active boolean, username text, notes text, PRIMARY KEY (table_name, upload_id));

create database testing_escalation;
\c testing_escalation;
create table if not exists data_upload_metadata (upload_id int, table_name text, upload_time timestamp, active boolean, username text, notes text, PRIMARY KEY (table_name, upload_id));
