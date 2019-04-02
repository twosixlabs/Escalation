docker build -t escalation-server .
docker tag escalation-server snovotney/escalation-server:0.8.3
docker push snovotney/escalation-server
