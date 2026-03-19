"""QA Manager AI 챗봇 - Streamlit 앱"""
import streamlit as st
from pathlib import Path

from config import ANTHROPIC_API_KEY, LLM_MODEL, IMAGE_DIR, KNOWLEDGE_BASE_PATH
from knowledge_base import load_knowledge_base, extract_image_refs
from llm_client import create_client, ask_qa_bot

# 페이지 설정
st.set_page_config(
    page_title="QA Manager AI Bot",
    page_icon="🔍",
    layout="wide",
)

# 사이드바
with st.sidebar:
    st.title("⚙️ 설정")

    api_key = st.text_input(
        "Anthropic API Key",
        value=ANTHROPIC_API_KEY,
        type="password",
        help="Claude API 키를 입력하세요.",
    )

    model = st.selectbox(
        "모델 선택",
        ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-6"],
        index=0,
    )

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        """
    ### QA Manager AI Bot
    게임베리 스튜디오 QA Manager의 업무 지식을 기반으로 답변합니다.

    **답변 가능한 주제:**
    - 역할 및 업무 프로세스
    - 버그 분류 및 트리아지
    - 품질 기준 및 Go/No-Go 판단
    - 릴리즈 사이클별 QA
    - 테스트 전략 및 자동화
    - 게임 특화 QA (밸런스, 결제, 호환성)
    - 개발팀 커뮤니케이션
    - KPI 및 리포팅
    """
    )

# 지식 베이스 로드
@st.cache_data
def get_knowledge_base() -> str:
    return load_knowledge_base(KNOWLEDGE_BASE_PATH)


# 이미지 표시
def display_images(image_filenames: list[str]):
    for filename in image_filenames:
        img_path = IMAGE_DIR / filename
        if img_path.exists():
            st.image(str(img_path), caption=filename, use_container_width=True)


# 메인 화면
st.title("🔍 QA Manager AI Bot")
st.caption("게임베리 스튜디오 QA Manager 페르소나 기반 챗봇")

# 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("images"):
            display_images(msg["images"])

# 사용자 입력
if prompt := st.chat_input("QA 관련 질문을 입력하세요..."):
    # API 키 확인
    if not api_key:
        st.error("사이드바에서 Anthropic API Key를 입력해주세요.")
        st.stop()

    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            try:
                knowledge = get_knowledge_base()
                client = create_client(api_key)

                # 대화 기록 (API 형식)
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]

                response = ask_qa_bot(
                    client=client,
                    user_question=prompt,
                    knowledge_base=knowledge,
                    chat_history=history,
                    model=model,
                )

                st.markdown(response)

                # 이미지 추출 및 표시
                images = extract_image_refs(response)
                if images:
                    display_images(images)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response, "images": images}
                )

            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
