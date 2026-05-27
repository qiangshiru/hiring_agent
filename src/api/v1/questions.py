"""面试题目生成相关接口

提供的端点：
- POST /questions/generate        : 根据 JD 和简历自动生成全套面试题目
- POST /questions/generate/by-type : 按指定类型（技术/行为/项目等）生成题目
- POST /questions/config          : 获取或更新题目生成配置（题型、难度分布等）
"""

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
    """依赖注入：获取题目生成服务实例"""
    return QuestionGeneratorService()


@router.post("/generate", response_model=QuestionGenerationResult, summary="Generate interview questions")
async def generate_questions(
    jd: JDParseResult,
    resume: ResumeParseResult,
    config: QuestionGenerationConfig | None = None,
    service: QuestionGeneratorService = Depends(get_question_generator_service),
) -> QuestionGenerationResult:
    """根据 JD 和简历自动生成全套面试题目，可选传入自定义配置"""
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
    """按指定类型和数量生成面试题目"""
    try:
        return service.generate_by_type(question_type, jd, resume, count)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/config", response_model=QuestionGenerationConfig, summary="Get or update config")
async def get_config(
    config: QuestionGenerationConfig | None = None,
    service: QuestionGeneratorService = Depends(get_question_generator_service),
) -> QuestionGenerationConfig:
    """获取当前生成配置，如果传入新配置则先更新再返回"""
    if config:
        service.set_config(config)
    return service.get_config()
