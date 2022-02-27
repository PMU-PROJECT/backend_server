# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

RUN pip3 install gunicorn

#TODO expose ports based on conf.cfg
EXPOSE 37888 5432
