from fastapi import APIRouter, Depends, HTTPException

from src.schemas.jd import JDParseResult
from src.schemas.resume import ResumeParseResult
from src.schemas.screening import ScreeningResult
from src.services.screening import ScreeningService

router = APIRouter(prefix="/screening", tags=["screening"])


def get_screening_service() -> ScreeningService:
    return ScreeningService()


@router.post("/screen", response_model=ScreeningResult, summary="Screen a resume against a JD")
async def screen_resume(
    jd: JDParseResult,
    resume: ResumeParseResult,
    service: ScreeningService = Depends(get_screening_service),
) -> ScreeningResult:
    try:
        return service.screen(jd, resume)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/screen/batch", summary="Screen multiple resumes against a JD")
async def screen_batch(
    jd: JDParseResult,
    resumes: list[ResumeParseResult],
    service: ScreeningService = Depends(get_screening_service),
) -> list[ScreeningResult]:
    try:
        return service.screen_batch(jd, resumes)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
