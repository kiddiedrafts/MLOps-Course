FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local
COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "airbnb_serving.app:app", "--host", "0.0.0.0", "--port", "8000"]
