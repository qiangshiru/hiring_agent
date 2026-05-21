import pytest
from datetime import datetime

from src.schemas.jd import EducationRequirement, JDParseResult, TechStackRequirement, WorkExperienceRequirement
from src.schemas.questions import QuestionType
from src.schemas.resume import Education, Project, ResumeParseResult, Skill, WorkExperience
from src.services.question_generator import QuestionGeneratorService


@pytest.fixture
def sample_jd() -> JDParseResult:
    return JDParseResult(
        学历=EducationRequirement(must=["本科"], bonus=["985", "硕士"]),
        工作经验=WorkExperienceRequirement(min_years=3),
        技术栈=TechStackRequirement(must=["Python", "RAG", "LangChain"], bonus=["Agent"]),
        城市要求=["北京"],
    )


@pytest.fixture
def sample_resume() -> ResumeParseResult:
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
                结束时间=datetime.now(),
                描述="负责推荐系统开发",
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
            Skill(名称="Python", 类别="编程语言"),
            Skill(名称="LangChain", 类别="AI/ML"),
            Skill(名称="RAG", 类别="AI/ML"),
        ],
    )


class TestQuestionGeneratorService:
    def test_generate_minimum_questions(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        result = service.generate(sample_jd, sample_resume)

        assert len(result.questions) >= 15
        assert result.config.total_questions == 15

    def test_all_question_types_covered(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        result = service.generate(sample_jd, sample_resume)

        question_types = set(q.type for q in result.questions)
        assert len(question_types) == 7
        assert question_types == set(QuestionType)

    def test_difficulty_distribution(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        result = service.generate(sample_jd, sample_resume)

        distribution = result.difficulty_distribution
        assert sum(distribution.values()) == len(result.questions)

        assert distribution["easy"] >= 2
        assert distribution["medium"] >= 4
        assert distribution["hard"] >= 3
        assert distribution["expert"] >= 1

    def test_type_distribution(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        result = service.generate(sample_jd, sample_resume)

        distribution = result.type_distribution
        assert sum(distribution.values()) == len(result.questions)

        for q_type in QuestionType:
            assert distribution.get(q_type.value, 0) >= 1

    def test_generate_by_type(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        questions = service.generate_by_type(QuestionType.FOUNDATION, sample_jd, sample_resume, count=3)

        assert len(questions) == 3
        for q in questions:
            assert q.type == QuestionType.FOUNDATION

    def test_generate_batch(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        results = service.generate_batch(sample_jd, [sample_resume, sample_resume])

        assert len(results) == 2
        assert len(results[0].questions) == len(results[1].questions)


class TestAcceptanceCriteria:
    def test_minimum_question_count(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        questions = service.generate(sample_jd, sample_resume)

        assert len(questions.questions) >= 15

    def test_all_seven_types(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        questions = service.generate(sample_jd, sample_resume)

        question_types = set(q.type for q in questions.questions)
        assert len(question_types) == 7

    def test_reasonable_difficulty_distribution(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        questions = service.generate(sample_jd, sample_resume)

        difficulties = [q.difficulty.value for q in questions.questions]
        easy_count = difficulties.count("easy")
        medium_count = difficulties.count("medium")
        hard_count = difficulties.count("hard")
        expert_count = difficulties.count("expert")

        assert easy_count > 0
        assert medium_count > 0
        assert hard_count > 0
        assert medium_count >= easy_count
        assert medium_count >= hard_count


class TestQuestionProperties:
    def test_question_has_expected_fields(self, sample_jd: JDParseResult, sample_resume: ResumeParseResult) -> None:
        service = QuestionGeneratorService()
        result = service.generate(sample_jd, sample_resume)

        for question in result.questions:
            assert question.id is not None
            assert question.content is not None
            assert len(question.content) > 10
            assert question.time_minutes > 0
            assert len(question.scoring_guide) >= 2
            assert len(question.follow_up_hints) >= 1
