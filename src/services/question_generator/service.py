import uuid
from typing import Optional

from src.schemas.jd import JDParseResult
from src.schemas.questions import (
    Question,
    QuestionDifficulty,
    QuestionGenerationConfig,
    QuestionGenerationResult,
    QuestionType,
)
from src.schemas.resume import ResumeParseResult
from src.services.question_generator.difficulty import DifficultyStrategy, get_strategy
from src.services.question_generator.generators import (
    DeepDiveQuestionGenerator,
    FailureQuestionGenerator,
    FoundationQuestionGenerator,
    ProjectQuestionGenerator,
    ScenarioQuestionGenerator,
    SystemDesignQuestionGenerator,
    TradeoffQuestionGenerator,
)


class QuestionGeneratorService:
    def __init__(
        self,
        config: QuestionGenerationConfig | None = None,
        difficulty_strategy: DifficultyStrategy | None = None,
    ):
        self._config = config or QuestionGenerationConfig()
        self._difficulty_strategy = difficulty_strategy or get_strategy("seniority")

        self._generators = {
            QuestionType.FOUNDATION: FoundationQuestionGenerator(),
            QuestionType.PROJECT: ProjectQuestionGenerator(),
            QuestionType.DEEP_DIVE: DeepDiveQuestionGenerator(),
            QuestionType.SCENARIO: ScenarioQuestionGenerator(),
            QuestionType.TRADEOFF: TradeoffQuestionGenerator(),
            QuestionType.FAILURE: FailureQuestionGenerator(),
            QuestionType.SYSTEM_DESIGN: SystemDesignQuestionGenerator(),
        }

    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        candidate: Optional[dict] = None,
    ) -> QuestionGenerationResult:
        questions: list[Question] = []
        difficulty_counts: dict[str, int] = {d.value: 0 for d in QuestionDifficulty}
        type_counts: dict[str, int] = {t.value: 0 for t in QuestionType}

        for question_type in QuestionType:
            count = self._calculate_count(question_type)
            if count == 0:
                continue

            difficulty = self._difficulty_strategy.calculate_difficulty(question_type, jd, resume)

            generator = self._generators[question_type]
            generated = generator.generate(jd, resume, difficulty, count)

            for q in generated:
                q.id = str(uuid.uuid4())
                questions.append(q)
                difficulty_counts[q.difficulty.value] += 1
                type_counts[q.type.value] += 1

        self._adjust_difficulty_distribution(questions, difficulty_counts)

        return QuestionGenerationResult(
            questions=questions,
            config=self._config,
            difficulty_distribution=difficulty_counts,
            type_distribution=type_counts,
        )

    def _calculate_count(self, question_type: QuestionType) -> int:
        ratio = self._config.type_distribution.get(question_type.value, 0)
        return max(1, round(self._config.total_questions * ratio))

    def _adjust_difficulty_distribution(
        self, questions: list[Question], difficulty_counts: dict[str, int]
    ) -> None:
        target_counts = {
            d.value: round(self._config.total_questions * self._config.difficulty_distribution.get(d, 0))
            for d in QuestionDifficulty
        }

        for difficulty in QuestionDifficulty:
            current = difficulty_counts[difficulty.value]
            target = target_counts[difficulty.value]

            if current < target:
                questions_to_convert = target - current
                for q in questions:
                    if questions_to_convert <= 0:
                        break
                    if q.difficulty.value != difficulty.value:
                        q.difficulty = difficulty
                        difficulty_counts[difficulty.value] += 1
                        difficulty_counts[q.difficulty.value] -= 1
                        questions_to_convert -= 1

    def set_config(self, config: QuestionGenerationConfig) -> None:
        self._config = config

    def get_config(self) -> QuestionGenerationConfig:
        return self._config

    def generate_by_type(
        self,
        question_type: QuestionType,
        jd: JDParseResult,
        resume: ResumeParseResult,
        count: int = 1,
        difficulty: QuestionDifficulty | None = None,
    ) -> list[Question]:
        generator = self._generators.get(question_type)
        if not generator:
            return []

        if difficulty is None:
            difficulty = self._difficulty_strategy.calculate_difficulty(question_type, jd, resume)

        questions = generator.generate(jd, resume, difficulty, count)
        for q in questions:
            q.id = str(uuid.uuid4())

        return questions

    def generate_batch(
        self,
        jd: JDParseResult,
        resumes: list[ResumeParseResult],
    ) -> list[QuestionGenerationResult]:
        return [self.generate(jd, resume) for resume in resumes]
