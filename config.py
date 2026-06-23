"""Application configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from the backend directory
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path)

# DeepSeek API configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Interview configuration
MAX_QUESTIONS = {
    "junior": 6,
    "mid": 8,
    "senior": 10,
}

INTERVIEW_STYLES = {
    "strict": "严厉施压型",
    "gentle": "温和引导型",
    "english": "外企全英文面试型",
}

INTERVIEW_ROUNDS = {
    "tech_basic": "初级技术面",
    "tech_advanced": "高级架构面",
    "hr_behavioral": "HR 行为面",
}
