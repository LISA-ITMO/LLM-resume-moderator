import json
import re
from typing import List

from schemas import (
    DEFAULT_RULES,
    ResponseWithReasoning,
    ResumeToGovernment,
    Rule
)
from service.resume_text_converter import resume_to_text
from service.llm_interface import llm_interface

NO_REASONING_PROMPT = """
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


REASONING_PROMPT = """
Ты — ИИ-модератор резюме. Проверь текст резюме на соответствие следующим правилам. Если есть нарушения, верни JSON-объект с типом нарушения и фрагментом текста, который нарушает правило. Если нарушений нет, верни статус "OK".

**Правила:**
{rules}

**Инструкции:**

- Тщательно проанализируй каждое предложение в резюме.
- Если нарушений нет, верни "status": "OK" и пустой массив violated_rules.
- Если фрагмент нарушает правило, укажи его точную цитату в resume_fragment.

Формат ответа: { "status": "OK" | "VIOLATION", "violated_rules": [] | [ { "id": "rule_id", "condition": "Текст условия правила на русском", "resume_fragment": "Точная цитата из резюме" } ] }

**Текст резюме:**
{resume_text}
"""


def parse_answer(response_str: str, reasoning: bool = False) -> ResponseWithReasoning:

    if reasoning:
        if reasoning:
            reasoning_start = response_str.find("<think>")
            reasoning_end = response_str.find("</think>")
        if reasoning_start != -1 and reasoning_end != -1:
            reasoning_string = response_str[reasoning_start + 7:reasoning_end].strip()
            parts = [reasoning_string, response_str[reasoning_end + 8:]]
        else:
            reasoning_string = ""
            parts = ["", response_str]
    else:
        parts = response_str.split("Результат:")
        reasoning_string = parts[0].replace("Рассуждения:", "").strip()

    json_match = re.search(r"```json\n(.*?)\n```", parts[1], re.DOTALL) or re.search(r"(\{.*?\})", parts[1], re.DOTALL)
    json_str = json_match.group(1) if json_match else "{}"

    try:
        result_dict = json.loads(json_str)
    except json.JSONDecodeError:
        result_dict = {"error": "Invalid JSON format"}

    return ResponseWithReasoning(reasoning=reasoning_string, violatedRules=result_dict['violated_rules'])


async def moderate(
    resume: ResumeToGovernment, rules: List[Rule] = None, moderator_model: str = None
) -> ResponseWithReasoning:
    if rules is None:
        rules = DEFAULT_RULES

    resume_text = resume_to_text(resume=resume)

    formated_reasoning_prompt = REASONING_PROMPT.replace(
        "{rules}", "\n".join([rule.model_dump_json() for rule in rules])
    ).replace("{resume_text}", resume_text)

    formated_no_reasoning_prompt = NO_REASONING_PROMPT.replace(
        "{rules}", "\n".join([rule.model_dump_json() for rule in rules])
    ).replace("{resume_text}", resume_text)

    answer_content = await llm_interface.create_completions(
        prompt=formated_no_reasoning_prompt,
        reasoning_prompt=formated_reasoning_prompt,
        model_name=moderator_model
    )

    reasoning = await llm_interface.define_llm_reasoning(model_name=moderator_model)
    parsed_result = parse_answer(
        response_str=answer_content,
        reasoning=reasoning
    )

    return parsed_result
