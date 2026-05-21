from typing import Dict, Any

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.shared_state import SharedState
from src.agents.multi_agent.message_bus import MessageBus, Message
from src.services.risk_detection import RiskDetectionService
from src.schemas.evaluation import InterviewRecord, InterviewTurnRecord
from datetime import datetime


class RiskAgent:
    def __init__(self, message_bus: MessageBus, shared_state: SharedState):
        self.name = "risk_agent"
        self.message_bus = message_bus
        self.shared_state = shared_state
        self.risk_service = RiskDetectionService()
        self.message_bus.subscribe("risk.evaluate", self._handle_evaluate)

    def _handle_evaluate(self, message: Message):
        jd = self.shared_state.get_jd()
        resume = self.shared_state.get_resume()

        if jd and resume:
            result = self.evaluate(jd, resume)
            self.shared_state.set_agent_result(self.name, result)
            self.message_bus.publish(
                Message(
                    sender=self.name,
                    recipient="orchestrator",
                    topic="agent.completed",
                    payload={"agent": self.name, "result": result},
                )
            )

    def evaluate(self, jd: JDParseResult, resume: ResumeParseResult) -> Dict[str, Any]:
        try:
            mock_interview = self._create_mock_interview(resume)
            risk_result = self.risk_service.detect(mock_interview, resume)

            risk_count = len(risk_result.risks)
            overall_risk_level = risk_result.overall_risk_level.value

            risk_score = self._calculate_risk_score(risk_count, overall_risk_level)

            return {
                "agent": self.name,
                "risk_count": risk_count,
                "overall_risk_level": overall_risk_level,
                "risk_score": risk_score,
                "recommendation": self._get_recommendation(risk_score),
                "risks": [
                    {
                        "type": r.risk_type.value,
                        "level": r.risk_level.value,
                        "description": r.description,
                    }
                    for r in risk_result.risks
                ],
            }
        except Exception as e:
            return {
                "agent": self.name,
                "error": str(e),
                "risk_count": 0,
                "overall_risk_level": "无",
                "risk_score": 0.5,
                "recommendation": "待定",
                "risks": [],
            }

    def _create_mock_interview(self, resume: ResumeParseResult) -> InterviewRecord:
        turns = []
        projects = resume.项目 if hasattr(resume, "项目") else []

        for i, project in enumerate(projects[:3]):
            turn = InterviewTurnRecord(
                turn_id=f"t{i+1}",
                question=f"请介绍一下你在 {project.项目名称} 项目中的职责？",
                question_type="project",
                answer="我负责核心模块开发，参与了架构设计...",
                answer_quality="good",
                confidence=0.7,
            )
            turns.append(turn)

        return InterviewRecord(
            session_id="mock-session",
            jd_id="mock-jd",
            resume_id="mock-resume",
            turns=turns,
            start_time=datetime.now(),
        )

    def _calculate_risk_score(self, risk_count: int, risk_level: str) -> float:
        base_score = 1.0

        if risk_count == 0:
            return 0.1
        elif risk_count == 1:
            if risk_level == "高":
                return 0.7
            elif risk_level == "中":
                return 0.4
            else:
                return 0.2
        elif risk_count >= 2:
            if risk_level == "高":
                return 0.9
            elif risk_level == "中":
                return 0.6
            else:
                return 0.4

        return base_score

    def _get_recommendation(self, risk_score: float) -> str:
        if risk_score <= 0.2:
            return "强烈推荐"
        elif risk_score <= 0.4:
            return "推荐"
        elif risk_score <= 0.6:
            return "待定"
        return "不推荐"
