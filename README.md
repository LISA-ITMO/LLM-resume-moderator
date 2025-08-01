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

### **Приготовления**
```bash
git clone https://github.com/LISA-ITMO/LLM-resume-moderator.git &&
cd LLM-resume-moderator &&
docker login ghcr.io -u {ВАШ_НИК_ГИТХАБ} -p {ВАШ_ГИХАБ_ТОКЕН} &&
echo "ELASTIC_PASSWORD='MY_SECRET_ELK_PASS'" >> .env &&
echo "KIBANA_PASSWORD='MY_SECRET_KIBANA_PASS'" >> .env
```

### **Запуск с локальной LLM**
```bash
echo "LLM_PROVIDER=local" >> .env &&
docker-compose -f docker-compose.prod.yaml --profile llm-local up --pull always -d
```

### **Запуск с LLM по API**
```bash
echo "MLP_API_KEY='{ВАШ_ТОКЕН_caila.io}'" >> .env &&
echo "LLM_PROVIDER='caila.io'" >> .env &&
docker-compose -f docker-compose.prod.yaml up --pull always -d 
```

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

## 📝 Публикации и доклады:
1. **Шилоносов В.Р.** (науч. рук. Федоров Д.А.)  
   [**Сервис автоматической модерации резюме на русском языке**](https://kmu.itmo.ru/digests/article/15750) Сборник тезисов докладов конгресса молодых ученых. Электронное издание. – СПб: Университет ИТМО, 2025.

2. **Выступление с докладом "Сервис автоматической модерации резюме на русском языке"**  
   XIV Конгресс молодых ученых ИТМО (Секция «Искусственный интеллект», подсекция «Интеллектуальные сервисы и приложения»)  
   📺 Видеозаписи:  
   [![YouTube](https://img.shields.io/badge/-YouTube-%23FF0000?style=flat&logo=youtube&logoColor=white)](https://youtu.be/gVLFGFRvW-o) 
   [![VK Video](https://img.shields.io/badge/-VK%20Video-%230077FF?style=flat&logo=vk&logoColor=white)](https://vkvideo.ru/video-223020743_456239042?t=3h44m23s)

## 📬 Контакты
Telegram: `@Vlodimirshil`
    
Email: `vladimir@itmo.ru`
