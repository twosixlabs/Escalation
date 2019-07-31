docker build -t escalation-server .
version=$(python VERSION.py)
docker tag escalation-server snovotney/escalation-server:$version
docker push snovotney/escalation-server:$version
