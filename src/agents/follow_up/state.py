from typing import List, Optional, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

from src.schemas.interview import (
    InterviewSessionState,
    QuestionType,
    QuestionDifficulty,
    AnswerQuality,
)


class InterviewAgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    session_state: InterviewSessionState
    current_question: Optional[str]
    current_difficulty: QuestionDifficulty
    follow_up_needed: bool
    should_continue: bool
    knowledge_gaps: List[str]
    strengths: List[str]
