FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./app/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ENV FLASK_APP=main

WORKDIR /app

COPY ./app .

CMD gunicorn -c ./config/gunicorn/gunicorn.conf.py main:app 
