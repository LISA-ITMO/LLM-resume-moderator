import asyncio
import logging
import os

from fastapi import UploadFile
from pdf2image import convert_from_bytes

from configs.settings import Settings

logger = logging.getLogger(__name__)


class DocumentValidationError(ValueError):
    """Ошибка валидации загружаемого документа."""


class DocumentService:
    """Сервис загрузки и хранения документов.

    Валидирует и сохраняет PDF-файлы на диск.

    Args:
        settings: Настройки приложения (storage_dir, max_file_size)

    Example:
        service = DocumentService(settings)
        await service.save_pdf(file)  # raises DocumentValidationError on failure
    """

    def __init__(self, settings: Settings) -> None:
        self._storage_dir = settings.storage_dir
        self._max_file_size = settings.max_file_size

    async def save_pdf(self, file: UploadFile) -> str:
        """Валидирует и сохраняет PDF-файл.

        Args:
            file: Загружаемый файл

        Returns:
            str: Имя сохранённого файла

        Raises:
            DocumentValidationError: Если файл не прошёл валидацию
        """
        logger.debug("save_pdf: start, filename=%s", file.filename)

        if not file.filename.lower().endswith(".pdf"):
            raise DocumentValidationError("Разрешены только PDF файлы")

        logger.debug("save_pdf: reading file bytes")
        file_bytes = await file.read()
        logger.debug("save_pdf: read %d bytes", len(file_bytes))

        if len(file_bytes) == 0:
            raise DocumentValidationError("Файл пустой")

        if len(file_bytes) > self._max_file_size:
            raise DocumentValidationError("Размер файла превышает 20 МБ")
        logger.debug("save_pdf: calling convert_from_bytes")
        try:
            await asyncio.to_thread(
                convert_from_bytes, file_bytes, dpi=50, first_page=1, last_page=1
            )
        except Exception as e:
            raise DocumentValidationError(
                f"Файл не является валидным PDF документом, {e}"
            )
        logger.debug("save_pdf: convert_from_bytes done")

        os.makedirs(self._storage_dir, exist_ok=True)
        file_path = os.path.join(self._storage_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        logger.info("PDF saved", extra={"doc_filename": file.filename})
        return file.filename

    def exists(self, filename: str) -> bool:
        """Проверяет наличие файла в хранилище.

        Args:
            filename: Имя файла

        Returns:
            bool: True если файл существует
        """
        return os.path.exists(os.path.join(self._storage_dir, filename))

    def delete(self, filename: str) -> None:
        """Удаляет файл из хранилища.

        Args:
            filename: Имя файла
        """
        path = os.path.join(self._storage_dir, filename)
        try:
            os.remove(path)
            logger.info("PDF deleted", extra={"doc_filename": filename})
        except FileNotFoundError:
            logger.warning("PDF not found on delete", extra={"doc_filename": filename})

    def get_path(self, filename: str) -> str:
        """Возвращает полный путь к файлу в хранилище.

        Args:
            filename: Имя файла

        Returns:
            str: Абсолютный путь к файлу
        """
        return os.path.join(self._storage_dir, filename)
