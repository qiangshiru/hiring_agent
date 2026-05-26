import uuid
from typing import Optional, Dict, Any

from src.core.logging import get_logger
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

logger = get_logger(__name__)


class QuestionGeneratorService:
    def __init__(
        self,
        config: Optional[QuestionGenerationConfig] = None,
        difficulty_strategy: Optional[DifficultyStrategy] = None,
    ):
        self._config = config or QuestionGenerationConfig()
        self._difficulty_strategy = difficulty_strategy or get_strategy("seniority")

        self._generators: Dict[QuestionType, Any] = {
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
        """生成面试问题。
        
        Args:
            jd: 解析后的 JD 结果
            resume: 解析后的简历结果
            candidate: 候选人额外信息（可选）
        
        Returns:
            问题生成结果，包含生成的问题列表和分布统计
        
        Raises:
            ValueError: JD 或简历为空
        """
        if not jd:
            raise ValueError("JD 不能为空")
        if not resume:
            raise ValueError("简历不能为空")

        logger.info(
            "question_generation_start",
            candidate_name=resume.姓名 or "unknown",
            total_questions=self._config.total_questions,
        )

        questions: list[Question] = []
        difficulty_counts: Dict[str, int] = {d.value: 0 for d in QuestionDifficulty}
        type_counts: Dict[str, int] = {t.value: 0 for t in QuestionType}

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

            logger.debug(
                "questions_generated",
                question_type=question_type.value,
                count=len(generated),
                difficulty=difficulty.value,
            )

        self._adjust_difficulty_distribution(questions, difficulty_counts)

        result = QuestionGenerationResult(
            questions=questions,
            config=self._config,
            difficulty_distribution=difficulty_counts,
            type_distribution=type_counts,
        )

        logger.info(
            "question_generation_complete",
            candidate_name=resume.姓名 or "unknown",
            total_generated=len(questions),
            types_covered=len(type_counts),
        )

        return result

    def _calculate_count(self, question_type: QuestionType) -> int:
        """计算特定类型问题的生成数量。"""
        ratio = self._config.type_distribution.get(question_type.value, 0)
        return max(1, round(self._config.total_questions * ratio))

    def _adjust_difficulty_distribution(
        self, questions: list[Question], difficulty_counts: Dict[str, int]
    ) -> None:
        """调整难度分布以符合配置目标。"""
        target_counts = {
            d.value: round(
                self._config.total_questions * self._config.difficulty_distribution.get(d, 0)
            )
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
                        old_difficulty = q.difficulty.value
                        q.difficulty = difficulty
                        difficulty_counts[difficulty.value] += 1
                        difficulty_counts[old_difficulty] -= 1
                        questions_to_convert -= 1

    def set_config(self, config: QuestionGenerationConfig) -> None:
        """设置问题生成配置。"""
        self._config = config
        logger.info("question_generator_config_updated")

    def get_config(self) -> QuestionGenerationConfig:
        """获取当前配置。"""
        return self._config

    def generate_by_type(
        self,
        question_type: QuestionType,
        jd: JDParseResult,
        resume: ResumeParseResult,
        count: int = 1,
        difficulty: Optional[QuestionDifficulty] = None,
    ) -> list[Question]:
        """按类型生成问题。
        
        Args:
            question_type: 问题类型
            jd: 解析后的 JD 结果
            resume: 解析后的简历结果
            count: 生成数量
            difficulty: 难度级别（可选）
        
        Returns:
            问题列表
        """
        generator = self._generators.get(question_type)
        if not generator:
            logger.warning(
                "unknown_question_type",
                question_type=question_type.value,
            )
            return []

        if difficulty is None:
            difficulty = self._difficulty_strategy.calculate_difficulty(question_type, jd, resume)

        questions = generator.generate(jd, resume, difficulty, count)
        for q in questions:
            q.id = str(uuid.uuid4())

        logger.info(
            "questions_generated_by_type",
            question_type=question_type.value,
            count=len(questions),
        )

        return questions

    def generate_batch(
        self,
        jd: JDParseResult,
        resumes: list[ResumeParseResult],
    ) -> list[QuestionGenerationResult]:
        """批量为多个简历生成问题。"""
        logger.info("question_generation_batch_start", extra={"resumes_count": len(resumes)})
        results = [self.generate(jd, resume) for resume in resumes]
        logger.info("question_generation_batch_complete", extra={"resumes_count": len(resumes)})
        return results
