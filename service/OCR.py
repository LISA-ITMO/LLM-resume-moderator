import re
import logging
import os
import glob

import pdf2image
from paddleocr import PaddleOCR

from configs.slovar import uni_spec
from schemas import Doc, EducationDocType
from configs.config import STORAGE_DIR
from service.llm_interface import llm_interface
from service.education_normalizer import education_matcher, Specialty


class OCRService:

    def __init__(self):
        self.pipeline = PaddleOCR(
            text_detection_model_name="PP-OCRv5_mobile_det",
            text_recognition_model_name="cyrillic_PP-OCRv5_mobile_rec",
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
            lang="ru",
            use_textline_orientation=False,
        )
        self.logger = logging.getLogger(name=__name__)

    def define_spec(self, uni_spec, cifr_spec):
        return uni_spec[cifr_spec]

    async def define_doc(self, filename) -> Doc:
        text_parts = []
        try:
            filename_stem = filename.split(".")[0]
            pdf_document = f"{STORAGE_DIR}/{filename}"
            pages = pdf2image.convert_from_path(pdf_document, dpi=200)
            for i, image in enumerate(pages):
                image.save(f"{STORAGE_DIR}/{filename_stem}_page_{i + 1}.jpg", "JPEG")
            for ind in range(len(pages)):
                result = self.pipeline.predict(
                    f"{STORAGE_DIR}/{filename_stem}_page_{ind + 1}.jpg"
                )
                data_page = result[0]
                parsing_list = data_page["rec_texts"]
                text_parts.append(" ".join(parsing_list))
                text = "\n\n".join(text_parts)
                partial_doc = await self._define_doc_by_text(text)
                if partial_doc.type in (
                    EducationDocType.DIPLOMA,
                    EducationDocType.HIGHER_EDU_СERT,
                ):
                    return partial_doc

                self.logger.info(
                    f"Отсканирована {ind + 1} страница документа об образовании"
                )
        except Exception as e:
            self.logger.error(
                f"Ошибка при распознавании текста документа об образовании: {e}"
            )
        finally:
            pattern = os.path.join(STORAGE_DIR, f"{filename_stem}*")
            for file_path in glob.glob(pattern):
                os.remove(file_path)

        return await self._define_doc_by_text(text)

    async def _define_old_diploma(self, text: str) -> Doc:
        if not (
            "диплом" in text.lower()
            and "о высшем образовании" in text.lower().replace("\n", "")
        ):
            return Doc(type=EducationDocType.OTHER)

        education_str = (
            (
                await llm_interface.create_completions(
                    "Вычлени строку о специальности из запроса и укажи ее в ответе\n\n"
                    f"Запрос: {text}\n"
                )
            )
            .split("</think>\n\n")[-1]
            .strip()
        )
        formated_education = await education_matcher.find_match(
            Specialty(original_text=education_str)
        )
        if not formated_education["found"]:
            return Doc(type=EducationDocType.OTHER)

        return Doc(
            type=EducationDocType.DIPLOMA,
            code=formated_education["code"],
            name=formated_education["name"],
        )

    async def _define_doc_by_text(self, text: str) -> Doc:
        answer = Doc(type=EducationDocType.OTHER)
        matches = re.findall(r"\d{2}\.\d{2}\.(?!20)\d{2}", text)

        for el in matches:
            if el in uni_spec:
                name_napr = self.define_spec(uni_spec, el)
                cifr_napr = el
                break
        else:
            return await self._define_old_diploma(text)

        if "справка" in text.lower():
            answer.type = EducationDocType.HIGHER_EDU_СERT
        elif "диплом" in text.lower():
            answer.type = EducationDocType.DIPLOMA
        answer.code = cifr_napr
        answer.name = name_napr
        return answer


ocr_service = OCRService()
