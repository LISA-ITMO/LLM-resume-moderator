from dotenv import load_dotenv

from schemas import Rool

import os
import json


load_dotenv()

MLP_API_KEY =  os.environ.get("MLP_API_KEY")

if os.environ.get('DEFAULT_MODERATOR'):
    DEFAULT_MODERATOR = os.environ.get('DEFAULT_MODERATOR')
else:
    DEFAULT_MODERATOR = 'just-ai/t-tech-T-pro-it-1.0'

DEFAULT_ROOLS = [Rool(**rool) for rool in json.load(open('resume_rools.json'))]

PROMPT = """
Ты — ИИ-модератор резюме. Проверь текст резюме на соответствие следующим правилам. Если есть нарушения, верни JSON-объект с типом нарушения и фрагментом текста, который нарушает правило. Если нарушений нет, верни статус "OK".

**Правила:** 
{rools}

**Инструкции:**

- Тщательно проанализируй каждое предложение в резюме.
- Если нарушений нет, верни "status": "OK" и пустой массив violated_rules.
- Если фрагмент нарушает правило, укажи его точную цитату в resume_fragment.
- Ответ должен содержать твои рассуждения по каждому правилу оканчивающийся вердиктом, затем должен быть результат в формате JSON, без Markdown и комментариев.

Формат ответа: Рассуждения:, Результат: { "status": "OK" | "VIOLATION", "violated_rules": [] | [ { "id": "rule_id", "condition": "Текст условия правила на русском", "resume_fragment": "Точная цитата из резюме" } ] }

**Текст резюме:**
{resume_text}
"""