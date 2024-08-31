FROM python:3.9-slim

WORKDIR /work

COPY . /work

RUN apt update && apt install -y git curl
RUN git config --global --add safe.directory /work
RUN pip install -r requirements.txt
