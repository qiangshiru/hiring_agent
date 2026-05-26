import json
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.services.interview import FollowUpService

router = APIRouter(prefix="/interview/ws", tags=["interview-ws"])
service = FollowUpService()


class InterviewConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = InterviewConnectionManager()


@router.websocket("/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        session = service.get_session(session_id)
        if not session:
            await websocket.send_json({"type": "error", "message": "Session not found"})
            return

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")

            if message_type == "next_question":
                question = session.next_question()
                if question:
                    await websocket.send_json({
                        "type": "question",
                        "question_id": question.question_id,
                        "content": question.question_content,
                        "type": question.question_type,
                        "difficulty": question.question_difficulty,
                    })

            elif message_type == "answer":
                question_id = message.get("question_id")
                answer = message.get("answer")
                if question_id and answer:
                    try:
                        turn = session.submit_answer(question_id, answer)
                        await websocket.send_json({
                            "type": "answer_evaluated",
                            "answer_quality": turn.answer_quality,
                            "confidence": turn.confidence,
                        })
                    except ValueError as e:
                        await websocket.send_json({"type": "error", "message": str(e)})

            elif message_type == "follow_up":
                answer = message.get("answer", "")
                follow_up = session.follow_up(answer)
                if follow_up:
                    await websocket.send_json({
                        "type": "question",
                        "question_id": follow_up.question_id,
                        "content": follow_up.question_content,
                        "type": follow_up.question_type,
                        "difficulty": follow_up.question_difficulty,
                    })

            elif message_type == "complete":
                session_info = session.complete()
                await websocket.send_json({
                    "type": "session_complete",
                    "session_info": session_info.model_dump(),
                })
                break

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        manager.disconnect(session_id)
