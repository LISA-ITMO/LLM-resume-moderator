import subprocess
import time
from typing import Generator

import pytest
import requests


@pytest.fixture(scope="module")
def app_server() -> Generator[None, None, None]:
    """Запускает FastAPI приложение и останавливает его после тестов"""
    # Запускаем приложение
    process = subprocess.Popen(
        ["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Даем время на запуск сервера
    time.sleep(3)

    # Проверяем, что процесс запустился
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        raise RuntimeError(f"Failed to start server: {stderr.decode()}")

    yield

    # Останавливаем приложение после тестов
    process.terminate()
    process.wait(timeout=5)


def test_reserve_selection_success(app_server):
    """E2E тест для POST /moderator/reserve/selection"""

    # Подготавливаем тело запроса
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
                        "specialty": "01.03.02 Прикладная математика и информатика",
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
        "moderation_model": "T_it_1_0",
    }

    # Отправляем POST запрос
    response = requests.post(
        "http://localhost:8000/moderator/reserve/selection",
        json=request_body,
        timeout=60,
    )

    # Проверяем статус код
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Получаем JSON ответ
    data = response.json()

    # Проверяем наличие всех обязательных полей
    assert "reasoning" in data, "Field 'reasoning' is missing"
    assert "result" in data, "Field 'result' is missing"
    assert "time_ms" in data, "Field 'time_ms' is missing"

    # Проверяем типы полей
    assert isinstance(data["reasoning"], str), "Field 'reasoning' must be a string"
    assert isinstance(data["result"], dict), "Field 'result' must be a dict"
    assert isinstance(data["time_ms"], int), "Field 'time_ms' must be an int"

    # Проверяем структуру result
    assert "status" in data["result"], "Field 'status' is missing in result"
    assert (
        "violated_rules" in data["result"]
    ), "Field 'violated_rules' is missing in result"

    # Проверяем значения
    assert (
        data["result"]["status"] == "OK"
    ), f"Expected status 'OK', got '{data['result']['status']}'"
    assert isinstance(
        data["result"]["violated_rules"], list
    ), "Field 'violated_rules' must be a list"
    assert (
        len(data["result"]["violated_rules"]) == 0
    ), f"Expected empty violated_rules, got {data['result']['violated_rules']}"

    # Проверяем, что time_ms положительное число
    assert data["time_ms"] > 0, f"Expected positive time_ms, got {data['time_ms']}"

    print("\n✓ Test passed successfully!")
    print(f"  - Reasoning length: {len(data['reasoning'])} chars")
    print(f"  - Status: {data['result']['status']}")
    print(f"  - Violated rules: {data['result']['violated_rules']}")
    print(f"  - Time: {data['time_ms']} ms")
