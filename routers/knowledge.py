"""Knowledge router: list available question banks and knowledge files."""
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

_KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


@router.get("/list")
async def list_knowledge():
    """List all available knowledge base files."""
    if not _KNOWLEDGE_DIR.exists():
        return {"files": [], "total": 0}
    files = []
    for f in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        size = f.stat().st_size
        files.append({"name": f.name, "size": size, "label": _file_label(f.stem)})
    return {"files": files, "total": len(files)}


def _file_label(stem: str) -> str:
    """Convert filename stem to human-readable label."""
    labels = {
        "interview-flows": "面试流程模板",
        "interviewer-personas": "面试官人设",
        "question-bank-algorithm": "算法题库",
        "question-bank-backend": "后端题库",
        "question-bank-frontend": "前端题库",
        "question-bank-system-design": "系统设计题库",
        "question-bank-hr": "HR 行为题库",
        "question-bank-go": "Go 题库",
        "question-bank-python": "Python 题库",
        "question-bank-testing": "测试题库",
        "question-bank-devops": "运维/SRE 题库",
        "question-bank-data": "数据工程题库",
        "question-bank-mobile": "移动端题库",
    }
    return labels.get(stem, stem)
