"""Claude API 클라이언트"""
import anthropic
from config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE


def create_client(api_key: str | None = None) -> anthropic.Anthropic:
    """Anthropic 클라이언트를 생성합니다."""
    key = api_key or ANTHROPIC_API_KEY
    if not key:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    return anthropic.Anthropic(api_key=key)


def call_llm(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_message: str,
    chat_history: list[dict] | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> str:
    """Claude API를 호출합니다."""
    messages = []
    if chat_history:
        messages.extend(chat_history[-20:])

    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model=model or LLM_MODEL,
        max_tokens=max_tokens or LLM_MAX_TOKENS,
        temperature=temperature if temperature is not None else LLM_TEMPERATURE,
        system=system_prompt,
        messages=messages,
    )

    return response.content[0].text
