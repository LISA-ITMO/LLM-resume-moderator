from pydantic import BaseModel

from typing import List
from enum import Enum


class ModerationStatus(str, Enum):
    """
    Represents the status of a moderation check.

        This class provides predefined constants to represent whether content
        passed moderation (OK) or violated moderation policies (VIOLATION).
    """

    OK = "OK"
    VIOLATION = "VIOLATION"


class Rule(BaseModel):
    """
    Represents a rule with an associated condition."""

    id: str
    condition: str


class ViolatedRule(BaseModel):
    """
    Represents a rule that has been violated during analysis.

        This class stores information about the specific rule violation,
        including its identifier, the condition that triggered it, and
        a relevant fragment of code where the violation occurred.
    """

    id: str
    condition: str
    resume_fragment: str


class ModeratorResponse(BaseModel):
    """
    Represents the response from a moderation check.

        This class encapsulates the status of a content moderation decision
        and any rules that were violated.

        Attributes:
            status: Indicates whether the content was approved or rejected.
            violated_rules: A list of rules that were broken by the content, if any.
    """

    status: ModerationStatus
    violated_rules: List[ViolatedRule]


class ResponseWithReasoning(BaseModel):
    """
    A class to encapsulate a response along with the reasoning behind it.

        This class is designed to hold both the final result of a process and
        the explanation or steps taken to arrive at that result, aiding in
        interpretability and debugging.

        Attributes:
            reasoning: A string containing the reasoning for the result.
            result: The actual result obtained.
    """

    reasoning: str
    result: ModeratorResponse


class Resume(BaseModel):
    """
    A class to represent a resume with experience, job title, education and additional education.
    """

    experience: str
    job_title: str
    education: str
    additional_education: str


class ModerationContext(BaseModel):
    """
    Encapsulates the context needed for moderation tasks.

        This class holds the rules, model, and resume information used during
        content moderation processes. It provides a centralized location to access
        these components.

        Attributes:
            rules: The set of rules governing the moderation process.
            moderation_model: The model used for content analysis.
            resume: Information about resuming a previous moderation session.
    """

    rules: List[Rule] | None
    moderation_model: str | None
    resume: Resume
