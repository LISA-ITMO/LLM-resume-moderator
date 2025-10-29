from fastapi import APIRouter

from schemas import ResponseWithReasoning, SelectionContext
from manager import moderate

router = APIRouter(prefix='/moderator',
                   tags=['Moderator'])


@router.post("/reserve/selection")
async def reserve_selection(selection_context: SelectionContext):
    return await moderate(
        resume=selection_context.resume,
        rules=selection_context.rules,
        moderator_model=selection_context.moderation_model
    )