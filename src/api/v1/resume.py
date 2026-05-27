"""简历解析相关接口

提供的端点：
- POST /resume/parse      : 通过文本解析简历
- POST /resume/parse/file : 通过文件上传解析简历（支持 PDF / Word 等格式）
"""

from pathlib import Path
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from src.schemas.resume import ResumeParseRequest, ResumeParseResponse
from src.services.resume_parser.service import ResumeParserService

router = APIRouter(prefix="/resume", tags=["resume-parser"])


def get_resume_parser_service() -> ResumeParserService:
    """依赖注入：获取简历解析服务实例"""
    return ResumeParserService()


@router.post("/parse", response_model=ResumeParseResponse, summary="Parse a resume from text")
async def parse_resume_text(
    payload: ResumeParseRequest,
    service: ResumeParserService = Depends(get_resume_parser_service),
) -> ResumeParseResponse:
    """接收纯文本简历内容，解析为结构化数据"""
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
    """接收上传的简历文件，先保存为临时文件再解析，解析后自动清理临时文件"""
    try:
        # 将上传文件写入临时文件，保留原始扩展名以支持格式检测
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or ".txt").suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = service.parse_resume(tmp_path, use_cache=False)
            return ResumeParseResponse(data=result, cached=False)
        finally:
            # 确保无论解析是否成功都清理临时文件
            Path(tmp_path).unlink(missing_ok=True)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
