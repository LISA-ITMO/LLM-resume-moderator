from pydantic import BaseModel, Field
from config import DEFAULT_MODERATOR

import json
from typing import List
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


class ModeratorResponse(BaseModel):
    status: ModerationStatus
    violated_rules: List[ViolatedRule]


class ResponseWithReasoning(BaseModel):
    reasoning: str
    result: ModeratorResponse


class Resume(BaseModel):
    experience: str
    job_title: str
    education: str
    additional_education: str


class ModerationModel(str, Enum):
    T_it_1_0 = 'T_it_1_0'


class ModerationContext(BaseModel):
    rules: List[Rule] | None = DEFAULT_RULES
    moderation_model: ModerationModel | None
    resume: Resume

class Reletive(BaseModel):
    relationship: str
    fullname: str
    birthdate: str
    job: str
    address: str


class Education(BaseModel):
    dateOfAdmission: str
    dateOfGraduation: str
    institutionName: str


class HigherEducation(Education):
    specialty: str
    level: str
    formOfEducation: str
    year: int
    haveDiploma: bool


class AdditionalEducation(Education):
    educationalProgram: str
    programType: str
    hoursИumber: int


class Postgraduate(Education):
    specialty: str
    degree: str
    scienceBranch: str


class EductationsInfo(BaseModel):
    higherEducation: List[HigherEducation]
    additionalEducation: List[AdditionalEducation]
    postgraduate: List[Postgraduate]


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
    name: str
    level: LanguageLevel


class SoftwareSkill(BaseModel):
    type: str
    nameOfProduct: str
    level: SoftwareSkillLevel


class WorkExperience(BaseModel):
    start_date: date = Field(None, description="Date of employment start")
    end_date: date = Field(None, description="Date of employment end")
    organization_name: str = Field(None, description="Name of the organization")
    position: str = Field(None, description="Job title or profession")
    description: str = Field(None, description="Brief description of performed duties")


class ResumeToGovernment(BaseModel):
    fullname: str
    fullnameChange: str | None
    citizenship: str
    passportOrEquivalent: str
    snils: str
    birthdate: str
    placeOfBirth: str
    registrationAddress: str
    actualResidenceAddress: str
    contactInformation: str
    closeRelatives: List[Reletive]
    education: EductationsInfo
    languges: List[Languge]
    softwareSkills: List[SoftwareSkill]
    publications: List[str]
    awards: List[str]
    militaryLiable: bool
    militaryСategory: str
    professionalInterests: str
    additionalInfo: str
    motivation: str
    source: str
