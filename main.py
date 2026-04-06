import logging
import signal
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from configs.settings import get_settings
from routers.api_routers import router as moderation_router
from service.document_service import DocumentService
from service.llm_service import LLMService
from service.resume_text_converter import ResumeTextConverter
from service.selection_service import SelectionService

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения.

    Инициализирует сервисы при старте и освобождает ресурсы при остановке.
    При ошибке инициализации отправляет SIGTERM.

    Args:
        app: Экземпляр FastAPI-приложения
    """
    try:
        app.state.settings = settings
        document_service = DocumentService(settings)
        llm_service = LLMService(settings)
        resume_text_converter = ResumeTextConverter()
        app.state.document_service = document_service
        app.state.selection_service = SelectionService(
            document_service, llm_service, resume_text_converter
        )
        yield

    except Exception:
        logger.error("An error occurred during startup", exc_info=True, stack_info=True)
        signal.raise_signal(signal.SIGTERM)


app = FastAPI(lifespan=lifespan, root_path=settings.root_path)
app.include_router(moderation_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.app_port)
