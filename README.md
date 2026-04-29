# LLM Resume Moderator

FastAPI-сервис для автоматической модерации резюме кандидатов в студенческий кадровый резерв. Проверяет резюме на соответствие правилам и верифицирует документы об образовании через VLM.

## Возможности

- Проверка резюме на соответствие правилам модерации (язык, токсичность, формат) через LLM
- Верификация PDF-документов об образовании (дипломов, справок) через VLM
- Нормализация специальностей по классификатору
- Проверка специальности на соответствие перечню допустимых
- Автоматическое удаление файлов после обработки
- OpenAI-совместимый API (поддержка любого провайдера)

## Запуск

```bash
git clone https://github.com/LISA-ITMO/LLM-resume-moderator.git
cd LLM-resume-moderator
cp .env.example .env  # заполнить переменные
docker compose build
docker compose up
```

Swagger-документация: `http://localhost:8000/docs`

## Конфигурация

Все настройки через `.env`:

| Переменная | Описание | По умолчанию |
|---|---|---|
| `APP_PORT` | Порт сервиса | `8001` |
| `LLM_BASE_URL` | Base URL OpenAI-совместимого провайдера | — |
| `LLM_API_KEY` | API-ключ провайдера | — |
| `LLM_MODEL` | Название модели | `default` |
| `LLM_TIMEOUT` | Таймаут запроса (сек) | `120` |
| `STORAGE_DIR` | Директория для загруженных файлов | `storage` |
| `MAX_FILE_SIZE` | Максимальный размер PDF (байт) | `20971520` |

## API

### `POST /moderator/reserve/upload-education-file`

Загружает PDF-документ об образовании. Возвращает имя сохранённого файла.

### `POST /moderator/reserve/selection`

Запускает полный цикл отбора: модерация резюме + верификация документа об образовании.

**Тело запроса:**
```json
{
  "rules": [{"id": "rule_4", "condition": "..."}],
  "resume": {
    "fullname": "Шилоносов Владимир Андреевич",
    "education": {
      "higherEducation": [
        {"educationFilename": "Diploma.pdf", "specialty": "09.03.04 Программная инженерия", "...": "..."}
      ]
    },
    "...": "..."
  }
}
```

**Ответ:**
```json
{
  "reasoning": "Резюме соответствует всем правилам.",
  "violatedRules": [],
  "educationInfo": [
    {
      "isHigherEducation": true,
      "code": "09.03.04",
      "name": "Программная инженерия",
      "degree": "Bachelor",
      "docType": "Diploma",
      "resolution": {"valid": true, "noValidReason": null}
    }
  ],
  "result": {
    "validEducationFound": true,
    "noViolatedRules": true,
    "overallSuccess": true
  },
  "timeMs": 4200
}
```

## Структура проекта

```
├── configs/
│   ├── settings.py              # Настройки из .env
│   ├── resume_rules.json        # Правила модерации по умолчанию
│   ├── required_specialties.py  # Перечень допустимых специальностей
│   └── specialties.py           # Полный классификатор специальностей
├── routers/
│   ├── api_routers.py           # Эндпоинты FastAPI
│   └── schemas.py               # Pydantic-схемы
├── service/
│   ├── llm_service.py           # LLM/VLM: модерация и верификация документов
│   ├── selection_service.py     # Оркестратор пайплайна отбора
│   ├── document_service.py      # Загрузка и хранение PDF
│   └── resume_text_converter.py # Конвертация резюме в текст для LLM
├── tests/
│   └── test_e2e.py              # E2E-тесты
├── debug/
│   └── test.ipynb               # Ноутбук для ручного тестирования
├── main.py                      # Точка входа
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Разработка

```bash
uv sync --dev          # установить зависимости
uv run pytest tests/   # запустить тесты
uv run flake8 .        # линтер
uv run black .         # форматирование
```

## Публикации

1. **Шилоносов В.Р.** (науч. рук. Федоров Д.А.) — [Сервис автоматической модерации резюме на русском языке](https://kmu.itmo.ru/digests/article/15750). Сборник тезисов докладов конгресса молодых ученых. СПб: Университет ИТМО, 2025.

2. Выступление на XIV Конгрессе молодых ученых ИТМО (Секция «Искусственный интеллект», подсекция «Интеллектуальные сервисы и приложения»)

[![YouTube](https://img.shields.io/badge/-YouTube-%23FF0000?style=flat&logo=youtube&logoColor=white)](https://youtu.be/gVLFGFRvW-o)
[![VK Video](https://img.shields.io/badge/-VK%20Video-%230077FF?style=flat&logo=vk&logoColor=white)](https://vkvideo.ru/video-223020743_456239042?t=3h44m23s)

## Контакты

Telegram: `@Vlodimirshil` | Email: `vladimir@itmo.ru`
