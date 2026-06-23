"""Resume file parsing: extract text from PDF/Word, then structure with AI."""
from __future__ import annotations

import io

from PyPDF2 import PdfReader
from docx import Document

from services.ai_client import chat_completion_json


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a Word (.docx) file."""
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text based on file extension."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}")


STRUCTURE_PROMPT = """你是一位专业的简历解析助手。请从以下简历文本中提取关键信息，以 JSON 格式返回。

要求返回的 JSON 结构：
{
  "name": "姓名",
  "skills": ["技能1", "技能2", ...],
  "experience": [
    {
      "company": "公司名称",
      "role": "职位",
      "duration": "在职时间",
      "highlights": "主要成就和职责（简洁总结）"
    }
  ],
  "projects": [
    {
      "name": "项目名称",
      "tech_stack": "技术栈",
      "difficulty": "技术难点",
      "description": "项目描述"
    }
  ],
  "education": {
    "school": "学校名称",
    "degree": "学历",
    "major": "专业",
    "year": "毕业年份"
  },
  "summary": "一句话总结候选人背景"
}

注意事项：
- 如果某项信息在简历中找不到，对应字段留空字符串或空数组
- skills 要提取具体的技术关键词（编程语言、框架、工具等）
- experience 的 highlights 要简洁，每条不超过50字
- 确保返回的是合法 JSON

简历文本：
"""


async def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """Full pipeline: extract text → AI structure → return dict."""
    raw_text = extract_text(file_bytes, filename)

    if not raw_text.strip():
        raise ValueError("无法从文件中提取到文本内容，请检查文件是否为有效的简历。")

    # Truncate very long resumes to stay within token limits
    if len(raw_text) > 8000:
        raw_text = raw_text[:8000] + "\n...(内容截断)"

    messages = [
        {"role": "system", "content": "你是一个专业的简历解析助手，擅长从简历文本中提取结构化信息。"},
        {"role": "user", "content": STRUCTURE_PROMPT + raw_text},
    ]

    result = await chat_completion_json(messages, temperature=0.1)
    result["raw_text"] = raw_text
    return result
