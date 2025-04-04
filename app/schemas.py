from pydantic import BaseModel

from typing import List
from enum import Enum


class ModerationStatus(str, Enum):
    OK = 'OK'
    VIOLATION = 'VIOLATION'


class Rool(BaseModel):
    id: str
    condition: str


class ViolatedRool(BaseModel):
    id: str
    condition: str
    resume_fragment: str


class ModeratorResponse(BaseModel):
    status: ModerationStatus
    violated_rools: List[ViolatedRool]


class ResponseWithReasoning(BaseModel):
    reasoning: str
    result: ModeratorResponse