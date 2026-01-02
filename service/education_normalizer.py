import json
import re
from typing import Optional, List

from pydantic import BaseModel

from schemas import SpecialtyResult, ResumeToGovernment
from configs.slovar import uni_spec
from service.llm_interface import llm_interface


class Specialty(BaseModel):
    """pydantic модель для специальности"""

    original_text: str
    code: Optional[str] = None
    name: Optional[str] = None


class SpecialtyNormalizer:

    async def normalize(self, raw_text: str, agent_model_name: str = None) -> Specialty:
        """Нормализуем: regex → LLM → fallback"""

        result = self._parse_with_regex(raw_text)

        if result:
            return Specialty(
                original_text=raw_text, code=result["code"], name=result["name"]
            )

        return await self._normalize_with_llm(raw_text, agent_model_name)

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

    async def _normalize_with_llm(
        self, raw_text: str, agent_model_name: str = None
    ) -> Specialty:
        """Нормализуем с помощью LLM"""
        prompt = self._build_prompt(raw_text)

        try:
            answer = await llm_interface.create_completions(
                prompt=prompt, model_name=agent_model_name
            )
            return self._parse_response(answer, raw_text)
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

    def __init__(self):
        self.specialites_by_code = uni_spec
        self.specialties_by_name = {
            name.lower(): code for code, name in uni_spec.items()
        }

    def find_match(self, specialty: Specialty) -> dict:
        "Ишем совпадение по коду или имени"
        if specialty.code:
            result = self._find_by_code(specialty.code)
            if result:
                return result
        if specialty.name:
            result = self._find_by_name(specialty.name)
            if result:
                return result

        return {"found": False, "matched_name": None, "method": "by_code_and_name"}

    def _find_by_code(self, code: str) -> dict | None:
        """Ищем по коду"""
        if code in self.specialites_by_code:
            name = self.specialites_by_code[code]
            return {"code": code, "name": name}

    def _find_by_name(self, name: str) -> dict | None:
        """Ищем по имени"""
        if name in self.specialties_by_name:
            code = self.specialties_by_name[name.lower()]
            return {"code": code, "name": name}


async def agent_normalizer(
    specialty: str, agent_model_name: str = None
) -> SpecialtyResult:
    """Нормализует специальность и проверяет её в перечне
    Args:
        specialty: Специальность которую ввел пользователь
        agent_model_name: имя модели агента, который будет стандартизовать специальность
    Returns:
        SpecialtyResult с результатом нормализации и поиска
    """
    normalizer = SpecialtyNormalizer()
    matcher = SpecialtyMatcher()

    normalized_specialty = await normalizer.normalize(specialty, agent_model_name)
    match_result = matcher.find_match(normalized_specialty)

    return SpecialtyResult(
        original_text=normalized_specialty.original_text,
        code=match_result["code"] if match_result else None,
        name=match_result["name"] if match_result else None,
    )


async def check_resume_specialties(
    resume: ResumeToGovernment, agent_model_name: str = None
) -> List[SpecialtyResult]:
    """Проверяет специальности из резюме через агент нормализации"""
    specialties_results = []

    if resume.education and resume.education.higherEducation:
        for edu in resume.education.higherEducation:
            if edu.specialty:
                specialty_result = await agent_normalizer(
                    specialty=edu.specialty, agent_model_name=agent_model_name
                )
                specialties_results.append(specialty_result)

    return specialties_results
