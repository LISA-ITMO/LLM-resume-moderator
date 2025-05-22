from pydantic import BaseModel

from typing import List


class OpenAiMessageMock(BaseModel):
    content: str

class OpenAiChoiceMock(BaseModel):
    message: OpenAiMessageMock


class OpenAiRespMock(BaseModel):
    choices: List[OpenAiChoiceMock]


success_content = \
"""Рассуждения: 
Анализирую резюме на соответствие правилам.
Результат: ```json
{
    "status": "OK",
    "violated_rules": []
}
```"""

violation_content = \
"""Рассуждения: 
Анализирую резюме на соответствие правилам.
Найдено нарушение правила rule_1.
Результат: ```json
{
    "status": "VIOLATION",
    "violated_rules": [
        {
            "id": "rule_1",
            "condition": "...",
            "resume_fragment": "..."
        }
    ]
}
```"""