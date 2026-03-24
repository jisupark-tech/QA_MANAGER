"""QA Manager 워크스테이션 - Streamlit 앱"""
import streamlit as st

from config import ANTHROPIC_API_KEY, IMAGE_DIR, KNOWLEDGE_BASE_PATH
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
    page_title="QA 워크스테이션",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- 커스텀 스타일 ----------
st.markdown("""
<style>
    /* 전체 톤: 따뜻한 다크 계열 */
    .stApp {
        background-color: #0e1117;
    }

    /* 탭 스타일 - 깔끔한 밑줄 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: transparent;
        border-bottom: 1px solid #1e2530;
        padding: 0 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        color: #8892a0;
        border: none;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #c4cdd8;
    }
    .stTabs [aria-selected="true"] {
        color: #e8ecf1 !important;
        border-bottom: 2px solid #5b8def !important;
        background: transparent !important;
    }

    /* 카드 스타일 컨테이너 */
    .card {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .card-header {
        color: #e8ecf1;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
    }
    .card-body {
        color: #8892a0;
        font-size: 0.85rem;
        line-height: 1.6;
    }

    /* 안내 텍스트 */
    .guide-text {
        color: #6b7685;
        font-size: 0.8rem;
        line-height: 1.6;
        padding: 0.75rem 1rem;
        background: #111820;
        border-left: 2px solid #2d333b;
        border-radius: 0 4px 4px 0;
        margin: 0.5rem 0;
    }

    /* 상태 배지 */
    .badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .badge-ready { background: #1a2e1a; color: #56d364; }
    .badge-warn { background: #2e2a1a; color: #d6a656; }

    /* 결과 영역 */
    .result-area {
        background: #111820;
        border: 1px solid #1e2530;
        border-radius: 8px;
        padding: 1.5rem;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: #0d1117;
        border-right: 1px solid #1e2530;
    }

    /* 히어로 영역 */
    .hero {
        text-align: center;
        padding: 2rem 0 1rem;
    }
    .hero h1 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e8ecf1;
        margin-bottom: 0.25rem;
    }
    .hero p {
        color: #6b7685;
        font-size: 0.85rem;
    }

    /* 빈 상태 */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #4a5568;
    }
    .empty-state h3 {
        color: #6b7685;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .empty-state p {
        font-size: 0.8rem;
        line-height: 1.6;
    }

    /* 입력 필드 */
    .stTextArea textarea, .stTextInput input {
        background: #111820 !important;
        border-color: #1e2530 !important;
        color: #c4cdd8 !important;
        font-size: 0.85rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3d5a99 !important;
        box-shadow: 0 0 0 1px #3d5a99 !important;
    }

    /* 버튼 */
    .stButton > button[kind="primary"] {
        background: #2563eb !important;
        border: none !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 6px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #1d4ed8 !important;
    }
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #2d333b !important;
        color: #8892a0 !important;
        font-size: 0.8rem !important;
    }

    /* 라디오/셀렉트 */
    .stRadio label, .stSelectbox label {
        font-size: 0.8rem !important;
        color: #8892a0 !important;
    }

    /* 스피너 */
    .stSpinner > div {
        border-color: #5b8def transparent transparent !important;
    }

    /* 구분선 */
    hr {
        border-color: #1e2530 !important;
    }

    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid #2d333b !important;
        color: #8892a0 !important;
        font-size: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)


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
    key = st.session_state.get("api_key", "")
    if not key:
        return None
    return create_client(key)


def check_api_key() -> bool:
    if not st.session_state.get("api_key"):
        st.error("사이드바에서 API Key를 설정해주세요.  (좌측 상단 > 화살표)")
        return False
    return True


def render_result(session_key: str, label: str = "결과"):
    """저장된 결과를 렌더링합니다."""
    if session_key in st.session_state and st.session_state[session_key]:
        result = st.session_state[session_key]
        st.markdown(result)
        st.divider()
        st.download_button(
            f"{label} 다운로드 (.md)",
            data=result,
            file_name=f"qa_{session_key}.md",
            mime="text/markdown",
            key=f"dl_{session_key}",
        )


# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown("### 설정")

    api_key = st.text_input(
        "Anthropic API Key",
        value=ANTHROPIC_API_KEY,
        type="password",
        label_visibility="collapsed",
        placeholder="sk-ant-...",
    )
    st.session_state["api_key"] = api_key

    if api_key:
        st.markdown('<span class="badge badge-ready">연결됨</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-warn">키 필요</span>', unsafe_allow_html=True)

    st.markdown("")
    model = st.selectbox(
        "모델",
        ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-6"],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state["model"] = model
    st.caption(f"현재: {model.split('-')[1].title()}")


# ---------- 히어로 ----------
st.markdown("""
<div class="hero">
    <h1>QA 워크스테이션</h1>
    <p>게임베리 스튜디오 QA Manager의 실무 프로세스를 기반으로 동작합니다</p>
</div>
""", unsafe_allow_html=True)


# ---------- 탭 ----------
tab_chat, tab_spec, tab_tc, tab_bug, tab_release = st.tabs(
    ["질문하기", "기획서 검증", "TC 생성", "버그 리포트", "릴리즈 판단"]
)


# ===== 탭 1: QA 챗봇 =====
with tab_chat:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # 빈 상태 안내
    if not st.session_state.chat_messages:
        st.markdown("""
<div class="empty-state">
    <h3>QA 프로세스에 대해 물어보세요</h3>
    <p>
        버그 분류 기준이 뭐야? / Go/No-Go는 어떻게 판단해? / 핫픽스 프로세스 알려줘<br>
        기획서 검증할 때 뭘 봐야 해? / 레드마인 상태 흐름이 어떻게 돼?
    </p>
</div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("images"):
                display_images(msg["images"])

    col_input, col_clear = st.columns([9, 1])
    with col_clear:
        if st.session_state.chat_messages:
            if st.button("초기화", key="chat_clear", type="secondary"):
                st.session_state.chat_messages = []
                st.rerun()

    if prompt := st.chat_input("질문을 입력하세요"):
        if not check_api_key():
            st.stop()

        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner(""):
                try:
                    knowledge = get_knowledge_base()
                    client = get_client()
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_messages[:-1]
                    ]
                    response = call_llm(
                        client=client,
                        system_prompt=CHATBOT_PROMPT.format(knowledge_base=knowledge),
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
                    st.error(str(e))


# ===== 탭 2: 기획서 검증 =====
with tab_spec:
    input_col, result_col = st.columns([5, 7])

    with input_col:
        st.markdown('<div class="card-header">기획서 입력</div>', unsafe_allow_html=True)

        spec_input = st.text_area(
            "기획서",
            height=380,
            placeholder="기획서 전체 또는 일부를 붙여넣으세요",
            key="spec_input",
            label_visibility="collapsed",
        )

        spec_context = st.text_input(
            "맥락",
            placeholder="연동 기능, 주의사항 등 (선택)",
            key="spec_context",
            label_visibility="collapsed",
        )

        st.markdown("""<div class="guide-text">
        검증 항목: 기획 공백 / 모순 및 중의성 / 데이터 테이블 검증 포인트 / 복합 기능 이슈 / QA 단계별 확인사항
        </div>""", unsafe_allow_html=True)

        if st.button("검증 시작", type="primary", key="spec_submit", use_container_width=True):
            if not check_api_key():
                st.stop()
            if not spec_input.strip():
                st.warning("기획서 내용을 입력해주세요.")
                st.stop()

            with result_col:
                with st.spinner("기획서 분석 중..."):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        user_msg = f"아래 기획서를 검증해주세요.\n\n"
                        if spec_context:
                            user_msg += f"추가 맥락: {spec_context}\n\n"
                        user_msg += f"---\n\n{spec_input}"

                        response = call_llm(
                            client=client,
                            system_prompt=SPEC_REVIEW_PROMPT.format(knowledge_base=knowledge),
                            user_message=user_msg,
                            model=st.session_state["model"],
                            max_tokens=8192,
                        )
                        st.session_state["spec_result"] = response
                    except Exception as e:
                        st.error(str(e))

    with result_col:
        if "spec_result" in st.session_state and st.session_state["spec_result"]:
            render_result("spec_result", "검증 결과")
        else:
            st.markdown("""
<div class="empty-state">
    <h3>검증 결과가 여기에 표시됩니다</h3>
    <p>기획서를 입력하고 '검증 시작'을 누르면<br>공백, 모순, 예외사항을 분석합니다</p>
</div>
            """, unsafe_allow_html=True)


# ===== 탭 3: TC 생성 =====
with tab_tc:
    input_col, result_col = st.columns([5, 7])

    with input_col:
        st.markdown('<div class="card-header">테스트 대상</div>', unsafe_allow_html=True)

        tc_type = st.radio(
            "유형",
            ["기본 기능 TC", "업데이트 TC", "Full TC", "탐색적 테스트 체크리스트"],
            key="tc_type",
            horizontal=True,
            label_visibility="collapsed",
        )

        tc_input = st.text_area(
            "기능",
            height=300,
            placeholder="테스트할 기능을 설명해주세요\n\n예: 스킬 시스템 - 직업별 4개 스킬, 레벨업, 쿨타임 존재",
            key="tc_input",
            label_visibility="collapsed",
        )

        tc_existing = st.text_area(
            "기존 기능",
            height=80,
            placeholder="기존 기능 목록 (복합 검증용, 선택)",
            key="tc_existing",
            label_visibility="collapsed",
        )

        type_guide = {
            "기본 기능 TC": "단독 기능의 기본 동작만 검증. 출시/업데이트마다 수행 (커버리지 ~10%)",
            "업데이트 TC": "신규 추가 기능 전체 검증",
            "Full TC": "인게임 모든 단독 기능 100% 커버",
            "탐색적 테스트 체크리스트": "복합 기능 + 예외사항 + 데이터 검증 + 어뷰징 체크",
        }
        st.markdown(f'<div class="guide-text">{type_guide[tc_type]}</div>', unsafe_allow_html=True)

        if st.button("TC 생성", type="primary", key="tc_submit", use_container_width=True):
            if not check_api_key():
                st.stop()
            if not tc_input.strip():
                st.warning("기능 설명을 입력해주세요.")
                st.stop()

            with result_col:
                with st.spinner("테스트케이스 생성 중..."):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        user_msg = f"TC 유형: {tc_type}\n\n기능 설명:\n{tc_input}\n\n"
                        if tc_existing:
                            user_msg += f"기존 구현 기능 (복합 검증용):\n{tc_existing}"

                        response = call_llm(
                            client=client,
                            system_prompt=TESTCASE_PROMPT.format(knowledge_base=knowledge),
                            user_message=user_msg,
                            model=st.session_state["model"],
                            max_tokens=8192,
                        )
                        st.session_state["tc_result"] = response
                    except Exception as e:
                        st.error(str(e))

    with result_col:
        if "tc_result" in st.session_state and st.session_state["tc_result"]:
            render_result("tc_result", "테스트케이스")
        else:
            st.markdown("""
<div class="empty-state">
    <h3>테스트케이스가 여기에 표시됩니다</h3>
    <p>기능을 설명하고 TC 유형을 선택하면<br>구조화된 테스트케이스를 생성합니다</p>
</div>
            """, unsafe_allow_html=True)


# ===== 탭 4: 버그 리포트 =====
with tab_bug:
    input_col, result_col = st.columns([5, 7])

    with input_col:
        st.markdown('<div class="card-header">결함 정보</div>', unsafe_allow_html=True)

        bug_type = st.radio(
            "유형",
            ["이슈 (결함)", "개선 (제안)"],
            key="bug_type",
            horizontal=True,
            label_visibility="collapsed",
        )

        bug_title = st.text_input(
            "증상",
            placeholder="스킬창에서 2번 스킬 사용 시 게임 멈춤",
            key="bug_title",
            label_visibility="collapsed",
        )

        bug_steps = st.text_area(
            "절차",
            height=150,
            placeholder="1. 메인 화면 > 스킬창 진입\n2. 2번 스킬 선택\n3. 사용 버튼 클릭\n4. 화면 멈춤 (Freezing)",
            key="bug_steps",
            label_visibility="collapsed",
        )

        bug_expected = st.text_input(
            "기대",
            placeholder="기대 동작 (선택)",
            key="bug_expected",
            label_visibility="collapsed",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            bug_repro = st.selectbox(
                "재현율", ["100%", "50%+", "50% 미만", "1회"],
                key="bug_repro", label_visibility="collapsed",
            )
        with col_b:
            bug_scope = st.selectbox(
                "영향 범위", ["전체 유저", "특정 기능", "엣지 케이스"],
                key="bug_scope", label_visibility="collapsed",
            )

        bug_device = st.text_input(
            "디바이스",
            placeholder="특정 단말에서만 재현 시 (선택)",
            key="bug_device",
            label_visibility="collapsed",
        )

        st.markdown("""<div class="guide-text">
        우선순위 자동 분류: 심각도 > 영향 범위 > 유저 인지 가능성 > 재현율
        </div>""", unsafe_allow_html=True)

        if st.button("리포트 생성", type="primary", key="bug_submit", use_container_width=True):
            if not check_api_key():
                st.stop()
            if not bug_title.strip():
                st.warning("증상을 입력해주세요.")
                st.stop()

            with result_col:
                with st.spinner("버그 리포트 생성 중..."):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        user_msg = (
                            f"유형: {bug_type}\n증상: {bug_title}\n"
                            f"재현 절차: {bug_steps or '미입력'}\n"
                            f"기대 동작: {bug_expected or '미입력'}\n"
                            f"재현율: {bug_repro}\n영향 범위: {bug_scope}\n"
                            f"디바이스: {bug_device or '해당 없음'}\n\n"
                            f"위 정보로 레드마인 버그 리포트를 작성해주세요."
                        )
                        response = call_llm(
                            client=client,
                            system_prompt=BUG_REPORT_PROMPT.format(knowledge_base=knowledge),
                            user_message=user_msg,
                            model=st.session_state["model"],
                        )
                        st.session_state["bug_result"] = response
                    except Exception as e:
                        st.error(str(e))

    with result_col:
        if "bug_result" in st.session_state and st.session_state["bug_result"]:
            render_result("bug_result", "버그 리포트")
        else:
            st.markdown("""
<div class="empty-state">
    <h3>버그 리포트가 여기에 표시됩니다</h3>
    <p>증상을 간단히 입력하면 레드마인 표준 형식으로<br>우선순위가 자동 분류된 리포트를 생성합니다</p>
</div>
            """, unsafe_allow_html=True)


# ===== 탭 5: 릴리즈 체크리스트 =====
with tab_release:
    input_col, result_col = st.columns([5, 7])

    with input_col:
        st.markdown('<div class="card-header">릴리즈 정보</div>', unsafe_allow_html=True)

        release_type = st.radio(
            "유형",
            ["Hotfix", "RC", "정기 업데이트", "신규 출시"],
            key="release_type",
            horizontal=True,
            label_visibility="collapsed",
        )

        release_content = st.text_area(
            "내용",
            height=180,
            placeholder="이번 릴리즈 포함 내용\n\n예: 스킬 시스템 추가, 던전 3종, 상품 5개, 채팅 버그 수정",
            key="release_content",
            label_visibility="collapsed",
        )

        release_bugs = st.text_area(
            "잔여 버그",
            height=120,
            placeholder="미수정 버그 (선택 - Go/No-Go 판단용)\n\n예: [중간] 스킬 이펙트 1개 미노출",
            key="release_bugs",
            label_visibility="collapsed",
        )

        time_guide = {
            "Hotfix": "예상 소요: ~2시간 | 긴급 패치 대상 + 결제/핵심 기능 확인",
            "RC": "예상 소요: ~4시간+ | 전수 검증 + 정책/호환성/어뷰징 체크",
            "정기 업데이트": "예상 소요: 기능별 상이 | 추가 기능 + 복합 검증 + 데이터 테이블",
            "신규 출시": "예상 소요: Full QA | 모든 기능 + 디바이스 + 성능 테스트",
        }
        st.markdown(f'<div class="guide-text">{time_guide[release_type]}</div>', unsafe_allow_html=True)

        if st.button("체크리스트 생성", type="primary", key="release_submit", use_container_width=True):
            if not check_api_key():
                st.stop()
            if not release_content.strip():
                st.warning("업데이트 내용을 입력해주세요.")
                st.stop()

            with result_col:
                with st.spinner("체크리스트 생성 중..."):
                    try:
                        knowledge = get_knowledge_base()
                        client = get_client()
                        user_msg = f"릴리즈 유형: {release_type}\n\n업데이트 내용:\n{release_content}\n"
                        if release_bugs.strip():
                            user_msg += f"\n잔여 버그 목록:\n{release_bugs}\n\n위 잔여 버그를 기반으로 Go/No-Go 판단도 함께 해주세요."

                        response = call_llm(
                            client=client,
                            system_prompt=RELEASE_CHECKLIST_PROMPT.format(knowledge_base=knowledge),
                            user_message=user_msg,
                            model=st.session_state["model"],
                            max_tokens=8192,
                        )
                        st.session_state["release_result"] = response
                    except Exception as e:
                        st.error(str(e))

    with result_col:
        if "release_result" in st.session_state and st.session_state["release_result"]:
            render_result("release_result", "체크리스트")
        else:
            st.markdown("""
<div class="empty-state">
    <h3>체크리스트가 여기에 표시됩니다</h3>
    <p>릴리즈 유형을 선택하고 업데이트 내용을 입력하면<br>맞춤 체크리스트와 Go/No-Go 판단을 생성합니다</p>
</div>
            """, unsafe_allow_html=True)
