# Phase 2: QA Monitor (Module 2)

> **Period**: Week 3~5
> **Prerequisite**: Phase 0 완료 + 게임 텔레메트리 접근
> **Output**: 이상 탐지, 버그 클러스터링, 치트 감지 시스템
> **GameScale 참조**: Security 패키지 + Analytics 패키지

---

## 0. 이 Phase의 목표

GameScale의 핵심 가치: **문제가 CS 티켓이 되기 전에 먼저 탐지**.

```
Phase 2 완료 시점:
✅ Anomaly Detector: 게임 경제/진행도 이상 패턴 탐지
✅ Bug Clusterer: CS 티켓 + 커뮤니티 버그 리포트 자동 그룹핑
✅ Cheat Detector: 봇/치트 의심 행동 패턴 탐지
✅ Alerter: 탐지 결과를 운영 채널에 실시간 알림
```

---

## 1. 필요 정보 (Data Requirements)

### 1-1. 게임 텔레메트리 스키마 (필수)

게임이 기록하는 데이터의 구조를 정의해야 합니다.
→ 템플릿: [`templates/telemetry_schema.yaml`](templates/telemetry_schema.yaml)

```yaml
# games/{game_name}/telemetry_schema.yaml

# 텔레메트리 접근 방식
access:
  method: database             # database / api / csv_dump / log_file
  # database 설정 (method: database 일 때)
  database:
    type: mysql
    # connection info → .env
    refresh_interval: 300      # 몇 초마다 조회 (기본 5분)
  # csv_dump 설정 (method: csv_dump 일 때)
  csv_dump:
    directory: "/data/exports/"
    filename_pattern: "telemetry_{date}.csv"
    schedule: daily            # daily / hourly
  # api 설정 (method: api 일 때)
  api:
    base_url: "https://api.mygame.com/analytics"
    auth_header: "X-API-Key"
    # api key → .env

# 유저 활동 데이터 (이상 탐지 핵심)
user_activity:
  table: "user_activity_log"   # 테이블명 또는 API 엔드포인트
  fields:
    user_id: "uid"
    timestamp: "created_at"
    action_type: "action"      # login / stage_clear / purchase / item_use / chat
    detail: "detail_json"      # 액션별 상세 데이터 (JSON)
  # 어떤 action_type 값들이 있는지
  action_types:
    - login
    - logout
    - stage_clear
    - stage_fail
    - purchase
    - item_acquire
    - item_use
    - currency_earn
    - currency_spend
    - pvp_match
    - chat_message

# 경제 데이터 (경제 이상 탐지)
economy:
  currency_log_table: "currency_log"
  fields:
    user_id: "uid"
    currency_type: "currency"  # gold / diamond / etc
    amount: "amount"           # 양수=획득, 음수=소비
    source: "source"           # stage_reward / shop / quest / admin
    balance_after: "balance"
    timestamp: "created_at"

# 진행도 데이터 (비정상 진행 탐지)
progression:
  table: "user_progression"
  fields:
    user_id: "uid"
    level: "level"
    stage: "current_stage"
    play_time_minutes: "total_playtime"
    updated_at: "updated_at"
```

### 1-2. 정상 범위 기준선 (선택 — 없으면 AI가 학습)

| # | 지표 | 정상 범위 예시 | 이상 판단 기준 |
|---|------|---------------|---------------|
| 1 | 시간당 골드 획득량 | 3,000 ~ 8,000 | > 30,000 (봇 의심) |
| 2 | 일일 스테이지 클리어 수 | 5 ~ 30 | > 100 (자동 플레이 의심) |
| 3 | 스테이지 클리어 시간 | 30초 ~ 5분 | < 3초 (치트 의심) |
| 4 | 일일 접속 시간 | 10분 ~ 3시간 | > 20시간 (봇 의심) |
| 5 | 첫 결제까지 시간 | Day 1 ~ Day 7 | < 1분 (사기 의심) |

```yaml
# games/{game_name}/baselines.yaml (선택)
baselines:
  gold_per_hour:
    normal_min: 3000
    normal_max: 8000
    alert_threshold: 30000     # 이 이상이면 알림

  stage_clear_per_day:
    normal_min: 5
    normal_max: 30
    alert_threshold: 100

  stage_clear_time_seconds:
    normal_min: 30
    normal_max: 300
    alert_threshold_low: 3     # 이 이하면 알림 (너무 빠름)

  daily_play_minutes:
    normal_min: 10
    normal_max: 180
    alert_threshold: 1200      # 20시간

  # 기준선이 없으면 시스템이 7일간 데이터로 자동 산출
  auto_baseline:
    enabled: true
    warmup_days: 7             # 데이터 수집 기간
    method: "percentile_95"    # 95 퍼센타일을 이상 기준으로
```

### 1-3. 버그 리포트 소스 (필수 — 최소 1개)

| # | 소스 | 접근 방법 | 설정 |
|---|------|----------|------|
| 1 | CS 티켓 (Phase 1) | 내부 이벤트 버스 | `module_cs` → Redis → `module_qa` |
| 2 | Discord #bug 채널 | Discord Bot이 해당 채널 감시 | `bug_report_channel_id` 설정 |
| 3 | Google Play 리뷰 | Google Play Developer API | API 키 필요 |
| 4 | App Store 리뷰 | App Store Connect API | API 키 필요 |
| 5 | 커뮤니티 (Cafe/Reddit) | 웹 스크래핑 또는 API | URL + 크롤링 간격 |

```yaml
# games/{game_name}/config.yaml 에 추가
bug_sources:
  - type: cs_tickets           # Phase 1 티켓 중 category=bug
    enabled: true

  - type: discord_channel
    enabled: true
    channel_id: "444555666"    # #bug-report 채널

  - type: google_play
    enabled: false             # 필요 시 활성화
    # package_name: "com.example.mygame"
    # API key → .env

  - type: app_store
    enabled: false
```

### 1-4. 알림 설정 (필수)

탐지된 이상을 어디로 보낼지 설정.

```yaml
# games/{game_name}/config.yaml 에 추가
alerts:
  channels:
    - type: discord
      channel_id: "111222333"  # #ops-alert 채널
      mention_role: "ops-team" # @ops-team 멘션

    - type: email              # 선택
      recipients:
        - "ops@company.com"

  # 알림 레벨별 동작
  levels:
    info:                      # 참고 수준
      notify: true
      mention: false
    warning:                   # 주의 필요
      notify: true
      mention: true
    critical:                  # 즉시 대응
      notify: true
      mention: true
      repeat_interval: 30      # 30분마다 반복 알림 (해결될 때까지)
```

### 1-5. 치트 패턴 정의 (선택)

알려진 치트/어뷰즈 패턴이 있으면 미리 등록합니다.

```yaml
# games/{game_name}/cheat_patterns.yaml
patterns:
  - id: cheat_001
    name: "자동 클리커 봇"
    detection:
      type: tap_pattern
      condition: "일정한 간격 (±50ms) 으로 1000회 이상 탭"
    severity: high

  - id: cheat_002
    name: "속도 핵"
    detection:
      type: clear_speed
      condition: "스테이지 클리어 시간 < 물리적 최소 시간의 50%"
    severity: critical

  - id: cheat_003
    name: "결제 사기"
    detection:
      type: payment_pattern
      condition: "동일 영수증 ID 중복 사용 또는 환불 후 아이템 보유"
    severity: critical

  - id: cheat_004
    name: "멀티 계정 어뷰즈"
    detection:
      type: account_link
      condition: "동일 기기에서 5개 이상 계정 생성"
    severity: medium
```

---

## 2. 필요 설정 (Configuration)

### 2-1. Anomaly Detection 설정

```yaml
# module_qa/config/anomaly_config.yaml
anomaly_detection:
  # 분석 주기
  schedule:
    realtime: false            # 실시간 스트림 분석 (리소스 많이 소모)
    interval_minutes: 5        # 배치 분석 주기
    daily_report: true         # 일일 종합 리포트

  # 분석 대상 지표
  metrics:
    - name: currency_earn_rate
      query: "SELECT uid, SUM(amount) as total FROM currency_log WHERE amount > 0 AND created_at > NOW() - INTERVAL 1 HOUR GROUP BY uid"
      threshold_type: percentile  # percentile / absolute / zscore
      threshold_value: 99         # 상위 1%를 이상으로 판단
      alert_level: warning

    - name: stage_clear_speed
      query: "SELECT uid, stage, clear_time FROM stage_log WHERE created_at > NOW() - INTERVAL 1 HOUR"
      threshold_type: absolute
      threshold_value: 3          # 3초 미만 클리어
      alert_level: critical

    - name: login_duration
      query: "SELECT uid, TIMESTAMPDIFF(MINUTE, login_at, logout_at) as duration FROM session_log WHERE login_at > NOW() - INTERVAL 1 DAY"
      threshold_type: percentile
      threshold_value: 99
      alert_level: info

  # LLM 분석 (쿼리로 잡기 어려운 복합 패턴)
  llm_analysis:
    enabled: true
    prompt: |
      아래는 지난 1시간 동안의 게임 활동 통계입니다.
      비정상적인 패턴이 있는지 분석하세요.

      분석 기준:
      1. 경제 이상: 비정상적인 재화 획득/소비
      2. 진행도 이상: 비현실적인 스테이지 클리어 속도
      3. 행동 패턴: 봇과 유사한 반복 행동
      4. 결제 이상: 비정상적인 결제 패턴

      응답 형식 (JSON):
      {"anomalies": [{"type": "...", "severity": "...", "user_ids": [...], "description": "..."}]}
```

### 2-2. Bug Clusterer 설정

```yaml
# module_qa/config/cluster_config.yaml
bug_clustering:
  # 유사도 기준
  similarity_threshold: 0.75   # 이 이상이면 같은 클러스터
  min_cluster_size: 3          # 최소 3건 이상이어야 클러스터로 인정

  # LLM 기반 클러스터링 프롬프트
  cluster_prompt: |
    아래는 최근 접수된 버그 리포트 목록입니다.
    유사한 버그끼리 그룹핑하고, 각 그룹에 대해:
    1. 버그 요약 (한 줄)
    2. 영향 범위 (어떤 유저/기기/스테이지에서 발생)
    3. 심각도 (critical / high / medium / low)
    4. 재현 조건 추정
    을 정리하세요.

  # 리포트 생성 주기
  report_schedule: daily       # daily / on_threshold
  report_threshold: 5          # on_threshold 시: 같은 버그 5건 이상 접수 시 즉시 리포트
```

---

## 3. 텔레메트리 없는 경우 (Fallback)

게임 DB나 텔레메트리 접근이 불가능한 경우에도 Phase 2를 부분 운영할 수 있습니다.

| 기능 | DB 있을 때 | DB 없을 때 (Fallback) |
|------|-----------|----------------------|
| Anomaly Detection | DB 쿼리 → 통계 분석 | CS 티켓 패턴 분석만 (예: "골드 버그" 문의 급증 탐지) |
| Bug Clustering | CS + 커뮤니티 + 텔레메트리 | CS + 커뮤니티만 |
| Cheat Detection | 행동 로그 분석 | CS 신고 기반만 |
| Economy Health | 재화 로그 통계 | 불가 |

```yaml
# DB 없는 경우 config
telemetry:
  access:
    method: none               # DB 없음
  fallback:
    cs_ticket_analysis: true   # CS 티켓 키워드/패턴 분석으로 대체
    community_monitoring: true # 커뮤니티 모니터링으로 대체
```

---

## 4. Module 구조

```
module_qa/
├── __init__.py
├── main.py                    # 스케줄러 + 이벤트 리스너
├── anomaly_detector.py        # 이상 탐지 엔진
├── bug_clusterer.py           # 버그 리포트 클러스터링
├── cheat_detector.py          # 치트/봇 패턴 감지
├── economy_monitor.py         # 게임 경제 건강도 체크
├── alerter.py                 # 알림 발송 (Discord, Email)
├── data_collector.py          # 텔레메트리 수집 (DB/API/CSV)
└── config/
    ├── anomaly_config.yaml
    └── cluster_config.yaml
```

---

## 5. Phase 2 완료 조건

| # | Deliverable | 측정 기준 |
|---|-------------|-----------|
| 1 | Anomaly Detection 작동 | 테스트 이상 데이터 주입 → 알림 발생 |
| 2 | Bug Clustering 작동 | 유사 버그 5건 → 1개 클러스터로 그룹핑 |
| 3 | Alert 전송 | Discord #ops-alert에 알림 메시지 도착 |
| 4 | Daily Report | 일일 종합 이상 리포트 자동 생성 |

---

## 6. Phase 2 → Phase 3 연결

| 다음 Phase에 필요한 것 | Phase 2에서 발생하는 데이터 |
|-----------------------|--------------------------|
| 버그 클러스터 리포트 | → Phase 3 핫픽스 우선순위 입력 |
| 경제 건강도 데이터 | → Phase 3 밸런스 리포트 입력 |
| 이상 탐지 이력 | → Phase 4 트렌드 분석 입력 |
