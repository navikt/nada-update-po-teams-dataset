FROM ghcr.io/navikt/baseimages/python:3.9

USER root

COPY . .

RUN pip3 install -r requirements.txt

WORKDIR /app/src
CMD ["python3", "main.py"]
