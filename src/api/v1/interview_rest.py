"""面试会话管理 REST 接口

提供的端点：
- POST /interview/session                      : 创建新的面试会话（基于 JD 和简历）
- GET  /interview/session/{session_id}          : 获取指定会话的详细信息
- POST /interview/session/{session_id}/next-question : 获取下一道面试题目
- POST /interview/session/{session_id}/answer   : 提交答案
- POST /interview/session/{session_id}/follow-up : 请求追问
- POST /interview/session/{session_id}/complete : 结束面试会话
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from src.schemas.interview import (
    InterviewSessionInfo,
    FollowUpRequest,
    FollowUpResponse,
)
from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.interview import FollowUpService

router = APIRouter(prefix="/interview", tags=["interview"])

# 全局追问服务实例，管理所有面试会话
service = FollowUpService()


@router.post("/session")
async def create_interview_session(jd: JDParseResult, resume: ResumeParseResult) -> InterviewSessionInfo:
    """创建新的面试会话，绑定 JD 和简历"""
    session = service.create_session(jd, resume)
    return InterviewSessionInfo(
        session_id=session.session_id,
        jd_id=session.state.jd_id,
        resume_id=session.state.resume_id,
    )


@router.get("/session/{session_id}")
async def get_session_info(session_id: str) -> InterviewSessionInfo:
    """获取指定会话的当前状态信息（进度、难度、是否完成等）"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return InterviewSessionInfo(
        session_id=session.session_id,
        jd_id=session.state.jd_id,
        resume_id=session.state.resume_id,
        start_time=session.start_time,
        total_turns=len(session.state.history),
        current_difficulty=session.state.current_difficulty,
        is_complete=session.state.is_complete,
    )


@router.post("/session/{session_id}/next-question")
async def get_next_question(session_id: str):
    """获取下一道面试题目（题目由系统根据之前表现动态调整）"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    question = session.next_question()
    if not question:
        raise HTTPException(status_code=500, detail="Failed to generate question")
    return {
        "question_id": question.question_id,
        "content": question.question_content,
        "type": question.question_type,
        "difficulty": question.question_difficulty,
    }


@router.post("/session/{session_id}/answer")
async def submit_answer(session_id: str, request: FollowUpRequest):
    """提交当前题目的答案，系统会评估回答质量"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        turn = session.submit_answer(request.question_id, request.answer)
        return {
            "turn_id": turn.turn_id,
            "answer_quality": turn.answer_quality,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/{session_id}/follow-up")
async def request_follow_up(session_id: str, request: FollowUpRequest):
    """根据上一轮回答请求追问，深入考察候选人"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    follow_up = session.follow_up(request.answer)
    if not follow_up:
        raise HTTPException(status_code=400, detail="No active question to follow up on")
    return FollowUpResponse(
        question_id=follow_up.question_id,
        content=follow_up.question_content,
        question_type=follow_up.question_type,
        difficulty=follow_up.question_difficulty,
        follow_up_of=request.question_id,
    )


@router.post("/session/{session_id}/complete")
async def complete_session(session_id: str) -> InterviewSessionInfo:
    """结束当前面试会话"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.complete()
