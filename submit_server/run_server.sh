docker run --name escalation -it --rm -p 8000:5000 --rm -e SECRET_KEY=perovskites-rule \
    --link escalation-mysql:dbserver \
    -e DATABASE_URL=mysql+pymysql://escalation:perovskites@dbserver/escalation \
    escalation-server:latest


docker run --name escalation -it --rm \
    -e TZ=`ls -la /etc/localtime | cut -d/ -f8-9` \
    -e DATABASE_URL=mysql+pymysql://escalation:perovskites@dbserver/escalation \
    -e ESCALATION_PERSISTENT_DATA_PATH=/persistent_data/escalation_data \
    -v /Users/nick.leiby/escalation_data:/persistent_data/escalation_data \
    -p 8000:5000 --rm -e SECRET_KEY=perovskites-rule --link escalation-mysql:dbserver \
    escalation-server:latest