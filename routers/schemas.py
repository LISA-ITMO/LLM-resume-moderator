import json
from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from configs.settings import get_settings

DEFAULT_MODERATOR = get_settings().default_moderator


class ModerationStatus(str, Enum):
    """Статус модерации резюме."""

    Ok = "Ok"
    Violation = "Violation"


class Rule(BaseModel):
    """Правило модерации.

    Args:
        id: Идентификатор правила
        condition: Текст условия проверки
    """

    id: str
    condition: str


DEFAULT_RULES = [
    Rule(**rule)
    for rule in json.load(open("configs/resume_rules.json", encoding="utf-8"))
]


class ViolatedRule(BaseModel):
    """Нарушенное правило с указанием фрагмента резюме.

    Args:
        id: Идентификатор правила
        condition: Текст условия
        resume_fragment: Фрагмент резюме, нарушающий правило
    """

    id: str
    condition: str
    resume_fragment: str


class ResponseWithReasoning(BaseModel):
    """Ответ с рассуждением и списком нарушенных правил.

    Args:
        reasoning: Объяснение результата проверки
        violatedRules: Список нарушенных правил
    """

    reasoning: str
    violatedRules: List[ViolatedRule]


class EducationDocType(str, Enum):
    """Тип документа об образовании."""

    Diploma = "Diploma"
    Certificate = "Certificate"


class Degree(str, Enum):
    """Степень высшего образования."""

    Bachelor = "Bachelor"
    Master = "Master"
    Specialist = "Specialist"


class NoValidReason(str, Enum):
    """Причина невалидности записи об образовании.

    NotHigherEducation: Не является высшим образованием
    SpecialtyNotFound: Не найден ни код, ни название специальности
    SpecialtyNotInList: Специальности нет в списке допустимых
    CertificateTooFar: Справка, предполагаемая дата окончания более чем через 1.5 года
    FullNameMissing: В документе не найдено ФИО
    FullNameMismatch: ФИО в документе не совпадает с ФИО в анкете
    """

    NotHigherEducation = "NotHigherEducation"
    SpecialtyNotFound = "SpecialtyNotFound"
    SpecialtyNotInList = "SpecialtyNotInList"
    CertificateTooFar = "CertificateTooFar"
    FullNameMissing = "FullNameMissing"
    FullNameMismatch = "FullNameMismatch"


class EducationResolution(BaseModel):
    """Вердикт по записи об образовании.

    Args:
        valid: Запись прошла все проверки
        noValidReason: Причина невалидности (None если valid=True)
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"valid": True, "noValidReason": None}}
    )

    valid: bool
    noValidReason: Optional[NoValidReason] = None


class EducationInfo(BaseModel):
    """Результат проверки одной записи об образовании.

    Args:
        isHigherEducation: Является ли высшим образованием
        fullName: ФИО владельца документа (None если не найдено в документе)
        code: Код специальности по классификатору (None если не высшее)
        name: Название специальности по классификатору (None если не высшее)
        degree: Степень высшего образования (None если не высшее)
        docType: Тип документа — Diploma или Certificate (None если не высшее)
        expectedGraduationYear: Предполагаемый год окончания (только для Certificate)
        resolution: Вердикт по данной записи
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "isHigherEducation": True,
                "fullName": "Шилоносов Владимир Андреевич",
                "code": "01.03.02",
                "name": "Прикладная математика и информатика",
                "degree": "Bachelor",
                "docType": "Diploma",
                "expectedGraduationYear": None,
                "resolution": {"valid": True, "noValidReason": None},
            }
        }
    )

    isHigherEducation: bool
    fullName: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    degree: Optional[Degree] = None
    docType: Optional[EducationDocType] = None
    expectedGraduationYear: Optional[int] = None
    resolution: EducationResolution


class SelectionResults(BaseModel):
    """Итоговые результаты отбора кандидата.

    Args:
        validEducationFound: Найдено хотя бы одно валидное высшее образование
        noViolatedRules: Нарушений правил не обнаружено
        overallSuccess: Кандидат прошёл все проверки
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "validEducationFound": True,
                "noViolatedRules": True,
                "overallSuccess": True,
            }
        }
    )

    validEducationFound: bool
    noViolatedRules: bool
    overallSuccess: bool


class FinalResponse(ResponseWithReasoning):
    """Итоговый ответ сервиса модерации резюме.

    Args:
        educationInfo: Результаты проверки каждой записи об образовании
        result: Итоговые результаты отбора
        timeMs: Время обработки запроса в миллисекундах
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reasoning": "Резюме соответствует всем правилам. Нарушений не обнаружено.",
                "violatedRules": [],
                "educationInfo": [
                    {
                        "isHigherEducation": True,
                        "code": "01.03.02",
                        "name": "Прикладная математика и информатика",
                        "degree": "Bachelor",
                        "docType": "Diploma",
                        "expectedGraduationYear": None,
                        "resolution": {"valid": True, "noValidReason": None},
                    }
                ],
                "result": {
                    "validEducationFound": True,
                    "noViolatedRules": True,
                    "overallSuccess": True,
                },
                "timeMs": 3420,
            }
        }
    )

    educationInfo: List[EducationInfo]
    result: SelectionResults
    timeMs: int


class UploadFileResponse(BaseModel):
    """Ответ на загрузку файла.

    Args:
        message: Сообщение о результате загрузки
        educationFilename: Имя сохранённого файла
    """

    message: str
    educationFilename: str


class BusynessErrorResponse(BaseModel):
    """Ответ с описанием бизнес-ошибки.

    Args:
        message: Текст ошибки
    """

    message: str


class Reletive(BaseModel):
    """Близкий родственник.

    Args:
        relationship: Степень родства
        fullname: Фамилия, имя, отчество
        birthdate: Дата рождения
        job: Место работы и должность
        address: Домашний адрес
    """

    relationship: str = Field(..., description="Степень родства", example="Отец")
    fullname: str = Field(
        ...,
        description="Фамилия, имя, отчество (при его наличии)",
        example="Шилоносов Андрей Петрович",
    )
    birthdate: str = Field(
        ..., description="Дата рождения (год, число и месяц)", example="1968-05-22"
    )
    job: str = Field(
        ...,
        description="Место работы (наименование и адрес организации), должность",
        example="АО «Газпром», инженер",
    )
    address: str = Field(
        ...,
        description="Домашний адрес (регистрация, фактическое проживание)",
        example="г. Санкт-Петербург, ул. Ленина, д. 15, кв. 8",
    )


class Education(BaseModel):
    """Базовая информация об образовании.

    Args:
        dateOfAdmission: Дата поступления
        dateOfGraduation: Дата окончания
        institutionName: Название учебного заведения
    """

    dateOfAdmission: str = Field(
        ..., description="Дата поступления", example="2016-09-01"
    )
    dateOfGraduation: str = Field(
        ..., description="Дата окончания", example="2020-06-30"
    )
    institutionName: str = Field(
        ...,
        description="Учебное заведение",
        example="Санкт-Петербургский государственный университет",
    )


class HigherEducation(Education):
    """Сведения о высшем образовании.

    Args:
        specialty: Специальность и код
        level: Уровень образования
        formOfEducation: Форма обучения
        year: Курс или год обучения
        haveDiploma: Наличие диплома
    """

    specialty: str = Field(
        ...,
        description="Специальность (направление подготовки), код",
        example="01.03.02 Прикладная математика и информатика",
    )
    level: str = Field(..., description="Уровень образования", example="Бакалавриат")
    formOfEducation: str = Field(..., description="Форма обучения", example="Очная")
    year: int = Field(..., description="Курс или год обучения", example=4)
    haveDiploma: bool = Field(..., description="Наличие диплома", example=True)
    educationFilename: Optional[str] = Field(
        None, description="Имя файла документа об образовании", example="Diploma.pdf"
    )


class AdditionalEducation(Education):
    """Дополнительное профессиональное образование.

    Args:
        educationalProgram: Наименование программы
        programType: Вид программы
        hoursИumber: Количество часов
    """

    educationalProgram: str = Field(
        ...,
        description="Наименование программы",
        example="Data Science и машинное обучение",
    )
    programType: str = Field(
        ..., description="Вид программы", example="Повышение квалификации"
    )
    hoursИumber: int = Field(..., description="Количество часов", example=144)


class Postgraduate(Education):
    """Сведения об аспирантуре, адъюнктуре, ординатуре.

    Args:
        specialty: Наименование специальности
        degree: Учёная степень
        scienceBranch: Отрасль наук
    """

    specialty: str = Field(
        ...,
        description="Наименование направления или специальности по документу",
        example="Информационные технологии",
    )
    degree: str = Field(
        ..., description="Учёная степень", example="Кандидат технических наук"
    )
    scienceBranch: str = Field(
        ..., description="Отрасль наук", example="Технические науки"
    )


class EductationsInfo(BaseModel):
    """Сводная информация об образовании.

    Args:
        higherEducation: Список записей о высшем образовании
        additionalEducation: Список записей о дополнительном образовании
        postgraduate: Список записей об аспирантуре/ординатуре
    """

    higherEducation: List[HigherEducation] = Field(
        ..., description="Сведения о высшем образовании"
    )
    additionalEducation: List[AdditionalEducation] = Field(
        ..., description="Сведения о дополнительном профессиональном образовании"
    )
    postgraduate: List[Postgraduate] = Field(
        ..., description="Сведения об аспирантуре, адъюнктуре, ординатуре"
    )


class LanguageLevel(str, Enum):
    """Уровень владения иностранным языком."""

    Native = "Native"
    SpeakFluently = "SpeakFluently"
    CanReadAndExplain = "CanReadAndExplain"
    ReadTranslateWithDict = "ReadTranslateWithDict"


class SoftwareSkillLevel(str, Enum):
    """Уровень владения программным обеспечением."""

    Fluent = "Fluent"
    HaveGeneralIdea = "HaveGeneralIdea"
    HaveNotSkill = "HaveNotSkill"


class Languge(BaseModel):
    """Владение иностранным языком.

    Args:
        name: Название языка
        level: Уровень владения
    """

    name: str = Field(..., description="Язык", example="Английский")
    level: LanguageLevel = Field(
        ..., description="Степень владения языком", example="SpeakFluently"
    )


class SoftwareSkill(BaseModel):
    """Навык работы с программным обеспечением.

    Args:
        type: Вид программного обеспечения
        nameOfProduct: Название продукта
        level: Уровень владения
    """

    type: str = Field(
        ..., description="Вид программного обеспечения", example="Текстовые редакторы"
    )
    nameOfProduct: str = Field(
        ..., description="Название программного продукта", example="Microsoft Word"
    )
    level: SoftwareSkillLevel = Field(
        ..., description="Степень владения программой", example="Fluent"
    )


class WorkExperience(BaseModel):
    """Запись об опыте работы.

    Args:
        start_date: Дата поступления на работу
        end_date: Дата увольнения
        organization_name: Наименование организации
        position: Должность
        description: Описание выполняемых обязанностей
    """

    start_date: date = Field(..., description="Дата поступления", example="2021-07-01")
    end_date: date = Field(..., description="Дата увольнения", example="2023-09-15")
    organization_name: str = Field(
        ..., description="Наименование организации", example="ООО «АналитикСофт»"
    )
    position: str = Field(
        ..., description="Должность, профессия", example="Аналитик данных"
    )
    description: str = Field(
        ...,
        description="Краткое описание выполняемой работы",
        example="Разработка моделей машинного обучения для анализа данных клиентов",
    )


class ResumeToGovernment(BaseModel):
    """Резюме в формате государственного кадрового резерва.

    Args:
        fullname: ФИО
        fullnameChange: Сведения об изменении ФИО
        citizenship: Гражданство
        passportOrEquivalent: Паспорт или заменяющий документ
        snils: СНИЛС
        birthdate: Дата рождения
        placeOfBirth: Место рождения
        registrationAddress: Адрес регистрации
        actualResidenceAddress: Адрес фактического проживания
        contactInformation: Контактная информация
        closeRelatives: Список близких родственников
        education: Сведения об образовании
        languges: Список языков
        softwareSkills: Навыки работы с ПО
        publications: Публикации и изобретения
        awards: Премии и награды
        militaryLiable: Военнообязанный
        militaryСategory: Категория годности
        professionalInterests: Профессиональные интересы
        additionalInfo: Дополнительная информация
        motivation: Мотивация вступления в резерв
        source: Источник информации о резерве
    """

    fullname: str = Field(
        ...,
        description="Фамилия, имя, отчество (при его наличии)",
        example="Шилоносов Владимир Андреевич",
    )
    fullnameChange: Optional[str] = Field(
        None,
        description="Изменение Ф.И.О.",
        example="До 2019 года — Иванов Владимир Андреевич, смена фамилии при вступлении в брак",
    )
    citizenship: str = Field(
        ..., description="Гражданство", example="Российская Федерация"
    )
    passportOrEquivalent: str = Field(
        ...,
        description="Паспорт гражданина или документ, его заменяющий",
        example="45 01 №123456, выдан УФМС по г. Москве 12.05.2016",
    )
    snils: str = Field(
        ...,
        description="СНИЛС",
        example="123-456 00 11",
    )
    birthdate: str = Field(..., description="Дата рождения", example="1998-07-22")
    placeOfBirth: str = Field(
        ..., description="Место рождения", example="г. Санкт-Петербург"
    )
    registrationAddress: str = Field(
        ...,
        description="Адрес регистрации",
        example="г. Санкт-Петербург, ул. Невский пр., д. 12, кв. 34",
    )
    actualResidenceAddress: str = Field(
        ...,
        description="Адрес фактического проживания",
        example="г. Санкт-Петербург, ул. Ленина, д. 5",
    )
    contactInformation: str = Field(
        ...,
        description="Контактная информация (телефоны, e-mail)",
        example="+7 (921) 123-45-67, vladimir@mail.ru",
    )
    closeRelatives: List[Reletive] = Field(
        ...,
        description="Близкие родственники (отец, мать, братья, сёстры, дети, супруг(а))",
    )
    education: EductationsInfo = Field(..., description="Сведения об образовании")
    languges: List[Languge] = Field(..., description="Какими языками владеете")
    softwareSkills: List[SoftwareSkill] = Field(
        ..., description="Навыки работы с компьютером"
    )
    publications: List[str] = Field(
        ...,
        description="Научные труды (публикации) или изобретения",
        example=["Применение ML в госуправлении"],
    )
    awards: List[str] = Field(
        ...,
        description="Премии, стипендии, награды",
        example=["Премия губернатора за успехи в учебе"],
    )
    militaryLiable: bool = Field(
        ...,
        description="Отношение к воинской обязанности",
        example=True,
    )
    militaryСategory: str = Field(
        ..., description="Годность к военной службе", example="Годен к военной службе"
    )
    professionalInterests: str = Field(
        ...,
        description="Сфера профессиональных интересов",
        example="Анализ данных, финансы, образование",
    )
    additionalInfo: str = Field(
        ...,
        description="Дополнительная информация о себе",
        example="Ответственный, коммуникабельный, интересуюсь IT и саморазвитием",
    )
    motivation: str = Field(
        ...,
        description="Почему хочу вступить в Молодёжный кадровый резерв",
        example="Хочу внести вклад в развитие Санкт-Петербурга и реализовать свой потенциал",
    )
    source: str = Field(
        ...,
        description="Откуда узнали о резерве",
        example="Информация в вузе (центр карьеры, ярмарка вакансий)",
    )


class SelectionContext(BaseModel):
    """Контекст запроса на прохождение отбора.

    Args:
        rules: Список правил модерации
        resume: Резюме кандидата
        moderation_model: Название LLM-модели для проверки
        educationFilename: Имя файла документа об образовании
    """

    rules: List[Rule] = Field(
        default=DEFAULT_RULES,
        description="Список правил на которые нужно проверить резюме",
        example=DEFAULT_RULES,
    )
    resume: ResumeToGovernment = Field(
        ..., description="Резюме которое нужно проверить"
    )
    moderation_model: Optional[str] = Field(
        None,
        description="LLM модель которая будет проверять резюме на соответствие правилам",
        example=DEFAULT_MODERATOR,
    )
