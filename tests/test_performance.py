import pytest
import time
from src.services.jd_parser import JDParserService
from src.services.resume_parser import ResumeParserService
from src.services.screening import ScreeningService
from src.services.question_generator import QuestionGeneratorService


@pytest.mark.slow
class TestPerformanceBenchmarks:
    @pytest.fixture
    def jd_text(self):
        return """
        招聘 AI 工程师
        
        要求：
        - 本科及以上学历
        - 3 年以上工作经验
        - 熟练掌握 Python, LangChain, LLM
        - 有 RAG 开发经验优先
        - 熟悉向量数据库
        - 有大型项目经验
        """

    @pytest.fixture
    def resume_text(self):
        return """
        张三
        
        教育：清华大学 计算机科学 硕士
        
        工作：字节跳动 高级工程师 4 年
        技能：Python, LangChain, RAG, Go, Kubernetes
        
        项目1：智能推荐系统
        - 基于 LangChain 和 RAG
        - 使用 Milvus 向量数据库
        
        项目2：对话系统
        - 使用 LangChain 和 GPT
        """

    def test_jd_parsing_performance(self, jd_text):
        service = JDParserService()
        
        start_time = time.time()
        result = service.parse(jd_text)
        elapsed = time.time() - start_time
        
        assert result is not None
        assert elapsed < 1.0, f"JD parsing took {elapsed:.2f}s, should be < 1.0s"

    def test_resume_parsing_performance(self, resume_text):
        service = ResumeParserService()
        
        start_time = time.time()
        result = service.parse_resume(resume_text)
        elapsed = time.time() - start_time
        
        assert result is not None
        assert elapsed < 1.0, f"Resume parsing took {elapsed:.2f}s, should be < 1.0s"

    def test_screening_performance(self, jd_text, resume_text):
        jd_service = JDParserService()
        resume_service = ResumeParserService()
        screening_service = ScreeningService()
        
        jd = jd_service.parse(jd_text)
        resume = resume_service.parse_resume(resume_text)
        
        start_time = time.time()
        result = screening_service.screen(jd, resume)
        elapsed = time.time() - start_time
        
        assert result is not None
        assert elapsed < 2.0, f"Screening took {elapsed:.2f}s, should be < 2.0s"

    def test_question_generation_performance(self, jd_text, resume_text):
        jd_service = JDParserService()
        resume_service = ResumeParserService()
        question_service = QuestionGeneratorService()
        
        jd = jd_service.parse(jd_text)
        resume = resume_service.parse_resume(resume_text)
        
        start_time = time.time()
        result = question_service.generate(jd, resume)
        elapsed = time.time() - start_time
        
        assert result is not None
        assert elapsed < 5.0, f"Question generation took {elapsed:.2f}s, should be < 5.0s"

    def test_batch_processing_performance(self, jd_text):
        service = JDParserService()
        num_iterations = 10
        
        start_time = time.time()
        for _ in range(num_iterations):
            service.parse(jd_text)
        elapsed = time.time() - start_time
        
        avg_time = elapsed / num_iterations
        assert avg_time < 0.5, f"Average parsing time {avg_time:.2f}s, should be < 0.5s"


@pytest.mark.slow
class TestConcurrentPerformance:
    def test_concurrent_jd_parsing(self):
        import concurrent.futures
        
        service = JDParserService()
        jd_text = "招聘 AI 工程师，要求 Python, LangChain"
        
        def parse_jd():
            return service.parse(jd_text)
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(parse_jd) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        elapsed = time.time() - start_time
        
        assert len(results) == 20
        assert elapsed < 3.0, f"Concurrent parsing took {elapsed:.2f}s, should be < 3.0s"
