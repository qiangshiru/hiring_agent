from datetime import datetime
from typing import Any

from src.services.screening.matchers.base import BaseMatcher, MatchResult


class ExperienceMatcher(BaseMatcher):
    def match(self, jd_requirement: str | list[str], resume_value: Any) -> MatchResult:
        if isinstance(jd_requirement, list):
            jd_years = self._parse_years(jd_requirement[0]) if jd_requirement else 0
        else:
            jd_years = self._parse_years(jd_requirement)

        resume_years = self._calculate_resume_years(resume_value)

        if jd_years <= 0:
            return MatchResult(
                score=1.0,
                matched=True,
                reason="无工作经验要求",
                confidence=1.0,
            )

        if resume_years <= 0:
            return MatchResult(
                score=0.0,
                matched=False,
                reason="简历中无工作经验",
                confidence=1.0,
            )

        score = min(1.0, resume_years / jd_years)
        matched = resume_years >= jd_years

        if matched:
            reason = f"工作经验满足: {resume_years:.1f}年 >= {jd_years}年"
        else:
            reason = f"工作经验不足: {resume_years:.1f}年 < {jd_years}年"

        return MatchResult(
            score=score,
            matched=matched,
            reason=reason,
            confidence=0.9,
            details={"resume_years": resume_years, "required_years": jd_years},
        )

    def _parse_years(self, requirement: str) -> int:
        if not requirement:
            return 0

        import re

        match = re.search(r"(\d+)", str(requirement))
        return int(match.group(1)) if match else 0

    def _calculate_resume_years(self, experience: Any) -> float:
        if not experience:
            return 0.0

        total_years = 0.0

        if hasattr(experience, "__iter__") and not isinstance(experience, str):
            for exp in experience:
                if hasattr(exp, "开始时间") and exp.开始时间:
                    end_time = exp.结束时间 or datetime.now()
                    years = (end_time - exp.开始时间).days / 365
                    total_years += years

        return total_years

    def match_company_tier(
        self, preferred_companies: list[str], resume_companies: list[str]
    ) -> MatchResult:
        if not preferred_companies:
            return MatchResult(score=1.0, matched=True, reason="无公司偏好")

        company_keywords = {
            "大厂": ["字节", "阿里", "腾讯", "百度", "京东", "美团", "滴滴", "拼多多", "华为"],
            "一线": ["字节跳动", "阿里巴巴", "腾讯", "百度", "京东", "美团", "华为", "小米"],
            "外企": ["Google", "Meta", "Amazon", "Microsoft", "Apple", "Netflix", "Uber"],
        }

        matched_tiers = []
        for company in resume_companies:
            for tier, keywords in company_keywords.items():
                if any(kw in company for kw in keywords):
                    matched_tiers.append(tier)
                    break

        score = len(set(matched_tiers)) / len(company_keywords) if company_keywords else 0

        return MatchResult(
            score=score,
            matched=len(matched_tiers) > 0,
            reason=f"匹配到 {len(set(matched_tiers))} 个公司层级",
            confidence=0.85,
            details={"matched_tiers": list(set(matched_tiers))},
        )
