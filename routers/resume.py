"""Resume parsing router."""
from fastapi import APIRouter, UploadFile, File, HTTPException

from services.resume_parser import parse_resume
from models.schemas import ResumeParseResponse

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """Upload and parse a resume file (PDF or DOCX)."""
    # Validate file type
    filename = file.filename or ""
    if not filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "仅支持 PDF 和 Word (.docx) 格式的简历文件。")

    try:
        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "文件大小不能超过 10MB。")

        data = await parse_resume(file_bytes, filename)
        return ResumeParseResponse(success=True, data=data)

    except ValueError as e:
        return ResumeParseResponse(success=False, error=str(e))
    except Exception as e:
        return ResumeParseResponse(success=False, error=f"简历解析失败: {str(e)}")
