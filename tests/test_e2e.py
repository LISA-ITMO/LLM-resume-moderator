import subprocess
import time
from typing import Generator

import pytest
import requests

from configs.settings import get_settings

BASE_URL = f"http://localhost:{get_settings().app_port}"

RESUME = {
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
                "educationFilename": None,  # подставляется в тесте
            }
        ],
        "additionalEducation": [
            {
                "dateOfAdmission": "2021-01-01",
                "dateOfGraduation": "2021-06-01",
                "institutionName": "Санкт-Петербургский государственный университет",
                "educationalProgram": "Data Science и машинное обучение",
                "programType": "Повышение квалификации",
                "hoursИumber": 144,
            }
        ],
        "postgraduate": [
            {
                "dateOfAdmission": "2020-09-01",
                "dateOfGraduation": "2024-06-30",
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
}

RULES = [
    {
        "id": "rule_4",
        "condition": (
            "Резюме должно быть заполнено на русском языке, допускаются иностранные термины "
            "для описания профессиональных навыков и других особых случаев, данные на английском "
            "допустимы в пунктах Контактная информация, Близкие родственники, Образование, "
            "Навыки работы с компьютером, Опыт работы"
        ),
    },
    {
        "id": "rule_7",
        "condition": (
            "Информация не должна содержать слова и выражения, не соответствующие нормам "
            "современного русского языка, допустимы стилистические неточности, но главное, "
            "чтобы не было матов и токсичности"
        ),
    },
]


@pytest.fixture(scope="module")
def app_server() -> Generator[None, None, None]:
    """Запускает FastAPI приложение и останавливает его после тестов."""
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
            f"Server failed to start on port {get_settings().app_port}.\n"
            f"STDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}"
        )
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        raise RuntimeError(f"Failed to start server: {stderr.decode()}")
    yield
    process.terminate()
    process.wait(timeout=5)


def upload_diploma(filename: str = "test_diploma.pdf") -> str:
    """Загружает тестовый диплом, возвращает сохранённое имя файла."""
    with open(f"tests/{filename}", "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/moderator/reserve/upload-education-file",
            files={"file": (filename, f, "application/pdf")},
            timeout=60,
        )
    resp.raise_for_status()
    data = resp.json()
    assert "educationFilename" in data
    return data["educationFilename"]


def run_selection(education_filename: str) -> dict:
    """Запускает отбор с указанным файлом диплома, возвращает JSON ответа."""
    resume = {**RESUME}
    resume["education"] = {
        **RESUME["education"],
        "higherEducation": [
            {
                **RESUME["education"]["higherEducation"][0],
                "educationFilename": education_filename,
            }
        ],
    }
    body = {"rules": RULES, "resume": resume}
    resp = requests.post(
        f"{BASE_URL}/moderator/reserve/selection",
        json=body,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def test_upload_returns_filename(app_server):
    """Загрузка PDF возвращает имя файла."""
    filename = upload_diploma()
    assert filename.endswith(".pdf")
    print(f"\n✓ Uploaded: {filename}")


def test_upload_rejects_non_pdf(app_server):
    """Загрузка не-PDF возвращает 422."""
    resp = requests.post(
        f"{BASE_URL}/moderator/reserve/upload-education-file",
        files={"file": ("test.txt", b"not a pdf", "text/plain")},
        timeout=10,
    )
    assert resp.status_code == 422


def test_full_moderation_pipeline(app_server):
    """E2E: загрузка диплома → модерация → структура ответа."""
    education_filename = upload_diploma()
    data = run_selection(education_filename)

    # Обязательные поля
    for field in ("reasoning", "violatedRules", "educationInfo", "result", "timeMs"):
        assert field in data, f"Field '{field}' missing in response"

    assert isinstance(data["reasoning"], str)
    assert isinstance(data["violatedRules"], list)
    assert isinstance(data["educationInfo"], list)
    assert isinstance(data["timeMs"], int) and data["timeMs"] > 0

    # result
    result = data["result"]
    for field in ("validEducationFound", "noViolatedRules", "overallSuccess"):
        assert field in result, f"Field '{field}' missing in result"
        assert isinstance(result[field], bool)

    # educationInfo
    assert len(data["educationInfo"]) > 0
    edu = data["educationInfo"][0]
    assert "isHigherEducation" in edu
    assert "resolution" in edu
    assert "valid" in edu["resolution"]

    print(f"\n✓ overallSuccess={result['overallSuccess']}  timeMs={data['timeMs']}")
    print(
        f"  violatedRules={len(data['violatedRules'])}  educationInfo={len(data['educationInfo'])}"
    )


def test_selection_without_diploma(app_server):
    """Отбор без файла диплома — educationInfo пустой, validEducationFound=False."""
    resume = {**RESUME}
    resume["education"] = {
        **RESUME["education"],
        "higherEducation": [
            {**RESUME["education"]["higherEducation"][0], "educationFilename": None}
        ],
    }
    body = {"rules": RULES, "resume": resume}
    resp = requests.post(
        f"{BASE_URL}/moderator/reserve/selection", json=body, timeout=120
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["educationInfo"] == []
    assert data["result"]["validEducationFound"] is False
    assert data["result"]["overallSuccess"] is False
    print("\n✓ No diploma: validEducationFound=False as expected")


def test_selection_missing_file_returns_422(app_server):
    """Несуществующий файл диплома → 422."""
    resume = {**RESUME}
    resume["education"] = {
        **RESUME["education"],
        "higherEducation": [
            {
                **RESUME["education"]["higherEducation"][0],
                "educationFilename": "nonexistent.pdf",
            }
        ],
    }
    body = {"rules": RULES, "resume": resume}
    resp = requests.post(
        f"{BASE_URL}/moderator/reserve/selection", json=body, timeout=30
    )
    assert resp.status_code == 422
    print("\n✓ Missing file → 422 as expected")
