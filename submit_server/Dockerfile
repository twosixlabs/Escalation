FROM alpine:3.10

RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

RUN echo "America/New_York" > /etc/timezone
RUN adduser -D escalation

WORKDIR /home/escalation

RUN apk add g++ libstdc++ python3-dev bash git gcc libffi-dev libressl-dev py-virtualenv

COPY requirements-app.txt requirements-app.txt
RUN python3 -m venv venv --system-site-packages --without-pip
RUN source venv/bin/activate
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements-app.txt
RUN pip3 install gunicorn pymysql

# use pre-built numpy and pandas Alpine Linux packages instead of installing wheels via pip

RUN echo '@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing/' >> /etc/apk/repositories
RUN echo '@community http://dl-cdn.alpinelinux.org/alpine/v3.10/community' >> /etc/apk/repositories
RUN apk add py3-numpy@community
RUN apk add py3-pandas@testing

ENV FLASK_APP escalation
ENV SECRET_KEY perovskite52cb883e323b48d

COPY server.py server.py
COPY boot.sh boot.sh
RUN chmod +x boot.sh

COPY escalation escalation
COPY migrations migrations
RUN chown -R escalation:escalation ./

USER escalation

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]