# LLM Resume Moderator

Проект для автоматизации модерации резюме на русском языке с использованием современных языковых моделей.

---

## 🌟 **Особенности**
- **Модерация резюме**: Анализ соответствия критериям, тональности и релевантности.
- **Zero-shot подход**: Классификация без предварительного обучения на доменных данных.

---

## 🛠️ **Технологии**
### Модели:
- `meta-llama/Llama-Guard-3-8B` — классификация резюме.
- `meta-llama/Llama-3.1-8B-Instruct` — zero-shot инференс.
- `seara/rubert-base-cased-russian-sentiment` — анализ тональности.
- `intfloat/multilingual-e5-large` — сравнение эмбеддингов.
- `t-tech/T-lite-it-1.0` — русскоязычная классификация.

### Библиотеки:
`PyTorch · Transformers · Pandas · llama-index`

## 🚀 **Развёртывание**

### Способ 1: Docker
```bash
docker run -d \
  -e MLP_API_KEY='ваш_openai_ключ' \
  -e DEFAULT_MODERATOR='just-ai/t-tech-T-pro-it-1.0' \
  -e PROVIDER_URL='https://caila.io/api/adapters/openai' \
  -p 8000:8000 \
  toponedevopssng/llm-resume-moderator:latest
```

### Способ 2: Python
```bash
cd app

echo "MLP_API_KEY='ваш_openai_ключ'
DEFAULT_MODERATOR='just-ai/t-tech-T-pro-it-1.0'
PROVIDER_URL='https://caila.io/api/adapters/openai'" > .env

pip install -r requirements.txt
python main.py
```

**Переменные окружения** (значения по умолчанию):
- `DEFAULT_MODERATOR`: Модель для модерации (`just-ai/t-tech-T-pro-it-1.0`)
- `PROVIDER_URL`: Провайдер OpenAI-совместимого API (`https://caila.io/api/adapters/openai`)

## **🌐 Доступ к демо**
Сервис уже развёрнут и доступен по адресам:
- api url: http://89.169.149.254:8000
- Swagger-документация: http://89.169.149.254:8000/docs

## 📂 Структура репозитория
| Ноутбук                            | Описание                                                              |
| ---------------------------------- | --------------------------------------------------------------------- |
| `1_EDA_preproc.ipynb`              | EDA, предобработка данных, анализ тональности и сходства эмбеддингов. |
| `2_llamaguard_3_8b_zeroshot.ipynb` | Zero-shot классификация резюме с Llama-Guard.                         |
| `3_extract_rules.ipynb`            | Извлечение критериев модерации из документов.                         |
| `4_inference.ipynb`                | Классификация резюме с Llama-3.1-8B-Instruct.                         |
| `5_local_inference.ipynb`          | Локальный инференс на русском с моделью T-lite-it-1.0.                |

## 📬 Контакты
Telegram: `@Vlodimirshil`
    
Email: `vladimir@itmo.ru`
