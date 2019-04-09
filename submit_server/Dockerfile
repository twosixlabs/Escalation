FROM python:3.6-alpine
RUN echo "America/New_York" > /etc/timezone
RUN adduser -D escalation

WORKDIR /home/escalation

RUN apk add g++ libstdc++ python3-dev bash git gcc libffi-dev libressl-dev
# RUN apk update && apk add libressl-dev libffi-dev gcc musl-dev python3-dev

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip3 install --upgrade pip
RUN venv/bin/pip3 install -r requirements.txt
RUN venv/bin/pip3 install gunicorn pymysql 

ENV FLASK_APP escalation
oENV SECRET_KEY perovskite52cb883e323b48d

COPY server.py server.py
COPY boot.sh boot.sh
RUN chmod +x boot.sh

COPY escalation escalation
COPY migrations migrations
RUN chown -R escalation:escalation ./

USER escalation

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]