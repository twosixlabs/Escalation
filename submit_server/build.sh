docker build -t escalation-server .
docker tag escalation-server snovotney/escalation-server:0.9.7
docker push snovotney/escalation-server
