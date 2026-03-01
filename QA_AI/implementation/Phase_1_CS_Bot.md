# Phase 1: CS Bot (Module 1)

> **Period**: Week 1~3
> **Prerequisite**: Phase 0 완료
> **Output**: FAQ/계정/결제 자동 응답 봇, 에스컬레이션 시스템

---

## 0. 이 Phase의 목표

```
Phase 1 완료 시점:
✅ FAQ Agent: 벡터 검색 기반 자동 응답 (단순 문의 60~70% 처리)
✅ Account Agent: 유저 DB 조회 + 계정 문의 응답
✅ Payment Agent: 결제 DB 조회 + 결제 문의 응답
✅ Classifier: LLM 기반 문의 유형 자동 분류
✅ QA Guard: 응답 검증 (민감정보 마스킹, 톤 체크)
✅ Escalation: 규칙 기반 사람 전환
✅ 1개 이상 채널 연동 (Discord 또는 KakaoTalk)
```

---

## 1. 필요 정보 (Data Requirements)

### 1-1. FAQ 데이터 (필수)

FAQ는 CS Bot의 핵심 지식베이스입니다.
최소 **10개**, 권장 **30~50개** 이상.

**수집 방법 (택 1)**:
- 기존 FAQ 문서/웹페이지가 있으면 그대로 복사
- 없으면 아래 템플릿에 직접 작성
- 과거 CS 로그에서 빈출 질문 추출

→ 템플릿: [`templates/faq_template.yaml`](templates/faq_template.yaml)

```yaml
# games/{game_name}/faq/general.yaml
faqs:
  - id: faq_001
    category: account        # account / payment / gameplay / event / bug / etc
    question: "비밀번호를 잊어버렸어요"
    answer: |
      비밀번호 재설정 방법:
      1. 로그인 화면에서 '비밀번호 찾기'를 탭하세요.
      2. 가입 시 사용한 이메일을 입력하세요.
      3. 이메일로 전송된 링크를 클릭하여 새 비밀번호를 설정하세요.

      이메일을 받지 못한 경우 스팸함을 확인해주세요.
    keywords:                # 검색 보조 키워드
      - 비번
      - 패스워드
      - password
      - 로그인 안됨

  - id: faq_002
    category: payment
    question: "결제했는데 아이템이 안 들어와요"
    answer: |
      결제 후 아이템 미지급 시:
      1. 앱을 완전히 종료 후 재접속해주세요.
      2. 5분 이내에 자동 지급됩니다.
      3. 10분 이상 미지급 시 결제 영수증과 함께 문의해주세요.
    keywords:
      - 결제 오류
      - 미지급
      - 구매 안됨
```

**FAQ 카테고리 분류 (권장)**:

| Category | 설명 | 파일명 예시 |
|----------|------|------------|
| `account` | 계정, 로그인, 연동 | `faq/account.yaml` |
| `payment` | 결제, 환불, 미지급 | `faq/payment.yaml` |
| `gameplay` | 게임 방법, 시스템 설명 | `faq/gameplay.yaml` |
| `event` | 이벤트, 보상, 출석 | `faq/event.yaml` |
| `bug` | 알려진 버그, 해결 방법 | `faq/bug.yaml` |
| `policy` | 정책, 이용약관, 제재 | `faq/policy.yaml` |

### 1-2. 정책 문서 (필수)

AI가 정책에 맞는 응답을 하려면 정책 문서가 필요합니다.

| # | 정책 종류 | 필요 내용 | 파일 위치 |
|---|----------|----------|-----------|
| 1 | **환불 정책** | 환불 가능 조건, 기간, 절차, 예외 | `policies/refund.md` |
| 2 | **제재 정책** | 제재 사유, 단계 (경고→일시→영구), 이의제기 절차 | `policies/ban.md` |
| 3 | **보상 정책** | 버그 보상 기준, 서버 점검 보상, 이벤트 오류 보상 | `policies/compensation.md` |
| 4 | **개인정보 처리** | 어디까지 조회 가능, 제3자 제공 범위 | `policies/privacy.md` |

**예시 (환불 정책)**:
```markdown
# 환불 정책

## 환불 가능 조건
- 결제 후 7일 이내
- 구매 아이템 미사용 상태
- 동일 계정 월 2회까지

## 환불 불가 조건
- 아이템 사용/장착 완료
- 이벤트 한정 상품
- 결제 후 30일 초과

## 절차
1. CS 문의 접수
2. 결제 내역 + 영수증 확인
3. 환불 조건 충족 시 3영업일 내 처리
```

### 1-3. 에스컬레이션 규칙 (필수)

어떤 경우에 AI가 사람에게 넘길지 정의합니다.

→ 템플릿: [`templates/escalation_rules.yaml`](templates/escalation_rules.yaml)

```yaml
# games/{game_name}/escalation_rules.yaml
rules:
  - id: esc_001
    name: "고액 결제 문의"
    condition:
      type: payment_amount
      operator: ">="
      value: 100000            # 원 단위
    action: human_review       # human_review / human_takeover
    priority: high             # low / medium / high / urgent
    reason: "고액 결제는 반드시 사람이 확인"

  - id: esc_002
    name: "분노 감지"
    condition:
      type: sentiment
      operator: "=="
      value: angry             # angry / frustrated / threatening
    action: human_takeover
    priority: urgent
    reason: "감정적 유저는 사람이 직접 대응"

  - id: esc_003
    name: "반복 문의"
    condition:
      type: repeat_count
      operator: ">="
      value: 3                 # 동일 유저 3회 이상 문의
    action: human_takeover
    priority: high
    reason: "반복 문의는 AI 해결 실패 의미"

  - id: esc_004
    name: "법적 언급"
    condition:
      type: keyword_match
      keywords:
        - 소송
        - 고소
        - 법률
        - 변호사
        - 소비자원
        - 신고
    action: human_takeover
    priority: urgent
    reason: "법적 분쟁 가능성 → 즉시 사람 전환"

  - id: esc_005
    name: "AI 확신도 낮음"
    condition:
      type: confidence
      operator: "<"
      value: 0.7               # LLM의 자체 확신도 점수
    action: human_review
    priority: medium
    reason: "AI가 확신이 낮은 응답은 검수 필요"
```

### 1-4. 응답 스타일 가이드 (선택)

| # | 항목 | 설정값 | 설명 |
|---|------|--------|------|
| 1 | 어조 | `formal` / `friendly` / `casual` | 존댓말 수준 |
| 2 | 이모지 사용 | `true` / `false` | 응답에 이모지 포함 여부 |
| 3 | 서명 | `"- GameOps AI"` | 응답 끝에 붙는 서명 |
| 4 | 최대 응답 길이 | `500` | 글자 수 제한 |
| 5 | 금지 표현 | `["확실합니다", "보장합니다"]` | AI가 절대 쓰면 안 되는 표현 |
| 6 | 필수 표현 | `["추가 문의가 있으시면..."]` | 매 응답 끝에 포함할 문구 |

```yaml
# games/{game_name}/config.yaml 에 추가
response_style:
  tone: formal
  emoji: false
  signature: "- 고객센터 AI"
  max_length: 500
  forbidden_phrases:
    - "확실합니다"
    - "보장합니다"
    - "100%"
  closing_phrase: "추가 문의가 있으시면 언제든 말씀해주세요."
```

### 1-5. 과거 CS 로그 (선택 — 강력 권장)

있으면 정확도가 크게 향상됩니다. 없어도 시작은 가능합니다.

**필요 포맷**:
```csv
date,user_id,category,question,answer,resolved,satisfaction
2026-01-15,user_001,payment,"결제했는데 다이아 안 들어와요","확인 후 지급 완료",true,5
2026-01-15,user_002,account,"계정 연동 방법이요","설정 > 계정연동에서...",true,4
2026-01-16,user_003,bug,"스테이지 5에서 튕겨요","알려진 이슈, 다음 패치에서 수정",true,3
```

**최소 필드**:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `date` | date | 문의 날짜 | YES |
| `user_id` | string | 유저 식별자 | YES |
| `category` | string | 문의 유형 | YES |
| `question` | text | 유저 질문 원문 | YES |
| `answer` | text | CS 응답 원문 | OPTIONAL |
| `resolved` | bool | 해결 여부 | OPTIONAL |
| `satisfaction` | int(1~5) | 만족도 | OPTIONAL |

### 1-6. 게임 DB 테이블 구조 (계정/결제 Agent용)

Account Agent와 Payment Agent가 유저 정보를 조회하려면 DB 구조를 알아야 합니다.

**필요한 테이블 정보**:

```yaml
# 유저 테이블
user_table:
  name: "users"              # 실제 테이블명
  fields:
    user_id: "uid"           # 유저 ID 컬럼명
    nickname: "nickname"
    email: "email"
    register_date: "created_at"
    last_login: "last_login_at"
    level: "level"
    vip_grade: "vip_level"
    ban_status: "is_banned"
    ban_reason: "ban_reason"
    ban_until: "ban_until"

# 결제 테이블
payment_table:
  name: "payments"
  fields:
    payment_id: "id"
    user_id: "uid"
    amount: "amount"
    currency: "currency"      # KRW / USD
    product_id: "product_id"
    product_name: "product_name"
    status: "status"          # completed / refunded / failed
    receipt: "receipt_data"
    created_at: "created_at"

# 아이템 지급 테이블
item_log_table:
  name: "item_logs"
  fields:
    user_id: "uid"
    item_id: "item_id"
    item_name: "item_name"
    quantity: "quantity"
    source: "source"          # purchase / event / quest / admin
    created_at: "created_at"
```

> **DB 접근이 없는 경우**: Account/Payment Agent는 비활성화하고, FAQ Agent + Escalation만 운영. 유저 DB 조회가 필요한 문의는 모두 에스컬레이션.

---

## 2. 필요 설정 (Configuration)

### 2-1. CS 채널 설정

**Discord (권장 — 설정이 가장 간단)**:

| 단계 | 작업 | 결과 |
|------|------|------|
| 1 | [Discord Developer Portal](https://discord.com/developers) 접속 | 앱 생성 |
| 2 | Bot 탭 → Add Bot | Bot Token 발급 |
| 3 | OAuth2 → URL Generator → `bot` + `applications.commands` | 초대 URL 생성 |
| 4 | 생성된 URL로 서버에 봇 초대 | 봇 서버 참가 |
| 5 | Bot Token을 `.env`에 저장 | `DISCORD_BOT_TOKEN=xxxxx` |
| 6 | CS 전용 채널 생성 | `#cs-support` |
| 7 | 알림 전용 채널 생성 | `#ops-alert` (Phase 2 QA Monitor용) |

**필요 권한**:
- `Send Messages`, `Read Message History`, `Embed Links`
- `Manage Messages` (선택 — 에스컬레이션 시 메시지 편집용)

**KakaoTalk (선택)**:

| 단계 | 작업 |
|------|------|
| 1 | [Kakao Developers](https://developers.kakao.com) 앱 등록 |
| 2 | 카카오톡 채널 생성 |
| 3 | 채널 API 키 발급 |
| 4 | Webhook URL 설정 (FastAPI 서버 주소) |

### 2-2. Vector DB (ChromaDB) FAQ 인덱싱

FAQ 문서를 ChromaDB에 임베딩하여 저장합니다.

```python
# 초기 FAQ 인덱싱 스크립트 (1회 실행)
import chromadb
import yaml

client = chromadb.PersistentClient(path="./data/chroma")
collection = client.get_or_create_collection(
    name="faq_{game_name}",
    metadata={"hnsw:space": "cosine"}
)

# FAQ YAML 로드
with open("games/mygame/faq/general.yaml") as f:
    data = yaml.safe_load(f)

for faq in data["faqs"]:
    collection.add(
        ids=[faq["id"]],
        documents=[faq["question"] + " " + " ".join(faq.get("keywords", []))],
        metadatas=[{
            "category": faq["category"],
            "answer": faq["answer"],
            "question": faq["question"]
        }]
    )
```

### 2-3. Classifier 프롬프트 설정

```yaml
# module_cs/config/classifier_prompt.yaml
system_prompt: |
  당신은 게임 고객센터 문의 분류기입니다.
  유저의 메시지를 읽고 아래 카테고리 중 하나로 분류하세요.

  카테고리:
  - faq: 일반적인 질문, 게임 방법, 시스템 설명
  - account: 계정, 로그인, 연동, 탈퇴
  - payment: 결제, 환불, 미지급, 구매
  - bug: 버그 신고, 오류, 크래시
  - suggestion: 건의, 요청, 개선 제안
  - ban: 제재, 차단, 이의제기
  - other: 위 카테고리에 해당하지 않는 문의

  응답 형식 (JSON):
  {"category": "카테고리명", "confidence": 0.0~1.0, "summary": "한줄요약"}
```

---

## 3. Module 구조

```
module_cs/
├── __init__.py
├── main.py                    # FastAPI 앱 + 라이프사이클
├── gateway/
│   ├── discord_gateway.py     # Discord 메시지 수신/발신
│   └── kakao_gateway.py       # KakaoTalk 수신/발신 (선택)
├── classifier.py              # LLM 기반 문의 유형 분류
├── router.py                  # 분류 결과 → Agent 라우팅
├── agents/
│   ├── faq_agent.py           # Vector 검색 + LLM 응답 생성
│   ├── account_agent.py       # 유저 DB 조회 + 응답
│   └── payment_agent.py       # 결제 DB 조회 + 응답
├── qa_guard.py                # 응답 검증 (민감정보, 톤, 금지어)
├── escalation.py              # 규칙 엔진 (YAML 기반)
├── responder.py               # 최종 응답 전송 + 로깅
└── config/
    ├── classifier_prompt.yaml
    └── agent_prompts.yaml     # 각 Agent의 시스템 프롬프트
```

---

## 4. Phase 1 완료 조건

| # | Deliverable | 측정 기준 |
|---|-------------|-----------|
| 1 | FAQ Agent 작동 | FAQ 질문 10개 테스트 → 정답률 70%+ |
| 2 | Classifier 정확도 | 분류 테스트 20건 → 정확도 80%+ |
| 3 | Escalation 작동 | 에스컬레이션 규칙 5개 시나리오 통과 |
| 4 | QA Guard 작동 | 민감정보 포함 응답 → 마스킹 확인 |
| 5 | 채널 연동 | Discord에서 실제 대화 가능 |
| 6 | 로깅 | 모든 문의/응답이 `data/tickets/`에 기록됨 |

---

## 5. Phase 1 → Phase 2 연결

| 다음 Phase에 필요한 것 | Phase 1에서 발생하는 데이터 |
|-----------------------|--------------------------|
| 문의 패턴 데이터 | 티켓 로그 → 버그 클러스터링 입력 (Phase 2) |
| 유저 행동 이상 신호 | 결제 이상 패턴 → 이상 탐지 입력 (Phase 2) |
| 자동 처리율 기준선 | Phase 1 auto-resolve rate → Phase 3 KPI 기준 |
