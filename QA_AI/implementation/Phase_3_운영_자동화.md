# Phase 3: 운영 자동화 (Module 3 - Ops Automation)

> **Period**: Week 5~7
> **Prerequisite**: Phase 1 (CS Bot) 완료
> **Output**: 공지 자동 생성, KPI 리포트, 핫픽스 우선순위, 이벤트 관리
> **GameScale 참조**: QA/운영 패키지 + Marketing 패키지 (공지/이벤트)

---

## 0. 이 Phase의 목표

```
Phase 3 완료 시점:
✅ Announcement Generator: 운영 지시 → 공지문 자동 작성
✅ KPI Reporter: 일일/주간 KPI 요약 리포트 자동 생성
✅ Hotfix Prioritizer: 버그 클러스터 × 영향도 → 우선순위 리포트
✅ Event Manager: 이벤트 일정 관리 + 자동 알림
```

---

## 1. 필요 정보 (Data Requirements)

### 1-1. 공지 작성용 데이터 (필수)

| # | 항목 | 설명 | 예시 | 필수 |
|---|------|------|------|------|
| 1 | 과거 공지문 샘플 | AI가 톤/형식을 학습할 기존 공지 3~5개 | 점검 공지, 이벤트 공지, 패치노트, 긴급 공지 | YES |
| 2 | 공지 카테고리 정의 | 어떤 유형의 공지를 생성할지 | 아래 표 참조 | YES |
| 3 | 게임 용어 사전 | 게임 내 고유 용어 | 아래 참조 | YES |
| 4 | 공지 게시 채널 | 어디에 공지를 올릴지 | Discord #notice, 인게임, 카페 | YES |

**공지 카테고리**:

| Category | 설명 | 예시 |
|----------|------|------|
| `maintenance` | 서버 점검 | "3/5(수) 10:00~12:00 정기 점검" |
| `update` | 업데이트/패치노트 | "v2.3.0 업데이트 안내" |
| `event` | 이벤트 시작/종료 | "봄맞이 출석 이벤트!" |
| `emergency` | 긴급 공지 | "결제 오류 긴급 점검 안내" |
| `compensation` | 보상 안내 | "점검 보상 지급 안내" |
| `known_issue` | 알려진 이슈 | "스테이지 5 크래시 현상 인지" |

**과거 공지 제출 형식**:
```yaml
# games/{game_name}/announcements/samples.yaml
samples:
  - category: maintenance
    title: "3/5(수) 정기 점검 안내"
    body: |
      안녕하세요, [게임명] 운영팀입니다.

      아래와 같이 정기 점검을 실시합니다.

      ■ 점검 일시: 3월 5일(수) 10:00 ~ 12:00 (약 2시간)
      ■ 점검 내용: 서버 안정화, 버그 수정
      ■ 점검 보상: 골드 1,000 + 다이아 10

      점검 시간 동안 게임 이용이 불가합니다.
      불편을 드려 죄송합니다.

      감사합니다.
      [게임명] 운영팀 드림

  - category: event
    title: "봄맞이 출석 이벤트"
    body: |
      (이벤트 공지 예시...)
```

### 1-2. 게임 용어 사전 (필수)

AI가 공지/리포트 작성 시 올바른 용어를 사용하도록 합니다.

```yaml
# games/{game_name}/glossary.yaml
terms:
  # 재화
  - term: "골드"
    aliases: ["금화", "gold", "G"]
    description: "기본 재화. 상점, 강화 등에 사용"

  - term: "다이아몬드"
    aliases: ["다이아", "보석", "diamond", "gem"]
    description: "프리미엄 재화. 현금 결제 또는 이벤트로 획득"

  # 시스템
  - term: "강화"
    aliases: ["upgrade", "enchant"]
    description: "장비 능력치 향상. 실패 시 파괴 가능"

  - term: "전투력"
    aliases: ["CP", "combat power", "파워"]
    description: "캐릭터 종합 전투 능력 수치"

  # 콘텐츠
  - term: "토벌전"
    aliases: ["레이드", "raid"]
    description: "4인 협동 보스 전투. 매일 3회 제한"
```

### 1-3. KPI 정의 및 데이터소스 (필수)

→ 템플릿: [`templates/kpi_definitions.yaml`](templates/kpi_definitions.yaml)

```yaml
# games/{game_name}/kpi_definitions.yaml

# KPI 리포트 생성 주기
report_schedule:
  daily: true                  # 매일 오전 10시
  weekly: true                 # 매주 월요일 오전 10시
  monthly: true                # 매월 1일

# KPI 지표 정의
metrics:
  # === 유저 지표 ===
  - id: dau
    name: "DAU (일일 활성 유저)"
    category: user
    source:
      type: database
      query: "SELECT COUNT(DISTINCT uid) FROM session_log WHERE DATE(login_at) = CURDATE()"
    format: number
    comparison: day_over_day    # 전일 대비 변화율 표시

  - id: nru
    name: "NRU (신규 가입)"
    category: user
    source:
      type: database
      query: "SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()"
    format: number
    comparison: day_over_day

  - id: retention_d1
    name: "D1 리텐션"
    category: user
    source:
      type: database
      query: |
        SELECT
          COUNT(DISTINCT s.uid) / COUNT(DISTINCT u.uid) * 100
        FROM users u
        LEFT JOIN session_log s ON u.uid = s.uid
          AND DATE(s.login_at) = DATE_ADD(DATE(u.created_at), INTERVAL 1 DAY)
        WHERE DATE(u.created_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
    format: percentage
    target: 40                 # 목표치 40%
    alert_below: 30            # 30% 미만 시 알림

  - id: retention_d7
    name: "D7 리텐션"
    category: user
    source:
      type: database
      query: "..."             # 유사 쿼리
    format: percentage
    target: 20
    alert_below: 15

  # === 매출 지표 ===
  - id: daily_revenue
    name: "일 매출"
    category: revenue
    source:
      type: database
      query: "SELECT SUM(amount) FROM payments WHERE status='completed' AND DATE(created_at) = CURDATE()"
    format: currency_krw
    comparison: day_over_day

  - id: arpu
    name: "ARPU"
    category: revenue
    source:
      type: calculated
      formula: "daily_revenue / dau"
    format: currency_krw

  - id: paying_rate
    name: "과금률"
    category: revenue
    source:
      type: database
      query: |
        SELECT
          COUNT(DISTINCT p.uid) / COUNT(DISTINCT s.uid) * 100
        FROM session_log s
        LEFT JOIN payments p ON s.uid = p.uid
          AND DATE(p.created_at) = CURDATE()
        WHERE DATE(s.login_at) = CURDATE()
    format: percentage

  # === CS 지표 ===
  - id: cs_auto_resolve_rate
    name: "CS 자동 처리율"
    category: cs
    source:
      type: internal           # Phase 1 모듈에서 수집
      module: module_cs
      metric: auto_resolve_rate
    format: percentage
    target: 70
    alert_below: 50

  - id: cs_avg_response_time
    name: "평균 응답 시간"
    category: cs
    source:
      type: internal
      module: module_cs
      metric: avg_response_seconds
    format: duration_seconds
    target: 10                 # 목표 10초 이내

  # === 게임 지표 ===
  - id: avg_session_length
    name: "평균 세션 시간"
    category: game
    source:
      type: database
      query: "SELECT AVG(TIMESTAMPDIFF(MINUTE, login_at, logout_at)) FROM session_log WHERE DATE(login_at) = CURDATE()"
    format: minutes

  # DB 없는 경우 manual 입력
  - id: manual_metric
    name: "수동 입력 지표"
    category: custom
    source:
      type: manual             # Admin Portal에서 직접 입력
    format: number
```

**DB 접근 불가 시 대안**:

| 데이터소스 | 대안 |
|-----------|------|
| Game DB 쿼리 | Firebase Analytics / Amplitude API 연동 |
| 쿼리도 불가 | Google Sheets 연동 (운영자가 수동 입력) |
| 분석 도구도 없음 | CS 기반 지표만 (자동처리율, 문의량, 응답시간) |

### 1-4. 핫픽스 우선순위 기준 (선택)

```yaml
# games/{game_name}/hotfix_priority.yaml
priority_factors:
  - factor: affected_users
    weight: 0.35
    description: "영향 받는 유저 수"
    scoring:
      - range: "1~10"
        score: 1
      - range: "11~100"
        score: 3
      - range: "101~1000"
        score: 7
      - range: "1001+"
        score: 10

  - factor: revenue_impact
    weight: 0.30
    description: "매출 영향도"
    scoring:
      - condition: "결제 불가"
        score: 10
      - condition: "결제 관련 오류"
        score: 7
      - condition: "결제 무관"
        score: 1

  - factor: severity
    weight: 0.20
    description: "버그 심각도"
    scoring:
      - condition: "크래시/데이터 손실"
        score: 10
      - condition: "기능 불가"
        score: 7
      - condition: "기능 저하"
        score: 4
      - condition: "미관/UX"
        score: 1

  - factor: workaround_exists
    weight: 0.15
    description: "우회 방법 존재 여부"
    scoring:
      - condition: "없음"
        score: 10
      - condition: "복잡한 우회"
        score: 5
      - condition: "간단한 우회"
        score: 2

# 최종 점수 = Σ(factor_score × weight)
# 8.0+ → Critical (즉시 핫픽스)
# 5.0~7.9 → High (다음 패치 포함)
# 3.0~4.9 → Medium (백로그)
# 1.0~2.9 → Low (여유 시 수정)
```

---

## 2. 필요 설정 (Configuration)

### 2-1. 공지 생성 프롬프트

```yaml
# module_ops/config/announcement_prompt.yaml
system_prompt: |
  당신은 게임 운영팀의 공지문 작성 AI입니다.

  규칙:
  1. 반드시 아래 형식을 따르세요
  2. 게임 용어 사전의 공식 용어만 사용하세요
  3. 존댓말, 정중한 어조
  4. 보상이 있으면 명확히 기재
  5. 날짜/시간은 한국 시간(KST) 기준

  공지 형식:
  ---
  제목: [카테고리] 제목
  본문:
    인사말
    ■ 핵심 내용 (불릿 포인트)
    ■ 보상 내역 (있는 경우)
    마무리 인사
    서명
  ---

# 카테고리별 추가 지시
category_instructions:
  maintenance:
    extra: "점검 시간, 점검 내용, 보상 내역을 반드시 포함"
  event:
    extra: "이벤트 기간, 참여 방법, 보상 목록을 반드시 포함"
  emergency:
    extra: "문제 상황, 현재 조치, 예상 복구 시간을 포함. 사과 문구 필수"
  compensation:
    extra: "보상 사유, 대상, 보상 내역, 수령 방법을 포함"
```

### 2-2. KPI 리포트 스케줄

```yaml
# module_ops/config/schedule.yaml
schedules:
  daily_kpi:
    cron: "0 10 * * *"        # 매일 오전 10시
    action: generate_kpi_report
    params:
      period: daily
      destination: discord     # discord / email / both

  weekly_kpi:
    cron: "0 10 * * 1"        # 매주 월요일 오전 10시
    action: generate_kpi_report
    params:
      period: weekly
      destination: both

  bug_priority_report:
    cron: "0 9 * * *"         # 매일 오전 9시
    action: generate_hotfix_priority
    params:
      destination: discord
```

---

## 3. Module 구조

```
module_ops/
├── __init__.py
├── main.py                    # 스케줄러 (APScheduler 또는 cron)
├── announcement_gen.py        # 공지문 생성기
├── kpi_reporter.py            # KPI 리포트 생성기
├── hotfix_prioritizer.py      # 핫픽스 우선순위 산출
├── event_manager.py           # 이벤트 일정 관리
├── data/
│   └── report_templates/      # 리포트 Markdown 템플릿
└── config/
    ├── announcement_prompt.yaml
    └── schedule.yaml
```

---

## 4. Phase 3 완료 조건

| # | Deliverable | 측정 기준 |
|---|-------------|-----------|
| 1 | 공지 생성 | 운영자 지시 → 공지문 초안 생성 (2분 이내) |
| 2 | KPI 리포트 | 일일 KPI 리포트가 Discord에 자동 전송 |
| 3 | 핫픽스 우선순위 | Phase 2 버그 클러스터 → 우선순위 정렬 리포트 |
| 4 | 이벤트 알림 | 이벤트 시작/종료 전 자동 알림 |
