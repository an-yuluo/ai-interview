"""Evaluation engine: scoring, per-question review, blind spot analysis."""
from __future__ import annotations

from services.ai_client import chat_completion_json


EVALUATION_PROMPT = """你是一位资深的面试评估专家。请根据以下面试对话记录，对候选人进行全面评估。

【候选人简历】
姓名: {name}
技能栈: {skills}
简介: {summary}

【面试配置】
目标岗位: {position}
面试轮次: {round_type}
难度等级: {difficulty}

【面试对话记录】
{conversation}

请返回以下 JSON 格式的评估结果：
{{
  "radar_scores": {{
    "technical_depth": <1-10分，技术深度，知识点掌握程度>,
    "project_experience": <1-10分，项目经验，是否有真实落地经验>,
    "communication": <1-10分，沟通表达，逻辑是否清晰>,
    "problem_solving": <1-10分，问题解决，面对不会的问题时的态度和方式>,
    "adaptability": <1-10分，应变能力，对新问题和压力的适应性>
  }},
  "overall_score": <1-10分，综合评分>,
  "overall_comment": "<2-3句总体评价>",
  "question_reviews": [
    {{
      "question": "<面试官问的问题>",
      "user_answer": "<候选人的回答>",
      "highlights": "<回答中的亮点，具体指出做得好的地方>",
      "weaknesses": "<失分点，具体指出不足之处>",
      "better_answer": "<结合候选人背景的高分回答示范，300字以内，可以直接背诵使用>"
    }}
  ],
  "blind_spots": [
    "<能力盲区1，包含具体的改进建议>",
    "<能力盲区2>"
  ],
  "strengths": [
    "<候选人优势1>",
    "<候选人优势2>"
  ]
}}

评估要求：
1. 评分要客观，不要因为候选人是模拟面试就放水
2. question_reviews 只针对候选人实际回答过的问题，每道题都要点评
3. better_answer 要结合候选人的实际背景来写，不能是泛泛的模板答案
4. blind_spots 要具体，指出明确的改进方向
5. strengths 要真实，找到候选人真正做得好的地方
"""


async def generate_evaluation(
    resume: dict,
    config: dict,
    conversation: list[dict],
) -> dict:
    """Generate full evaluation from interview conversation."""
    # Build conversation text
    conv_lines = []
    for msg in conversation:
        role_label = "面试官" if msg["role"] == "interviewer" else "候选人"
        conv_lines.append(f"[{role_label}]: {msg['content']}")
    conv_text = "\n\n".join(conv_lines)

    prompt = EVALUATION_PROMPT.format(
        name=resume.get("name", "未知"),
        skills=", ".join(resume.get("skills", [])),
        summary=resume.get("summary", ""),
        position=config.get("target_position", "通用技术岗"),
        round_type=config.get("round_type", "tech_basic"),
        difficulty=config.get("difficulty", "mid"),
        conversation=conv_text,
    )

    messages = [
        {"role": "system", "content": "你是一位严谨、专业的面试评估专家。请严格按照 JSON 格式输出评估结果。"},
        {"role": "user", "content": prompt},
    ]

    result = await chat_completion_json(messages, temperature=0.3)
    return result
