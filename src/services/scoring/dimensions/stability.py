from datetime import datetime

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.scoring.dimensions.base import BaseDimensionScorer, DimensionResult


class StabilityScorer(BaseDimensionScorer):
    def __init__(self) -> None:
        super().__init__("stability", "稳定性", weight=0.15)

    def score(self, jd: JDParseResult, resume: ResumeParseResult) -> DimensionResult:
        if not resume.工作经验:
            return DimensionResult(
                score=50.0,
                reason="无工作经历记录",
                confidence=0.5,
            )

        job_changes = len(resume.工作经验)
        total_years = self._calculate_total_years(resume.工作经验)
        avg_job_duration = total_years / job_changes if job_changes > 0 else 0

        duration_score = self._calculate_duration_score(avg_job_duration)
        change_score = self._calculate_change_score(job_changes, total_years)
        recent_stability = self._calculate_recent_stability(resume.工作经验)

        total_score = (
            duration_score * 0.4 +
            change_score * 0.3 +
            recent_stability * 0.3
        )

        reasons = []
        if avg_job_duration >= 2:
            reasons.append(f"平均任职: {avg_job_duration:.1f}年")
        if job_changes <= 3:
            reasons.append(f"工作变化: {job_changes}次")
        reasons.append(f"总经验: {total_years:.1f}年")

        return DimensionResult(
            score=total_score,
            reason=" | ".join(reasons),
            confidence=0.85,
            details={
                "job_changes": job_changes,
                "total_years": total_years,
                "avg_duration": round(avg_job_duration, 1),
                "recent_stability": recent_stability,
            },
        )

    def _calculate_total_years(self, experiences: list) -> float:
        if not experiences:
            return 0.0

        total_years = 0.0
        for exp in experiences:
            if hasattr(exp, "开始时间") and exp.开始时间:
                end_time = exp.结束时间 or datetime.now()
                years = (end_time - exp.开始时间).days / 365
                total_years += years

        return round(total_years, 1)

    def _calculate_duration_score(self, avg_duration: float) -> float:
        if avg_duration >= 3:
            return 100.0
        elif avg_duration >= 2:
            return 80.0
        elif avg_duration >= 1.5:
            return 60.0
        elif avg_duration >= 1:
            return 40.0
        else:
            return max(10.0, avg_duration * 30)

    def _calculate_change_score(self, job_changes: int, total_years: float) -> float:
        if total_years <= 0:
            return 50.0

        change_rate = job_changes / total_years

        if change_rate <= 0.3:
            return 100.0
        elif change_rate <= 0.5:
            return 80.0
        elif change_rate <= 0.8:
            return 60.0
        elif change_rate <= 1.0:
            return 40.0
        else:
            return max(10.0, 30 - change_rate * 10)

    def _calculate_recent_stability(self, experiences: list) -> float:
        if not experiences:
            return 50.0

        sorted_exps = sorted(
            experiences,
            key=lambda e: e.开始时间 or datetime.min,
            reverse=True
        )

        if len(sorted_exps) >= 2:
            latest = sorted_exps[0]
            if latest.开始时间:
                latest_duration = (datetime.now() - latest.开始时间).days / 365
                if latest_duration >= 1.5:
                    return 100.0
                elif latest_duration >= 1:
                    return 80.0
                elif latest_duration >= 0.5:
                    return 50.0
                else:
                    return 30.0

        return 60.0
