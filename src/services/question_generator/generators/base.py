from abc import ABC, abstractmethod
from typing import Optional

from src.schemas.jd import JDParseResult
from src.schemas.questions import Question, QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult


class BaseQuestionGenerator(ABC):
    @property
    @abstractmethod
    def question_type(self) -> QuestionType:
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        jd: JDParseResult,
        resume: ResumeParseResult,
        difficulty: QuestionDifficulty,
        count: int = 1,
    ) -> list[Question]:
        raise NotImplementedError

    def _generate_id(self, index: int) -> str:
        return f"{self.question_type.value}_{index}"

    def _adjust_difficulty(self, question: Question, difficulty: QuestionDifficulty) -> Question:
        question.difficulty = difficulty
        if difficulty == QuestionDifficulty.EASY:
            question.time_minutes = 3
            question.tags.append("入门")
        elif difficulty == QuestionDifficulty.MEDIUM:
            question.time_minutes = 5
            question.tags.append("进阶")
        elif difficulty == QuestionDifficulty.HARD:
            question.time_minutes = 8
            question.tags.append("高级")
        else:
            question.time_minutes = 10
            question.tags.append("专家")
        return question
