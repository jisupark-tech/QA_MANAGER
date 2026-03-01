# Phase 4: 분석 대시보드 (Module 4 - Analytics)

> **Period**: Week 7~9
> **Prerequisite**: Phase 0 완료 + 유저/결제 데이터 접근
> **Output**: 이탈 예측, 매출 분석, 리텐션 추적, 유저 세그멘테이션
> **GameScale 참조**: Marketing 패키지 (이탈 예측 164% 리텐션 향상) + Analytics 패키지

---

## 0. 이 Phase의 목표

GameScale이 증명한 핵심: **이탈 예측만으로 리텐션 164% 향상 가능**.

```
Phase 4 완료 시점:
✅ Churn Predictor: 이탈 위험 유저 식별 + 조기 개입 추천
✅ Revenue Analyzer: 매출 세그먼트 분석 (Whale/Dolphin/Minnow/Free)
✅ Retention Tracker: D1/D7/D30 리텐션 코호트 분석
✅ Trend Analyzer: 주요 지표 트렌드 + 이상 변동 알림
```

---

## 1. 필요 정보 (Data Requirements)

### 1-1. 유저 데이터 (필수)

| # | 데이터 | 테이블/소스 | 필드 | 용도 |
|---|--------|-----------|------|------|
| 1 | **유저 프로필** | `users` | uid, created_at, level, vip_grade, country | 세그멘테이션 |
| 2 | **로그인 이력** | `session_log` | uid, login_at, logout_at, device | 리텐션, 이탈 예측 |
| 3 | **결제 이력** | `payments` | uid, amount, product_id, created_at, status | 매출 분석 |
| 4 | **게임 활동** | `activity_log` | uid, action, timestamp | 행동 패턴 분석 |

**데이터 접근 설정**:

```yaml
# games/{game_name}/analytics_sources.yaml
sources:
  # 방법 1: 직접 DB 연결
  database:
    enabled: true
    # connection → .env

  # 방법 2: Firebase Analytics
  firebase:
    enabled: false
    # project_id: "my-game-project"
    # credentials_path → .env

  # 방법 3: Amplitude
  amplitude:
    enabled: false
    # api_key → .env

  # 방법 4: CSV/수동 입력
  manual:
    enabled: false
    import_directory: "./data/imports/"
    # 운영자가 CSV를 이 폴더에 업로드
```

### 1-2. 이탈 정의 (필수)

이탈(Churn)을 어떻게 정의할지 비즈니스 룰이 필요합니다.

```yaml
# games/{game_name}/churn_config.yaml
churn_definition:
  # 이탈 판정 기준
  inactive_days: 7             # N일 미접속 시 이탈로 판정
  # 장르별 권장값:
  # - 캐주얼: 3~5일
  # - RPG/Idle: 7일
  # - 전략/SLG: 14일

  # 이탈 위험 단계
  risk_levels:
    - level: low
      condition: "마지막 접속 3~4일 전"
      action: "모니터링"

    - level: medium
      condition: "마지막 접속 5~6일 전"
      action: "푸시 알림 또는 이메일 발송 추천"

    - level: high
      condition: "마지막 접속 7일+ 전"
      action: "보상 제공 + 인앱 메시지 추천"

    - level: churned
      condition: "마지막 접속 14일+ 전"
      action: "복귀 캠페인 대상"

  # 이탈 예측 피처 (LLM 분석에 사용)
  prediction_features:
    - name: login_frequency
      description: "최근 7일 접속 횟수"
      high_risk: "< 2회"

    - name: session_duration_trend
      description: "최근 7일 평균 세션 시간 변화"
      high_risk: "전주 대비 50% 이상 감소"

    - name: spending_trend
      description: "최근 30일 결제 패턴"
      high_risk: "정기 결제 유저가 이번 달 미결제"

    - name: content_progress
      description: "콘텐츠 소진율"
      high_risk: "최종 스테이지 도달 + 신규 콘텐츠 없음"

    - name: social_activity
      description: "길드/친구 활동"
      high_risk: "길드 탈퇴 또는 친구 삭제"

    - name: cs_sentiment
      description: "최근 CS 문의 감정"
      high_risk: "부정적 감정 문의 2건 이상"
```

### 1-3. 유저 세그먼트 정의 (필수)

```yaml
# games/{game_name}/segments.yaml
segments:
  # 결제 기반 세그먼트
  spending_segments:
    - name: whale
      label: "고래 (Whale)"
      condition:
        monthly_spend: ">= 100000"    # 월 10만원 이상
      description: "매출의 핵심. VIP 관리 필요"

    - name: dolphin
      label: "돌핀 (Dolphin)"
      condition:
        monthly_spend: ">= 10000"
        monthly_spend_lt: "100000"
      description: "소액 과금 유저. 전환 유도 대상"

    - name: minnow
      label: "미노우 (Minnow)"
      condition:
        monthly_spend: ">= 1000"
        monthly_spend_lt: "10000"
      description: "최소 과금 유저"

    - name: free
      label: "무과금 (Free)"
      condition:
        monthly_spend: "0"
      description: "광고 수익 또는 전환 대상"

  # 활동 기반 세그먼트
  activity_segments:
    - name: hardcore
      condition:
        daily_playtime: ">= 120"      # 분 단위
      description: "코어 유저"

    - name: casual
      condition:
        daily_playtime: "< 30"
      description: "가벼운 플레이어"

    - name: returning
      condition:
        days_since_last_login: ">= 7"
        logged_in_today: true
      description: "복귀 유저 — 특별 관리 대상"

  # 라이프사이클 세그먼트
  lifecycle_segments:
    - name: new
      condition:
        account_age_days: "<= 7"
      description: "신규 유저 — 튜토리얼 이탈 모니터링"

    - name: growing
      condition:
        account_age_days: "8~30"
      description: "성장 유저 — 콘텐츠 소진 모니터링"

    - name: mature
      condition:
        account_age_days: "> 30"
      description: "장기 유저 — 이탈 예방 중요"
```

### 1-4. 리텐션 코호트 설정 (필수)

```yaml
# games/{game_name}/retention_config.yaml
retention:
  # 측정할 리텐션 포인트
  checkpoints:
    - day: 1
      target: 40               # 목표 % (장르별 조정)
      alert_below: 30
    - day: 3
      target: 25
      alert_below: 18
    - day: 7
      target: 15
      alert_below: 10
    - day: 14
      target: 10
      alert_below: 7
    - day: 30
      target: 5
      alert_below: 3

  # 코호트 그룹핑 기준
  cohort_by:
    - install_date              # 가입일 기준 (기본)
    - acquisition_channel       # 유입 채널별 (UA 데이터 있을 때)
    - country                   # 국가별
    - device_type               # 기기별

  # 장르별 리텐션 벤치마크 (참고용)
  # genre_benchmarks:
  #   casual: { d1: 35, d7: 12, d30: 4 }
  #   rpg:    { d1: 40, d7: 18, d30: 8 }
  #   idle:   { d1: 45, d7: 20, d30: 10 }
  #   puzzle: { d1: 38, d7: 15, d30: 6 }
```

---

## 2. 데이터 없는 경우 단계별 대응

| 데이터 수준 | 사용 가능 기능 | 불가능 기능 |
|------------|---------------|------------|
| **Level 0**: 아무것도 없음 | CS 지표만 (Phase 1 데이터) | 이탈 예측, 매출, 리텐션 전부 |
| **Level 1**: 로그인 로그만 | DAU, 리텐션, 세션 분석, 간이 이탈 예측 | 매출 분석, 세그먼트 |
| **Level 2**: 로그인 + 결제 | 위 + 매출 분석, 세그먼트 | 행동 기반 이탈 예측 |
| **Level 3**: 전체 텔레메트리 | 모든 기능 가능 | - |

**최소 시작 조건**: Level 1 (로그인 로그) 이상이면 의미 있는 분석 가능.

---

## 3. 필요 설정 (Configuration)

### 3-1. LLM 기반 이탈 예측 프롬프트

```yaml
# module_analytics/config/churn_prompt.yaml
system_prompt: |
  당신은 게임 유저 이탈 예측 분석가입니다.

  아래 유저 데이터를 분석하여:
  1. 이탈 위험도 (0.0 ~ 1.0)
  2. 주요 이탈 신호 (어떤 행동이 이탈 징후인지)
  3. 추천 개입 방법 (푸시, 보상, VIP 케어 등)
  을 JSON으로 응답하세요.

  응답 형식:
  {
    "user_id": "...",
    "churn_risk": 0.0~1.0,
    "risk_level": "low/medium/high/churned",
    "signals": ["최근 7일 접속 1회", "세션 시간 80% 감소"],
    "recommended_action": "푸시 알림 + 복귀 보상 500 다이아",
    "reasoning": "..."
  }
```

### 3-2. 리포트 전송 설정

```yaml
# module_analytics/config/report_config.yaml
reports:
  churn_alert:
    schedule: daily
    time: "09:00"
    destination:
      - type: discord
        channel_id: "111222333"
      - type: email
        to: "ops@company.com"
    content:
      - high_risk_count
      - whale_at_risk_list       # 고래 유저 중 이탈 위험자 (최우선)
      - recommended_actions

  revenue_report:
    schedule: daily
    time: "10:00"
    destination:
      - type: discord
    content:
      - daily_revenue
      - segment_breakdown
      - paying_rate
      - arpu

  retention_report:
    schedule: weekly
    day: monday
    time: "10:00"
    content:
      - cohort_table
      - benchmark_comparison
      - trend_chart_url          # Streamlit 대시보드 URL
```

---

## 4. Module 구조

```
module_analytics/
├── __init__.py
├── main.py                    # 스케줄러 + API 엔드포인트
├── churn_predictor.py         # 이탈 예측 엔진
├── revenue_analyzer.py        # 매출 분석
├── retention_tracker.py       # 리텐션 코호트 분석
├── segment_manager.py         # 유저 세그멘테이션
├── trend_analyzer.py          # 지표 트렌드 + 이상 변동 탐지
├── data/
│   ├── snapshots/             # 일일 스냅샷 저장
│   └── cache/                 # 분석 결과 캐시
└── config/
    ├── churn_prompt.yaml
    └── report_config.yaml
```

---

## 5. Phase 4 완료 조건

| # | Deliverable | 측정 기준 |
|---|-------------|-----------|
| 1 | 이탈 예측 | High-risk 유저 리스트 일일 생성 |
| 2 | 매출 분석 | 세그먼트별 매출 리포트 자동 생성 |
| 3 | 리텐션 추적 | D1/D7/D30 코호트 테이블 자동 생성 |
| 4 | 이상 변동 알림 | KPI 급변 시 Discord 알림 |

---

## 6. Phase 4 → Phase 5 연결

| 다음 Phase에 필요한 것 | Phase 4에서 제공 |
|-----------------------|-----------------|
| 대시보드 데이터 | 분석 결과 JSON API → Admin Portal에서 시각화 |
| 알림 이력 | 알림 로그 → Admin Portal에서 조회 |
| 세그먼트 데이터 | 유저 세그먼트 → Admin Portal 필터 |
