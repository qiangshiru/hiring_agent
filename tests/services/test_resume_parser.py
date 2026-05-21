import pytest
from src.services.resume_parser import ResumeParserService


class TestResumeParserService:
    @pytest.fixture
    def service(self):
        return ResumeParserService()

    def test_parse_basic_resume(self, service):
        resume_text = """
        张三
        
        教育背景：
        清华大学 计算机科学 硕士 2020-2023
        
        工作经历：
        字节跳动 高级工程师 2021-至今
        - 负责 AI 平台开发
        - 使用 Python, Go
        
        项目经验：
        智能推荐系统
        - 基于 LangChain 和 RAG
        - 使用 Python, Milvus
        """
        result = service.parse_resume(resume_text)
        
        assert result is not None
        assert hasattr(result, "姓名")
        assert hasattr(result, "教育")

    def test_parse_education(self, service):
        resume_text = """
        李四
        
        教育背景：
        北京大学 计算机科学 学士 2016-2020
        清华大学 计算机科学 硕士 2020-2022
        """
        result = service.parse_resume(resume_text)
        
        assert len(result.教育) >= 1
        assert result.教育[0].学校 is not None

    def test_parse_work_experience(self, service):
        resume_text = """
        王五
        
        工作经历：
        阿里巴巴 架构师 2018-至今
        - 负责系统架构设计
        - 精通 Python, Java
        """
        result = service.parse_resume(resume_text)
        
        assert hasattr(result, "工作经验")
        assert len(result.工作经验) >= 1

    def test_parse_projects(self, service):
        resume_text = """
        赵六
        
        项目经验：
        电商推荐系统
        - 使用 Python, TensorFlow
        - 实现个性化推荐算法
        """
        result = service.parse_resume(resume_text)
        
        assert hasattr(result, "项目")
        assert len(result.项目) >= 1

    def test_parse_skills(self, service):
        resume_text = """
        钱七
        
        技能：
        Python, Go, LangChain, RAG, Kubernetes, Docker
        """
        result = service.parse_resume(resume_text)
        
        assert hasattr(result, "技能")
        assert len(result.技能) >= 3

    def test_parse_empty_text(self, service):
        result = service.parse_resume("")
        assert result is not None
        assert result.姓名 == ""
