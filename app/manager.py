from openai import AsyncOpenAI
from httpx import AsyncClient

from config import MLP_API_KEY, DEFAULT_MODERATOR, PROMPT, PROVIDER_URL, MODELS_DICT
from schemas import Rule, ResponseWithReasoning, ResumeToGovernment, DEFAULT_RULES
from resume_text_converter import resume_to_text

from typing import List
import json
import re


client = AsyncOpenAI(
    api_key=MLP_API_KEY,
    base_url=PROVIDER_URL,
    http_client=AsyncClient(
        proxy=None,
        timeout=600
    )
)


def parse_answer(response_str: str) -> ResponseWithReasoning:
    parts = response_str.split("Результат:")
    
    reasoning = parts[0].replace("Рассуждения:", "").strip()

    json_match = re.search(r'```json\n(.*?)\n```', parts[1], re.DOTALL)
    json_str = json_match.group(1) if json_match else '{}'

    try:
        result_dict = json.loads(json_str)
    except json.JSONDecodeError:
        result_dict = {"error": "Invalid JSON format"}
    
    return ResponseWithReasoning.model_validate({"reasoning": reasoning, "result": result_dict})


async def moderate(resume: ResumeToGovernment, rules: List[Rule]=None, moderator_model: str=None) -> ResponseWithReasoning:
    if rules is None:
        rules = DEFAULT_RULES
    
    if moderator_model is None:
        provider_model_name = MODELS_DICT[DEFAULT_MODERATOR]
    else:
        provider_model_name = MODELS_DICT[moderator_model.name]

    resume_text = resume_to_text(resume=resume)

    formatted_prompt = PROMPT.replace('{rules}', '\n'.join([rule.model_dump_json() for rule in rules])).replace('{resume_text}', resume_text)

    completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": formatted_prompt
            }
        ],
        model=provider_model_name,
    )
    
    answer_content = completion.choices[0].message.content

    return parse_answer(answer_content)
