from fastapi import APIRouter, Depends, HTTPException

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.scoring import DimensionWeights
from src.schemas.screening import ScoringResult
from src.services.scoring import ScoringService

router = APIRouter(prefix="/scoring", tags=["scoring"])


def get_scoring_service() -> ScoringService:
    return ScoringService()


@router.post("/score", response_model=ScoringResult, summary="Score a resume against a JD")
async def score_resume(
    jd: JDParseResult,
    resume: ResumeParseResult,
    service: ScoringService = Depends(get_scoring_service),
) -> ScoringResult:
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
    try:
        service.set_weights(weights)
        return service.score(jd, resume)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
