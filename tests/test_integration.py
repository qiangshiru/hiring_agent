import pytest
from src.services.jd_parser import JDParserService
from src.services.resume_parser import ResumeParserService
from src.services.screening import ScreeningService
from src.services.question_generator import QuestionGeneratorService
from src.services.evaluation import EvaluationService
from src.services.risk_detection import RiskDetectionService
from src.agents.multi_agent import MultiAgentOrchestrator


@pytest.mark.integration
class TestFullRecruitmentFlow:
    @pytest.fixture
    def jd_text(self):
        return """
        招聘 AI 工程师
        
        要求：
        - 本科及以上学历
        - 3 年以上工作经验
        - 熟练掌握 Python, LangChain
        - 有 RAG 开发经验优先
        """

    @pytest.fixture
    def resume_text(self):
        return """
        张三
        
        教育：清华大学 计算机科学 硕士
        
        工作：字节跳动 高级工程师 4 年
        技能：Python, LangChain, RAG
        
        项目：智能推荐系统
        - 基于 LangChain 和 RAG
        """

    def test_full_recruitment_flow(self, jd_text, resume_text):
        jd_service = JDParserService()
        resume_service = ResumeParserService()
        screening_service = ScreeningService()
        
        jd = jd_service.parse(jd_text)
        resume = resume_service.parse_resume(resume_text)
        
        screening_result = screening_service.screen(jd, resume)
        
        assert screening_result is not None
        assert 0 <= screening_result.综合评分 <= 1

    def test_question_generation_flow(self, jd_text, resume_text):
        jd_service = JDParserService()
        resume_service = ResumeParserService()
        question_service = QuestionGeneratorService()
        
        jd = jd_service.parse(jd_text)
        resume = resume_service.parse_resume(resume_text)
        
        questions = question_service.generate(jd, resume)
        
        assert len(questions.questions) >= 15
        assert len(set(q.type for q in questions.questions)) == 7


@pytest.mark.integration
class TestMultiAgentIntegration:
    @pytest.fixture
    def sample_jd(self):
        from src.schemas.jd import JDParseResult, WorkExperienceRequirement
        return JDParseResult(
            工作经验=WorkExperienceRequirement(min_years=3),
        )

    @pytest.fixture
    def sample_resume(self):
        from src.schemas.resume import ResumeParseResult, Education, Project
        return ResumeParseResult(
            姓名="张三",
            教育=[Education(学校="清华大学", 学历="硕士", 专业="计算机科学")],
            项目=[Project(项目名称="智能推荐系统", 技术栈=["Python", "LangChain", "RAG"])],
            技能=["Python", "LangChain", "RAG"],
        )

    def test_multi_agent_orchestrator(self, sample_jd, sample_resume):
        orchestrator = MultiAgentOrchestrator()
        
        result = orchestrator.run_full_interview(sample_jd, sample_resume)
        
        assert result is not None
        assert result["hr_agent_output"] is not None
        assert result["tech_agent_output"] is not None
        assert result["architect_agent_output"] is not None
        assert result["risk_agent_output"] is not None
        assert result["final_recommendation"] in ["强烈推荐", "推荐", "待定", "不推荐"]


@pytest.mark.integration
class TestInterviewSession:
    @pytest.fixture
    def sample_jd(self):
        from src.schemas.jd import JDParseResult, WorkExperienceRequirement
        return JDParseResult(
            工作经验=WorkExperienceRequirement(min_years=3),
        )

    @pytest.fixture
    def sample_resume(self):
        from src.schemas.resume import ResumeParseResult, Education
        return ResumeParseResult(
            教育=[Education(学校="清华大学", 学历="硕士", 专业="计算机科学")],
            技能=["Python", "LangChain"],
        )

    def test_interview_session_flow(self, sample_jd, sample_resume):
        from src.services.interview import InterviewSession
        
        session = InterviewSession(sample_jd, sample_resume)
        
        question1 = session.next_question()
        assert question1 is not None
        
        turn1 = session.submit_answer(question1.question_id, "我使用了 RAG 技术...")
        assert turn1 is not None
        
        follow_up = session.follow_up("我使用了 RAG 技术...")
        assert follow_up is not None
        
        session_info = session.complete()
        assert session_info is not None
        assert session_info.is_complete
