import logging
import time
from uuid import uuid4

from routers.schemas import (
    FinalResponse,
    SelectionContext,
    SelectionResults,
)
from service.document_service import DocumentService, DocumentValidationError
from service.llm_service import LLMService
from service.resume_text_converter import ResumeTextConverter

logger = logging.getLogger(__name__)


class SelectionService:
    """Оркестратор пайплайна отбора кандидата в студенческий резерв.

    Координирует проверку резюме и верификацию документов об образовании.

    Args:
        document_service: Сервис работы с файлами
        llm_service: Сервис взаимодействия с LLM/VLM
        resume_text_converter: Конвертер резюме в текст

    Example:
        service = SelectionService(document_service, llm_service, resume_text_converter)
        result = await service.run(selection_context)
    """

    def __init__(
        self,
        document_service: DocumentService,
        llm_service: LLMService,
        resume_text_converter: ResumeTextConverter,
    ) -> None:
        self._document_service = document_service
        self._llm_service = llm_service
        self._resume_text_converter = resume_text_converter

    async def run(self, context: SelectionContext) -> FinalResponse:
        """Запускает полный цикл отбора кандидата.

        Args:
            context: Контекст отбора (резюме, правила, файлы дипломов)

        Returns:
            FinalResponse: Полный результат проверки

        Raises:
            DocumentValidationError: Если файл диплома не найден
        """
        trace = uuid4()
        start_time = time.perf_counter()

        higher_educations = context.resume.education.higherEducation
        for edu in higher_educations:
            if edu.educationFilename and not self._document_service.exists(
                edu.educationFilename
            ):
                raise DocumentValidationError(
                    f"Файл диплома не найден: {edu.educationFilename}"
                )

        resume_text = self._resume_text_converter.convert(context.resume)

        moderation_result = await self._llm_service.moderate_resume(
            resume_text=resume_text,
            rules=context.rules,
        )

        education_info = []
        for edu in higher_educations:
            if not edu.educationFilename:
                continue
            file_path = self._document_service.get_path(edu.educationFilename)
            info = await self._llm_service.check_education(edu=edu, file_path=file_path)
            education_info.append(info)
            self._document_service.delete(edu.educationFilename)

        time_ms = int((time.perf_counter() - start_time) * 1000)

        valid_education_found = any(info.resolution.valid for info in education_info)
        no_violated_rules = len(moderation_result.violatedRules) == 0
        overall_success = valid_education_found and no_violated_rules

        logger.info(
            "Selection completed",
            extra={
                "trace": str(trace),
                "time_ms": time_ms,
                "overall_success": overall_success,
            },
        )

        return FinalResponse(
            reasoning=moderation_result.reasoning,
            violatedRules=moderation_result.violatedRules,
            educationInfo=education_info,
            result=SelectionResults(
                validEducationFound=valid_education_found,
                noViolatedRules=no_violated_rules,
                overallSuccess=overall_success,
            ),
            timeMs=time_ms,
        )
