"""Pydantic data models for the application."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ── Resume ────────────────────────────────────────────────────────────────────

class Experience(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""
    highlights: str = ""


class Project(BaseModel):
    name: str = ""
    tech_stack: str = ""
    difficulty: str = ""
    description: str = ""


class Education(BaseModel):
    school: str = ""
    degree: str = ""
    major: str = ""
    year: str = ""


class ResumeData(BaseModel):
    name: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    education: Optional[Education] = None
    summary: str = ""
    raw_text: str = ""


class ResumeParseResponse(BaseModel):
    success: bool = True
    data: Optional[ResumeData] = None
    error: str = ""


# ── Interview ─────────────────────────────────────────────────────────────────

class InterviewConfig(BaseModel):
    target_position: str = ""
    target_company: str = ""
    round_type: str = "tech_basic"       # tech_basic | tech_advanced | hr_behavioral
    difficulty: str = "mid"              # junior | mid | senior
    style: str = "gentle"               # strict | gentle | english
    custom_instructions: str = ""
    multi_round_enabled: bool = False
    multi_round_rounds: list[str] = Field(default_factory=list)  # e.g. ["tech_basic", "tech_advanced", "hr_behavioral"]


class InterviewStartRequest(BaseModel):
    resume: ResumeData
    config: InterviewConfig


class InterviewAnswerRequest(BaseModel):
    session_id: str
    answer: str


class InterviewMessage(BaseModel):
    role: str            # "interviewer" | "candidate"
    content: str
    question_number: int = 0


# ── Evaluation ────────────────────────────────────────────────────────────────

class RadarScores(BaseModel):
    technical_depth: float = 0.0
    project_experience: float = 0.0
    communication: float = 0.0
    problem_solving: float = 0.0
    adaptability: float = 0.0


class QuestionReview(BaseModel):
    question: str
    user_answer: str
    highlights: str = ""
    weaknesses: str = ""
    better_answer: str = ""


class EvaluationResult(BaseModel):
    radar_scores: RadarScores
    overall_score: float = 0.0
    overall_comment: str = ""
    question_reviews: list[QuestionReview] = Field(default_factory=list)
    blind_spots: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)


class EvaluationRequest(BaseModel):
    session_id: str
    resume: ResumeData
    config: InterviewConfig
    messages: list[InterviewMessage]


class EvaluationResponse(BaseModel):
    success: bool = True
    data: Optional[EvaluationResult] = None
    error: str = ""
