#!/usr/bin/env bash
# Тестовые curl-запросы к LLM-resume-moderator (порт 8000)
# Использование: bash debug/test_curls.sh [fullname]
# Пример: bash debug/test_curls.sh "Селиванов Алексей"

BASE_URL="http://localhost:8000"
PDF="/Users/shilonosovvr/Downloads/Диплом 123.pdf"
FULLNAME="${1:-Шилоносов Владимир Андреевич}"

echo "=== 1. Загрузка диплома ==="
curl -s -X POST "$BASE_URL/moderator/reserve/upload-education-file" \
  -F "file=@$PDF"
echo ""

echo ""
echo "=== 2. Отбор (selection), fullname: $FULLNAME ==="
curl -s -X POST "$BASE_URL/moderator/reserve/selection" \
  -H "Content-Type: application/json" \
  -d "{
  \"rules\": [
    {\"id\": \"rule_4\", \"condition\": \"Резюме должно быть заполнено на русском языке, допускаются иностранные термины для описания профессиональных навыков и других особых случаев, данные на английском допустимы в пунктах Контактная информация, Близкие родственники, Образование, Навыки работы с компьютером, Опыт работы\"},
    {\"id\": \"rule_7\", \"condition\": \"Информация не должна содержать слова и выражения, не соответствующие нормам современного русского языка, допустимы стилистические неточности, но главное, чтобы не было матов и токсичности\"}
  ],
  \"resume\": {
    \"fullname\": \"$FULLNAME\",
    \"fullnameChange\": null,
    \"citizenship\": \"Российская Федерация\",
    \"passportOrEquivalent\": \"45 01 №123456, выдан УФМС по г. Москве 12.05.2016\",
    \"snils\": \"123-456 00 11\",
    \"birthdate\": \"1998-07-22\",
    \"placeOfBirth\": \"г. Санкт-Петербург\",
    \"registrationAddress\": \"г. Санкт-Петербург, ул. Невский пр., д. 12, кв. 34\",
    \"actualResidenceAddress\": \"г. Санкт-Петербург, ул. Ленина, д. 5\",
    \"contactInformation\": \"+7 (921) 123-45-67, vladimir@mail.ru\",
    \"closeRelatives\": [{\"relationship\": \"Отец\", \"fullname\": \"Шилоносов Андрей Петрович\", \"birthdate\": \"1968-05-22\", \"job\": \"АО «Газпром», инженер\", \"address\": \"г. Санкт-Петербург, ул. Ленина, д. 15, кв. 8\"}],
    \"education\": {
      \"higherEducation\": [{\"dateOfAdmission\": \"2016-09-01\", \"dateOfGraduation\": \"2020-06-30\", \"institutionName\": \"Санкт-Петербургский государственный университет\", \"specialty\": \"01.03.02 Прикладная математика и информатика\", \"level\": \"Бакалавриат\", \"formOfEducation\": \"Очная\", \"year\": 4, \"haveDiploma\": true, \"educationFilename\": \"Диплом 123.pdf\"}],
      \"additionalEducation\": [{\"dateOfAdmission\": \"2016-09-01\", \"dateOfGraduation\": \"2020-06-30\", \"institutionName\": \"Санкт-Петербургский государственный университет\", \"educationalProgram\": \"Data Science и машинное обучение\", \"programType\": \"Повышение квалификации\", \"hoursИumber\": 144}],
      \"postgraduate\": [{\"dateOfAdmission\": \"2016-09-01\", \"dateOfGraduation\": \"2020-06-30\", \"institutionName\": \"Санкт-Петербургский государственный университет\", \"specialty\": \"Информационные технологии\", \"degree\": \"Кандидат технических наук\", \"scienceBranch\": \"Технические науки\"}]
    },
    \"languges\": [{\"name\": \"Английский\", \"level\": \"SpeakFluently\"}],
    \"softwareSkills\": [{\"type\": \"Текстовые редакторы\", \"nameOfProduct\": \"Microsoft Word\", \"level\": \"Fluent\"}],
    \"publications\": [\"Применение ML в госуправлении\"],
    \"awards\": [\"Премия губернатора за успехи в учебе\"],
    \"militaryLiable\": true,
    \"militaryСategory\": \"Годен к военной службе\",
    \"professionalInterests\": \"Анализ данных, финансы, образование\",
    \"additionalInfo\": \"Ответственный, коммуникабельный, интересуюсь IT и саморазвитием\",
    \"motivation\": \"Хочу внести вклад в развитие Санкт-Петербурга и реализовать свой потенциал\",
    \"source\": \"Информация в вузе (центр карьеры, ярмарка вакансий)\"
  },
  \"moderation_model\": \"Qwen/Qwen3.5-122B-A10B\"
}" | python3 -m json.tool
