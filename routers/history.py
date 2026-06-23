"""History router: list, detail, delete interview records."""
from fastapi import APIRouter, HTTPException

from services import history_service
from models.history import HistoryListResponse, HistoryDetailResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryListResponse)
async def get_history():
    """List all interview history records."""
    records = history_service.list_records()
    return HistoryListResponse(success=True, records=records, total=len(records))


@router.get("/{record_id}", response_model=HistoryDetailResponse)
async def get_history_detail(record_id: str):
    """Get detailed interview record."""
    record = history_service.get_record(record_id)
    if not record:
        raise HTTPException(404, "记录不存在")
    return HistoryDetailResponse(success=True, record=record)


@router.delete("/{record_id}")
async def delete_history(record_id: str):
    """Delete an interview record."""
    deleted = history_service.delete_record(record_id)
    if not deleted:
        raise HTTPException(404, "记录不存在")
    return {"success": True}
