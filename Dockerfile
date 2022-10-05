FROM navikt/python:3.9

USER root

COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]