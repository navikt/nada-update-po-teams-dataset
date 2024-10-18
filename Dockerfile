FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

RUN python3 -m venv venv
ENV PATH=/app/venv/bin:$PATH
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

FROM cgr.dev/chainguard/python:latest AS runner

WORKDIR /app

COPY src src
COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
# ENV PYTHONPATH=/venv/lib/python3.11/site-packages

ENTRYPOINT ["python", "src/main.py"]