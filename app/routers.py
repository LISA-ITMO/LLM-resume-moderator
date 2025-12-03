from fastapi import APIRouter

from schemas import SelectionContext, FinalResponse
from manager import moderate

import time

from pydantic import BaseModel
from OCR import define_doc

router = APIRouter(prefix='/moderator',
                   tags=['Moderator'])


@router.post("/reserve/selection")
async def reserve_selection(selection_context: SelectionContext) -> FinalResponse:
    start_time = time.perf_counter()

    moderation_result = await moderate(
        resume=selection_context.resume,
        rules=selection_context.rules,
        moderator_model=selection_context.moderation_model
    )

    doc_answer = define_doc(selection_context.filename)

    end_time = time.perf_counter()
    time_ms = int((end_time - start_time) * 1000)

    return FinalResponse(
        reasoning=moderation_result.reasoning,
        result=moderation_result.result,
        time_ms=time_ms,
        doc_scan_answer=doc_answer
    )
