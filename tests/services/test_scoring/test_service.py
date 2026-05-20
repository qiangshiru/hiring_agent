import pytest
from datetime import datetime

from src.schemas.jd import EducationRequirement, JDParseResult, TechStackRequirement, WorkExperienceRequirement
from src.schemas.resume import Education, Project, ResumeParseResult, Skill, WorkExperience
from src.services.scoring import (
    DefaultWeights,
    ScoringService,
)


@pytest.fixture
def sample_jd() -> JDParseResult:
    return JDParseResult(
        学历=EducationRequirement(must=["本科"], bonus=["985", "211", "硕士"]),
        工作经验=WorkExperienceRequirement(min_years=3),
        技术栈=TechStackRequirement(must=["Python", "RAG", "LangChain"], bonus=["Agent"]),
        城市要求=["北京"],
    )


@pytest.fixture
def strong_candidate() -> ResumeParseResult:
    return ResumeParseResult(
        姓名="张三",
        性别="男",
        城市="北京",
        教育=[
            Education(
                学校="清华大学",
                学历="本科",
                专业="计算机科学与技术",
                开始时间=datetime(2014, 9, 1),
                结束时间=datetime(2018, 6, 30),
                置信度=1.0,
            )
        ],
        工作经验=[
            WorkExperience(
                公司="字节跳动",
                职位="高级工程师",
                开始时间=datetime(2021, 1, 1),
                结束时间=datetime.now(),
                描述="负责抖音推荐系统开发，精通Python和RAG技术栈，使用LangChain构建智能应用",
                技能=["Python", "LangChain", "RAG", "TensorFlow"],
                置信度=0.9,
            )
        ],
        项目=[
            Project(
                项目名称="智能推荐系统",
                角色="技术负责人",
                技术栈=["Python", "TensorFlow", "LangChain", "RAG"],
                描述="基于深度学习的个性化推荐系统",
                置信度=1.0,
            )
        ],
        技能=[
            Skill(名称="Python", 类别="编程语言", 熟练度="精通", 置信度=1.0),
            Skill(名称="LangChain", 类别="AI/ML", 熟练度="熟练", 置信度=0.9),
            Skill(名称="RAG", 类别="AI/ML", 熟练度="熟练", 置信度=0.9),
            Skill(名称="Agent", 类别="AI/ML", 熟练度="了解", 置信度=0.7),
            Skill(名称="TensorFlow", 类别="AI/ML", 熟练度="熟练", 置信度=0.8),
        ],
    )


@pytest.fixture
def weak_candidate() -> ResumeParseResult:
    return ResumeParseResult(
        姓名="李四",
        性别="男",
        城市="上海",
        教育=[
            Education(
                学校="某专科学校",
                学历="大专",
                专业="会计",
                置信度=0.8,
            )
        ],
        工作经验=[
            WorkExperience(
                公司="小公司",
                职位="文员",
                描述="日常行政工作",
                技能=["Excel", "Word"],
                置信度=0.5,
            )
        ],
        技能=[
            Skill(名称="Excel", 类别="办公软件", 熟练度="了解", 置信度=0.5),
            Skill(名称="Word", 类别="办公软件", 熟练度="了解", 置信度=0.5),
        ],
    )


class TestScoringService:
    def test_score_strong_candidate(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        result = service.score(sample_jd, strong_candidate)

        assert 0 <= result.total <= 100
        assert len(result.dimensions) == 5
        assert result.total >= 50

    def test_score_weak_candidate(self, sample_jd: JDParseResult, weak_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        result = service.score(sample_jd, weak_candidate)

        assert 0 <= result.total <= 100
        assert len(result.dimensions) == 5
        assert result.total < 50

    def test_score_batch(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult, weak_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        results = service.score_batch(sample_jd, [strong_candidate, weak_candidate])

        assert len(results) == 2
        assert results[0].total > results[1].total

    def test_custom_weights(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult) -> None:
        weights = DefaultWeights.ai_focus()
        service = ScoringService(weights=weights)

        assert service.get_weights().ai_depth == 0.35

        result = service.score(sample_jd, strong_candidate)
        assert 0 <= result.total <= 100


class TestDimensionScores:
    def test_dimension_count(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        result = service.score(sample_jd, strong_candidate)

        assert len(result.dimensions) == 5
        dimension_names = {d.name for d in result.dimensions}
        assert "tech_match" in dimension_names
        assert "ai_depth" in dimension_names
        assert "engineering" in dimension_names
        assert "education" in dimension_names
        assert "stability" in dimension_names

    def test_dimension_weights_sum(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        result = service.score(sample_jd, strong_candidate)

        total_weight = sum(d.weight for d in result.dimensions)
        assert abs(total_weight - 1.0) < 0.01

    def test_dimension_has_reason(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        result = service.score(sample_jd, strong_candidate)

        for dim in result.dimensions:
            assert dim.reason is not None or dim.score > 0


class TestAcceptanceCriteria:
    def test_score_range(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        result = service.score(sample_jd, strong_candidate)

        assert 0 <= result.total <= 100

    def test_dimension_count_equals_5(self, sample_jd: JDParseResult, strong_candidate: ResumeParseResult) -> None:
        service = ScoringService()
        result = service.score(sample_jd, strong_candidate)

        assert len(result.dimensions) == 5
