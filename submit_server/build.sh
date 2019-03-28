docker build -t escalation-server .
docker tag escalation-server snovotney/escalation-server:0.7.4
docker push snovotney/escalation-server
