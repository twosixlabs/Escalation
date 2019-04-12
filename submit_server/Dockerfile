FROM frolvlad/alpine-python-machinelearning

#xgboost
RUN apk add --update --no-cache \
    --virtual=.build-dependencies \
    git && \
    mkdir /src && \
    cd /src && \
    git clone --recursive -b v0.81 https://github.com/dmlc/xgboost && \
    sed -i '/#define DMLC_LOG_STACK_TRACE 1/d' /src/xgboost/dmlc-core/include/dmlc/base.h && \
    sed -i '/#define DMLC_LOG_STACK_TRACE 1/d' /src/xgboost/rabit/include/dmlc/base.h && \
    apk del .build-dependencies

RUN apk add --update --no-cache \
    --virtual=.build-dependencies \
    make gfortran \
    python3-dev \
    py-setuptools g++ && \
    apk add --no-cache openblas lapack-dev libexecinfo-dev libstdc++ libgomp && \
    ln -s locale.h /usr/include/xlocale.h && \
    cd /src/xgboost; make -j4 && \
    cd /src/xgboost/python-package && \
    python3 setup.py install && \
    rm /usr/include/xlocale.h && \
    apk del .build-dependencies


RUN echo "America/New_York" > /etc/timezone
RUN adduser -D escalation

WORKDIR /home/escalation

RUN apk add g++ libstdc++ python3-dev bash git gcc libffi-dev libressl-dev
# RUN apk update && apk add libressl-dev libffi-dev gcc musl-dev python3-dev

COPY requirements.txt requirements.txt
RUN python3 -m venv venv --system-site-packages
RUN venv/bin/pip3 install --upgrade pip
RUN venv/bin/pip3 install -r requirements.txt
RUN venv/bin/pip3 install gunicorn pymysql 

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