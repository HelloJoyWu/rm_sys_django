FROM python:3.10
MAINTAINER rmpeter0474

LABEL version='1.0'
LABEL description='python3.8 with django'

WORKDIR /
COPY requirements.txt ./
COPY . /rmsys
RUN mkdir /tmp/log

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y supervisor \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /run/rmsys_daphne/
