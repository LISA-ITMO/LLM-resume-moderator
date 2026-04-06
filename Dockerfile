FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apk add --no-cache poppler-utils

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

CMD ["python", "main.py"]
