docker build -t escalation-server .
docker tag escalation-server snovotney/escalation-server:0.7.3
docker push snovotney/escalation-server
