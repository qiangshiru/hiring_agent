from typing import Dict, Any

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.shared_state import SharedState
from src.agents.multi_agent.message_bus import MessageBus, Message
from src.services.screening import ScreeningService


class TechAgent:
    def __init__(self, message_bus: MessageBus, shared_state: SharedState):
        self.name = "tech_agent"
        self.message_bus = message_bus
        self.shared_state = shared_state
        self.screening_service = ScreeningService()
        self.message_bus.subscribe("tech.evaluate", self._handle_evaluate)

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
            screening_result = self.screening_service.screen(jd, resume)
            tech_match = screening_result.技术匹配度
            ai_depth = screening_result.AI能力深度
            engineering_ability = screening_result.工程能力

            overall_score = (tech_match + ai_depth + engineering_ability) / 3

            return {
                "agent": self.name,
                "tech_match": tech_match,
                "ai_depth": ai_depth,
                "engineering_ability": engineering_ability,
                "overall_score": overall_score,
                "recommendation": self._get_recommendation(overall_score),
                "key_skills": [s for s in resume.技能[:5]],
            }
        except Exception as e:
            return {
                "agent": self.name,
                "error": str(e),
                "overall_score": 0.0,
                "recommendation": "待定",
            }

    def _get_recommendation(self, score: float) -> str:
        if score >= 0.8:
            return "强烈推荐"
        elif score >= 0.6:
            return "推荐"
        elif score >= 0.4:
            return "待定"
        return "不推荐"
