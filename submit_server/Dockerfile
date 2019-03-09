FROM python:3.6-alpine

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
ENV SECRET_KEY perovskite52cb883e323b48d

COPY escalation escalation
RUN chown -R escalation:escalation ./

COPY server.py server.py
COPY boot.sh boot.sh

RUN chmod +x boot.sh

USER escalation

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]