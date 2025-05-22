from pydantic import BaseModel
from config import DEFAULT_MODERATOR

import json
from typing import List
from enum import Enum


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
