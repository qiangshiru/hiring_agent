from fastapi import APIRouter, Depends, HTTPException

from src.schemas.jd import JDParseResult
from src.schemas.questions import (
    QuestionGenerationConfig,
    QuestionGenerationResult,
    QuestionType,
)
from src.schemas.resume import ResumeParseResult
from src.services.question_generator import QuestionGeneratorService

router = APIRouter(prefix="/questions", tags=["question-generator"])


def get_question_generator_service() -> QuestionGeneratorService:
    return QuestionGeneratorService()


@router.post("/generate", response_model=QuestionGenerationResult, summary="Generate interview questions")
async def generate_questions(
    jd: JDParseResult,
    resume: ResumeParseResult,
    config: QuestionGenerationConfig | None = None,
    service: QuestionGeneratorService = Depends(get_question_generator_service),
) -> QuestionGenerationResult:
    try:
        if config:
            service.set_config(config)
        return service.generate(jd, resume)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate/by-type", summary="Generate questions by type")
async def generate_by_type(
    question_type: QuestionType,
    jd: JDParseResult,
    resume: ResumeParseResult,
    count: int = 3,
    service: QuestionGeneratorService = Depends(get_question_generator_service),
) -> list:
    try:
        return service.generate_by_type(question_type, jd, resume, count)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/config", response_model=QuestionGenerationConfig, summary="Get or update config")
async def get_config(
    config: QuestionGenerationConfig | None = None,
    service: QuestionGeneratorService = Depends(get_question_generator_service),
) -> QuestionGenerationConfig:
    if config:
        service.set_config(config)
    return service.get_config()
