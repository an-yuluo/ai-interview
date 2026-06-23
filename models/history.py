"""History models for interview records."""
from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime


class InterviewRecord(BaseModel):
    id: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    resume_name: str = ""
    target_position: str = ""
    target_company: str = ""
    round_type: str = ""
    round_label: str = ""
    difficulty: str = ""
    overall_score: float = 0.0
    radar_scores: dict = Field(default_factory=dict)
    strengths: list[str] = Field(default_factory=list)
    blind_spots: list[str] = Field(default_factory=list)
    question_count: int = 0
    conversation: list[dict] = Field(default_factory=list)
    question_reviews: list[dict] = Field(default_factory=list)
    overall_comment: str = ""


class HistoryListItem(BaseModel):
    id: str
    created_at: str
    resume_name: str
    target_position: str
    round_label: str
    overall_score: float
    question_count: int


class HistoryListResponse(BaseModel):
    success: bool = True
    records: list[HistoryListItem] = Field(default_factory=list)
    total: int = 0


class HistoryDetailResponse(BaseModel):
    success: bool = True
    record: InterviewRecord | None = None
    error: str = ""
