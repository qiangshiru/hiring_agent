"""简历评分相关接口

提供的端点：
- POST /scoring/score         : 对单份简历进行 JD 匹配评分
- POST /scoring/score/batch   : 批量对多份简历评分
- POST /scoring/score/weights : 使用自定义维度权重进行评分
"""

from fastapi import APIRouter, Depends, HTTPException

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.scoring import DimensionWeights
from src.schemas.screening import ScoringResult
from src.services.scoring import ScoringService

router = APIRouter(prefix="/scoring", tags=["scoring"])


def get_scoring_service() -> ScoringService:
    """依赖注入：获取简历评分服务实例"""
    return ScoringService()


@router.post("/score", response_model=ScoringResult, summary="Score a resume against a JD")
async def score_resume(
    jd: JDParseResult,
    resume: ResumeParseResult,
    service: ScoringService = Depends(get_scoring_service),
) -> ScoringResult:
    """根据 JD 要求对单份简历进行多维度打分"""
    try:
        return service.score(jd, resume)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/score/batch", summary="Score multiple resumes against a JD")
async def score_batch(
    jd: JDParseResult,
    resumes: list[ResumeParseResult],
    service: ScoringService = Depends(get_scoring_service),
) -> list[ScoringResult]:
    """批量评分：对多份简历进行 JD 匹配评分"""
    try:
        return service.score_batch(jd, resumes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/score/weights", response_model=ScoringResult, summary="Score with custom weights")
async def score_with_weights(
    jd: JDParseResult,
    resume: ResumeParseResult,
    weights: DimensionWeights,
    service: ScoringService = Depends(get_scoring_service),
) -> ScoringResult:
    """使用自定义维度权重（如经验占比、学历占比等）进行评分"""
    try:
        service.set_weights(weights)
        return service.score(jd, resume)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
