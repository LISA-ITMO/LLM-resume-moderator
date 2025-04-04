from openai import AsyncOpenAI

from config import MLP_API_KEY, DEFAULT_MODERATOR, PROMPT
from schemas import Rool

from typing import List, Dict
import json


client = AsyncOpenAI(
    api_key=MLP_API_KEY,
    base_url="https://caila.io/api/adapters/openai"
)


def parse_answer(response_str: str) -> None:
    parts = response_str.split("Результат:")
    
    reasoning = parts[0].replace("Рассуждения:\n", "").strip()

    try:
        result_dict = json.loads(parts[1])
    except json.JSONDecodeError:
        result_dict = {"error": "Invalid JSON format"}
    
    return {
        "reasoning": reasoning,
        "result": result_dict
    }


async def llm_answer(resume_text: str, rools: List[Rool], moderator_model: str=None) -> None:

    formatted_prompt = PROMPT.replace('{rools}', '\n'.join([rool.model_dump_json() for rool in rools])).replace('{resume_text}', resume_text)

    completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": formatted_prompt
            }
        ],
        model=DEFAULT_MODERATOR,
    )
    
    answer_content = completion.choices[0].message

    return parse_answer(answer_content)
