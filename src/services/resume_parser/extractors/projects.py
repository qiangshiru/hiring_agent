import re
from datetime import datetime
from typing import Optional

from src.schemas.resume import Project
from src.services.resume_parser.extractors.base import (
    BaseExtractor,
    RuleBasedExtractor,
)


class ProjectExtractor(RuleBasedExtractor[list[Project]]):
    section_titles = ["项目经历", "项目经验", "项目", "Project"]
    tech_patterns = [
        r"(?:技术栈|使用技术|使用|基于)\s*[:：]?\s*([^\n]+)",
        r"([A-Za-z0-9+#.\s]{10,})",
    ]

    def extract(self, text: str) -> list[Project]:
        projects: list[Project] = []
        blocks = self._split_into_project_blocks(text)

        for block in blocks:
            project = self._parse_project_block(block)
            if project:
                projects.append(project)

        return self._merge_duplicate_projects(projects)

    def _split_into_project_blocks(self, text: str) -> list[str]:
        lines = text.split("\n")
        blocks: list[str] = []
        current_block: list[str] = []
        in_project_section = False

        for line in lines:
            stripped = line.strip()
            if self._is_project_header(stripped):
                if current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
                current_block.append(stripped)
                in_project_section = True
            elif in_project_section:
                if stripped:
                    if len(current_block) == 1:
                        current_block.append(stripped)
                    elif not stripped:
                        blocks.append("\n".join(current_block[1:]))
                        current_block = []
                    else:
                        current_block.append(stripped)
                else:
                    blocks.append("\n".join(current_block[1:]))
                    current_block = []
                    in_project_section = False
            else:
                current_block = []

        if current_block and in_project_section:
            blocks.append("\n".join(current_block[1:]))

        return [b for b in blocks if b.strip()]

    def _is_project_header(self, line: str) -> bool:
        return any(title in line for title in self.section_titles)

    def _parse_project_block(self, block: str) -> Optional[Project]:
        project_name = self._extract_project_name(block)
        role = self._extract_role(block)
        start_date, end_date = self._extract_dates(block)
        description = self._extract_description(block, project_name)
        tech_stack = self._extract_tech_stack(block)

        if not project_name and not description:
            return None

        confidence = self._calculate_confidence(block, project_name, description)
        return Project(
            项目名称=project_name,
            角色=role,
            开始时间=start_date,
            结束时间=end_date,
            描述=description,
            技术栈=tech_stack,
            置信度=confidence,
        )

    def _extract_project_name(self, block: str) -> Optional[str]:
        patterns = [
            r"([^\n]{2,30}项目)",
            r"(?:项目名称|项目名)\s*[:：]?\s*([^\n,，]+)",
            r"(?:《|「)([^》」]+)(?:》|」)",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                name = match.group(1).strip()
                if len(name) >= 2 and "项目" not in name[:3]:
                    return name
                return name.replace("项目", "").strip()
        return None

    def _extract_role(self, block: str) -> Optional[str]:
        patterns = [
            r"(?:担任|角色|职责)\s*[:：]?\s*([^\n,，]+)",
            r"((?:负责人|主|开|开|技术)\s*人\s*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                role = match.group(1).strip()
                if len(role) >= 2:
                    return role
        return None

    def _extract_dates(self, block: str) -> tuple[Optional[datetime], Optional[datetime]]:
        patterns = [
            r"(\d{4}[-/年]\d{1,2})\s*[-~至]\s*(\d{4}[-/年]\d{1,2}|至今)",
            r"(\d{4})\s*[-~至]\s*(\d{4}|至今)",
        ]

        for pattern in patterns:
            match = re.search(pattern, block)
            if match:
                start_str = match.group(1)
                end_str = match.group(2)
                start = self._parse_date(start_str)
                end = None if end_str == "至今" else self._parse_date(end_str)
                if start:
                    return start, end
        return None, None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        try:
            date_str = re.sub(r"年|月", "-", date_str).rstrip("-")
            parts = date_str.split("-")
            if len(parts) >= 2:
                return datetime(int(parts[0]), int(parts[1]), 1)
            return None
        except (ValueError, IndexError):
            return None

    def _extract_description(self, block: str, project_name: Optional[str]) -> Optional[str]:
        lines = block.split("\n")
        description_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if project_name and project_name in line:
                continue
            if any(title in line for title in self.section_titles):
                continue
            if re.match(r"^(?:项目名称|角色|时间|技术栈)", line):
                continue
            if re.match(r"^\d{4}", line):
                continue
            if len(line) >= 10:
                description_lines.append(line)

        description = " ".join(description_lines)
        return description if len(description) >= 10 else None

    def _extract_tech_stack(self, block: str) -> list[str]:
        techs: list[str] = []
        common_techs = [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
            "React", "Vue", "Angular", "Node.js", "Django", "Flask", "Spring",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Kafka",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "TensorFlow", "PyTorch", "Keras", "Pandas", "NumPy",
            "Git", "Linux", "Nginx", "Apache",
        ]

        block_upper = block.upper()
        for tech in common_techs:
            if tech.upper() in block_upper:
                techs.append(tech)

        return list(set(techs))[:15]

    def _calculate_confidence(
        self, block: str, project_name: Optional[str], description: Optional[str]
    ) -> float:
        confidence = 0.5
        if project_name:
            confidence += 0.3
        if description:
            confidence += 0.2
        return min(1.0, confidence)

    def _merge_duplicate_projects(self, projects: list[Project]) -> list[Project]:
        if not projects:
            return []
        seen: dict[str, Project] = {}
        for proj in sorted(projects, key=lambda x: x.开始时间 or datetime.min, reverse=True):
            key = proj.项目名称 or ""
            if key not in seen:
                seen[key] = proj
        return list(seen.values())
