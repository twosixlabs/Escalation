# Building the web server and mysql server locally


## MYSQL

1. Install mysql on your local machine

2. Stand up a mysql server in a docker container.

```
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
```
3. If desired, connect to the db directly with  `mysql -h localhost -P 3306 --protocol=tcp -u escalation -pperovskites -D escalation`

## Build the web server container

This assumes you have a public docker hub account. If not, go make one at https://hub.docker.com/

```
# set your escalation app version (should be tracked in VERSION.py
ESCALATION_VERSION=0.2
# change to your Docker user ID
DOCKERUSER=snovotney
docker build -t escalation-server .
docker tag escalation-server:latest $DOCKERUSER/escalation:ESCALATION_VERSION
docker push $DOCKERUSER/escalation:ESCALATION_VERSION
```

## Run the web server locally in a docker container

This will create the server on `127.0.0.1:8000` and connect to the mysql server you stood up before.

```
docker run --name escalation -d -p 8000:5000 --rm -e SECRET_KEY=perovskites-rule \
    --link escalation-mysql:dbserver \
    -e DATABASE_URL=mysql+pymysql://escalation:perovskites@dbserver/escalation \
    escalation-server:latest
```

Go to `http://127.0.0.1:8000` in your browser

## Debug with flask

You can also run the web server outside of docker. There are a couple useful commands:

1. setup the virtual environment venv (instructions incomplete, I know, I know)
2. `source venv/bin/activate`
3. `pip install -r requirements-dev.txt`
4. `flask init-db` creates the tables in the database (run once)
5. `export ESCALATION_PERSISTENT_DATA_PATH='/Users/nick.leiby/escalation_data'` tells the app where to store persistent data 
6. `flask run`

Steps 4 and 6 should use the environment variables in `.env`. If not, then source the variables inside there directly.

There are two other useful commands:
- `flask demo-data` loads fake demo data into the db.
- `flask reset-db` deletes all data from the tables.


## Update stateset from current perovskites versioned data manifest

`python3 submit_server/scripts/upload_stateset.py --endpoint http://127.0.0.1:5000/admin --dev`

## Upload submissions on the command line

1. Run `make_perovskites_blank_submission.py`
2. Run `python3 submit_server/scripts/upload_submission.py --endpoint http://127.0.0.1:5000/submission --dev --csv 0038_train_12f4ffd_NickLeiby.csv --expname first --notes "These are my awesome notes"`

Here's example output of running both
```
python3 submit_server/scripts/upload_stateset.py --endpoint http://127.0.0.1:5000/admin --dev
Filtering ../versioned-datasets/data/perovskite/stateset/0017.stateset.csv to /var/folders/08/cb19qzd92wsbhh3n4cz145v00000gp/T/tmpbx31mcn6
Pushing filtered csv to http://escalation.sd2e.org/admin
200 OK <Response [200]>
{'success': 'updated to crank 0017 and stateset hash a301494d902 with 465426 rows'}
(venv) scott.novotney@mac0561:~/trunk/sd2/escalation$ python3 submit_server/scripts/upload_submission.py --endpoint http://127.0.0.1:5000/submission --dev --csv submit_server/tests/0017_train_c4844e9_snovotney.csv --expname first
0017 c4844e9 snovotney
crank 0017
username snovotney
expname first
notes
csv submit_server/tests/0017_train_c4844e9_snovotney.csv
200 OK <Response [200]>
{'success': 'Added submission'}
```

# todo: tag code on gitlab with version once I push
