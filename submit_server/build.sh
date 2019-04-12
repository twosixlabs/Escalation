docker build -t escalation-server .
docker tag escalation-server snovotney/escalation-server:0.9.2o
docker push snovotney/escalation-server
