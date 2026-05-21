from typing import Dict, Any

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.agents.multi_agent.shared_state import SharedState
from src.agents.multi_agent.message_bus import MessageBus, Message
from src.services.question_generator import QuestionGeneratorService


class ArchitectAgent:
    def __init__(self, message_bus: MessageBus, shared_state: SharedState):
        self.name = "architect_agent"
        self.message_bus = message_bus
        self.shared_state = shared_state
        self.question_generator = QuestionGeneratorService()
        self.message_bus.subscribe("architect.evaluate", self._handle_evaluate)

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
        project_complexity = self._evaluate_project_complexity(resume)
        system_design_score = self._evaluate_system_design(jd, resume)
        architecture_experience = self._evaluate_architecture_experience(resume)

        overall_score = (project_complexity + system_design_score + architecture_experience) / 3

        return {
            "agent": self.name,
            "project_complexity": project_complexity,
            "system_design_score": system_design_score,
            "architecture_experience": architecture_experience,
            "overall_score": overall_score,
            "recommendation": self._get_recommendation(overall_score),
            "suggested_questions": self._generate_questions(jd, resume),
        }

    def _evaluate_project_complexity(self, resume: ResumeParseResult) -> float:
        projects = resume.项目 if hasattr(resume, "项目") else []
        if not projects:
            return 0.4

        complexity_scores = []
        for project in projects[:3]:
            desc = project.描述 if hasattr(project, "描述") else ""
            tech_stack = project.技术栈 if hasattr(project, "技术栈") else []

            score = 0.4
            if len(desc) > 100:
                score += 0.2
            if len(tech_stack) >= 3:
                score += 0.2
            if any(tech in ["微服务", "分布式", "高并发"] for tech in tech_stack):
                score += 0.2

            complexity_scores.append(min(1.0, score))

        return sum(complexity_scores) / len(complexity_scores)

    def _evaluate_system_design(self, jd: JDParseResult, resume: ResumeParseResult) -> float:
        keywords = ["架构", "设计", "系统", "分布式", "高可用"]
        job_requirements = str(jd.技术栈) if hasattr(jd, "技术栈") else ""

        score = 0.5
        if any(kw in job_requirements for kw in keywords):
            score += 0.3

        resume_text = str(resume.工作经验) + str(resume.项目)
        if any(kw in resume_text for kw in keywords):
            score += 0.2

        return min(1.0, score)

    def _evaluate_architecture_experience(self, resume: ResumeParseResult) -> float:
        experiences = resume.工作经验 if hasattr(resume, "工作经验") else []
        arch_roles = ["架构", "技术负责人", "技术总监"]

        for exp in experiences:
            position = exp.职位 if hasattr(exp, "职位") else ""
            if any(role in position for role in arch_roles):
                return 0.85

        return 0.5

    def _get_recommendation(self, score: float) -> str:
        if score >= 0.8:
            return "强烈推荐"
        elif score >= 0.6:
            return "推荐"
        elif score >= 0.4:
            return "待定"
        return "不推荐"

    def _generate_questions(self, jd: JDParseResult, resume: ResumeParseResult) -> list:
        try:
            result = self.question_generator.generate(jd, resume)
            system_design_questions = [
                q for q in result.questions if q.type == "system_design"
            ]
            return [q.content for q in system_design_questions[:3]]
        except:
            return ["请描述你参与设计过的最复杂的系统架构？"]
