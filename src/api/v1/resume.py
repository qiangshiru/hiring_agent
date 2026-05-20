from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.schemas.resume import ResumeParseRequest, ResumeParseResponse
from src.services.resume_parser.service import ResumeParserService

router = APIRouter(prefix="/resume", tags=["resume-parser"])


def get_resume_parser_service() -> ResumeParserService:
    return ResumeParserService()


@router.post("/parse", response_model=ResumeParseResponse, summary="Parse a resume from text")
async def parse_resume_text(
    payload: ResumeParseRequest,
    service: ResumeParserService = Depends(get_resume_parser_service),
) -> ResumeParseResponse:
    try:
        result = service.parse_text(payload.text, use_cache=payload.use_cache)
        return ResumeParseResponse(data=result, cached=False)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/parse/file", response_model=ResumeParseResponse, summary="Parse a resume from file upload")
async def parse_resume_file(
    file: UploadFile = File(...),
    service: ResumeParserService = Depends(get_resume_parser_service),
) -> ResumeParseResponse:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or ".txt").suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = service.parse_resume(tmp_path, use_cache=False)
            return ResumeParseResponse(data=result, cached=False)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


import tempfile
