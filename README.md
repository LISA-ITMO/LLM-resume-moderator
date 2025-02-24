# LLM Resume Moderator & Generator 🔍✨

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

## 📂 Структура репозитория
Ноутбук	Описание
1_EDA_preproc.ipynb	EDA, предобработка данных, анализ тональности и сходства эмбеддингов.
2_llamaguard_3_8b_zeroshot.ipynb	Zero-shot классификация резюме с Llama-Guard.
3.extract_rules.ipynb	Извлечение критериев модерации из документов.
4.inference.ipynb	Классификация резюме с Llama-3.1-8B-Instruct.
5.local_inference.ipynb	Локальный инференс на русском с моделью T-lite-it-1.0.

📬 Контакты

    Telegram: @Vlodimirshil
    
    Email: vladimir@itmo.ru
