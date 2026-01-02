from httpx import AsyncClient
from openai import AsyncOpenAI

from configs.config import (
    MLP_API_KEY,
    PROVIDER_URL,
    MODELS_DICT,
    DEFAULT_MODERATOR,
    REASONING_MAPPING,
)


class LLMInterface:
    def __init__(self):
        self.reasoning_mapping = REASONING_MAPPING

        self.models_dict = MODELS_DICT
        self.default_moderator = DEFAULT_MODERATOR

        self.client = AsyncOpenAI(
            api_key=MLP_API_KEY,
            base_url=PROVIDER_URL,
            http_client=AsyncClient(proxy=None, timeout=600),
        )

    async def define_llm_reasoning(self, model_name: str) -> bool:

        provider_model_name = self.models_dict.get(model_name, model_name)

        if provider_model_name in self.reasoning_mapping:
            return self.reasoning_mapping[provider_model_name]

        response = await self.client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model=provider_model_name,
            max_tokens=1,
        )

        first_token = response.choices[0].message.content
        if first_token.startswith("<think>"):
            self.reasoning_mapping[model_name] = True
            return True
        else:
            self.reasoning_mapping[model_name] = False
            return False

    async def create_completions(
        self, prompt: str, reasoning_prompt: str = None, model_name: str = None
    ) -> str:

        if model_name is None:
            provider_model_name = self.models_dict.get(
                self.default_moderator, self.default_moderator
            )
        else:
            provider_model_name = self.models_dict.get(model_name, model_name)

        reasoning = await self.define_llm_reasoning(model_name)
        if reasoning and reasoning_prompt:
            prompt_to_model = reasoning_prompt
        else:
            prompt_to_model = prompt

        completion = await self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_to_model}],
            model=provider_model_name,
        )

        answer_content = completion.choices[0].message.content

        return answer_content


llm_interface = LLMInterface()
