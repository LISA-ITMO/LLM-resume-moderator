from fastapi import APIRouter

from schemas import ResponseWithReasoning, ModerationContext, SelectionContext
from manager import moderate
from resume_text_converter import resume_to_text

router = APIRouter(prefix='/moderator',
                   tags=['Moderator'])


@router.post('/answer')
async def moderation_resp(moderation_context: ModerationContext) -> ResponseWithReasoning:
    return await moderate(
        resume=moderation_context.resume,
        rules=moderation_context.rules,
        moderator_model=moderation_context.moderation_model
    )

@router.post("/reserve/selection")
async def reserve_selection(selection_context: SelectionContext):
    print(resume_to_text(selection_context.resume))
    return "hello)"