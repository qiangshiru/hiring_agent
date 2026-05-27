"""面试追问与会话管理服务。

管理多个并行的面试会话，提供面试流程的完整生命周期管理：
创建会话、获取下一个问题、提交回答、生成追问、完成会话。
作为面试流程的编排层，将请求路由到对应的 InterviewSession 实例。
"""

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
    """面试追问与会话管理服务。

    维护所有活跃的面试会话字典，对每个会话提供统一的操作入口，
    包括问题推进、答案提交、追问生成和会话完成。
    """

    def __init__(self):
        self.sessions: Dict[str, InterviewSession] = {}

    def create_session(self, jd: JDParseResult, resume: ResumeParseResult) -> InterviewSession:
        """根据 JD 和简历创建新的面试会话并注册到会话字典中。"""
        session = InterviewSession(jd, resume)
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """根据会话 ID 获取对应的面试会话实例。"""
        return self.sessions.get(session_id)

    def next_question(self, session_id: str):
        """获取指定会话的下一个面试问题。"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session.next_question()

    def submit_answer(self, request: FollowUpRequest):
        """提交候选人对当前问题的回答。"""
        session = self.get_session(request.session_id)
        if not session:
            return None
        return session.submit_answer(request.question_id, request.answer)

    def follow_up(self, session_id: str, answer: str):
        """基于候选人的回答生成追问问题。"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session.follow_up(answer)

    def complete_session(self, session_id: str):
        """标记指定会话为已完成，返回会话汇总信息。"""
        session = self.get_session(session_id)
        if not session:
            return None
        return session.complete()
