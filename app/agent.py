import json
import os
import re
from typing import Optional

from httpx import AsyncClient
from pydantic import BaseModel
from schemas import SpecialtyResult


class Specialty(BaseModel):
    """pydantic модель для специальности"""

    original_text: str
    code: Optional[str] = None
    name: Optional[str] = None


class SpecialtyNormalizer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://caila.io/api/adapters/openai/chat/completions"

    async def normalize(self, raw_text: str) -> Specialty:
        """Нормализуем: regex → LLM → fallback"""

        result = self._parse_with_regex(raw_text)

        if result:
            return Specialty(
                original_text=raw_text, code=result["code"], name=result["name"]
            )

        return await self._normalize_with_llm(raw_text)

    def _parse_with_regex(self, text: str) -> Optional[dict]:
        """Парсим регуляками"""
        code_match = re.search(r"(\d{2}\.\d{2}\.\d{2}|\d{5,})", text)
        if not code_match:
            return None

        code = code_match.group(1)

        digits = code.replace(".", "")
        if len(digits) == 6:
            code = f"{digits[0:2]}.{digits[2:4]}.{digits[4:6]}"

        name = text.replace(code_match.group(1), "", 1)

        name = re.sub(r"[;,\(\)]", " ", name)
        name = " ".join(name.split()).strip()

        if not name or name[0].isdigit():
            return None

        return {"code": code, "name": name}

    async def _normalize_with_llm(self, raw_text: str) -> Specialty:
        """Нормализуем с помощью LLM"""
        prompt = self._build_prompt(raw_text)

        try:
            async with AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "just-ai/t-tech-T-pro-it-1.0",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    },
                )

                if response.status_code == 200:
                    answer = response.json()["choices"][0]["message"]["content"]
                    return self._parse_response(answer, raw_text)
                else:
                    return self._create_fallback(raw_text)

        except Exception as e:
            print(f"Ошибка при запросе к LLM: {e}")
            return self._create_fallback(raw_text)

    def _build_prompt(self, raw_text: str) -> str:
        """Создаем промт"""
        return f"""
        Извлеки код и название специальности из текста: "{raw_text}"

        Правила:
        - Если есть несколько кодов, бери ПЕРВЫЙ
        - Название: только слова, без кодов
        - Если код или название не найдены, используй null

        Верни JSON:
        {{
            "code": "код или null",
            "name": "название или null",
        }}
        """

    def _parse_response(self, response_text: str, original_text: str) -> Specialty:
        """Парсим ответ от LLM"""
        try:
            json_match = re.search(r"\{.*?\}", response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return Specialty(
                    original_text=original_text,
                    code=data.get("code"),
                    name=data.get("name"),
                )
        except BaseException:
            pass

        return self._create_fallback(original_text)

    def _create_fallback(self, raw_text: str) -> Specialty:
        """В случае ошибки"""
        return Specialty(
            original_text=raw_text,
            name=raw_text,
        )


class SpecialtyMatcher:
    """Проверяем есть ли специальность в перечне"""

    def __init__(self, reference_file: str):
        self.specialties_list = self._load_specialties_list(reference_file)

    @staticmethod
    def _load_specialties_list(file_path: str) -> list:
        """Загружаем перечень специальностей, Файл txt"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл перечня {file_path} не найден")

        with open(file_path, "r", encoding="utf-8") as f:
            data = [line.strip() for line in f.readlines() if line.strip()]

        return data

    def find_match(self, specialty: Specialty) -> dict:
        "Ишем совпадение только по коду"
        if specialty.code:
            result = self._find_by_code(specialty.code)
            if result:
                return result

        return {"found": False, "matched_name": None, "method": "by_code"}

    def _find_by_code(self, code: str) -> dict | None:
        """Ищем по коду"""
        for speciality in self.specialties_list:
            if code in speciality:
                return {"found": True, "matched_name": speciality, "method": "by_code"}
        return None


async def agent_normalizer(
    specialty: str, api_key: str, specialties_path
) -> SpecialtyResult:
    """Нормализует специальность и проверяет её в перечне
    Args:
        specialty: Специальность которую ввел пользователь
        api_key: API ключ для LLM
        specialties_path: Путь к файлу с перечнем специальностей

    Returns:
        SpecialtyResult с результатом нормализации и поиска
    """
    normalizer = SpecialtyNormalizer(api_key)
    matcher = SpecialtyMatcher(specialties_path)

    normalized_specialty = await normalizer.normalize(specialty)
    match_result = matcher.find_match(normalized_specialty)

    return SpecialtyResult(
        original_text=normalized_specialty.original_text,
        code=normalized_specialty.code,
        name=normalized_specialty.name,
        found=match_result["found"],
        matched_name=match_result["matched_name"],
    )
