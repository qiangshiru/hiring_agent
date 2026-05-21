import pytest
from src.services.question_generator import QuestionGeneratorService


class TestQuestionGeneratorService:
    @pytest.fixture
    def service(self):
        return QuestionGeneratorService()

    def test_generate_basic(self, service, sample_jd, sample_resume):
        result = service.generate(sample_jd, sample_resume)
        
        assert result is not None
        assert hasattr(result, "questions")
        assert hasattr(result, "difficulty_distribution")

    def test_generate_minimum_questions(self, service, sample_jd, sample_resume):
        result = service.generate(sample_jd, sample_resume)
        
        assert len(result.questions) >= 15

    def test_generate_covers_all_types(self, service, sample_jd, sample_resume):
        result = service.generate(sample_jd, sample_resume)
        
        question_types = set(q.type for q in result.questions)
        assert len(question_types) == 7

    def test_generate_difficulty_distribution(self, service, sample_jd, sample_resume):
        result = service.generate(sample_jd, sample_resume)
        
        assert isinstance(result.difficulty_distribution, dict)
        assert sum(result.difficulty_distribution.values()) == len(result.questions)

    def test_generate_question_content(self, service, sample_jd, sample_resume):
        result = service.generate(sample_jd, sample_resume)
        
        for question in result.questions:
            assert question.content is not None
            assert len(question.content) > 0

    def test_generate_question_id(self, service, sample_jd, sample_resume):
        result = service.generate(sample_jd, sample_resume)
        
        for question in result.questions:
            assert question.id is not None
            assert len(question.id) > 0

    def test_generate_question_difficulty(self, service, sample_jd, sample_resume):
        result = service.generate(sample_jd, sample_resume)
        
        for question in result.questions:
            assert question.difficulty in ["easy", "medium", "hard", "expert"]

    def test_generate_with_config(self, service, sample_jd, sample_resume):
        from src.schemas.questions import QuestionGenerationConfig
        
        config = QuestionGenerationConfig(
            total_questions=20,
            question_type_counts={
                "foundation": 3,
                "project": 3,
                "deep_dive": 4,
                "scenario": 2,
                "tradeoff": 2,
                "failure": 2,
                "system_design": 4,
            },
        )
        result = service.generate(sample_jd, sample_resume, config=config)
        
        assert len(result.questions) == 20
