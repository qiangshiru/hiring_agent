from datetime import datetime

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.scoring.dimensions.base import BaseDimensionScorer, DimensionResult


class EngineeringScorer(BaseDimensionScorer):
    def __init__(self) -> None:
        super().__init__("engineering", "工程能力", weight=0.2)
        self._engineering_keywords = [
            "架构", "系统设计", "微服务", "分布式", "高并发",
            "性能优化", "代码规范", "重构", "设计模式",
            "devops", "ci/cd", "自动化测试", "单元测试",
            "数据库设计", "缓存", "消息队列", "负载均衡",
            "容灾", "监控", "日志", "安全", "api",
        ]

    def score(self, jd: JDParseResult, resume: ResumeParseResult) -> DimensionResult:
        resume_text = self._build_resume_text(resume)
        resume_text_lower = resume_text.lower()

        matched_keywords = [
            kw for kw in self._engineering_keywords
            if kw.lower() in resume_text_lower
        ]

        project_count = len(resume.项目) if resume.项目 else 0
        experience_years = self._calculate_total_years(resume.工作经验)

        score = 0.0

        keyword_score = min(50.0, len(matched_keywords) * 10)
        score += keyword_score

        project_score = min(30.0, project_count * 10)
        score += project_score

        experience_score = min(20.0, experience_years * 4)
        score += experience_score

        score = min(100.0, score)

        reasons = []
        if matched_keywords:
            reasons.append(f"工程关键词: {len(matched_keywords)}个")
        if project_count > 0:
            reasons.append(f"项目数: {project_count}")
        if experience_years > 0:
            reasons.append(f"经验年限: {experience_years:.1f}年")

        return DimensionResult(
            score=score,
            reason=" | ".join(reasons) if reasons else "工程经验一般",
            confidence=self._calculate_confidence(jd, resume),
            details={
                "matched_keywords": matched_keywords[:10],
                "project_count": project_count,
                "experience_years": experience_years,
            },
        )

    def _build_resume_text(self, resume: ResumeParseResult) -> str:
        parts = []
        for proj in resume.项目:
            if proj.描述:
                parts.append(proj.描述)
        for exp in resume.工作经验:
            if exp.描述:
                parts.append(exp.描述)
        return " ".join(parts)

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
