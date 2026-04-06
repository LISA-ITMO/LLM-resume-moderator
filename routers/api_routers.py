import logging

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from service.document_service import DocumentValidationError
from routers.schemas import (
    BusynessErrorResponse,
    FinalResponse,
    SelectionContext,
    UploadFileResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/moderator", tags=["Moderator"])


@router.post(
    "/reserve/upload-education-file",
    summary="Загрузка PDF документа об образовании",
    responses={
        200: {"model": UploadFileResponse, "description": "Файл успешно загружен"},
        422: {
            "model": BusynessErrorResponse,
            "description": "Ошибка загрузки или валидации файла (если документ не pdf или больше 20 МБ)",
        },
    },
)
async def upload_education_file(request: Request, file: UploadFile = File(...)):
    """Загружает и сохраняет PDF-документ об образовании.

    Args:
        file: PDF-файл для загрузки (не более 20 МБ)
        request: FastAPI Request для доступа к app.state

    Returns:
        UploadFileResponse: Имя сохранённого файла

    Raises:
        JSONResponse 422: Если файл не является PDF, пустой или превышает 20 МБ

    Example:
        POST /moderator/reserve/upload-education-file
        Content-Type: multipart/form-data
    """
    try:
        filename = await request.app.state.document_service.save_pdf(file)
    except DocumentValidationError as e:
        return JSONResponse(
            status_code=422,
            content=BusynessErrorResponse(message=str(e)).model_dump(mode="json"),
        )

    logger.info("Education file uploaded", extra={"doc_filename": filename})
    return {"message": "Файл успешно загружен", "educationFilename": filename}


@router.post(
    "/reserve/selection",
    summary="Ручка для прохождения отбора в студенческий резерв",
    responses={
        200: {
            "model": FinalResponse,
            "description": "Ответ в случае если сервис отработал успешно",
        },
        422: {
            "model": BusynessErrorResponse,
            "description": "Документ об образовании не найден",
        },
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def reserve_selection(selection_context: SelectionContext, request: Request):
    """Запускает полный цикл отбора кандидата в студенческий резерв.

    Args:
        selection_context: Контекст отбора (резюме, правила, файлы дипломов)
        request: FastAPI Request для доступа к app.state

    Returns:
        FinalResponse: Полный результат проверки со всеми критериями отбора

    Raises:
        JSONResponse 422: Если файл диплома не найден
        HTTPException 500: При ошибке выполнения сервисов

    Example:
        POST /moderator/reserve/selection
        Body: SelectionContext(resume=..., educationFilename="Diploma.pdf")
    """
    try:
        return await request.app.state.selection_service.run(selection_context)
    except DocumentValidationError as e:
        return JSONResponse(
            status_code=422,
            content=BusynessErrorResponse(message=str(e)).model_dump(mode="json"),
        )
    except Exception as e:
        logger.error("Selection pipeline failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
