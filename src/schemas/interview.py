from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    FOUNDATION = "foundation"
    PROJECT = "project"
    DEEP_DIVE = "deep_dive"
    SCENARIO = "scenario"
    TRADEOFF = "tradeoff"
    FAILURE = "failure"
    SYSTEM_DESIGN = "system_design"
    FOLLOW_UP = "follow_up"


class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class AnswerQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NO_ANSWER = "no_answer"


class InterviewTurn(BaseModel):
    turn_id: str
    question_id: str
    question_content: str
    question_type: QuestionType
    question_difficulty: QuestionDifficulty
    answer_content: str
    answer_quality: AnswerQuality
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class InterviewSessionState(BaseModel):
    session_id: str
    jd_id: str
    resume_id: str
    current_question: Optional[InterviewTurn] = None
    history: List[InterviewTurn] = Field(default_factory=list)
    current_difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    knowledge_gaps: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    is_complete: bool = False
    total_score: float = Field(default=0.0, ge=0.0, le=100.0)


class InterviewMessage(BaseModel):
    session_id: str
    message_type: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class FollowUpRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class FollowUpResponse(BaseModel):
    question_id: str
    content: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    follow_up_of: str
    reasoning: Optional[str] = None


class InterviewSessionInfo(BaseModel):
    session_id: str
    jd_id: str
    resume_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_turns: int = 0
    current_difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    is_complete: bool = False
    overall_score: float = 0.0
