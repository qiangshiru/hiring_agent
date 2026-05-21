from typing import TypedDict

from src.schemas.jd import JDParseResult
from src.schemas.questions import (
    QuestionGenerationConfig,
    QuestionGenerationResult,
)
from src.schemas.resume import ResumeParseResult
from src.services.question_generator import QuestionGeneratorService


class QuestionAgentState(TypedDict, total=False):
    jd: JDParseResult
    resume: ResumeParseResult
    candidate: dict | None
    questions: QuestionGenerationResult | None


class QuestionGenerationAgent:
    def __init__(self, service: QuestionGeneratorService | None = None):
        self._service = service or QuestionGeneratorService()

    async def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        candidate: dict | None = None,
        config: QuestionGenerationConfig | None = None,
    ) -> QuestionGenerationResult:
        if config:
            self._service.set_config(config)

        result = self._service.generate(jd, resume, candidate)
        return result

    async def generate_with_strategy(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        strategy: str = "seniority",
        total_questions: int = 15,
    ) -> QuestionGenerationResult:
        from src.services.question_generator.difficulty import get_strategy

        difficulty_strategy = get_strategy(strategy)
        service = QuestionGeneratorService(difficulty_strategy=difficulty_strategy)

        config = QuestionGenerationConfig(total_questions=total_questions)
        service.set_config(config)

        return service.generate(jd, resume)


def build_question_agent(
    service: QuestionGeneratorService | None = None,
) -> QuestionGenerationAgent:
    return QuestionGenerationAgent(service)
