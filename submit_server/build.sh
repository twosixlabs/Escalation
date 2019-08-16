docker build -t escalation-server .
version=$(python escalation/VERSION.py)
docker tag escalation-server snovotney/escalation-server:$version
docker push snovotney/escalation-server:$version
