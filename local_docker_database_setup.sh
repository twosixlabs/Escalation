#!/usr/bin/env bash
# Copyright [2020] [Two Six Labs, LLC]
# Licensed under the Apache License, Version 2.0

docker-compose up --build -d

# to connect to db from host
#docker exec -it escos_db psql -h localhost -p 5432 -U escalation -d escalation
