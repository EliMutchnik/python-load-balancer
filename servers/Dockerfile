FROM python:3.7-slim

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY server.py .

ENTRYPOINT python3.7 server.py