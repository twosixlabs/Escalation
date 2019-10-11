# NB: have to define your own persistent data path /Users/nick.leiby/escalation_data

 # link the db container to the app
 # mount a local directory as a volume
 # define where the flask app can find the persistent data volume


docker run --name escalation -it --rm \
    -e TZ=`ls -la /etc/localtime | cut -d/ -f8-9` \
    -e DATABASE_URL=mysql+pymysql://escalation:perovskites@dbserver/escalation --link escalation-mysql:dbserver \
    -v /Users/scott.novotney/trunk/sd2/escalation_data:/data \
    -e ESCALATION_PERSISTENT_DATA_PATH=/data \
    -e SECRET_KEY=perovskites-rule \
    -p 8000:5000 --rm \
    escalation-server:latest
