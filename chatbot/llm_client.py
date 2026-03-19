"""Claude API 클라이언트"""
import anthropic
from config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE, SYSTEM_PROMPT


def create_client(api_key: str | None = None) -> anthropic.Anthropic:
    """Anthropic 클라이언트를 생성합니다."""
    key = api_key or ANTHROPIC_API_KEY
    if not key:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    return anthropic.Anthropic(api_key=key)


def ask_qa_bot(
    client: anthropic.Anthropic,
    user_question: str,
    knowledge_base: str,
    chat_history: list[dict] | None = None,
    model: str | None = None,
) -> str:
    """QA 봇에게 질문합니다."""
    system = SYSTEM_PROMPT.format(knowledge_base=knowledge_base)

    messages = []
    if chat_history:
        # 최근 20개 메시지만 유지
        messages.extend(chat_history[-20:])

    messages.append({"role": "user", "content": user_question})

    response = client.messages.create(
        model=model or LLM_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE,
        system=system,
        messages=messages,
    )

    return response.content[0].text
