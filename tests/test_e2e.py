import subprocess
import time
from typing import Generator

import pytest
import requests

from configs.config import FASTAPI_PORT

BASE_URL = f"http://localhost:{FASTAPI_PORT}"


@pytest.fixture(scope="module")
def app_server() -> Generator[None, None, None]:
    """Запускает FastAPI приложение и останавливает его после тестов"""
    process = subprocess.Popen(
        ["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    for _ in range(30):
        try:
            if requests.get(f"{BASE_URL}/docs", timeout=1).status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        stdout, stderr = process.communicate()
        raise RuntimeError(
            f"Server failed to start on port {FASTAPI_PORT}.\n"
            f"STDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}"
        )
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        raise RuntimeError(f"Failed to start server: {stderr.decode()}")
    yield
    process.terminate()
    process.wait(timeout=5)


def test_full_moderation_pipeline(app_server):
    """E2E тест для полного пайплайна: загрузка диплома → модерация"""

    # --- Шаг 1: Загрузка файла диплома ---
    with open("tests/test_diploma.pdf", "rb") as f:
        files = {"file": ("Diploma.pdf", f, "application/pdf")}
        upload_response = requests.post(
            f"{BASE_URL}/moderator/reserve/upload-education-file",
            files=files,
            timeout=60,
        )

    assert (
        upload_response.status_code == 200
    ), f"Upload failed: {upload_response.status_code} — {upload_response.text}"

    upload_data = upload_response.json()
    assert "message" in upload_data, "No 'message' in upload response"
    assert (
        "educationFilename" in upload_data
    ), "No 'educationFilename' in upload response"

    uploaded_filename = upload_data["educationFilename"]
    print(f"✓ Diploma uploaded successfully: {uploaded_filename}")

    # --- Шаг 2: Полная модерация с указанием файла ---
    request_body = {
        "rules": [
            {
                "id": "rule_4",
                "condition": "Резюме должно быть заполнено на русском языке, допускаются инстранные термины для описанию профессиональных навыков и других особых случаев, данные на английском допустимы в пунктах Контактная информация, Близкие родственники, Образование, Навыки работы с компьютером, Опыт работы",
            },
            {
                "id": "rule_7",
                "condition": "Информация не должна содержать слова и выражения, не соответствующие нормам современного русского языка, допустимы стилистические неточности, но главное, чтобы не было матов и токсичности",
            },
        ],
        "resume": {
            "fullname": "Шилоносов Владимир Андреевич",
            "fullnameChange": "До 2019 года — Иванов Владимир Андреевич, смена фамилии при вступлении в брак",
            "citizenship": "Российская Федерация",
            "passportOrEquivalent": "45 01 №123456, выдан УФМС по г. Москве 12.05.2016",
            "snils": "123-456 00 11",
            "birthdate": "1998-07-22",
            "placeOfBirth": "г. Санкт-Петербург",
            "registrationAddress": "г. Санкт-Петербург, ул. Невский пр., д. 12, кв. 34",
            "actualResidenceAddress": "г. Санкт-Петербург, ул. Ленина, д. 5",
            "contactInformation": "+7 (921) 123-45-67, vladimir@mail.ru",
            "closeRelatives": [
                {
                    "relationship": "Отец",
                    "fullname": "Шилоносов Андрей Петрович",
                    "birthdate": "1968-05-22",
                    "job": "АО «Газпром», инженер",
                    "address": "г. Санкт-Петербург, ул. Ленина, д. 15, кв. 8",
                }
            ],
            "education": {
                "higherEducation": [
                    {
                        "dateOfAdmission": "2016-09-01",
                        "dateOfGraduation": "2020-06-30",
                        "institutionName": "Санкт-Петербургский государственный университет",
                        "specialty": "09.03.04 Программная инженерия",
                        "level": "Бакалавриат",
                        "formOfEducation": "Очная",
                        "year": 4,
                        "haveDiploma": True,
                    }
                ],
                "additionalEducation": [
                    {
                        "dateOfAdmission": "2016-09-01",
                        "dateOfGraduation": "2020-06-30",
                        "institutionName": "Санкт-Петербургский государственный университет",
                        "educationalProgram": "Data Science и машинное обучение",
                        "programType": "Повышение квалификации",
                        "hoursИumber": 144,
                    }
                ],
                "postgraduate": [
                    {
                        "dateOfAdmission": "2016-09-01",
                        "dateOfGraduation": "2020-06-30",
                        "institutionName": "Санкт-Петербургский государственный университет",
                        "specialty": "Информационные технологии",
                        "degree": "Кандидат технических наук",
                        "scienceBranch": "Технические науки",
                    }
                ],
            },
            "languges": [{"name": "Английский", "level": "SpeakFluently"}],
            "softwareSkills": [
                {
                    "type": "Текстовые редакторы",
                    "nameOfProduct": "Microsoft Word",
                    "level": "Fluent",
                }
            ],
            "publications": ["Применение ML в госуправлении"],
            "awards": ["Премия губернатора за успехи в учебе"],
            "militaryLiable": True,
            "militaryСategory": "Годен к военной службе",
            "professionalInterests": "Анализ данных, финансы, образование",
            "additionalInfo": "Ответственный, коммуникабельный, интересуюсь IT и саморазвитием",
            "motivation": "Хочу внести вклад в развитие Санкт-Петербурга и реализовать свой потенциал",
            "source": "Информация в вузе (центр карьеры, ярмарка вакансий)",
        },
        "moderation_model": "default",
        "educationFilename": uploaded_filename,  # ← важно: имя файла из загрузки
    }

    moderation_response = requests.post(
        "http://localhost:8000/moderator/reserve/selection",
        json=request_body,
        timeout=60,
    )

    assert (
        moderation_response.status_code == 200
    ), f"Moderation failed: {moderation_response.status_code} — {moderation_response.text}"

    data = moderation_response.json()

    # Проверяем обязательные поля
    required_fields = [
        "reasoning",
        "violatedRules",
        "docScanAnswer",
        "educationFromForm",
        "result",
        "timeMs",
    ]
    for field in required_fields:
        assert field in data, f"Field '{field}' is missing"

    # Проверяем типы
    assert isinstance(data["reasoning"], str), "reasoning must be string"
    assert isinstance(data["violatedRules"], list), "violatedRules must be list"
    assert isinstance(data["docScanAnswer"], dict), "docScanAnswer must be dict"
    assert isinstance(data["educationFromForm"], list), "educationFromForm must be list"
    assert isinstance(data["result"], dict), "result must be dict"
    assert isinstance(data["timeMs"], int), "timeMs must be int"

    # Проверяем структуру result
    result_fields = [
        "validEducationDocument",
        "educationMatch",
        "educationInList",
        "noViolatedRules",
        "overallSuccess",
    ]
    for field in result_fields:
        assert field in data["result"], f"Field '{field}' missing in result"
        assert isinstance(data["result"][field], bool), f"{field} must be boolean"

    # Проверяем, что всё прошло успешно (по умолчанию)
    assert (
        data["result"]["overallSuccess"] is True
    ), "Overall success expected to be True"
    assert len(data["violatedRules"]) == 0, "Expected no violated rules"

    # Проверяем docScanAnswer
    assert data["docScanAnswer"]["type"] == "Diploma", "Expected type 'Diploma'"
    assert isinstance(data["docScanAnswer"]["code"], str), "code must be string"
    assert isinstance(data["docScanAnswer"]["name"], str), "name must be string"

    # Проверяем educationFromForm (должен быть хотя бы один элемент)
    assert (
        len(data["educationFromForm"]) > 0
    ), "educationFromForm should contain at least one item"
    for edu in data["educationFromForm"]:
        assert "original_text" in edu, "original_text missing"
        assert "code" in edu, "code missing"
        assert "name" in edu, "name missing"

    # Проверяем время
    assert data["timeMs"] > 0, f"Expected positive timeMs, got {data['timeMs']}"

    print("\n✅ Full moderation pipeline passed successfully!")
    print(f"  - Reasoning length: {len(data['reasoning'])} chars")
    print(f"  - Violated rules: {len(data['violatedRules'])}")
    print(f"  - Overall success: {data['result']['overallSuccess']}")
    print(f"  - Time: {data['timeMs']} ms")
