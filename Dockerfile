FROM python:3.12-slim

USER root
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src /app/
CMD ["python3", "main.py"]
