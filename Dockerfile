FROM python:3.12-slim

WORKDIR ./

RUN apt update && apt install curl -y

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY configs ./configs
COPY service ./service

CMD ["python", "main.py"]