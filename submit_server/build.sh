docker build -t escalation-server:latest .
docker tag escalation-server:latest snovotney/escalation:latest
docker push snovotney/escalation:latest
