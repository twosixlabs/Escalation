docker build -t escalation-server .
docker tag escalation-server snovotney/escalation-server:1.0.1
docker push snovotney/escalation-server
