FROM python:3

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /
RUN pip install -r /requirements.txt \
    && apt-get -y update \
    && apt-get -y install redis-server

COPY webui /
COPY scraper /

WORKDIR /webui

EXPOSE 4433
