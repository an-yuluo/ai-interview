"""Knowledge base loader: reads MD documents and provides them to the interview engine."""
from __future__ import annotations

import re
from pathlib import Path

_KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
_cache: dict[str, str] = {}


def _read_md(filename: str) -> str:
    """Read and cache an MD file from the knowledge directory."""
    if filename in _cache:
        return _cache[filename]
    path = _KNOWLEDGE_DIR / filename
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    _cache[filename] = text
    return text


def get_interview_flow(round_type: str) -> str:
    """Get the interview flow template for a given round type."""
    content = _read_md("interview-flows.md")
    if not content:
        return ""

    # Extract the relevant section based on round type
    section_map = {
        "tech_basic": "一、初级技术面",
        "tech_advanced": "二、高级架构面",
        "hr_behavioral": "三、HR 行为面",
    }
    target = section_map.get(round_type, "")

    if not target:
        return content

    # Extract from target header to the next top-level header or end
    pattern = rf"(## {re.escape(target)}.+?)(?=\n## [一二三]|\n---\n\n## 通用|$)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()

    return content


def get_persona(style: str, round_type: str) -> str:
    """Get interviewer persona based on style and round type."""
    content = _read_md("interviewer-personas.md")
    if not content:
        return ""

    # Map style + round_type to persona
    persona_map = {
        # (style, round_type) → persona name
        ("strict", "tech_basic"): "刘建国",
        ("strict", "tech_advanced"): "张鹏飞",
        ("strict", "hr_behavioral"): "刘建国",
        ("gentle", "tech_basic"): "陈刚",
        ("gentle", "tech_advanced"): "林薇",
        ("gentle", "hr_behavioral"): "王海燕",
        ("english", "tech_basic"): "Sarah Chen",
        ("english", "tech_advanced"): "Sarah Chen",
        ("english", "hr_behavioral"): "Sarah Chen",
    }

    target_name = persona_map.get((style, round_type), "")
    if not target_name:
        # Fallback: just pick based on style
        fallback = {
            "strict": "刘建国",
            "gentle": "陈刚",
            "english": "Sarah Chen",
        }
        target_name = fallback.get(style, "陈刚")

    # Extract persona section
    pattern = rf"(## \d+\. {re.escape(target_name)}.+?)(?=\n## \d+\. |\n## 人设使用规则|$)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: return usage rules section
    rules_match = re.search(r"## 人设使用规则.*", content, re.DOTALL)
    return rules_match.group(0) if rules_match else ""


def get_persona_usage_rules() -> str:
    """Get the persona usage rules section."""
    content = _read_md("interviewer-personas.md")
    match = re.search(r"## 人设使用规则.*", content, re.DOTALL)
    return match.group(0).strip() if match else ""


def get_question_bank(position: str, round_type: str) -> str:
    """Get relevant question bank based on position and round type."""
    pos_lower = position.lower()

    # Determine which question banks to load
    banks = []

    if round_type == "hr_behavioral":
        banks.append("question-bank-hr.md")
    elif round_type == "tech_advanced":
        # Advanced: system design + domain-specific
        banks.append("question-bank-system-design.md")
        if any(kw in pos_lower for kw in ["后端", "backend", "java", "go", "python", "服务端"]):
            banks.append("question-bank-backend.md")
        elif any(kw in pos_lower for kw in ["前端", "frontend", "react", "vue", "web"]):
            banks.append("question-bank-frontend.md")
        else:
            banks.append("question-bank-backend.md")
    else:
        # Basic tech: fundamentals + algorithm
        banks.append("question-bank-algorithm.md")
        if any(kw in pos_lower for kw in ["后端", "backend", "java", "go", "python", "服务端"]):
            banks.append("question-bank-backend.md")
        elif any(kw in pos_lower for kw in ["前端", "frontend", "react", "vue", "web"]):
            banks.append("question-bank-frontend.md")
        else:
            banks.append("question-bank-backend.md")

    # Load and concatenate
    parts = []
    for bank_file in banks:
        content = _read_md(bank_file)
        if content:
            # Take a portion — not the entire bank (to save tokens)
            # Extract the questions (skip very long content)
            lines = content.split("\n")
            if len(lines) > 150:
                lines = lines[:150]
            parts.append("\n".join(lines))

    return "\n\n---\n\n".join(parts)


def clear_cache():
    """Clear the cached MD content (useful for development)."""
    _cache.clear()
