FROM python:3.7-slim

RUN apt-get update -y && apt-get install gcc -y
COPY requirements.txt .
RUN pip3 install -r requirements.txt

ADD app /app

ENTRYPOINT python3.7 /app/loadbalancer.py