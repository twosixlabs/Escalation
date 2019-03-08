docker build -t escalation-server .
docker tag escalation-server snovotney/escalation
docker push snovotney/escalation:latest
