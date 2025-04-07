from pydantic import BaseModel

from typing import List
from enum import Enum


class ModerationStatus(str, Enum):
    OK = 'OK'
    VIOLATION = 'VIOLATION'


class Rule(BaseModel):
    id: str
    condition: str


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


class ModerationContext(BaseModel):
    rules: List[Rule] | None
    moderation_model: str | None
    resume: Resume