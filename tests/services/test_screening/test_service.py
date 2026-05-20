import pytest
from datetime import datetime

from src.schemas.jd import EducationRequirement, JDParseResult, TechStackRequirement, WorkExperienceRequirement
from src.schemas.resume import Education, Project, ResumeParseResult, Skill, WorkExperience
from src.services.screening import (
    EducationRule,
    ScreeningService,
    TechStackRule,
    WorkExperienceRule,
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
def matching_resume() -> ResumeParseResult:
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
            )
        ],
        工作经验=[
            WorkExperience(
                公司="字节跳动",
                职位="高级工程师",
                开始时间=datetime(2021, 1, 1),
                结束_time=datetime.now(),
                描述="负责抖音推荐系统开发，精通Python和RAG技术栈",
                技能=["Python", "LangChain", "RAG"],
            )
        ],
        项目=[
            Project(
                项目名称="智能推荐系统",
                角色="技术负责人",
                技术栈=["Python", "TensorFlow", "LangChain"],
            )
        ],
        技能=[
            Skill(名称="Python", 类别="编程语言", 熟练度="精通"),
            Skill(名称="LangChain", 类别="AI/ML", 熟练度="熟练"),
            Skill(名称="RAG", 类别="AI/ML", 熟练度="熟练"),
            Skill(名称="Agent", 类别="AI/ML", 熟练度="了解"),
        ],
    )


@pytest.fixture
def mismatched_resume() -> ResumeParseResult:
    return ResumeParseResult(
        姓名="李四",
        性别="男",
        城市="上海",
        教育=[
            Education(
                学校="某专科学校",
                学历="大专",
                专业="会计",
            )
        ],
        工作经验=[
            WorkExperience(
                公司="小公司",
                职位="文员",
                描述="日常行政工作",
            )
        ],
        技能=[
            Skill(名称="Excel", 类别="办公软件"),
        ],
    )


class TestEducationRule:
    def test_education_rule_pass(self, sample_jd: JDParseResult, matching_resume: ResumeParseResult) -> None:
        rule = EducationRule(
            rule_id="test",
            rule_name="学历要求",
            required_degrees=["本科"],
        )
        result = rule.evaluate(sample_jd, matching_resume)

        assert result.passed is True
        assert result.score >= 0.5

    def test_education_rule_fail(self, sample_jd: JDParseResult, mismatched_resume: ResumeParseResult) -> None:
        rule = EducationRule(
            rule_id="test",
            rule_name="学历要求",
            required_degrees=["本科"],
        )
        result = rule.evaluate(sample_jd, mismatched_resume)

        assert result.passed is False
        assert result.score < 0.5


class TestWorkExperienceRule:
    def test_work_experience_pass(self, sample_jd: JDParseResult, matching_resume: ResumeParseResult) -> None:
        rule = WorkExperienceRule(
            rule_id="test",
            rule_name="工作经验要求",
            min_years=3,
        )
        result = rule.evaluate(sample_jd, matching_resume)

        assert result.passed is True
        assert result.score > 0

    def test_work_experience_fail(self, sample_jd: JDParseResult, mismatched_resume: ResumeParseResult) -> None:
        rule = WorkExperienceRule(
            rule_id="test",
            rule_name="工作经验要求",
            min_years=3,
        )
        result = rule.evaluate(sample_jd, mismatched_resume)

        assert result.passed is False


class TestTechStackRule:
    def test_tech_stack_pass(self, sample_jd: JDParseResult, matching_resume: ResumeParseResult) -> None:
        rule = TechStackRule(
            rule_id="test",
            rule_name="技术栈要求",
        )
        result = rule.evaluate(sample_jd, matching_resume)

        assert result.passed is True
        assert result.score >= 0.5

    def test_tech_stack_fail(self, sample_jd: JDParseResult, mismatched_resume: ResumeParseResult) -> None:
        rule = TechStackRule(
            rule_id="test",
            rule_name="技术栈要求",
        )
        result = rule.evaluate(sample_jd, mismatched_resume)

        assert result.passed is False


class TestScreeningService:
    def test_screen_pass(self, sample_jd: JDParseResult, matching_resume: ResumeParseResult) -> None:
        service = ScreeningService()
        result = service.screen(sample_jd, matching_resume)

        assert result.passed is True
        assert len(result.matched_rules) > 0
        assert len(result.failed_rules) == 0

    def test_screen_fail(self, sample_jd: JDParseResult, mismatched_resume: ResumeParseResult) -> None:
        service = ScreeningService()
        result = service.screen(sample_jd, mismatched_resume)

        assert result.passed is False
        assert len(result.failed_rules) > 0

    def test_screen_batch(self, sample_jd: JDParseResult, matching_resume: ResumeParseResult, mismatched_resume: ResumeParseResult) -> None:
        service = ScreeningService()
        results = service.screen_batch(sample_jd, [matching_resume, mismatched_resume])

        assert len(results) == 2
        assert results[0].passed is True
        assert results[1].passed is False
