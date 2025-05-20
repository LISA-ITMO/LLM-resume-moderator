from openai import AsyncOpenAI
from httpx import AsyncClient

from config import MLP_API_KEY, DEFAULT_MODERATOR, PROMPT, DEFAULT_RULES, PROVIDER_URL
from schemas import Rule, ResponseWithReasoning, Resume

from typing import List
import json
import re


client = AsyncOpenAI(
    api_key=MLP_API_KEY,
    base_url=PROVIDER_URL,
    http_client=AsyncClient(proxy=None, timeout=240.0),
)


def parse_answer(response_str: str) -> ResponseWithReasoning:
    """
    Parses a string response to extract reasoning and JSON result.

        Args:
            response_str: The string containing the reasoning and JSON result,
                formatted with "Рассуждения:" followed by reasoning text,
                and "Результат:" followed by a JSON block enclosed in ```json ... ```.

        Returns:
            A ResponseWithReasoning object containing the extracted reasoning and parsed JSON result.
            If the JSON is invalid, the result will be a dictionary with an "error" key.
    """
    parts = response_str.split("Результат:")

    reasoning = parts[0].replace("Рассуждения:", "").strip()

    json_match = re.search(r"```json\n(.*?)\n```", parts[1], re.DOTALL)
    json_str = json_match.group(1) if json_match else "{}"

    try:
        result_dict = json.loads(json_str)
    except json.JSONDecodeError:
        result_dict = {"error": "Invalid JSON format"}

    return ResponseWithReasoning.model_validate(
        {"reasoning": reasoning, "result": result_dict}
    )


async def moderate(
    resume: Resume, rules: List[Rule] = None, moderator_model: str = None
) -> ResponseWithReasoning:
    """
    Moderates a resume based on provided rules and a language model.

        Args:
            resume: The resume object to be moderated.
            rules: A list of moderation rules to apply. If None, defaults to DEFAULT_RULES.
            moderator_model: The name of the language model to use for moderation.
                If None, defaults to DEFAULT_MODERATOR.

        Returns:
            ResponseWithReasoning: The result of the moderation process, containing the answer and reasoning.
    """

    if rules is None:
        rules = DEFAULT_RULES

    if moderator_model is None:
        moderator_model = DEFAULT_MODERATOR

    resume_text = (
        "Опыт работы: "
        + resume.experience
        + "\n"
        + "Желаемая должность: "
        + resume.job_title
        + "\n"
        + "Образование: "
        + resume.additional_education
        + "\n"
        + "ДПО: "
        + resume.additional_education
    )

    formatted_prompt = PROMPT.replace(
        "{rules}", "\n".join([rule.model_dump_json() for rule in rules])
    ).replace("{resume_text}", resume_text)

    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": formatted_prompt}],
        model=moderator_model,
    )

    answer_content = completion.choices[0].message.content

    print(answer_content)

    return parse_answer(answer_content)
