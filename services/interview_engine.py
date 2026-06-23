"""Interview engine: question generation, follow-up logic, context management.
Now powered by structured knowledge base (MD documents) for realistic interviews."""
from __future__ import annotations

import json
import uuid
from typing import AsyncIterator

from config import MAX_QUESTIONS
from services.ai_client import stream_chat_completion
from services.knowledge_loader import (
    get_interview_flow,
    get_persona,
    get_persona_usage_rules,
    get_question_bank,
)

# In-memory session storage (MVP — replace with Redis/DB for production)
_sessions: dict[str, dict] = {}


def _build_system_prompt(resume: dict, config: dict) -> str:
    """Build a rich system prompt using the knowledge base."""
    style = config.get("style", "gentle")
    round_type = config.get("round_type", "tech_basic")
    position = config.get("target_position", "通用技术岗")
    difficulty = config.get("difficulty", "mid")
    max_q = MAX_QUESTIONS.get(difficulty, 8)

    # Load knowledge base content
    persona = get_persona(style, round_type)
    persona_rules = get_persona_usage_rules()
    flow = get_interview_flow(round_type)
    questions = get_question_bank(position, round_type)

    # Build the rich system prompt
    system = f"""# 你是一位经验丰富的真实面试官

## 你的面试官身份

{persona}

## 面试官行为准则

{persona_rules}

## 本场面试流程（必须严格遵守）

{flow}

## 参考题库（根据候选人背景灵活选用，不要照搬）

{questions}

## 本场面试信息

- **目标岗位**: {position}
- **目标公司**: {config.get('target_company', '互联网公司')}
- **面试轮次**: {round_type}
- **难度等级**: {difficulty}
- **本场面试总题数**: {max_q} 题

## 候选人简历

- **姓名**: {resume.get('name', '未知')}
- **技能栈**: {', '.join(resume.get('skills', []))}
- **简介**: {resume.get('summary', '无')}
"""

    # Add experience
    exp_list = resume.get("experience", [])
    if exp_list:
        system += "\n### 工作经历\n"
        for e in exp_list:
            system += f"- {e.get('company', '')} / {e.get('role', '')} / {e.get('duration', '')}\n"
            if e.get("highlights"):
                system += f"  - {e['highlights']}\n"

    # Add projects
    proj_list = resume.get("projects", [])
    if proj_list:
        system += "\n### 项目经历\n"
        for p in proj_list:
            system += f"- **{p.get('name', '')}** [{p.get('tech_stack', '')}]\n"
            if p.get("description"):
                system += f"  - {p['description']}\n"
            if p.get("difficulty"):
                system += f"  - 技术难点: {p['difficulty']}\n"

    # Custom instructions
    if config.get("custom_instructions"):
        system += f"\n## 面试官额外指令\n\n{config['custom_instructions']}\n"

    # Output rules
    system += """
## 输出规则（最高优先级）

1. **你必须扮演上述面试官角色**，保持人设一致，使用角色的口头禅和说话风格
2. **严格按照面试流程推进**，从破冰开始，经过项目深挖、技术考察、到反问环节
3. **每次只问一个问题**，等候选人回答后再继续，绝不一次性列出多个问题
4. **自然地追问**：候选人回答后，根据回答质量决定是否追问（最多追问 1-2 次），然后过渡到下一个话题
5. **口语化表达**：用真人面试官的口吻说话，可以有停顿（用"..."），有口头禅，有自然的过渡语
6. **因人而异**：从候选人简历中选取相关话题提问，不要问与简历完全无关的内容
7. **容错空间**：如果候选人答不上来，给台阶下（"没关系，这个比较细"），然后换一个话题
8. **禁止行为**：不要打断候选人，不要直接说"你答错了"，不要一次问多个问题
9. **题目计数**：每个新问题（非追问）算一题，追问不算。当达到总题数时，进入反问环节
10. **面试结束**：当所有问题问完后，回复中包含 `[INTERVIEW_END]` 标记
"""

    return system


def create_session(resume: dict, config: dict) -> str:
    """Create a new interview session and return session_id."""
    session_id = str(uuid.uuid4())[:12]
    max_q = MAX_QUESTIONS.get(config.get("difficulty", "mid"), 8)

    _sessions[session_id] = {
        "resume": resume,
        "config": config,
        "messages": [
            {"role": "system", "content": _build_system_prompt(resume, config)},
        ],
        "question_count": 0,
        "max_questions": max_q,
        "current_phase": "opening",  # opening → project_dive → tech_fundamentals → coding → closing
        "conversation": [],
        "ended": False,
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)


async def stream_first_question(session_id: str) -> AsyncIterator[str]:
    """Generate and stream the first interview question."""
    session = _sessions[session_id]
    round_type = session["config"].get("round_type", "tech_basic")

    # Phase-aware opening instruction
    if round_type == "hr_behavioral":
        opening_instruction = (
            "请开始面试。按照你的面试官人设做一个简短的自我介绍和暖场，"
            "然后请候选人做自我介绍。保持口语化，像真人 HR 一样。"
        )
    elif round_type == "tech_advanced":
        opening_instruction = (
            "请开始面试。按照你的面试官人设做一个简短的自我介绍，"
            "然后直接从候选人的项目经历开始提问（高级面试可以跳过自我介绍，直接进入项目深挖）。"
            "保持口语化。"
        )
    else:
        opening_instruction = (
            "请开始面试。按照你的面试官人设做一个简短的自我介绍（作为面试官），"
            "然后请候选人做自我介绍。保持口语化，像真人技术面试官一样。"
        )

    session["messages"].append({
        "role": "user",
        "content": opening_instruction,
    })

    full_response = ""
    async for chunk in stream_chat_completion(session["messages"]):
        full_response += chunk
        yield chunk

    session["messages"].append({"role": "assistant", "content": full_response})
    session["question_count"] = 1
    session["current_phase"] = "opening"
    session["conversation"].append({
        "role": "interviewer",
        "content": full_response,
        "question_number": 1,
    })


async def stream_answer_response(session_id: str, user_answer: str) -> AsyncIterator[str]:
    """Process user's answer and stream the next question/follow-up."""
    session = _sessions[session_id]

    # Record user's answer
    session["messages"].append({"role": "user", "content": user_answer})
    session["conversation"].append({
        "role": "candidate",
        "content": user_answer,
        "question_number": session["question_count"],
    })

    q_num = session["question_count"]
    max_q = session["max_questions"]
    current_phase = session["current_phase"]
    round_type = session["config"].get("round_type", "tech_basic")

    if q_num >= max_q:
        # Last question — wrap up
        hint = (
            f"这是候选人对最后一题（第 {q_num} 题）的回答。\n"
            f"请对回答做简短反馈，然后进入反问环节：'我这边的问题差不多了，你有什么想问我的吗？'\n"
            f"在回复末尾加上 [INTERVIEW_END] 标记。"
        )
    else:
        # Determine phase transition hints
        phase_hint = _get_phase_hint(q_num, max_q, current_phase, round_type)
        hint = (
            f"这是候选人对第 {q_num} 题的回答。\n"
            f"{phase_hint}\n"
            f"请根据回答质量决定是否追问（最多 1 次），然后用自然的过渡语进入下一题。\n"
            f"（进度：已问 {q_num}/{max_q} 题）"
        )

    session["messages"].append({"role": "user", "content": hint})

    full_response = ""
    async for chunk in stream_chat_completion(session["messages"]):
        full_response += chunk
        yield chunk

    session["messages"].append({"role": "assistant", "content": full_response})

    if "[INTERVIEW_END]" in full_response:
        session["ended"] = True
    else:
        session["question_count"] = min(q_num + 1, max_q)
        # Update phase
        session["current_phase"] = _advance_phase(q_num + 1, max_q, round_type)

    session["conversation"].append({
        "role": "interviewer",
        "content": full_response,
        "question_number": session["question_count"],
    })


def _get_phase_hint(q_num: int, max_q: int, current_phase: str, round_type: str) -> str:
    """Generate a hint about which interview phase to be in."""
    progress = q_num / max_q

    if round_type == "hr_behavioral":
        if progress < 0.2:
            return "当前阶段：暖场和自我介绍。请继续了解候选人的基本情况。"
        elif progress < 0.6:
            return "当前阶段：行为面试 / STAR 追问。请用 STAR 法则深挖候选人的具体经历。"
        elif progress < 0.85:
            return "当前阶段：动机与稳定性评估。请了解候选人的职业规划和求职动机。"
        else:
            return "当前阶段：收尾。准备进入反问环节。"

    elif round_type == "tech_advanced":
        if progress < 0.15:
            return "当前阶段：开场。直接从候选人的项目架构开始提问。"
        elif progress < 0.5:
            return "当前阶段：项目架构深挖。追问架构决策、trade-off、线上表现。"
        elif progress < 0.8:
            return "当前阶段：系统设计题。给一个开放式的系统设计问题，考察全局视角。"
        else:
            return "当前阶段：技术视野与收尾。考察技术广度和学习能力。"

    else:  # tech_basic
        if progress < 0.15:
            return "当前阶段：破冰和自我介绍。"
        elif progress < 0.4:
            return "当前阶段：项目深挖。从简历中选取项目深入追问技术细节。"
        elif progress < 0.65:
            return "当前阶段：技术基础 / 八股文。考察编程语言、数据结构、网络、数据库等基础知识。"
        elif progress < 0.85:
            return "当前阶段：算法题。出一道适合候选人水平的编程题，观察思路和代码风格。"
        else:
            return "当前阶段：收尾。准备进入反问环节。"


def _advance_phase(q_num: int, max_q: int, round_type: str) -> str:
    """Determine the current phase based on progress."""
    progress = q_num / max_q
    if round_type == "hr_behavioral":
        if progress < 0.2:
            return "opening"
        elif progress < 0.6:
            return "behavioral"
        elif progress < 0.85:
            return "motivation"
        else:
            return "closing"
    elif round_type == "tech_advanced":
        if progress < 0.15:
            return "opening"
        elif progress < 0.5:
            return "architecture_dive"
        elif progress < 0.8:
            return "system_design"
        else:
            return "vision"
    else:
        if progress < 0.15:
            return "opening"
        elif progress < 0.4:
            return "project_dive"
        elif progress < 0.65:
            return "tech_fundamentals"
        elif progress < 0.85:
            return "coding"
        else:
            return "closing"


async def stream_standard_answer(session_id: str) -> AsyncIterator[str]:
    """Generate and stream a model/standard answer for the current question.
    This does NOT affect the interview flow — it's a side-channel learning aid."""
    session = _sessions[session_id]
    resume = session["resume"]
    conversation = session["conversation"]

    # Find the last interviewer question
    last_question = ""
    for msg in reversed(conversation):
        if msg["role"] == "interviewer":
            last_question = msg["content"]
            break

    if not last_question:
        yield "暂时无法生成标准回答。"
        return

    # Build a separate prompt for standard answer generation
    answer_messages = [
        {
            "role": "system",
            "content": (
                "你是一位资深技术面试官和面试辅导专家。请针对下面的面试问题，"
                "结合候选人的背景，生成一份高分标准回答。\n\n"
                "要求：\n"
                "1. 回答结构清晰，用 STAR 法则或分层递进的方式组织\n"
                "2. 结合候选人的实际项目经验来举例，不要泛泛而谈\n"
                "3. 包含关键技术细节和数据指标\n"
                "4. 篇幅控制在 300-500 字\n"
                "5. 在最后加上【答题要点】总结 2-3 个关键得分点\n"
            ),
        },
        {
            "role": "user",
            "content": (
                f"候选人背景：{resume.get('summary', '')}\n"
                f"技能栈：{', '.join(resume.get('skills', []))}\n\n"
                f"面试问题：{last_question}\n\n"
                f"请生成一份高分标准回答："
            ),
        },
    ]

    async for chunk in stream_chat_completion(answer_messages, temperature=0.5):
        yield chunk


async def stream_skip_question(session_id: str) -> AsyncIterator[str]:
    """Skip the current question and stream the next one.
    The candidate's 'answer' is recorded as '[跳过此题]'."""
    session = _sessions[session_id]

    # Record skip in conversation
    session["conversation"].append({
        "role": "candidate",
        "content": "[跳过此题]",
        "question_number": session["question_count"],
    })

    q_num = session["question_count"]
    max_q = session["max_questions"]
    round_type = session["config"].get("round_type", "tech_basic")

    skip_hint = (
        f"候选人选择跳过了第 {q_num} 题，没有作答。\n"
        f"请不要追问此题，直接用自然的过渡语提出下一个新问题。\n"
        f"（进度：已问 {q_num}/{max_q} 题）"
    )

    if q_num >= max_q:
        skip_hint = (
            f"候选人跳过了最后一题。请直接进入反问环节：\n"
            f"'好的，那我这边的问题差不多了，你有什么想问我的吗？'\n"
            f"在回复末尾加上 [INTERVIEW_END] 标记。"
        )

    # Add skip instruction as a user message (don't add the skipped question to LLM context)
    session["messages"].append({"role": "user", "content": skip_hint})

    full_response = ""
    async for chunk in stream_chat_completion(session["messages"]):
        full_response += chunk
        yield chunk

    session["messages"].append({"role": "assistant", "content": full_response})

    if "[INTERVIEW_END]" in full_response:
        session["ended"] = True
    else:
        session["question_count"] = min(q_num + 1, max_q)
        session["current_phase"] = _advance_phase(q_num + 1, max_q, round_type)

    session["conversation"].append({
        "role": "interviewer",
        "content": full_response,
        "question_number": session["question_count"],
    })


def end_session(session_id: str) -> dict | None:
    """End session and return conversation data for evaluation."""
    session = _sessions.get(session_id)
    if not session:
        return None

    data = {
        "resume": session["resume"],
        "config": session["config"],
        "conversation": session["conversation"],
        "question_count": session["question_count"],
    }

    del _sessions[session_id]
    return data
