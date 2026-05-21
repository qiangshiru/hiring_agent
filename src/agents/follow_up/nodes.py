from typing import Dict, Any

from src.agents.follow_up.state import InterviewAgentState
from src.schemas.interview import QuestionDifficulty, AnswerQuality, QuestionType


class FollowUpNodes:
    def __init__(self):
        pass

    def evaluate_answer(self, state: InterviewAgentState) -> Dict[str, Any]:
        current_question = state.get("current_question", "")
        messages = state.get("messages", [])
        last_message = messages[-1].content if messages else ""

        quality = self._simple_evaluate(last_message)

        return {
            "session_state": {**state["session_state"], "answer_quality": quality},
            "should_continue": quality in [AnswerQuality.GOOD, AnswerQuality.FAIR],
        }

    def generate_follow_up(self, state: InterviewAgentState) -> Dict[str, Any]:
        current_question = state.get("current_question", "")
        messages = state.get("messages", [])
        last_answer = messages[-1].content if messages else ""

        follow_up = self._simple_generate_follow_up(current_question, last_answer)

        return {
            "messages": [("assistant", follow_up)],
            "current_question": follow_up,
            "follow_up_needed": False,
        }

    def adjust_difficulty(self, state: InterviewAgentState) -> Dict[str, Any]:
        session_state = state.get("session_state", {})
        quality = session_state.get("answer_quality", AnswerQuality.FAIR)
        current_difficulty = state.get("current_difficulty", QuestionDifficulty.MEDIUM)

        new_difficulty = self._adjust_difficulty_logic(current_difficulty, quality)

        return {
            "current_difficulty": new_difficulty,
            "session_state": {**session_state, "current_difficulty": new_difficulty},
        }

    def check_should_continue(self, state: InterviewAgentState) -> Dict[str, Any]:
        session_state = state.get("session_state", {})
        history = session_state.get("history", [])
        turn_count = len(history)

        should_continue = turn_count < 20
        return {"should_continue": should_continue}

    def _simple_evaluate(self, answer: str) -> AnswerQuality:
        if not answer or len(answer.strip()) < 10:
            return AnswerQuality.NO_ANSWER
        score = len(answer.strip()) / 500
        if score > 0.8:
            return AnswerQuality.EXCELLENT
        elif score > 0.5:
            return AnswerQuality.GOOD
        elif score > 0.2:
            return AnswerQuality.FAIR
        return AnswerQuality.POOR

    def _simple_generate_follow_up(self, question: str, answer: str) -> str:
        follow_ups = [
            "你刚才提到的这个方案，在实际项目中是如何应用的？",
            "为什么你会选择这种技术方案？有什么权衡考虑吗？",
            "能否详细说明一下实现细节？",
            "这个方案有什么潜在的问题或改进空间？",
            "能否举一个具体的例子来说明？",
        ]
        import random
        return random.choice(follow_ups)

    def _adjust_difficulty_logic(
        self, current: QuestionDifficulty, quality: AnswerQuality
    ) -> QuestionDifficulty:
        order = [QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD, QuestionDifficulty.EXPERT]
        current_idx = order.index(current)

        if quality in [AnswerQuality.EXCELLENT, AnswerQuality.GOOD]:
            return order[min(current_idx + 1, len(order) - 1)]
        elif quality in [AnswerQuality.POOR, AnswerQuality.NO_ANSWER]:
            return order[max(current_idx - 1, 0)]
        return current
