import os

from dotenv import load_dotenv

load_dotenv()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
STORAGE_DIR = "storage"

LLM_SERVICE_PORT = os.environ['LLM_SERVICE_PORT']

llm_providers = {
    'local': {
        'PROVIDER_URL': f'http://localhost:{LLM_SERVICE_PORT}/v1',
        'models': {"default": "ggml-org/Qwen3-1.7B-GGUF"}
    },
    'caila.io': {
        'PROVIDER_URL': 'https://caila.io/api/adapters/openai',
        'models': {"default": "just-ai/Qwen3-30B-A3B"}
    }
}

LLM_PROVIDER = os.environ.get("LLM_PROVIDER")
PROVIDER_URL = llm_providers[LLM_PROVIDER]["PROVIDER_URL"]
MLP_API_KEY = os.environ['MLP_API_KEY']
MODELS_DICT = llm_providers[LLM_PROVIDER]["models"]

DEFAULT_MODERATOR = "default"

REASONING_MAPPING = {
    "just-ai/Qwen3-30B-A3B": True,
    "ggml-org/Qwen3-1.7B-GGUF": True
}

FASTAPI_PORT = int(os.environ['FASTAPI_PORT'])
