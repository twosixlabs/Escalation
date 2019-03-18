docker run --name escalation -d -p 8000:5000 --rm -e SECRET_KEY=perovskites-rule \
    --link escalation-mysql:dbserver \
    -e DATABASE_URL=mysql+pymysql://escalation:perovskites@dbserver/escalation \
    escalation-server:latest
