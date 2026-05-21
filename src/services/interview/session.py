import uuid
from datetime import datetime
from typing import Dict, Optional

from src.schemas.interview import (
    InterviewSessionState,
    InterviewTurn,
    InterviewSessionInfo,
    QuestionType,
    QuestionDifficulty,
    AnswerQuality,
)
from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.interview.memory import InterviewMemory
from src.services.question_generator import QuestionGeneratorService


class InterviewSession:
    def __init__(self, jd: JDParseResult, resume: ResumeParseResult, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.jd = jd
        self.resume = resume
        self.state = InterviewSessionState(
            session_id=self.session_id,
            jd_id="jd-" + self.session_id[:8],
            resume_id="resume-" + self.session_id[8:16],
        )
        self.memory = InterviewMemory()
        self.question_service = QuestionGeneratorService()
        self.current_turn_index = 0
        self.start_time = datetime.now()

    def next_question(self) -> InterviewTurn:
        questions = self.question_service.generate(self.jd, self.resume)
        if questions.questions:
            question = questions.questions[self.current_turn_index % len(questions.questions)]
            turn = InterviewTurn(
                turn_id=str(uuid.uuid4()),
                question_id=question.id,
                question_content=question.content,
                question_type=question.type,
                question_difficulty=self.state.current_difficulty,
                answer_content="",
                answer_quality=AnswerQuality.NO_ANSWER,
            )
            self.state.current_question = turn
            return turn

    def submit_answer(self, question_id: str, answer: str) -> InterviewTurn:
        if not self.state.current_question or self.state.current_question.question_id != question_id:
            raise ValueError("Question mismatch")
        turn = self.state.current_question.model_copy(deep=True)
        turn.answer_content = answer
        turn.answer_quality = self._evaluate_answer(answer)
        self._update_session_state(turn)
        self.memory.add_turn(turn)
        self.state.history.append(turn)
        self.current_turn_index += 1
        return turn

    def follow_up(self, answer: str) -> Optional[InterviewTurn]:
        if not self.state.current_question:
            return None

        question_id = self.state.current_question.question_id
        original_question = self.state.current_question.question_content
        content = self._generate_follow_up(original_question, answer)
        follow_up_turn = InterviewTurn(
            turn_id=str(uuid.uuid4()),
            question_id=str(uuid.uuid4()),
            question_content=content,
            question_type=QuestionType.FOLLOW_UP,
            question_difficulty=self.state.current_difficulty,
            answer_content="",
            answer_quality=AnswerQuality.NO_ANSWER,
        )
        self.state.current_question = follow_up_turn
        return follow_up_turn

    def complete(self) -> InterviewSessionInfo:
        self.state.is_complete = True
        end_time = datetime.now()
        return InterviewSessionInfo(
            session_id=self.session_id,
            jd_id=self.state.jd_id,
            resume_id=self.state.resume_id,
            start_time=self.start_time,
            end_time=end_time,
            total_turns=len(self.state.history),
            current_difficulty=self.state.current_difficulty,
            is_complete=True,
            overall_score=self.state.total_score,
        )

    def _evaluate_answer(self, answer: str) -> AnswerQuality:
        if not answer or len(answer.strip()) < 10:
            return AnswerQuality.NO_ANSWER
        quality_score = min(len(answer.strip()) / 500, 1.0)
        if quality_score > 0.6:
            return AnswerQuality.GOOD
        elif quality_score > 0.3:
            return AnswerQuality.FAIR
        return AnswerQuality.POOR

    def _update_session_state(self, turn: InterviewTurn) -> None:
        quality = turn.answer_quality
        if quality in [AnswerQuality.EXCELLENT, AnswerQuality.GOOD]:
            self._increase_difficulty()
            self.state.strengths.append(turn.question_content[:50])
        elif quality in [AnswerQuality.POOR, AnswerQuality.NO_ANSWER]:
            self._decrease_difficulty()
            self.state.knowledge_gaps.append(turn.question_content[:50])
    def _increase_difficulty(self) -> None:
        order = [QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD, QuestionDifficulty.EXPERT]
        current_idx = order.index(self.state.current_difficulty)
        if current_idx < len(order) - 1:
            self.state.current_difficulty = order[current_idx + 1]

    def _decrease_difficulty(self) -> None:
        order = [QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD, QuestionDifficulty.EXPERT]
        current_idx = order.index(self.state.current_difficulty)
        if current_idx > 0:
            self.state.current_difficulty = order[current_idx - 1]

    def _generate_follow_up(self, question: str, answer: str) -> str:
        follow_up_templates = [
            f"你刚才提到...，能否详细说明一下？",
            f"为什么你会选择这种方法？有什么考虑？",
            f"能否举一个实际的例子来说明？",
            f"这个问题的核心挑战是什么？",
            f"你是如何解决这个问题的？",
            f"这个方案有什么潜在的改进空间？",
        ]

        keywords = ["为什么", "如何", "如何实现", "如何优化"]
        for keyword in keywords:
            if keyword in question and keyword not in answer:
                return f"关于{keyword}...，能否进一步说明？"

        import random
        return random.choice(follow_up_templates)
