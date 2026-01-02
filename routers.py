import os
import time

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from pdf2image import convert_from_bytes

from configs.config import MAX_FILE_SIZE, STORAGE_DIR
from configs.required_specialties import required_specialties
from schemas import BusynessErrorResponse, EducationDocType, FinalResponse, SelectionResults, SelectionContext, UploadFileResponse
from service.education_normalizer import check_resume_specialties
from service.OCR import ocr_service
from service.rules_moderator import moderate

router = APIRouter(prefix="/moderator", tags=["Moderator"])


@router.post(
    "/reserve/upload-education-file",
    summary="Загрузка PDF документа об образовании",
    responses={
        200: {"model": UploadFileResponse, "description": "Файл успешно загружен"},
        422: {"model": BusynessErrorResponse, "description": "Ошибка загрузки или валидации файла (если документ не pdf или больше 20 МБ)"},
    },
)
async def upload_education_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=422,
            content=BusynessErrorResponse(message="Разрешены только PDF файлы").model_dump(mode='json')
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=422,
            content=BusynessErrorResponse(message="Размер файла превышает 20 МБ").model_dump(mode='json')
        )

    if len(file_bytes) == 0:
        return JSONResponse(
            status_code=422,
            content=BusynessErrorResponse(message="Файл пустой").model_dump(mode='json')
        )

    try:
        convert_from_bytes(
            file_bytes,
            dpi=50,
            first_page=1,
            last_page=1
        )
    except Exception:
        return JSONResponse(
            status_code=422,
            content=BusynessErrorResponse(message="Файл не является валидным PDF документом").model_dump(mode='json')
        )

    os.makedirs(STORAGE_DIR, exist_ok=True)
    file_path = os.path.join(STORAGE_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return {
        "message": "Файл успешно загружен",
        "educationFilename": file.filename
    }


@router.post(
    "/reserve/selection",
    summary="Ручка для прохождения отбора в студенческий резерв",
    responses={
        200: {'model': FinalResponse, "description": "Ответ в случае если сервис отработал успешно"},
        422: {'model': BusynessErrorResponse, "description": "Ответ документ об образовании не найден"}
    }
)
async def reserve_selection(selection_context: SelectionContext):
    start_time = time.perf_counter()

    if not os.path.exists(f"{STORAGE_DIR}/{selection_context.educationFilename}"):
        return JSONResponse(
            status_code=422,
            content=BusynessErrorResponse(
                message="Файл диплома не найден"
            ).model_dump(mode='json')
        )

    moderation_result = await moderate(
        resume=selection_context.resume,
        rules=selection_context.rules,
        moderator_model=selection_context.moderation_model,
    )

    speciality_result = await check_resume_specialties(selection_context.resume, agent_model_name=selection_context.moderation_model)

    doc_answer = ocr_service.define_doc(selection_context.educationFilename)

    end_time = time.perf_counter()
    time_ms = int((end_time - start_time) * 1000)

    valid_education_document = doc_answer.type in (EducationDocType.DIPLOMA, EducationDocType.HIGHER_EDU_СERT)
    education_match = speciality_result and (doc_answer.code == speciality_result[0].code or doc_answer.name == speciality_result[0].name)
    education_in_list = doc_answer.name in required_specialties or (speciality_result and speciality_result[0].name in required_specialties)
    no_violated_rules = len(moderation_result.violatedRules) == 0
    overall_success = valid_education_document and education_match and education_in_list and no_violated_rules

    return FinalResponse(
        reasoning=moderation_result.reasoning,
        violatedRules=moderation_result.violatedRules,
        docScanAnswer=doc_answer,
        educationFromForm=speciality_result,
        result=SelectionResults(
            validEducationDocument=valid_education_document,
            educationMatch=education_match,
            educationInList=education_in_list,
            noViolatedRules=no_violated_rules,
            overallSuccess=overall_success
        ),
        timeMs=time_ms
    )
