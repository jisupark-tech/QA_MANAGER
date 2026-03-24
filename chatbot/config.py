"""QA 워크스테이션 설정"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
ANSWER_DIR = BASE_DIR.parent / "QA_AI" / "Answer"
KNOWLEDGE_BASE_PATH = ANSWER_DIR / "06_qa_manager_김도빈_260318.md"
IMAGE_DIR = ANSWER_DIR

# LLM
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "8192"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
