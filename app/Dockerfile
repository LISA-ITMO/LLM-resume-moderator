FROM python:3.12-slim

WORKDIR /app


RUN apt update && apt install curl -y

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY resume_rules.json .

EXPOSE 8000

CMD ["python", "main.py"]