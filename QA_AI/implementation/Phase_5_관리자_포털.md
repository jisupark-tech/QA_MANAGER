# Phase 5: 관리자 포털 (Module 5 - Admin Portal)

> **Period**: Week 9~10
> **Prerequisite**: Phase 1~4 (모든 모듈 최소 1개 이상 가동)
> **Output**: 웹 대시보드, 권한 관리, 멀티게임 설정, 통합 모니터링
> **GameScale 참조**: Dual Portal (Business + Developer) 구조

---

## 0. 이 Phase의 목표

```
Phase 5 완료 시점:
✅ Operator Dashboard: CS 팀용 — 티켓 큐, 에스컬레이션, 응답 로그
✅ Admin Dashboard: 개발팀용 — 시스템 설정, 규칙 편집, 모듈 상태
✅ Analytics View: 경영진용 — KPI, 리텐션, 매출 시각화
✅ Multi-Game Support: 게임 선택기 → 모든 뷰가 해당 게임으로 필터
✅ Role-Based Access: 역할별 접근 권한 제어
```

---

## 1. 필요 정보 (Data Requirements)

### 1-1. 사용자 역할 정의 (필수)

누가 어떤 화면에 접근할 수 있는지 정의합니다.

```yaml
# admin_config/roles.yaml
roles:
  - id: admin
    name: "관리자"
    description: "전체 시스템 설정 + 모든 기능 접근"
    permissions:
      - dashboard_view
      - cs_view
      - cs_respond            # 수동 CS 응답
      - qa_view
      - ops_view
      - analytics_view
      - settings_edit         # 설정 변경 권한
      - rules_edit            # 에스컬레이션 규칙 편집
      - user_manage           # 포털 사용자 관리

  - id: cs_operator
    name: "CS 담당자"
    description: "CS 티켓 조회 + 에스컬레이션 처리"
    permissions:
      - dashboard_view
      - cs_view
      - cs_respond

  - id: ops_manager
    name: "운영 매니저"
    description: "운영 도구 + 분석 조회"
    permissions:
      - dashboard_view
      - cs_view
      - qa_view
      - ops_view
      - analytics_view

  - id: developer
    name: "개발자"
    description: "QA 모니터 + 설정"
    permissions:
      - dashboard_view
      - qa_view
      - ops_view
      - settings_edit
      - rules_edit

  - id: viewer
    name: "뷰어"
    description: "조회만 가능 (경영진, 외부 관계자)"
    permissions:
      - dashboard_view
      - analytics_view
```

### 1-2. 포털 사용자 목록 (필수)

| # | 항목 | 설명 | 예시 |
|---|------|------|------|
| 1 | 사용자 이름 | 로그인 표시명 | "김운영" |
| 2 | 이메일 | 로그인 ID | "ops@company.com" |
| 3 | 역할 | 위 역할 중 선택 | `cs_operator` |
| 4 | 담당 게임 | 접근 가능 게임 | `["CarMatch", "MyIdleGame"]` 또는 `"all"` |

```yaml
# admin_config/users.yaml
users:
  - email: "admin@company.com"
    name: "관리자"
    role: admin
    games: all

  - email: "cs01@company.com"
    name: "CS 담당자 1"
    role: cs_operator
    games: ["CarMatch"]

  - email: "dev@company.com"
    name: "개발자"
    role: developer
    games: all
```

### 1-3. 대시보드 레이아웃 설정 (선택)

```yaml
# admin_config/dashboard.yaml
dashboard:
  # 메인 대시보드 위젯 배치
  widgets:
    row_1:
      - type: metric_card
        metric: dau
        size: small

      - type: metric_card
        metric: daily_revenue
        size: small

      - type: metric_card
        metric: cs_auto_resolve_rate
        size: small

      - type: metric_card
        metric: active_alerts
        size: small

    row_2:
      - type: chart
        chart_type: line
        metric: dau
        period: 30d            # 최근 30일
        size: large

      - type: chart
        chart_type: pie
        metric: spending_segments
        size: medium

    row_3:
      - type: table
        source: escalation_queue
        columns: [ticket_id, user_id, category, priority, created_at]
        max_rows: 10
        size: large

  # 페이지 구성
  pages:
    - id: overview
      name: "Overview"
      icon: "home"
      roles: [admin, ops_manager, viewer]

    - id: cs_tickets
      name: "CS 티켓"
      icon: "chat"
      roles: [admin, cs_operator, ops_manager]

    - id: escalation
      name: "에스컬레이션"
      icon: "alert"
      roles: [admin, cs_operator, ops_manager]

    - id: qa_monitor
      name: "QA 모니터"
      icon: "shield"
      roles: [admin, developer, ops_manager]

    - id: analytics
      name: "분석"
      icon: "chart"
      roles: [admin, ops_manager, viewer]

    - id: ops_tools
      name: "운영 도구"
      icon: "tools"
      roles: [admin, ops_manager]

    - id: settings
      name: "설정"
      icon: "gear"
      roles: [admin, developer]
```

### 1-4. 멀티게임 설정 (해당 시)

복수 게임을 관리하는 경우, 게임별 설정이 필요합니다.

```yaml
# admin_config/games.yaml
games:
  - id: carmatch
    name: "CarMatch"
    platform: android
    config_path: "games/carmatch/config.yaml"
    status: active             # active / maintenance / archived
    icon: "🚗"

  - id: myidlegame
    name: "MyIdleGame"
    platform: both
    config_path: "games/myidlegame/config.yaml"
    status: active
    icon: "⚔️"

# 전체 게임 공통 설정
global:
  default_game: carmatch       # 로그인 시 기본 선택 게임
  allow_cross_game_view: true  # 여러 게임 동시 조회 허용
```

### 1-5. 브랜딩 (선택)

```yaml
# admin_config/branding.yaml
branding:
  company_name: "My Game Studio"
  logo_path: "static/logo.png"    # 로고 이미지 파일
  primary_color: "#4A90D9"
  dark_mode: true                  # 기본 다크모드
  favicon_path: "static/favicon.ico"
```

---

## 2. 필요 설정 (Configuration)

### 2-1. 인증 방식 선택

| 방식 | 복잡도 | 권장 상황 |
|------|--------|----------|
| **Simple Password** | 낮음 | MVP / 내부 전용 (3~5명) |
| **OAuth (Google)** | 중간 | 회사 Google Workspace 사용 시 |
| **SSO (SAML)** | 높음 | 대기업, 기존 SSO 시스템 있을 때 |

```yaml
# admin_config/auth.yaml
auth:
  method: simple_password      # simple_password / google_oauth / saml

  # simple_password 설정
  simple_password:
    session_timeout: 3600      # 초 (1시간)
    max_attempts: 5
    lockout_minutes: 15

  # google_oauth 설정 (선택)
  # google_oauth:
  #   client_id → .env
  #   client_secret → .env
  #   allowed_domain: "company.com"  # 이 도메인만 허용
```

### 2-2. Admin Portal 기술 선택

| 옵션 | 장점 | 단점 | 권장 |
|------|------|------|------|
| **Streamlit** | Python만으로 빌드, 빠른 개발 | 커스텀 UI 한계, 동시접속 제한 | MVP (1~5명) |
| **FastAPI + React** | 완전한 커스텀 UI, 확장성 | 프론트엔드 개발 필요 | Production (5명+) |
| **Gradio** | ML 대시보드에 특화, 간단 | 복잡한 레이아웃 어려움 | 분석 전용 뷰 |

```yaml
# admin_config/portal.yaml
portal:
  framework: streamlit         # streamlit / fastapi_react
  host: "0.0.0.0"
  port: 8080

  # Streamlit 설정
  streamlit:
    theme: dark
    page_title: "GameOps AI"
    layout: wide

  # FastAPI + React 설정 (나중에)
  # fastapi_react:
  #   api_port: 8000
  #   frontend_port: 3000
```

---

## 3. Module 구조

```
module_admin/
├── __init__.py
├── app.py                     # Streamlit 메인 앱 (또는 FastAPI)
├── pages/                     # Streamlit 페이지
│   ├── 01_Overview.py         # 메인 대시보드
│   ├── 02_CS_Tickets.py       # CS 티켓 관리
│   ├── 03_Escalation.py       # 에스컬레이션 큐
│   ├── 04_QA_Monitor.py       # QA 알림/이력
│   ├── 05_Analytics.py        # 분석 대시보드
│   ├── 06_Ops_Tools.py        # 운영 도구 (공지 생성 등)
│   └── 07_Settings.py         # 시스템 설정
├── auth/
│   ├── authenticator.py       # 로그인/세션 관리
│   └── role_checker.py        # 권한 검사
├── api/
│   └── module_client.py       # 다른 모듈 API 호출
├── static/                    # 로고, 아이콘 등
└── config/
    ├── roles.yaml
    ├── users.yaml
    ├── dashboard.yaml
    └── auth.yaml
```

---

## 4. Phase 5 완료 조건

| # | Deliverable | 측정 기준 |
|---|-------------|-----------|
| 1 | 로그인 | 이메일 + 비밀번호로 로그인 성공 |
| 2 | 역할 기반 접근 | cs_operator는 설정 페이지 접근 불가 확인 |
| 3 | CS 티켓 뷰 | 에스컬레이션 큐에서 티켓 조회 + 수동 응답 가능 |
| 4 | QA 알림 뷰 | Phase 2 알림 이력 조회 가능 |
| 5 | 분석 대시보드 | KPI, 리텐션 차트 표시 |
| 6 | 설정 편집 | 에스컬레이션 규칙 YAML 수정 + 저장 |
| 7 | 멀티게임 | 게임 선택기로 전환 시 데이터 필터 작동 |

---

## 5. 전체 시스템 통합 검증

Phase 5 완료 = 전체 시스템 완성. 아래 E2E 시나리오를 검증합니다.

| # | 시나리오 | 경로 |
|---|---------|------|
| 1 | 유저가 Discord에 결제 문의 | Gateway → Classifier → Payment Agent → 자동 응답 → 로그 기록 → Admin에서 조회 |
| 2 | 비정상 골드 획득 탐지 | Telemetry → Anomaly Detector → Alert → Discord #ops-alert → Admin QA 뷰 |
| 3 | 버그 5건 클러스터 | CS 버그 티켓 5건 → Clusterer → 리포트 → Hotfix Prioritizer → Admin 운영 도구 |
| 4 | 일일 KPI 리포트 | 매일 10시 → KPI Reporter → Discord + Admin Analytics |
| 5 | 고래 유저 이탈 위험 | Churn Predictor → High-risk whale → Alert → CS 팀 VIP 케어 |
| 6 | 긴급 점검 공지 | 운영자 → Admin 운영 도구 → "긴급 점검" 입력 → AI 공지문 생성 → 검수 → Discord 게시 |
