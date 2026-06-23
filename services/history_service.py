"""History service: persists interview records in SQLite."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from models.history import InterviewRecord, HistoryListItem

_DB_DIR = Path(__file__).parent.parent / "data"
_DB_PATH = _DB_DIR / "history.db"


def _get_conn() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interview_records (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            resume_name TEXT NOT NULL DEFAULT '',
            target_position TEXT NOT NULL DEFAULT '',
            target_company TEXT NOT NULL DEFAULT '',
            round_type TEXT NOT NULL DEFAULT '',
            round_label TEXT NOT NULL DEFAULT '',
            difficulty TEXT NOT NULL DEFAULT '',
            overall_score REAL NOT NULL DEFAULT 0.0,
            radar_scores TEXT NOT NULL DEFAULT '{}',
            strengths TEXT NOT NULL DEFAULT '[]',
            blind_spots TEXT NOT NULL DEFAULT '[]',
            question_count INTEGER NOT NULL DEFAULT 0,
            conversation TEXT NOT NULL DEFAULT '[]',
            question_reviews TEXT NOT NULL DEFAULT '[]',
            overall_comment TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


# Initialize on import
_init_db()

_ROUND_LABELS = {
    "tech_basic": "初级技术面",
    "tech_advanced": "高级架构面",
    "hr_behavioral": "HR 行为面",
}


def save_record(
    *,
    resume: dict,
    config: dict,
    evaluation: dict,
    conversation: list[dict],
    question_count: int,
) -> str:
    """Save an interview record and return the record ID."""
    record_id = str(uuid.uuid4())[:12]
    round_type = config.get("round_type", "tech_basic")

    conn = _get_conn()
    conn.execute(
        """INSERT INTO interview_records
           (id, created_at, resume_name, target_position, target_company,
            round_type, round_label, difficulty, overall_score, radar_scores,
            strengths, blind_spots, question_count, conversation,
            question_reviews, overall_comment)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            record_id,
            datetime.now().isoformat(),
            resume.get("name", "未知"),
            config.get("target_position", ""),
            config.get("target_company", ""),
            round_type,
            _ROUND_LABELS.get(round_type, round_type),
            config.get("difficulty", "mid"),
            evaluation.get("overall_score", 0.0),
            json.dumps(evaluation.get("radar_scores", {}), ensure_ascii=False),
            json.dumps(evaluation.get("strengths", []), ensure_ascii=False),
            json.dumps(evaluation.get("blind_spots", []), ensure_ascii=False),
            question_count,
            json.dumps(conversation, ensure_ascii=False),
            json.dumps(evaluation.get("question_reviews", []), ensure_ascii=False),
            evaluation.get("overall_comment", ""),
        ),
    )
    conn.commit()
    conn.close()
    return record_id


def list_records() -> list[HistoryListItem]:
    """List all interview records, newest first."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT id, created_at, resume_name, target_position, round_label, overall_score, question_count "
        "FROM interview_records ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [
        HistoryListItem(
            id=r["id"],
            created_at=r["created_at"],
            resume_name=r["resume_name"],
            target_position=r["target_position"],
            round_label=r["round_label"],
            overall_score=r["overall_score"],
            question_count=r["question_count"],
        )
        for r in rows
    ]


def get_record(record_id: str) -> InterviewRecord | None:
    """Get a single record by ID."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM interview_records WHERE id = ?", (record_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return InterviewRecord(
        id=row["id"],
        created_at=row["created_at"],
        resume_name=row["resume_name"],
        target_position=row["target_position"],
        target_company=row["target_company"],
        round_type=row["round_type"],
        round_label=row["round_label"],
        difficulty=row["difficulty"],
        overall_score=row["overall_score"],
        radar_scores=json.loads(row["radar_scores"]),
        strengths=json.loads(row["strengths"]),
        blind_spots=json.loads(row["blind_spots"]),
        question_count=row["question_count"],
        conversation=json.loads(row["conversation"]),
        question_reviews=json.loads(row["question_reviews"]),
        overall_comment=row["overall_comment"],
    )


def delete_record(record_id: str) -> bool:
    """Delete a record. Returns True if deleted."""
    conn = _get_conn()
    cursor = conn.execute(
        "DELETE FROM interview_records WHERE id = ?", (record_id,)
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
