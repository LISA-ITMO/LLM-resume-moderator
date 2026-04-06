from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения / .env файла.

    Args:
        app_port: Порт FastAPI-сервера
        root_path: Root path для FastAPI (например /llm-resume-moderator)
        storage_dir: Директория для хранения загруженных файлов
        llm_base_url: Base URL LLM-провайдера (OpenAI-совместимый)
        llm_api_key: API-ключ LLM-провайдера
        llm_model: Название модели
        llm_timeout: Таймаут запроса в секундах

    Example:
        APP_PORT=8001
        ROOT_PATH=/llm-resume-moderator
        STORAGE_DIR=storage
        LLM_BASE_URL=http://localhost:8000/v1
        LLM_API_KEY=your-key
        LLM_MODEL=default
        LLM_TIMEOUT=120
    """

    app_port: int = 8001
    root_path: str = ""
    storage_dir: str = "storage"

    llm_base_url: str = "http://localhost:8000/v1"
    llm_api_key: str = ""
    llm_model: str = "default"
    llm_timeout: int = 120

    max_file_size: int = 20 * 1024 * 1024
    default_moderator: str = "default"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Загружает и кэширует настройки из .env.

    Returns:
        Settings: Объект с настройками приложения
    """
    return Settings()
