from enum import Enum
from typing import Protocol

from src.schemas.jd import JDParseResult
from src.schemas.questions import QuestionDifficulty, QuestionType
from src.schemas.resume import ResumeParseResult


class DifficultyStrategy(Protocol):
    def calculate_difficulty(
        self,
        question_type: QuestionType,
        jd: JDParseResult,
        resume: ResumeParseResult,
    ) -> QuestionDifficulty:
        ...


class SeniorityDifficultyStrategy:
    def __init__(self, default_difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM):
        self._default_difficulty = default_difficulty

    def calculate_difficulty(
        self,
        question_type: QuestionType,
        jd: JDParseResult,
        resume: ResumeParseResult,
    ) -> QuestionDifficulty:
        seniority = self._assess_seniority(jd, resume)

        if seniority >= 8:
            return QuestionDifficulty.EXPERT
        elif seniority >= 6:
            if question_type in [QuestionType.SYSTEM_DESIGN, QuestionType.TRADEOFF]:
                return QuestionDifficulty.EXPERT
            return QuestionDifficulty.HARD
        elif seniority >= 4:
            return QuestionDifficulty.MEDIUM
        else:
            return QuestionDifficulty.EASY

    def _assess_seniority(self, jd: JDParseResult, resume: ResumeParseResult) -> int:
        score = 0

        if jd.工作经验.min_years >= 5:
            score += 3
        elif jd.工作经验.min_years >= 3:
            score += 2
        elif jd.工作经验.min_years >= 2:
            score += 1

        total_experience = self._calculate_experience_years(resume)
        if total_experience >= 8:
            score += 3
        elif total_experience >= 5:
            score += 2
        elif total_experience >= 3:
            score += 1

        highest_degree = self._get_highest_degree(resume)
        if highest_degree in ["硕士", "博士"]:
            score += 1

        has_senior_title = any(
            "高级" in exp.职位 or "专家" in exp.职位 or "架构" in exp.职位
            for exp in resume.工作经验
            if exp.职位
        )
        if has_senior_title:
            score += 2

        return min(10, score)

    def _calculate_experience_years(self, resume: ResumeParseResult) -> float:
        from datetime import datetime

        total = 0.0
        for exp in resume.工作经验:
            if exp.开始时间:
                end_time = exp.结束时间 or datetime.now()
                total += (end_time - exp.开始时间).days / 365
        return total

    def _get_highest_degree(self, resume: ResumeParseResult) -> str:
        degree_order = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
        highest_degree = ""
        highest_score = 0

        for edu in resume.教育:
            if edu.学历:
                score = degree_order.get(edu.学历, 0)
                if score > highest_score:
                    highest_score = score
                    highest_degree = edu.学历

        return highest_degree


class AdaptiveDifficultyStrategy:
    def calculate_difficulty(
        self,
        question_type: QuestionType,
        jd: JDParseResult,
        resume: ResumeParseResult,
    ) -> QuestionDifficulty:
        tech_match = self._calculate_tech_match(jd, resume)
        experience_score = self._calculate_experience_score(resume)

        base_score = (tech_match + experience_score) / 2

        if base_score >= 0.8:
            difficulty = QuestionDifficulty.HARD
        elif base_score >= 0.6:
            difficulty = QuestionDifficulty.MEDIUM
        else:
            difficulty = QuestionDifficulty.EASY

        if question_type in [QuestionType.SYSTEM_DESIGN, QuestionType.TRADEOFF]:
            if difficulty == QuestionDifficulty.EASY:
                difficulty = QuestionDifficulty.MEDIUM
            elif difficulty == QuestionDifficulty.MEDIUM:
                difficulty = QuestionDifficulty.HARD
            else:
                difficulty = QuestionDifficulty.EXPERT

        return difficulty

    def _calculate_tech_match(self, jd: JDParseResult, resume: ResumeParseResult) -> float:
        jd_techs = set(jd.技术栈.must + jd.技术栈.bonus)
        resume_skills = {s.名称.lower() for s in resume.技能}

        if not jd_techs:
            return 0.5

        matched = sum(1 for tech in jd_techs if tech.lower() in resume_skills)
        return matched / len(jd_techs)

    def _calculate_experience_score(self, resume: ResumeParseResult) -> float:
        from datetime import datetime

        total_years = 0.0
        for exp in resume.工作经验:
            if exp.开始时间:
                end_time = exp.结束时间 or datetime.now()
                total_years += (end_time - exp.开始时间).days / 365

        return min(1.0, total_years / 10)


class FixedDifficultyStrategy:
    def __init__(self, difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM):
        self._difficulty = difficulty

    def calculate_difficulty(
        self,
        question_type: QuestionType,
        jd: JDParseResult,
        resume: ResumeParseResult,
    ) -> QuestionDifficulty:
        return self._difficulty


def get_strategy(name: str = "seniority") -> DifficultyStrategy:
    strategies = {
        "seniority": SeniorityDifficultyStrategy(),
        "adaptive": AdaptiveDifficultyStrategy(),
        "easy": FixedDifficultyStrategy(QuestionDifficulty.EASY),
        "medium": FixedDifficultyStrategy(QuestionDifficulty.MEDIUM),
        "hard": FixedDifficultyStrategy(QuestionDifficulty.HARD),
        "expert": FixedDifficultyStrategy(QuestionDifficulty.EXPERT),
    }
    return strategies.get(name, strategies["seniority"])
