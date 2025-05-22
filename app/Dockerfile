FROM python:3.12-slim

WORKDIR /app

COPY *.py .
COPY requirements.txt .
COPY resume_rules.json .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "main.py"]