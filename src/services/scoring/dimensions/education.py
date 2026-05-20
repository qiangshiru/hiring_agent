from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.scoring.dimensions.base import BaseDimensionScorer, DimensionResult


class EducationScorer(BaseDimensionScorer):
    def __init__(self) -> None:
        super().__init__("education", "教育背景", weight=0.15)
        self._degree_scores = {
            "博士": 100,
            "博士后": 100,
            "硕士": 80,
            "MBA": 85,
            "EMBA": 90,
            "本科": 60,
            "一本": 70,
            "二本": 50,
            "大专": 30,
            "高职": 20,
        }
        self._tier_schools = {
            "清华": 100, "北大": 100, "复旦": 95, "上交": 95, "浙大": 95,
            "中科大": 95, "南大": 90, "人大": 90, "北航": 88, "同济": 85,
            "985": 80, "211": 60,
        }

    def score(self, jd: JDParseResult, resume: ResumeParseResult) -> DimensionResult:
        if not resume.教育:
            return DimensionResult(
                score=20.0,
                reason="无教育背景信息",
                confidence=0.5,
            )

        best_education = max(resume.教育, key=lambda e: self._get_education_score(e))

        degree_score = self._get_degree_score(best_education.学历 or "")
        school_score = self._get_school_score(best_education.学校 or "")

        major_score = 0.0
        if best_education.专业:
            major_score = self._get_major_score(best_education.专业)

        total_score = (degree_score * 0.5 + school_score * 0.3 + major_score * 0.2)

        reasons = []
        if best_education.学校:
            reasons.append(f"学校: {best_education.学校}")
        if best_education.学历:
            reasons.append(f"学历: {best_education.学历}")
        if best_education.专业:
            reasons.append(f"专业: {best_education.专业}")

        return DimensionResult(
            score=total_score,
            reason=" | ".join(reasons) if reasons else "教育背景一般",
            confidence=0.95,
            details={
                "degree_score": degree_score,
                "school_score": school_score,
                "major_score": major_score,
                "best_education": {
                    "school": best_education.学校,
                    "degree": best_education.学历,
                    "major": best_education.专业,
                },
            },
        )

    def _get_education_score(self, education) -> float:
        degree_score = self._get_degree_score(education.学历 or "")
        school_score = self._get_school_score(education.学校 or "")
        return degree_score + school_score

    def _get_degree_score(self, degree: str) -> float:
        if not degree:
            return 30.0
        degree_upper = degree.upper()
        for key, score in self._degree_scores.items():
            if key in degree_upper or degree_upper in key:
                return score
        return 40.0

    def _get_school_score(self, school: str) -> float:
        if not school:
            return 20.0
        school_lower = school.lower()
        for key, score in self._tier_schools.items():
            if key.lower() in school_lower:
                return score
        return 30.0

    def _get_major_score(self, major: str) -> float:
        if not major:
            return 0.0

        high_value_majors = [
            "计算机", "软件工程", "人工智能", "数据科学", "机器学习",
            "电子工程", "自动化", "通信工程", "数学", "统计",
        ]
        major_lower = major.lower()
        for m in high_value_majors:
            if m.lower() in major_lower:
                return 80.0

        return 50.0
