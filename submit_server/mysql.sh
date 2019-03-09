docker volume create db_volume

docker run \
    -e MYSQL_ROOT_PASSWORD=perovskites \
    -e MYSQL_DATABASE=escalation \
    -e MYSQL_USER=escalation \
    -e MYSQL_PASSWORD=perovskites \
    --mount type=volume,src=db_volume,dst=/var/lib/mysql \
    -p 3306:3306 \
    -d \
    mysql:latest
