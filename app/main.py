import uvicorn
from fastapi import FastAPI

from utils import kill_port
from config import FASTAPI_PORT
from routers import router as moderation_router
from logger import LoggingMiddleware


app = FastAPI(title='LLM Resume Moderator API',
              description='Here is LLM Resume Moderator fastapi backend')

app.include_router(moderation_router)
app.add_middleware(LoggingMiddleware)

if __name__ == "__main__":
    kill_port(FASTAPI_PORT)
    uvicorn.run(app, host="0.0.0.0", log_level="info", port=FASTAPI_PORT, reload=False)
