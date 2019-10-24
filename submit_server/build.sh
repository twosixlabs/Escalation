docker build -t escalation-server .
version=$(python escalation/VERSION.py)
docker tag escalation-server nleiby/escalation-server:$version
docker push nleiby/escalation-server:$version
