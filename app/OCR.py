import pdf2image
from paddleocr import PPStructureV3
from collections import defaultdict
import re
from slovar import uni_spec
from pydantic import BaseModel

class Doc(BaseModel):
    type : str = ''
    code : str = '-1'
    name : str = '-1'

def define_spec(uni_spec, cifr_spec):
    return uni_spec[cifr_spec]

def define_doc(filename) -> Doc:
    answer = Doc()
    pdf_document = filename
    pages = pdf2image.convert_from_path(pdf_document, dpi=200)
    for i, image in enumerate(pages):
        image.save(f"page_{i+1}.jpg", "JPEG")


    pipeline = PPStructureV3(
        lang='ru',  # или 'cyrillic'
        device='cpu'
    )

    data = defaultdict(str)

    text = ''
    for ind in range(len(pages)):
        result = pipeline.predict(f"page_{ind+1}.jpg")
        data_page = result[0]
        parsing_list = data_page['parsing_res_list']
        all_content = []
        for block in parsing_list:
            content_text = block.content
            if content_text:
                cleaned_text = content_text.strip()
                if cleaned_text:
                    all_content.append(cleaned_text)

        for block in all_content:
            text += block

    #номер направления
    matches = re.findall(r'\d{2}\.\d{2}\.\d{2}', text)
    if len(matches) == 0: #не нашел цифры
        answer.type = 'Ни диплом, ни справка'
        return answer
    dictttt = defaultdict(int)
    for el in matches:
        dictttt[el] += 1
    cifr_napr = max(dictttt, key=dictttt.get)
    name_napr = define_spec(uni_spec, cifr_napr)

    #определение типа документа
    if 'диплом' in text.lower():
        answer.type = 'Это диплом'
    if 'справка' in text.lower():
        answer.type = 'Это справка'
    answer.code = f'Код направления: {cifr_napr}'
    answer.name = f'Название направления: {name_napr}'
    return answer

print(define_doc('Diploma.pdf'))