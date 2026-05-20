import re
from datetime import datetime
from typing import Optional

from src.schemas.resume import WorkExperience
from src.services.resume_parser.extractors.base import (
    BaseExtractor,
    RuleBasedExtractor,
)


class ExperienceExtractor(RuleBasedExtractor[list[WorkExperience]]):
    company_keywords = ["公司", "企业", "集团", "有限", "科技", "网络", "软件"]
    position_keywords = ["工程师", "开发", "经理", "主管", "总监", "专家", "架构师", "设计师", "分析师"]
    section_titles = ["工作经历", "工作经验", "实习经历", "工作经历", "任职经历"]

    def extract(self, text: str) -> list[WorkExperience]:
        experiences: list[WorkExperience] = []
        blocks = self._split_into_sections(text)

        for block in blocks:
            experience = self._parse_experience_block(block)
            if experience:
                experiences.append(experience)

        return self._merge_duplicate_experiences(experiences)

    def _split_into_sections(self, text: str) -> list[str]:
        lines = text.split("\n")
        sections: list[list[str]] = []
        current_section: list[str] = []
        in_section = False

        for line in lines:
            stripped = line.strip()
            if self._is_section_header(stripped):
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
                current_section.append(stripped)
                in_section = True
            elif in_section and stripped:
                current_section.append(stripped)
            elif not in_section and stripped:
                current_section.append(stripped)
                if len(current_section) >= 3:
                    sections.append("\n".join(current_section))
                    current_section = []
                    in_section = True

        if current_section:
            sections.append("\n".join(current_section))

        return sections

    def _is_section_header(self, line: str) -> bool:
        line_lower = line.lower()
        return any(title in line for title in self.section_titles)

    def _parse_experience_block(self, block: str) -> Optional[WorkExperience]:
        company = self._extract_company(block)
        position = self._extract_position(block)
        start_date, end_date = self._extract_dates(block)
        skills = self._extract_skills(block)
        description = self._clean_description(block, company, position)

        if not company and not position:
            return None

        confidence = self._calculate_confidence(block, company, position)
        return WorkExperience(
            公司=company,
            职位=position,
            开始时间=start_date,
            结束时间=end_date,
            描述=description,
            技能=skills,
            置信度=confidence,
        )

    def _extract_company(self, block: str) -> Optional[str]:
        patterns = [
            r"([^\n,，。\s]{2,20}(?:公司|企业|集团|有限|科技|网络|软件))\s*(?:,|，|$)",
            r"(?:于|在)\s*([^\n,，。]+(?:公司|企业|集团|有限))\s*(?:任|做|担任|从事|$)",
            r"([A-Z][A-Za-z0-9\s]{2,30})(?:公司|Inc|Corp|Ltd)",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                company = match.group(1).strip()
                if len(company) >= 2:
                    return company
        return None

    def _extract_position(self, block: str) -> Optional[str]:
        patterns = [
            r"(?:担任|任职|职位|岗位)\s*[:：]?\s*([^\n,，。]+)",
            r"([^\n,，。]{2,15}(?:工程师|开发|经理|主管|总监|专家|架构师|设计师|分析师|顾问|负责人|专员|助理))",
            r"((?:高级|资深|中级|初级)?\s*(?:前端|后端|全栈|测试|运维|算法|数据|产品|运营|市场)?\s*(?:工程师|开发者|经理|设计师))",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                position = match.group(1).strip()
                if len(position) >= 2:
                    return position
        return None

    def _extract_dates(self, block: str) -> tuple[Optional[datetime], Optional[datetime]]:
        patterns = [
            r"(\d{4}[-/年]\d{1,2}[-/月]?)\s*[-~至]\s*(\d{4}[-/年]\d{1,2}[-/月]?|至今|现在)",
            r"(\d{4})\s*[-~至]\s*(\d{4}|至今|现在)",
            r"(\d{4}年)\s*[-~至]\s*(\d{4}年|至今)",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                start_str = match.group(1)
                end_str = match.group(2)

                start = self._parse_date(start_str)
                end = None if end_str in ["至今", "现在"] else self._parse_date(end_str)

                if start:
                    return start, end
        return None, None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        try:
            date_str = date_str.replace("年", "-").replace("月", "")
            if re.match(r"^\d{4}$", date_str):
                return datetime(int(date_str), 1, 1)
            parts = date_str.split("-")
            if len(parts) == 2:
                return datetime(int(parts[0]), int(parts[1]), 1)
            return None
        except (ValueError, IndexError):
            return None

    def _extract_skills(self, block: str) -> list[str]:
        skills: list[str] = []
        skill_patterns = [
            r"(?:使用|掌握|熟悉|精通)\s*[:：]?\s*([A-Za-z0-9+#.\s,，、]+)",
            r"([A-Za-z0-9+#]{2,20}(?:\s*[,，、]\s*[A-Za-z0-9+#]{2,20})+)",
        ]

        for pattern in skill_patterns:
            match = re.search(pattern, block)
            if match:
                skill_text = match.group(1)
                extracted = [s.strip() for s in re.split(r"[,，、\s]+", skill_text) if s.strip()]
                skills.extend(extracted[:10])
                break

        return list(set(skills))[:15]

    def _clean_description(
        self, block: str, company: Optional[str], position: Optional[str]
    ) -> Optional[str]:
        lines = block.split("\n")
        description_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if company and company in line:
                continue
            if position and position in line:
                continue
            if any(title in line for title in self.section_titles):
                continue
            if re.match(r"^\d{4}", line):
                continue
            if len(line) >= 5:
                description_lines.append(line)

        description = " ".join(description_lines)
        return description if len(description) > 10 else None

    def _calculate_confidence(
        self, block: str, company: Optional[str], position: Optional[str]
    ) -> float:
        confidence = 0.5
        if company:
            confidence += 0.2
        if position:
            confidence += 0.2
        if re.search(r"\d{4}", block):
            confidence += 0.1
        return min(1.0, confidence)

    def _merge_duplicate_experiences(
        self, experiences: list[WorkExperience]
    ) -> list[WorkExperience]:
        if not experiences:
            return []
        seen: dict[str, WorkExperience] = {}
        for exp in sorted(experiences, key=lambda x: x.开始时间 or datetime.min, reverse=True):
            key = (exp.公司 or "") + (exp.职位 or "")
            if key not in seen:
                seen[key] = exp
        return list(seen.values())
