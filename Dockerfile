FROM python:3

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && sudo apt-get upgrade \
    && apt-get install -y python3.7-dev

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY webui /
COPY scraper /

WORKDIR /webui

EXPOSE 4433
