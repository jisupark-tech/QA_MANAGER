"""QA Manager 워크스테이션 - Streamlit 앱"""
import streamlit as st
from pathlib import Path

from config import ANTHROPIC_API_KEY, LLM_MODEL, IMAGE_DIR, KNOWLEDGE_BASE_PATH
from knowledge_base import load_knowledge_base, extract_image_refs
from llm_client import create_client, call_llm
from prompts import (
    CHATBOT_PROMPT,
    SPEC_REVIEW_PROMPT,
    TESTCASE_PROMPT,
    BUG_REPORT_PROMPT,
    RELEASE_CHECKLIST_PROMPT,
)

# ---------- 페이지 설정 ----------
st.set_page_config(
    page_title="QA Manager 워크스테이션",
    page_icon="🛠️",
    layout="wide",
)


# ---------- 공통 함수 ----------
@st.cache_data
def get_knowledge_base() -> str:
    return load_knowledge_base(KNOWLEDGE_BASE_PATH)


def display_images(image_filenames: list[str]):
    for filename in image_filenames:
        img_path = IMAGE_DIR / filename
        if img_path.exists():
            st.image(str(img_path), caption=filename, use_container_width=True)


def get_client():
    """API 클라이언트를 가져옵니다. 키가 없으면 None 반환."""
    key = st.session_state.get("api_key", "")
    if not key:
        return None
    return create_client(key)


def check_api_key() -> bool:
    """API 키가 설정되었는지 확인합니다."""
    if not st.session_state.get("api_key"):
        st.warning("사이드바에서 Anthropic API Key를 입력해주세요.")
        return False
    return True


# ---------- 사이드바 ----------
with st.sidebar:
    st.title("🛠️ QA 워크스테이션")

    api_key = st.text_input(
        "Anthropic API Key",
        value=ANTHROPIC_API_KEY,
        type="password",
    )
    st.session_state["api_key"] = api_key

    model = st.selectbox(
        "모델",
        ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-6"],
        index=0,
    )
    st.session_state["model"] = model

    st.divider()
    st.markdown("""
**기능 안내**
- **QA 챗봇**: QA 업무 관련 질문 답변
- **기획서 검증**: 공백/모순/예외사항 탐지
- **TC 생성**: 테스트케이스 자동 생성
- **버그 리포트**: 표준 형식 버그 리포트 작성
- **릴리즈 체크리스트**: 유형별 체크리스트 생성
    """)


# ---------- 탭 구성 ----------
tab_chat, tab_spec, tab_tc, tab_bug, tab_release = st.tabs(
    ["💬 QA 챗봇", "📋 기획서 검증", "🧪 TC 생성", "🐛 버그 리포트", "🚀 릴리즈 체크리스트"]
)


# ========== 탭 1: QA 챗봇 ==========
with tab_chat:
    st.header("QA Manager AI 챗봇")
    st.caption("QA 업무 프로세스, 판단 기준, 버그 분류 등에 대해 질문하세요")

    if st.button("대화 초기화", key="chat_clear"):
        st.session_state.chat_messages = []
        st.rerun()

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("images"):
                display_images(msg["images"])

    if prompt := st.chat_input("QA 관련 질문을 입력하세요..."):
        if not check_api_key():
            st.stop()

        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                try:
                    knowledge = get_knowledge_base()
                    client = get_client()
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_messages[:-1]
                    ]
                    system = CHATBOT_PROMPT.format(knowledge_base=knowledge)
                    response = call_llm(
                        client=client,
                        system_prompt=system,
                        user_message=prompt,
                        chat_history=history,
                        model=st.session_state["model"],
                    )
                    st.markdown(response)
                    images = extract_image_refs(response)
                    if images:
                        display_images(images)
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": response, "images": images}
                    )
                except Exception as e:
                    st.error(f"오류: {e}")


# ========== 탭 2: 기획서 검증 ==========
with tab_spec:
    st.header("기획서 검증")
    st.caption("기획서를 입력하면 공백, 모순, 예외사항을 분석합니다")

    col1, col2 = st.columns([1, 1])

    with col1:
        spec_input = st.text_area(
            "기획서 내용을 붙여넣으세요",
            height=500,
            placeholder="기획서 전체 또는 일부를 여기에 붙여넣으세요.\n\n예시:\n- 스킬 시스템 기획서\n- 던전 기획서\n- 상품/BM 기획서\n- 데이터 테이블 내용",
            key="spec_input",
        )

        spec_context = st.text_input(
            "추가 맥락 (선택)",
            placeholder="예: 이 기능은 무기 시스템과 연동됩니다",
            key="spec_context",
        )

        if st.button("기획서 검증 시작", type="primary", key="spec_submit"):
            if not check_api_key():
                st.stop()
            if not spec_input.strip():
                st.warning("기획서 내용을 입력해주세요.")
                st.stop()

            with col2:
                with st.spinner("기획서 분석 중... (30초~1분 소요)"):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        system = SPEC_REVIEW_PROMPT.format(knowledge_base=knowledge)

                        user_msg = f"아래 기획서를 검증해주세요.\n\n"
                        if spec_context:
                            user_msg += f"추가 맥락: {spec_context}\n\n"
                        user_msg += f"---\n\n{spec_input}"

                        response = call_llm(
                            client=client,
                            system_prompt=system,
                            user_message=user_msg,
                            model=st.session_state["model"],
                            max_tokens=8192,
                        )
                        st.markdown(response)
                        st.session_state["spec_result"] = response
                    except Exception as e:
                        st.error(f"오류: {e}")

    with col2:
        if "spec_result" in st.session_state and not spec_input:
            st.markdown(st.session_state["spec_result"])


# ========== 탭 3: TC 생성 ==========
with tab_tc:
    st.header("테스트케이스 생성")
    st.caption("기능 설명을 입력하면 테스트케이스를 자동 생성합니다")

    col1, col2 = st.columns([1, 1])

    with col1:
        tc_type = st.radio(
            "TC 유형",
            ["기본 기능 TC", "업데이트 TC", "Full TC", "탐색적 테스트 체크리스트"],
            key="tc_type",
        )

        tc_input = st.text_area(
            "기능 설명",
            height=400,
            placeholder="테스트할 기능을 설명해주세요.\n\n예시:\n- 스킬 시스템: 직업별 4개 스킬, 각 스킬 레벨업 가능, 쿨타임 존재\n- 던전: 3종류, 각 10단계, 보상 차등 지급\n- 상품: 일반/횟수제한/패스/광고제거 4가지 유형",
            key="tc_input",
        )

        tc_existing = st.text_area(
            "기존 기능 목록 (선택 - 복합 검증용)",
            height=100,
            placeholder="이미 구현된 기능 목록 (복합 검증 항목 생성에 활용)",
            key="tc_existing",
        )

        if st.button("TC 생성", type="primary", key="tc_submit"):
            if not check_api_key():
                st.stop()
            if not tc_input.strip():
                st.warning("기능 설명을 입력해주세요.")
                st.stop()

            with col2:
                with st.spinner("테스트케이스 생성 중..."):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        system = TESTCASE_PROMPT.format(knowledge_base=knowledge)

                        user_msg = f"TC 유형: {tc_type}\n\n"
                        user_msg += f"기능 설명:\n{tc_input}\n\n"
                        if tc_existing:
                            user_msg += f"기존 구현 기능 (복합 검증용):\n{tc_existing}"

                        response = call_llm(
                            client=client,
                            system_prompt=system,
                            user_message=user_msg,
                            model=st.session_state["model"],
                            max_tokens=8192,
                        )
                        st.markdown(response)
                        st.session_state["tc_result"] = response
                    except Exception as e:
                        st.error(f"오류: {e}")

    with col2:
        if "tc_result" in st.session_state and not tc_input:
            st.markdown(st.session_state["tc_result"])


# ========== 탭 4: 버그 리포트 ==========
with tab_bug:
    st.header("버그 리포트 작성")
    st.caption("증상을 간단히 입력하면 레드마인 표준 형식의 버그 리포트를 생성합니다")

    col1, col2 = st.columns([1, 1])

    with col1:
        bug_title = st.text_input(
            "증상 요약",
            placeholder="예: 스킬창에서 2번 스킬 사용 시 게임 멈춤",
            key="bug_title",
        )

        bug_type = st.radio(
            "유형", ["이슈 (결함)", "개선 (제안)"], key="bug_type", horizontal=True
        )

        bug_steps = st.text_area(
            "재현 절차 / 상세 설명",
            height=200,
            placeholder="1. 메인 화면에서 스킬창 진입\n2. 2번 스킬 선택\n3. 사용 버튼 클릭\n4. 화면 멈춤 발생",
            key="bug_steps",
        )

        bug_expected = st.text_input(
            "기대 동작 (선택)",
            placeholder="예: 스킬이 정상적으로 발동되어야 함",
            key="bug_expected",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            bug_repro = st.selectbox(
                "재현율",
                ["100% (항상)", "50% 이상", "50% 미만", "1회만 발생"],
                key="bug_repro",
            )
        with col_b:
            bug_scope = st.selectbox(
                "영향 범위",
                ["전체 유저 (大)", "특정 기능 (中)", "엣지 케이스 (小)"],
                key="bug_scope",
            )

        bug_device = st.text_input(
            "디바이스/환경 (선택 - 특정 단말에서만 재현 시)",
            placeholder="예: 갤럭시A10, Android 12",
            key="bug_device",
        )

        if st.button("버그 리포트 생성", type="primary", key="bug_submit"):
            if not check_api_key():
                st.stop()
            if not bug_title.strip():
                st.warning("증상 요약을 입력해주세요.")
                st.stop()

            with col2:
                with st.spinner("버그 리포트 생성 중..."):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        system = BUG_REPORT_PROMPT.format(knowledge_base=knowledge)

                        user_msg = f"""아래 정보로 레드마인 버그 리포트를 작성해주세요.

유형: {bug_type}
증상: {bug_title}
재현 절차: {bug_steps if bug_steps else '미입력'}
기대 동작: {bug_expected if bug_expected else '미입력'}
재현율: {bug_repro}
영향 범위: {bug_scope}
디바이스: {bug_device if bug_device else '해당 없음'}
"""
                        response = call_llm(
                            client=client,
                            system_prompt=system,
                            user_message=user_msg,
                            model=st.session_state["model"],
                        )
                        st.markdown(response)
                        st.session_state["bug_result"] = response
                    except Exception as e:
                        st.error(f"오류: {e}")

    with col2:
        if "bug_result" in st.session_state and not bug_title:
            st.markdown(st.session_state["bug_result"])


# ========== 탭 5: 릴리즈 체크리스트 ==========
with tab_release:
    st.header("릴리즈 체크리스트")
    st.caption("릴리즈 유형을 선택하면 맞춤 체크리스트를 생성합니다")

    col1, col2 = st.columns([1, 1])

    with col1:
        release_type = st.radio(
            "릴리즈 유형",
            ["Hotfix (긴급 패치)", "RC (Release Candidate)", "정기 업데이트", "신규 출시"],
            key="release_type",
        )

        release_content = st.text_area(
            "업데이트 내용",
            height=200,
            placeholder="이번 릴리즈에 포함된 내용을 적어주세요.\n\n예시:\n- 스킬 시스템 추가\n- 던전 3종 추가\n- 상품 5개 추가\n- 채팅 버그 수정",
            key="release_content",
        )

        release_bugs = st.text_area(
            "잔여 버그 목록 (선택 - Go/No-Go 판단용)",
            height=150,
            placeholder="아직 수정되지 않은 버그가 있다면 적어주세요.\n\n예시:\n- [중간] 특정 스킬 이펙트 1개 미노출\n- [낮음] 랭킹 유저 정보 갱신 미연동",
            key="release_bugs",
        )

        if st.button("체크리스트 생성", type="primary", key="release_submit"):
            if not check_api_key():
                st.stop()
            if not release_content.strip():
                st.warning("업데이트 내용을 입력해주세요.")
                st.stop()

            with col2:
                with st.spinner("체크리스트 생성 중..."):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        system = RELEASE_CHECKLIST_PROMPT.format(knowledge_base=knowledge)

                        user_msg = f"""릴리즈 유형: {release_type}

업데이트 내용:
{release_content}
"""
                        if release_bugs.strip():
                            user_msg += f"""
잔여 버그 목록:
{release_bugs}

위 잔여 버그를 기반으로 Go/No-Go 판단도 함께 해주세요.
"""
                        response = call_llm(
                            client=client,
                            system_prompt=system,
                            user_message=user_msg,
                            model=st.session_state["model"],
                            max_tokens=8192,
                        )
                        st.markdown(response)
                        st.session_state["release_result"] = response
                    except Exception as e:
                        st.error(f"오류: {e}")

    with col2:
        if "release_result" in st.session_state and not release_content:
            st.markdown(st.session_state["release_result"])
