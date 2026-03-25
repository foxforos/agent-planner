FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN pip install pytest


ENTRYPOINT ["python", "agent.py"]