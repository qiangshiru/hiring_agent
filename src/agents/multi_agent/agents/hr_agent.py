from typing import Dict, Any

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.shared_state import SharedState
from src.agents.multi_agent.message_bus import MessageBus, Message


class HRAgent:
    def __init__(self, message_bus: MessageBus, shared_state: SharedState):
        self.name = "hr_agent"
        self.message_bus = message_bus
        self.shared_state = shared_state
        self.message_bus.subscribe("hr.evaluate", self._handle_evaluate)

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
        education_match = self._evaluate_education(jd, resume)
        experience_match = self._evaluate_experience(jd, resume)
        location_match = self._evaluate_location(jd, resume)

        overall_score = (education_match + experience_match + location_match) / 3

        return {
            "agent": self.name,
            "education_match": education_match,
            "experience_match": experience_match,
            "location_match": location_match,
            "overall_score": overall_score,
            "recommendation": self._get_recommendation(overall_score),
            "comments": self._generate_comments(jd, resume, overall_score),
        }

    def _evaluate_education(self, jd: JDParseResult, resume: ResumeParseResult) -> float:
        jd_degree = jd.学历 if hasattr(jd, "学历") else None
        resume_degrees = [edu.学历 for edu in resume.教育]

        degree_scores = {"博士": 1.0, "硕士": 0.85, "本科": 0.7, "大专": 0.5}

        if not resume_degrees:
            return 0.5

        highest_degree = max(resume_degrees, key=lambda d: degree_scores.get(d, 0))
        return degree_scores.get(highest_degree, 0.5)

    def _evaluate_experience(self, jd: JDParseResult, resume: ResumeParseResult) -> float:
        if hasattr(jd, "工作经验") and jd.工作经验:
            min_years = jd.工作经验.min_years or 0
        else:
            min_years = 0

        total_exp = len(resume.工作经验)
        if total_exp >= min_years:
            return min(1.0, 0.6 + total_exp * 0.08)
        return max(0.3, total_exp / max(min_years, 1))

    def _evaluate_location(self, jd: JDParseResult, resume: ResumeParseResult) -> float:
        return 0.8

    def _get_recommendation(self, score: float) -> str:
        if score >= 0.8:
            return "强烈推荐"
        elif score >= 0.6:
            return "推荐"
        elif score >= 0.4:
            return "待定"
        return "不推荐"

    def _generate_comments(self, jd, resume, score) -> str:
        comments = []
        if score >= 0.8:
            comments.append("候选人背景与职位要求高度匹配")
        elif score >= 0.6:
            comments.append("候选人基本符合职位要求")
        else:
            comments.append("建议进一步评估")
        return "; ".join(comments)
