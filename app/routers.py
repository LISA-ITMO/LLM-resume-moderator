from fastapi import APIRouter

from schemas import ResponseWithReasoning, ModerationContext
from manager import moderate

router = APIRouter(prefix='/moderator',
                   tags=['Moderator'])


@router.post('/answer')
async def moderation_resp(moderation_context: ModerationContext) -> ResponseWithReasoning:
    return await moderate(
        resume=moderation_context.resume,
        rules=moderation_context.rules,
        moderator_model=moderation_context.moderation_model
    )
