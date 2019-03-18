docker volume create db_volume
docker run \
    -e MYSQL_ROOT_PASSWORD=sd2 \
    -e MYSQL_DATABASE=escalation \
    -e MYSQL_USER=escalation \
    -e MYSQL_PASSWORD=perovskites \
    --mount type=volume,src=db_volume,dst=/var/lib/mysql \
    -p 3306:3306 \
    -d \
    --name escalation-mysql \
    mysql:latest

# mysql -h localhost -P 3306 --protocol=tcp -u escalation -pperovskites
