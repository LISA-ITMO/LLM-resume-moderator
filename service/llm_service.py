import base64
import logging
import re
from datetime import date, timedelta
from io import BytesIO
from typing import Optional

from openai import AsyncOpenAI
from pdf2image import convert_from_path
from pydantic import BaseModel

from configs.required_specialties import required_specialties
from configs.settings import Settings
from configs.specialties import uni_spec
from routers.schemas import (
    Degree,
    EducationDocType,
    EducationInfo,
    EducationResolution,
    HigherEducation,
    NoValidReason,
    ResponseWithReasoning,
    Rule,
)

logger = logging.getLogger(__name__)

_MAX_PAGES = 3
_BASE64_RE = re.compile(r"(data:image/[^;]+;base64,)[A-Za-z0-9+/=]{40,}")


def _truncate_base64(text: str) -> str:
    return _BASE64_RE.sub(r"\1<base64 truncated>", text)


_SPECIALTIES_TEXT = "\n".join(f"{code}: {name}" for code, name in uni_spec.items())


class _EducationLLMResult(BaseModel):
    """Внутренняя модель структурированного ответа LLM по образованию.

    Не содержит resolution — он вычисляется отдельно по бизнес-правилам.
    fullNameMatches: None если ФИО не найдено в документе, иначе результат сравнения с анкетой.
    """

    isHigherEducation: bool
    fullName: Optional[str] = None
    fullNameMatches: Optional[bool] = None
    code: Optional[str] = None
    name: Optional[str] = None
    degree: Optional[Degree] = None
    docType: Optional[EducationDocType] = None
    expectedGraduationYear: Optional[int] = None


class LLMService:
    """Сервис для взаимодействия с LLM/VLM.

    Предоставляет две функции:
    - moderate_resume: проверка текста резюме на соответствие правилам
    - check_education: верификация документа об образовании через VLM

    Args:
        settings: Настройки приложения (base_url, api_key, model, timeout)

    Example:
        service = LLMService(settings)
        result = await service.moderate_resume(resume_text, rules)
        edu_info = await service.check_education(edu, "/app/storage/Diploma.pdf")
    """

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            timeout=settings.llm_timeout,
        )
        self._model = settings.llm_model

    async def moderate_resume(
        self, resume_text: str, rules: list[Rule]
    ) -> ResponseWithReasoning:
        """Проверяет текст резюме на соответствие правилам модерации.

        Args:
            resume_text: Форматированный текст резюме (из ResumeTextConverter)
            rules: Список правил модерации

        Returns:
            ResponseWithReasoning: Рассуждение и список нарушенных правил
        """
        rules_text = "\n".join(f"{r.id}. {r.condition}" for r in rules)

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты модератор резюме для государственного кадрового резерва. "
                        "Проверь резюме на соответствие каждому правилу. "
                        "Для каждого нарушенного правила укажи его id, условие и конкретный "
                        "фрагмент резюме, который нарушает правило. "
                        "Если нарушений нет — violatedRules должен быть пустым списком. "
                        "Верни строго валидный JSON без markdown: "
                        '{"reasoning": "...", "violatedRules": [{"id": "...", "condition": "...", "resume_fragment": "..."}]}'
                        " /no_think"
                    ),
                },
                {
                    "role": "user",
                    "content": f"ПРАВИЛА МОДЕРАЦИИ:\n{rules_text}\n\nРЕЗЮМЕ:\n{resume_text}",
                },
            ],
        )
        content = response.choices[0].message.content
        logger.debug("moderate_resume raw response: %s", content)
        return ResponseWithReasoning.model_validate_json(self._extract_json(content))

    async def check_education(
        self, edu: HigherEducation, file_path: str, resume_fullname: str
    ) -> EducationInfo:
        """Верифицирует документ об образовании через VLM.

        Если данные из анкеты противоречат документу — приоритет у документа.
        Код специальности берётся из uni_spec (если в документе другой код — ищем по названию).

        Args:
            edu: Запись о высшем образовании из анкеты
            file_path: Путь к PDF-файлу документа об образовании
            resume_fullname: ФИО владельца из анкеты для сверки с документом

        Returns:
            EducationInfo: Верифицированные данные об образовании с вердиктом

        Raises:
            Exception: Если PDF не читается или VLM вернул невалидный ответ
        """
        logger.info(
            "check_education start: resume_fullname=%r file=%r",
            resume_fullname,
            file_path,
        )
        pages = convert_from_path(file_path, dpi=150, last_page=_MAX_PAGES)
        image_contents = [self._page_to_content(page) for page in pages]

        edu_text = (
            f"ФИО из анкеты: {resume_fullname}\n"
            f"Специальность: {edu.specialty}\n"
            f"Уровень: {edu.level}\n"
            f"Учебное заведение: {edu.institutionName}\n"
            f"Период: {edu.dateOfAdmission} — {edu.dateOfGraduation}\n"
            f"Наличие диплома: {'Да' if edu.haveDiploma else 'Нет'}"
        )

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты эксперт по верификации документов об образовании. "
                        "Ты получаешь данные из анкеты и изображения документа. "
                        "Если данные из анкеты противоречат документу — доверяй документу. "
                        "Определи: является ли это высшим образованием (не СПО, не ДПО, не курсы — "
                        "только бакалавриат, магистратура, специалитет). "
                        "Тип документа: Diploma если диплом о завершённом высшем образовании, "
                        "Certificate если справка о прохождении (образование ещё не завершено), "
                        "null если не высшее. "
                        "Степень (degree): Bachelor, Master, Specialist или null если не высшее. "
                        "Найди стандартизованное название и код специальности из предоставленного списка. "
                        "Код должен быть из списка — если в документе другой код, найди по названию. "
                        "Если это Certificate — укажи предполагаемый год окончания в expectedGraduationYear. "
                        "Извлеки ФИО владельца документа точно как написано в документе в поле fullName "
                        "(null если ФИО не найдено). "
                        "Сравни ФИО из документа с ФИО из анкеты по следующим правилам: "
                        "1) учитывай разный регистр и родительный падеж; "
                        "2) если в анкете нет отчества — сравнивай только по фамилии и имени, отсутствие отчества не является несовпадением тоесть если в анкете или дипломе нет отчества то не проверяй отчкство а смотри имя и фамилию "
                        "3) если владелец документа — женщина (определяй по имени и отчеству)тк фамилия может отличаться (девичья фамилия) "
                        "то сравнивай по имени и отчеству (фамилия могла измениться после замужества); "
                        "если совпадают — fullNameMatches = true, иначе false; если ФИО не найдено в документе — null. "
                        "Верни строго валидный JSON без markdown: "
                        '{"isHigherEducation": true/false, '
                        '"fullName": "Фамилия Имя Отчество" or null, '
                        '"fullNameMatches": true/false/null, '
                        '"code": "01.03.02" or null, '
                        '"name": "Название" or null, '
                        '"degree": "Bachelor"/"Master"/"Specialist" or null, '
                        '"docType": "Diploma"/"Certificate" or null, '
                        '"expectedGraduationYear": 2026 or null}'
                        " /no_think"
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"ДАННЫЕ ИЗ АНКЕТЫ:\n{edu_text}\n\n"
                                f"СПИСОК СПЕЦИАЛЬНОСТЕЙ (код: название):\n{_SPECIALTIES_TEXT}\n\n"
                                "Проанализируй документ на изображениях и верни структурированный ответ."
                            ),
                        },
                        *image_contents,
                    ],
                },
            ],
        )

        content = response.choices[0].message.content
        logger.info("check_education raw response: %s", _truncate_base64(content or ""))
        result = _EducationLLMResult.model_validate_json(self._extract_json(content))
        logger.info(
            "check_education parsed: fullName=%r fullNameMatches=%r",
            result.fullName,
            result.fullNameMatches,
        )
        resolution = self._compute_resolution(result)

        return EducationInfo(
            isHigherEducation=result.isHigherEducation,
            fullName=result.fullName,
            code=result.code,
            name=result.name,
            degree=result.degree,
            docType=result.docType,
            expectedGraduationYear=result.expectedGraduationYear,
            resolution=resolution,
        )

    def _compute_resolution(self, result: _EducationLLMResult) -> EducationResolution:
        """Вычисляет вердикт по результату LLM на основе бизнес-правил.

        Args:
            result: Структурированный ответ LLM

        Returns:
            EducationResolution: Вердикт с причиной невалидности (если есть)
        """
        if not result.isHigherEducation:
            return EducationResolution(
                valid=False, noValidReason=NoValidReason.NotHigherEducation
            )

        if result.fullName is None:
            return EducationResolution(
                valid=False, noValidReason=NoValidReason.FullNameMissing
            )

        if result.fullNameMatches is False:
            return EducationResolution(
                valid=False, noValidReason=NoValidReason.FullNameMismatch
            )

        if result.code is None and result.name is None:
            return EducationResolution(
                valid=False, noValidReason=NoValidReason.SpecialtyNotFound
            )

        if result.name not in required_specialties:
            return EducationResolution(
                valid=False, noValidReason=NoValidReason.SpecialtyNotInList
            )

        if (
            result.docType == EducationDocType.Certificate
            and result.expectedGraduationYear is not None
        ):
            cutoff_year = (date.today() + timedelta(days=548)).year  # ~1.5 года
            if result.expectedGraduationYear > cutoff_year:
                return EducationResolution(
                    valid=False, noValidReason=NoValidReason.CertificateTooFar
                )

        return EducationResolution(valid=True)

    @staticmethod
    def _extract_json(text: str) -> str:
        """Извлекает JSON из ответа модели, убирая markdown и think-теги.

        Args:
            text: Текст ответа LLM (может содержать ```json...``` или <think>...</think>)

        Returns:
            str: Чистая JSON-строка
        """
        if not text:
            return text
        # убираем <think>...</think>
        text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
        # markdown code block
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            return match.group(1).strip()
        # просто ищем первый { ... последний }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return text[start:end]
        return text

    @staticmethod
    def _page_to_content(page) -> dict:
        """Конвертирует страницу PDF в base64 image_url для OpenAI API.

        Args:
            page: PIL Image объект страницы

        Returns:
            dict: Контент-блок формата OpenAI vision API
        """
        buffer = BytesIO()
        page.save(buffer, format="JPEG")
        b64 = base64.b64encode(buffer.getvalue()).decode()
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        }
