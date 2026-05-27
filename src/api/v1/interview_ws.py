"""面试会话 WebSocket 接口

提供的端点：
- WS /interview/ws/{session_id} : WebSocket 实时面试通信

支持的消息类型：
- next_question : 请求下一道面试题
- answer        : 提交答案，返回评估结果
- follow_up     : 请求追问
- complete      : 结束面试会话
- ping          : 心跳保活
"""

import json
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.services.interview import FollowUpService

router = APIRouter(prefix="/interview/ws", tags=["interview-ws"])

# 全局服务实例
service = FollowUpService()


class InterviewConnectionManager:
    """WebSocket 连接管理器，负责管理所有活跃的面试会话连接"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """接受 WebSocket 连接并注册到活跃连接池"""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """从活跃连接池中移除指定会话"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: dict):
        """向指定会话推送 JSON 消息"""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = InterviewConnectionManager()


@router.websocket("/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """WebSocket 入口：建立连接后进入消息循环，解析客户端消息类型并分发处理"""
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
                # 生成下一道面试题并推送
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
                # 评估候选人回答质量
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
                # 生成追问题目
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
                # 结束会话并返回汇总信息
                session_info = session.complete()
                await websocket.send_json({
                    "type": "session_complete",
                    "session_info": session_info.model_dump(),
                })
                break

            elif message_type == "ping":
                # 心跳保活机制
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        manager.disconnect(session_id)
