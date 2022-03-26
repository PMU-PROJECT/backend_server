# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY . .

RUN apt update

RUN apt -y install gcc

RUN python -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

#TODO expose ports based on conf.cfg
EXPOSE 37888 5432
