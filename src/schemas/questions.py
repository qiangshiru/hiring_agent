from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    FOUNDATION = "foundation"
    PROJECT = "project"
    DEEP_DIVE = "deep_dive"
    SCENARIO = "scenario"
    TRADEOFF = "tradeoff"
    FAILURE = "failure"
    SYSTEM_DESIGN = "system_design"


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Question(BaseModel):
    id: str
    type: QuestionType
    difficulty: QuestionDifficulty
    content: str
    expected_skills: list[str] = Field(default_factory=list)
    scoring_guide: list[str] = Field(default_factory=list)
    follow_up_hints: list[str] = Field(default_factory=list)
    time_minutes: int = 5
    tags: list[str] = Field(default_factory=list)


class QuestionGenerationConfig(BaseModel):
    total_questions: int = 15
    difficulty_distribution: dict[QuestionDifficulty, float] = Field(
        default={"easy": 0.2, "medium": 0.4, "hard": 0.3, "expert": 0.1}
    )
    type_distribution: dict[QuestionType, float] = Field(
        default={
            "foundation": 0.15,
            "project": 0.15,
            "deep_dive": 0.2,
            "scenario": 0.15,
            "tradeoff": 0.15,
            "failure": 0.1,
            "system_design": 0.1,
        }
    )


class QuestionGenerationResult(BaseModel):
    questions: list[Question]
    config: QuestionGenerationConfig
    difficulty_distribution: dict[str, int]
    type_distribution: dict[str, int]
