FROM python:3.12-slim

RUN apt-get update && apt-get install -y build-essential cmake git
RUN pip install llama-cpp-python[server]

WORKDIR /app
COPY t-lite-it-1.0-q8_0.gguf .

CMD ["python3", "-m", "llama_cpp.server",  "--model", "/app/t-lite-it-1.0-q8_0.gguf", "--use_mmap", "True", "--cache", "True", "--cache_type", "disk", "--n_threads", "16", "--parallel", "1", "--host", "0.0.0.0", "--port", "8000"]
