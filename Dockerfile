FROM python:3

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY webui /
COPY scraper /

WORKDIR /webui

EXPOSE 4433
