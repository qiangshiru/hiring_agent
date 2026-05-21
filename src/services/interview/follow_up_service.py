import uuid
from typing import Dict, Optional

from src.schemas.interview import (
    FollowUpRequest,
    FollowUpResponse,
    QuestionType,
    QuestionDifficulty,
)
from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.interview.session import InterviewSession


class FollowUpService:
    def __init__(self):
        self.sessions: Dict[str, InterviewSession] = {}

    def create_session(self, jd: JDParseResult, resume: ResumeParseResult) -> InterviewSession:
        session = InterviewSession(jd, resume)
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.sessions.get(session_id)

    def next_question(self, session_id: str):
        session = self.get_session(session_id)
        if not session:
            return None
        return session.next_question()

    def submit_answer(self, request: FollowUpRequest):
        session = self.get_session(request.session_id)
        if not session:
            return None
        return session.submit_answer(request.question_id, request.answer)

    def follow_up(self, session_id: str, answer: str):
        session = self.get_session(session_id)
        if not session:
            return None
        return session.follow_up(answer)

    def complete_session(self, session_id: str):
        session = self.get_session(session_id)
        if not session:
            return None
        return session.complete()
