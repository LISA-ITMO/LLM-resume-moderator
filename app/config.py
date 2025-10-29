from dotenv import load_dotenv

import os


load_dotenv("../.env")
load_dotenv(".env")

ELASTIC_PASSWORD = os.environ.get('ELASTIC_PASSWORD')

llm_providers = {
    'local': {
        'PROVIDER_URL': 'http://llm-service:8000/v1',
        'MLP_API_KEY': 'sk-no-key-required',
        'models': {
            'T_it_1_0': 't-lite-it-1.0-q8_0.gguf'
            }
        },
    'caila.io': {
        'PROVIDER_URL': 'https://caila.io/api/adapters/openai',
        'MLP_API_KEY': os.environ.get('MLP_API_KEY'),
        'models': {
            'T_it_1_0': 'just-ai/t-tech-T-pro-it-1.0'
            }
        }
}

LLM_PROVIDER = os.environ.get('LLM_PROVIDER')
PROVIDER_URL = llm_providers[LLM_PROVIDER]['PROVIDER_URL']
MLP_API_KEY = llm_providers[LLM_PROVIDER]['MLP_API_KEY']
MODELS_DICT = llm_providers[LLM_PROVIDER]['models']

DEFAULT_MODERATOR = 'T_it_1_0'

PROMPT = """
Ты — ИИ-модератор резюме. Проверь текст резюме на соответствие следующим правилам. Если есть нарушения, верни JSON-объект с типом нарушения и фрагментом текста, который нарушает правило. Если нарушений нет, верни статус "OK".

**Правила:** 
{rules}

**Инструкции:**

- Тщательно проанализируй каждое предложение в резюме.
- Если нарушений нет, верни "status": "OK" и пустой массив violated_rules.
- Если фрагмент нарушает правило, укажи его точную цитату в resume_fragment.
- Ответ должен содержать твои рассуждения по каждому правилу оканчивающийся вердиктом, затем должен быть результат в формате JSON, без Markdown и комментариев.

Формат ответа: Рассуждения:, Результат: { "status": "OK" | "VIOLATION", "violated_rules": [] | [ { "id": "rule_id", "condition": "Текст условия правила на русском", "resume_fragment": "Точная цитата из резюме" } ] }

**Текст резюме:**
{resume_text}
"""

FASTAPI_PORT = 8000
