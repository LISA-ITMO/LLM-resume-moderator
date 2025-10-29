from pydantic import BaseModel, Field

import json
from typing import List, Optional
from enum import Enum
from datetime import date


class ModerationStatus(str, Enum):
    OK = 'OK'
    VIOLATION = 'VIOLATION'


class Rule(BaseModel):
    id: str
    condition: str


DEFAULT_RULES = [Rule(**rule) for rule in json.load(open('resume_rules.json'))]


class ViolatedRule(BaseModel):
    id: str
    condition: str
    resume_fragment: str


class SelectionResponse(BaseModel):
    status: ModerationStatus
    violated_rules: List[ViolatedRule]


class ResponseWithReasoning(BaseModel):
    reasoning: str
    result: SelectionResponse


class ModerationModel(str, Enum):
    T_it_1_0 = 'T_it_1_0'


class Reletive(BaseModel):
    relationship: str = Field(..., description="Степень родства", example="Отец")
    fullname: str = Field(..., description="Фамилия, имя, отчество (при его наличии)", example="Шилоносов Андрей Петрович")
    birthdate: str = Field(..., description="Дата рождения (год, число и месяц)", example="1968-05-22")
    job: str = Field(..., description="Место работы (наименование и адрес организации), должность", example="АО «Газпром», инженер")
    address: str = Field(..., description="Домашний адрес (регистрация, фактическое проживание)", example="г. Санкт-Петербург, ул. Ленина, д. 15, кв. 8")


class Education(BaseModel):
    dateOfAdmission: str = Field(..., description="Дата поступления", example="2016-09-01")
    dateOfGraduation: str = Field(..., description="Дата окончания", example="2020-06-30")
    institutionName: str = Field(..., description="Учебное заведение", example="Санкт-Петербургский государственный университет")


class HigherEducation(Education):
    specialty: str = Field(..., description="Специальность (направление подготовки), код", example="01.03.02 Прикладная математика и информатика")
    level: str = Field(..., description="Уровень образования", example="Бакалавриат")
    formOfEducation: str = Field(..., description="Форма обучения", example="Очная")
    year: int = Field(..., description="Курс или год обучения", example=4)
    haveDiploma: bool = Field(..., description="Наличие диплома", example=True)


class AdditionalEducation(Education):
    educationalProgram: str = Field(..., description="Наименование программы", example="Data Science и машинное обучение")
    programType: str = Field(..., description="Вид программы", example="Повышение квалификации")
    hoursИumber: int = Field(..., description="Количество часов", example=144)


class Postgraduate(Education):
    specialty: str = Field(..., description="Наименование направления или специальности по документу", example="Информационные технологии")
    degree: str = Field(..., description="Учёная степень", example="Кандидат технических наук")
    scienceBranch: str = Field(..., description="Отрасль наук", example="Технические науки")


class EductationsInfo(BaseModel):
    higherEducation: List[HigherEducation] = Field(..., description="Сведения о высшем образовании")
    additionalEducation: List[AdditionalEducation] = Field(..., description="Сведения о дополнительном профессиональном образовании")
    postgraduate: List[Postgraduate] = Field(..., description="Сведения об аспирантуре, адъюнктуре, ординатуре")


class LanguageLevel(Enum):
    NATIVE = "Native"
    SPEAK_FLUENTLY = "SpeakFluently"
    CAN_READ_AND_EXPLAIN = "CanReadAndExplain"
    READ_TRANSLATE_WITH_DICT = "ReadTranslateWithDict"


class SoftwareSkillLevel(Enum):
    FLUENT = "Fluent"
    HAVE_GENERAL_IDEA = "HaveGeneralIdea"
    HAVE_NOT_SKILL = "HaveNotSkill"


class Languge(BaseModel):
    name: str = Field(..., description="Язык", example="Английский")
    level: LanguageLevel = Field(..., description="Степень владения языком", example="SpeakFluently")


class SoftwareSkill(BaseModel):
    type: str = Field(..., description="Вид программного обеспечения", example="Текстовые редакторы")
    nameOfProduct: str = Field(..., description="Название программного продукта", example="Microsoft Word")
    level: SoftwareSkillLevel = Field(..., description="Степень владения программой", example="Fluent")


class WorkExperience(BaseModel):
    start_date: date = Field(..., description="Дата поступления", example="2021-07-01")
    end_date: date = Field(..., description="Дата увольнения", example="2023-09-15")
    organization_name: str = Field(..., description="Наименование организации", example="ООО «АналитикСофт»")
    position: str = Field(..., description="Должность, профессия", example="Аналитик данных")
    description: str = Field(..., description="Краткое описание выполняемой работы", example="Разработка моделей машинного обучения для анализа данных клиентов")


class ResumeToGovernment(BaseModel):
    fullname: str = Field(..., description="Фамилия, имя, отчество (при его наличии)", example="Шилоносов Владимир Андреевич")
    fullnameChange: Optional[str] = Field(None, description="Изменение Ф.И.О. (указать старое Ф.И.О., время, место и причину изменения)", example="До 2019 года — Иванов Владимир Андреевич, смена фамилии при вступлении в брак")
    citizenship: str = Field(..., description="Гражданство", example="Российская Федерация")
    passportOrEquivalent: str = Field(..., description="Паспорт гражданина или документ, его заменяющий", example="45 01 №123456, выдан УФМС по г. Москве 12.05.2016")
    snils: str = Field(..., description="Страховой номер индивидуального лицевого счёта (СНИЛС)", example="123-456 00 11")
    birthdate: str = Field(..., description="Дата рождения", example="1998-07-22")
    placeOfBirth: str = Field(..., description="Место рождения", example="г. Санкт-Петербург")
    registrationAddress: str = Field(..., description="Адрес регистрации", example="г. Санкт-Петербург, ул. Невский пр., д. 12, кв. 34")
    actualResidenceAddress: str = Field(..., description="Адрес фактического проживания", example="г. Санкт-Петербург, ул. Ленина, д. 5")
    contactInformation: str = Field(..., description="Контактная информация (телефоны, e-mail)", example="+7 (921) 123-45-67, vladimir@mail.ru")
    closeRelatives: List[Reletive] = Field(..., description="Близкие родственники (отец, мать, братья, сёстры, дети, супруг(а))")
    education: EductationsInfo = Field(..., description="Сведения об образовании")
    languges: List[Languge] = Field(..., description="Какими языками владеете")
    softwareSkills: List[SoftwareSkill] = Field(..., description="Навыки работы с компьютером")
    publications: List[str] = Field(..., description="Научные труды (публикации) или изобретения", example=["Применение ML в госуправлении"])
    awards: List[str] = Field(..., description="Премии, стипендии, награды", example=["Премия губернатора за успехи в учебе"])
    militaryLiable: bool = Field(..., description="Отношение к воинской обязанности (военнообязанный/не военнообязанный)", example=True)
    militaryСategory: str = Field(..., description="Годность к военной службе", example="Годен к военной службе")
    professionalInterests: str = Field(..., description="Сфера профессиональных интересов", example="Анализ данных, финансы, образование")
    additionalInfo: str = Field(..., description="Дополнительная информация о себе", example="Ответственный, коммуникабельный, интересуюсь IT и саморазвитием")
    motivation: str = Field(..., description="Почему хочу вступить в Молодёжный кадровый резерв", example="Хочу внести вклад в развитие Санкт-Петербурга и реализовать свой потенциал")
    source: str = Field(..., description="Откуда узнали о резерве", example="Информация в вузе (центр карьеры, ярмарка вакансий)")


class SelectionContext(BaseModel):
    rules: List[Rule] = Field(default=DEFAULT_RULES, description="Список правил на которые нужно проверить резюме", example=DEFAULT_RULES)
    resume: ResumeToGovernment = Field(..., description="Резюме которое нужно проверить")
    moderation_model: Optional[ModerationModel] = Field(..., description="LLM модель которая будет проверять резюме на соответствие правилам", example=ModerationModel.T_it_1_0)
