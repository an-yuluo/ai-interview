"""Interview router with SSE streaming endpoints."""
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.schemas import InterviewStartRequest, InterviewAnswerRequest
from services import interview_engine

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/start")
async def start_interview(req: InterviewStartRequest):
    """Start a new interview session. Returns session_id and streams first question."""
    resume_dict = req.resume.model_dump()
    config_dict = req.config.model_dump()

    session_id = interview_engine.create_session(resume_dict, config_dict)

    async def event_stream():
        try:
            async for chunk in interview_engine.stream_first_question(session_id):
                yield f"data: {json.dumps({'type': 'text', 'content': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-Id": session_id,
        },
    )


@router.post("/answer")
async def submit_answer(req: InterviewAnswerRequest):
    """Submit candidate's answer and stream next question/follow-up."""
    session = interview_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(404, "面试会话不存在或已过期。")

    # Markers to strip from streamed text
    _MARKERS = ("[FOLLOW_UP]", "[NEW_QUESTION]")

    async def event_stream():
        try:
            async for chunk in interview_engine.stream_answer_response(req.session_id, req.answer):
                # Strip internal markers from streamed text
                clean_chunk = chunk
                for m in _MARKERS:
                    clean_chunk = clean_chunk.replace(m, "")
                if clean_chunk.strip():
                    yield f"data: {json.dumps({'type': 'text', 'content': clean_chunk}, ensure_ascii=False)}\n\n"

            # Check if interview ended and if it was a follow-up
            updated_session = interview_engine.get_session(req.session_id)
            if updated_session:
                ended = updated_session["ended"]
                is_follow_up = updated_session.get("is_follow_up", False)
                round_transition = updated_session.get("_round_transition", False)
                next_round = updated_session.get("_next_round", "")
            else:
                ended = True
                is_follow_up = False
                round_transition = False
                next_round = ""
            yield f"data: {json.dumps({'type': 'done', 'ended': ended, 'is_follow_up': is_follow_up, 'round_transition': round_transition, 'next_round': next_round})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/standard-answer")
async def get_standard_answer(req: InterviewAnswerRequest):
    """Generate a model/standard answer for the current question (SSE stream)."""
    session = interview_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(404, "面试会话不存在或已过期。")

    async def event_stream():
        try:
            async for chunk in interview_engine.stream_standard_answer(req.session_id):
                yield f"data: {json.dumps({'type': 'text', 'content': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/skip")
async def skip_question(req: InterviewAnswerRequest):
    """Skip the current question and stream the next one (SSE stream)."""
    session = interview_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(404, "面试会话不存在或已过期。")

    async def event_stream():
        try:
            async for chunk in interview_engine.stream_skip_question(req.session_id):
                yield f"data: {json.dumps({'type': 'text', 'content': chunk}, ensure_ascii=False)}\n\n"

            updated_session = interview_engine.get_session(req.session_id)
            ended = updated_session["ended"] if updated_session else True
            yield f"data: {json.dumps({'type': 'done', 'ended': ended})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/next-round")
async def start_next_round(req: InterviewAnswerRequest):
    """Start the next round in multi-round mode (streams first question)."""
    session = interview_engine.get_session(req.session_id)
    if not session:
        raise HTTPException(404, "面试会话不存在或已过期。")

    async def event_stream():
        try:
            async for chunk in interview_engine.stream_next_round(req.session_id):
                yield f"data: {json.dumps({'type': 'text', 'content': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/end/{session_id}")
async def end_interview(session_id: str):
    """End the interview session and return conversation data."""
    data = interview_engine.end_session(session_id)
    if not data:
        raise HTTPException(404, "面试会话不存在或已过期。")
    return {"success": True, "data": data}


@router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Check if a session is still active."""
    session = interview_engine.get_session(session_id)
    if not session:
        return {"active": False}
    return {
        "active": True,
        "ended": session["ended"],
        "question_count": session["question_count"],
        "max_questions": session["max_questions"],
    }
