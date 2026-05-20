from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.services.scoring.dimensions.base import BaseDimensionScorer, DimensionResult


class AIDepthScorer(BaseDimensionScorer):
    def __init__(self) -> None:
        super().__init__("ai_depth", "AI深度", weight=0.25)
        self._ai_keywords = {
            "llm": ["llm", "大模型", "大语言模型", "gpt", "chatgpt", "claude", "gemini"],
            "rag": ["rag", "retrieval", "向量检索", "知识库", "embedding"],
            "agent": ["agent", "智能体", "multi-agent", "agentic"],
            "nlp": ["nlp", "自然语言处理", "文本分类", "实体识别", "情感分析", "ner"],
            "cv": ["cv", "计算机视觉", "图像识别", "目标检测", "ocr", "yolo"],
            "ml": ["机器学习", "ml", "machine learning", "监督学习", "无监督学习"],
            "dl": ["深度学习", "dl", "deep learning", "神经网络", "cnn", "rnn", "transformer"],
            "frameworks": ["langchain", "llamaindex", "huggingface", "vllm", "ollama", "tensorrt"],
        }

    def score(self, jd: JDParseResult, resume: ResumeParseResult) -> DimensionResult:
        resume_text = self._build_resume_text(resume)
        resume_text_lower = resume_text.lower()

        jd_ai_required = self._extract_ai_requirements(jd)
        resume_ai_skills = self._extract_ai_skills(resume_text_lower)

        if not jd_ai_required:
            max_depth = self._calculate_max_depth(resume_ai_skills)
            score = min(100.0, max_depth * 20)
            return DimensionResult(
                score=score,
                reason=f"AI能力深度评分: {score:.0f}分",
                confidence=0.85,
                details={"ai_skills": list(resume_ai_skills)},
            )

        matched = jd_ai_required & resume_ai_skills
        score = (len(matched) / len(jd_ai_required)) * 100

        depth_bonus = 0.0
        for category, keywords in self._ai_keywords.items():
            if any(kw in resume_text_lower for kw in keywords):
                depth_bonus += 5

        total_score = min(100.0, score + depth_bonus)

        return DimensionResult(
            score=total_score,
            reason=f"AI技能匹配: {len(matched)}/{len(jd_ai_required)} 相关技能",
            confidence=0.9,
            details={
                "matched_ai_skills": list(matched),
                "resume_ai_categories": [c for c, kws in self._ai_keywords.items() if any(kw in resume_text_lower for kw in kws)],
            },
        )

    def _build_resume_text(self, resume: ResumeParseResult) -> str:
        parts = []
        if resume.姓名:
            parts.append(resume.姓名)
        for skill in resume.技能:
            parts.append(skill.名称)
        for proj in resume.项目:
            if proj.描述:
                parts.append(proj.描述)
            if proj.技术栈:
                parts.extend(proj.技术栈)
        for exp in resume.工作经验:
            if exp.描述:
                parts.append(exp.描述)
            if exp.技能:
                parts.extend(exp.技能)
        return " ".join(parts)

    def _extract_ai_requirements(self, jd: JDParseResult) -> set[str]:
        requirements = set()
        all_tech = jd.技术栈.must + jd.技术栈.bonus
        for tech in all_tech:
            tech_lower = tech.lower()
            for category, keywords in self._ai_keywords.items():
                if tech_lower in keywords or any(kw in tech_lower for kw in keywords):
                    requirements.add(category)
        return requirements

    def _extract_ai_skills(self, text: str) -> set[str]:
        skills = set()
        for category, keywords in self._ai_keywords.items():
            if any(kw in text for kw in keywords):
                skills.add(category)
        return skills

    def _calculate_max_depth(self, ai_skills: set[str]) -> float:
        depth_mapping = {
            "ml": 1,
            "dl": 2,
            "nlp": 2,
            "cv": 2,
            "rag": 3,
            "llm": 4,
            "agent": 5,
            "frameworks": 3,
        }
        if not ai_skills:
            return 0.0
        return max(depth_mapping.get(s, 0) for s in ai_skills)
