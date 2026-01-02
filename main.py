import uvicorn
from fastapi import FastAPI

from configs.config import FASTAPI_PORT
from configs.logging_config import setup_logging
from routers import router as moderation_router
from service.utils import kill_port

setup_logging()

app = FastAPI(
    title="LLM Resume Moderator API",
    description="Here is LLM Resume Moderator fastapi backend",
)

app.include_router(moderation_router)

if __name__ == "__main__":
    kill_port(FASTAPI_PORT)
    uvicorn.run(app, host="0.0.0.0", log_level="info", port=FASTAPI_PORT, reload=False)
