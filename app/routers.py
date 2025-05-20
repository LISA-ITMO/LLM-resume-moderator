from fastapi import APIRouter

from schemas import ResponseWithReasoning, ModerationContext
from manager import moderate

router = APIRouter(prefix="/moderator", tags=["Moderator"])


@router.post("/answer")
async def moderation_resp(
    moderation_context: ModerationContext,
) -> ResponseWithReasoning:
    """
    Handles a moderation request and returns the response with reasoning.

        Args:
            moderation_context: The context containing the resume, rules, and
                moderator model for moderation.

        Returns:
            ResponseWithReasoning: The result of the moderation process, including
                the response and any associated reasoning.
    """
    return await moderate(
        resume=moderation_context.resume,
        rules=moderation_context.rules,
        moderator_model=moderation_context.moderation_model,
    )
