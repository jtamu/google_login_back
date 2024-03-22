FROM python:3.9-slim

WORKDIR /work

COPY . /work

RUN pip install -r requirements.txt
