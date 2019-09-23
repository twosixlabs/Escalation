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

### Populate the database from a SQL dump 

NB: You can populate the database from a SQL dump.  To get a fresh dump:

1. connect to the chombo database container
2. Create a dump of the escalation db: `mysqldump --databases escalation -u escalation -pperovskites > dump.sql`
3. install scp if needed (`sudo apt-get install openssh-client`)
4. scp FROM the chombo container TO your work directory (e.g., `nleiby@login1.maverick2.tacc.utexas.edu:/work/05839/nleiby/maverick2/escalation_dumps`)
5. On your local machine, run `mysql -h localhost -P 3306 --protocol=tcp -psd2 < dump.sql`.  If you are overwriting an existing escalation db, you'll need to drop it first

## Build the web server container

To build a local image from your code:

```
docker build -t escalation-server .
```

## Make database changes

We track the db with alembic.  To make changes to the db table schemas:

1. edit the models in database.py
2. run `flask db migrate` to create the revision file that will implement the changes to the table
3. (for local development) run `flask db upgrade` to propagate changes to your local db

## Run the web server locally in a docker container

Run `run_server.sh`. This will create the server on `127.0.0.1:8000` and connect to the mysql server you stood up before.

Go to `http://127.0.0.1:8000` in your browser

## Debug with flask

You can also run the web server outside of docker. There are a couple useful commands:

1. setup the virtual environment venv (instructions incomplete, I know, I know)
2. `source venv/bin/activate`
3. `pip install -r requirements-dev.txt`
4. `flask init-db` creates the tables in the database (run once)
5. `flask db stamp head` Tells the db that it is up to date with revisions
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


# Deploy the image to the web

To deploy the container, you'll need to upload an image to dockerhub.  You need a public docker hub account. If not, go make one at https://hub.docker.com/ . You'll also need access to the `snovotney/escalation-server` repo- talk to Scott.

We have a dev and a prd site at `http://escalation-dev.sd2e.org` and `http://escalation.sd2e.org`.  These are hosted using the Portainer service at `https://chombo.sd2e.org/#/auth`.  

- Update the app version in `VERSION.py`.  We use the semantic versioning scheme with major, minor, and patch revisions: https://semver.org/
- Run `escalation/submit_server/build.sh` to build and tag the local container and deploy to the 
- Deploy the new container version to the Portainer host on the Chombo site.  First deploy and test on the dev app to validate changes
    - On Chombo, click `Containers`->`escalation-dev-server`->`Duplicate/edit`
    - edit the link in `Image` to point to your new version
    - click `Deploy the container`
- After deploying and ensuring the version is ok, merge the pull request on Gitlab with your code changes to master.  We also want to tag the code commit corresponding to the version:
    - Run `git checkout master && git pull` to switch your local branch to master and get the updated code with merge locally
    - Run `git tag X.X.X && git push origin refs/tags/X.X.X` with your version in place of `X.X.X` to locally tag the commit with the version and push that tag to Gitlab