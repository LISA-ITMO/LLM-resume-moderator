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
        self.grouped_unispec = self._group_specialties_by_category(uni_spec)

    def _group_specialties_by_category(self, uni_spec: dict) -> dict:
        grouped = {}
        last_prefix = None
        for code, name in uni_spec.items():
            if (not last_prefix) or code[:2] != last_prefix:
                last_prefix = code[:2]
                category_key = f"{last_prefix}: {name}"
                grouped[category_key] = {code: name}
            else:
                grouped[category_key][code] = name

        return grouped

    async def find_match(self, specialty: Specialty) -> dict:
        "Ишем совпадение по коду или имени"
        if specialty.code:
            result = self._find_by_code(specialty.code)
            if result["found"]:
                return result
        if specialty.name:
            result = self._find_by_name(specialty.name)
            if result["found"]:
                return result

        return await self._find_specialty_with_llm(specialty.original_text)

    def _find_by_code(self, code: str) -> dict | None:
        """Ищем по коду"""
        if code in self.specialites_by_code:
            name = self.specialites_by_code[code]
            return {"found": True, "code": code, "name": name}
        else:
            return {"found": False, "code": None, "name": None}

    def _find_by_name(self, name: str) -> dict | None:
        """Ищем по имени"""
        if name.lower() in self.specialties_by_name:
            code = self.specialties_by_name[name.lower()]
            return {"found": True, "code": code, "name": name}
        else:
            return {"found": False, "code": None, "name": None}

    async def _find_specialty_with_llm(self, query: str) -> dict:
        """
        Двухэтапный поиск образовательной программы.
        На первом этапе LLM определяет укрупнённое направление (2 цифры) либо
        возвращает NONE, если запрос не относится к образовательным направлениям.
        На втором этапе LLM выбирает конкретный код образовательной программы.
        """
        stage1_prompt = (
            "Определи, относится ли запрос к образовательному направлению.\n"
            "Если не относится — ответь строго: NONE\n"
            "Если относится — ответь строго двумя цифрами начала кода "
            "укрупнённого направления (например: 01, 02, 03).\n"
            "Отвечай не думая и если будет несколько вариантов выдавай первый.\n\n"
            f"Запрос: {query}\n"
            f"Доступные направления:\n" + "\n".join(self.grouped_unispec.keys())
        )

        stage1_response: str = (
            (await llm_interface.create_completions(stage1_prompt))
            .split("</think>\n\n")[-1]
            .strip()
        )

        if stage1_response == "NONE":
            return {"found": False, "code": None, "name": None}

        prefix: str = stage1_response
        category_key: str | None = None

        for key in self.grouped_unispec.keys():
            if key.startswith(prefix):
                category_key = key
                break

        if category_key is None:
            return {"found": False, "code": None, "name": None}

        programs: dict[str, str] = self.grouped_unispec[category_key]

        stage2_prompt = (
            "Выбери наиболее подходящую образовательную программу.\n"
            "Ответь строго кодом образовательной программы.\n"
            "Отвечай не думая и если будет несколько вариантов выдавай первый.\n\n"
            f"Запрос: {query}\n"
            "Варианты:\n"
            + "\n".join(f"{code} — {name}" for code, name in programs.items())
        )

        stage2_response: str = (
            (await llm_interface.create_completions(stage2_prompt))
            .split("</think>\n\n")[-1]
            .strip()
        )

        if stage2_response not in programs:
            return {"found": False, "code": None, "name": None}

        return {
            "found": True,
            "code": stage2_response,
            "name": programs[stage2_response],
        }


speciality_normalizer = SpecialtyNormalizer()
education_matcher = SpecialtyMatcher()


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

    normalized_specialty = await speciality_normalizer.normalize(
        specialty, agent_model_name
    )
    match_result = await education_matcher.find_match(normalized_specialty)

    return SpecialtyResult(
        original_text=normalized_specialty.original_text,
        code=match_result["code"] if match_result["found"] else None,
        name=(
            match_result["name"].lower().capitalize() if match_result["found"] else None
        ),
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
