from datetime import datetime
from typing import Dict, List, Optional

from src.schemas.interview import InterviewTurn


class InterviewMemory:
    def __init__(self, max_turns: int = 50, summary_window: int = 10):
        self.short_term_turns: List[InterviewTurn] = []
        self.long_term_summaries: List[str] = []
        self.max_turns = max_turns
        self.summary_window = summary_window

    def add_turn(self, turn: InterviewTurn) -> None:
        self.short_term_turns.append(turn)
        self._maybe_compress()

    def get_recent_turns(self, count: int = 5) -> List[InterviewTurn]:
        return self.short_term_turns[-count:]

    def get_full_history(self) -> List[InterviewTurn]:
        return list(self.short_term_turns)

    def get_summary(self) -> str:
        if not self.long_term_summaries:
            return self._generate_summary_from_turns()
        return "\n".join(self.long_term_summaries)

    def _maybe_compress(self) -> None:
        if len(self.short_term_turns) <= self.max_turns:
            return
        compress_count = min(self.summary_window, len(self.short_term_turns) // 2)
        turns_to_compress = self.short_term_turns[:compress_count]
        self.short_term_turns = self.short_term_turns[compress_count:]
        summary = self._summarize_turns(turns_to_compress)
        self.long_term_summaries.append(summary)

    def _summarize_turns(self, turns: List[InterviewTurn]) -> str:
        summary_parts = [
            f"Question {i+1}: {turn.question_content[:100]}..."
            for i, turn in enumerate(turns)
        ]
        return "\n".join(summary_parts)

    def _generate_summary_from_turns(self) -> str:
        if not self.short_term_turns:
            return "No interview history yet."
        return f"Interview started with {len(self.short_term_turns)} turns."


class LongTermMemory:
    def __init__(self):
        self.candidate_histories: Dict[str, List[Dict]] = {}

    def add_interview(self, candidate_id: str, interview_data: Dict) -> None:
        if candidate_id not in self.candidate_histories:
            self.candidate_histories[candidate_id] = []
        self.candidate_histories[candidate_id].append(interview_data)

    def get_history(self, candidate_id: str) -> List[Dict]:
        return self.candidate_histories.get(candidate_id, [])
