FROM python:3.11-slim AS builder

RUN python3 -m venv /venv
ENV PATH=/venv/bin:$PATH

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot AS runner

COPY src app/
COPY --from=builder /venv /venv

ENV PYTHONPATH=/venv/lib/python3.11/site-packages

CMD ["app/main.py"]   