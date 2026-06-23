"""Evaluation router."""
from fastapi import APIRouter

from models.schemas import EvaluationRequest, EvaluationResponse, EvaluationResult
from services.evaluation_engine import generate_evaluation

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.post("/generate", response_model=EvaluationResponse)
async def generate_eval(req: EvaluationRequest):
    """Generate evaluation report from interview conversation."""
    try:
        resume_dict = req.resume.model_dump()
        config_dict = req.config.model_dump()
        messages = [m.model_dump() for m in req.messages]

        result = await generate_evaluation(resume_dict, config_dict, messages)

        eval_result = EvaluationResult(
            radar_scores=result.get("radar_scores", {}),
            overall_score=result.get("overall_score", 0),
            overall_comment=result.get("overall_comment", ""),
            question_reviews=result.get("question_reviews", []),
            blind_spots=result.get("blind_spots", []),
            strengths=result.get("strengths", []),
        )
        return EvaluationResponse(success=True, data=eval_result)

    except Exception as e:
        return EvaluationResponse(success=False, error=f"评估生成失败: {str(e)}")
