# Phase 0: 프로젝트 기반 (Project Foundation)

> **Period**: Week 0~1
> **Prerequisite**: None
> **Output**: 프로젝트 스켈레톤, 공통 인프라, 게임 설정 완료

---

## 0. 이 Phase의 목표

Phase 0은 전체 시스템의 기반을 세우는 단계입니다.
여기서 수집하고 설정한 정보가 Phase 1~5 전체에 걸쳐 사용됩니다.

```
Phase 0 완료 시점:
✅ 프로젝트 디렉토리 구조 생성
✅ 공통 인프라 (LLM, DB, Queue) 연결 확인
✅ 대상 게임 설정 파일 작성
✅ 개발 환경 구동 확인 (docker-compose up)
```

---

## 1. 필요 정보 (Data Requirements)

### 1-1. 프로젝트 기본 정보

| # | 항목 | 설명 | 예시 | 필수 |
|---|------|------|------|------|
| 1 | 프로젝트명 | QA Manager 프로젝트 이름 | `GameOps-AI` | YES |
| 2 | 대상 게임 목록 | 관리할 게임 이름 + 플랫폼 | `CarMatch (Android)`, `MyIdleGame (iOS/Android)` | YES |
| 3 | 팀 구성 | CS/운영/개발 인원 수 | `CS 2명, 개발 1명, 운영 1명` | YES |
| 4 | 현재 CS 처리량 | 일일/주간 평균 문의 건수 | `일 50건`, `주 300건` | YES |
| 5 | CS 문의 유형 비율 | 어떤 문의가 가장 많은지 | `FAQ 40%, 결제 25%, 버그 20%, 기타 15%` | OPTIONAL |

### 1-2. 인프라 정보

| # | 항목 | 설명 | 선택지 | 필수 |
|---|------|------|--------|------|
| 6 | 배포 환경 | 시스템을 어디서 운영할지 | `local` / `aws` / `gcp` / `company_server` | YES |
| 7 | 게임 DB 종류 | 게임 서버의 데이터베이스 | `mysql` / `postgresql` / `mongodb` / `none` | YES |
| 8 | 게임 DB 접근 방법 | 어떻게 데이터를 읽을지 | `direct_connection` / `rest_api` / `csv_export` / `no_access` | YES |
| 9 | 기존 분석 도구 | 이미 사용 중인 분석 서비스 | `firebase` / `amplitude` / `mixpanel` / `none` | OPTIONAL |
| 10 | 기존 CS 도구 | 현재 CS에 사용하는 도구 | `zendesk` / `freshdesk` / `spreadsheet` / `discord_only` | OPTIONAL |

### 1-3. API 키 및 인증 정보

| # | 항목 | 용도 | 발급처 | 필수 |
|---|------|------|--------|------|
| 11 | Claude API Key | LLM 엔진 | [console.anthropic.com](https://console.anthropic.com) | YES |
| 12 | Discord Bot Token | CS 채널 (Discord 선택 시) | [discord.com/developers](https://discord.com/developers) | CONDITIONAL |
| 13 | KakaoTalk Channel Key | CS 채널 (카카오톡 선택 시) | [developers.kakao.com](https://developers.kakao.com) | CONDITIONAL |
| 14 | Game DB 접속 정보 | 유저/결제 데이터 조회 | 게임 서버 관리자 | CONDITIONAL |

> **보안 주의**: API 키는 절대 Git에 커밋하지 마세요. `.env` 파일에 넣고 `.gitignore`에 추가.

---

## 2. 필요 설정 (Configuration)

### 2-1. 게임 설정 파일 작성

각 게임마다 `game_config.yaml`을 작성합니다.
→ 템플릿: [`templates/game_config.yaml`](templates/game_config.yaml)

```yaml
# games/{game_name}/config.yaml
game:
  name: "MyGame"
  platform: android          # android / ios / both / web
  genre: idle                # rpg / idle / merge / puzzle / casual / slg / etc
  language: ko               # 기본 언어
  supported_languages:       # 지원 언어 목록
    - ko
    - en

database:
  type: mysql                # mysql / postgresql / mongodb / none
  host: "db.example.com"
  port: 3306
  name: "game_db"
  read_only: true            # 반드시 true (안전)
  # credentials → .env 파일에서 관리

channels:
  primary: discord           # 메인 CS 채널
  secondary: []              # 추가 채널
  discord:
    guild_id: "123456789"
    cs_channel_id: "987654321"
    alert_channel_id: "111222333"  # QA Monitor 알림용

currencies:
  - name: "골드"
    code: "gold"
    type: soft               # soft / hard / premium
  - name: "다이아"
    code: "diamond"
    type: hard
```

### 2-2. 환경변수 설정

→ 템플릿: [`templates/env_template.env`](templates/env_template.env)

```env
# .env (Git에 절대 커밋하지 마세요)

# LLM
ANTHROPIC_API_KEY=sk-ant-xxxxx
LLM_MODEL=claude-sonnet-4-6
LLM_MAX_TOKENS=4096

# Vector DB
CHROMA_PERSIST_DIR=./data/chroma

# Game DB (게임별로 접두사 구분)
MYGAME_DB_HOST=localhost
MYGAME_DB_PORT=3306
MYGAME_DB_USER=readonly_user
MYGAME_DB_PASS=xxxxx
MYGAME_DB_NAME=game_db

# Discord
DISCORD_BOT_TOKEN=xxxxx

# Redis (모듈 간 통신)
REDIS_URL=redis://localhost:6379
```

### 2-3. 프로젝트 디렉토리 구조

Phase 0에서 생성할 전체 프로젝트 스켈레톤:

```
qa_manager/
├── .env                         # 환경변수 (gitignore)
├── .env.example                 # 환경변수 예시 (커밋 OK)
├── .gitignore
├── docker-compose.yml           # 전체 서비스 구동
├── requirements.txt             # Python 의존성
├── shared/                      # 공통 모듈
│   ├── __init__.py
│   ├── config.py                # 게임 설정 로더
│   ├── llm_client.py            # Claude API 래퍼
│   ├── db_connector.py          # Game DB 커넥터
│   ├── vector_store.py          # ChromaDB 래퍼
│   └── event_bus.py             # Redis Pub/Sub 래퍼
├── module_cs/                   # Phase 1
├── module_qa/                   # Phase 2
├── module_ops/                  # Phase 3
├── module_analytics/            # Phase 4
├── module_admin/                # Phase 5
├── games/                       # 게임별 설정
│   └── {game_name}/
│       ├── config.yaml
│       ├── faq/                 # FAQ 문서
│       ├── policies/            # 정책 문서
│       └── escalation_rules.yaml
├── data/                        # 런타임 데이터 (gitignore)
│   ├── chroma/                  # Vector DB 저장소
│   ├── logs/                    # 시스템 로그
│   └── tickets/                 # 처리된 티켓 이력
└── tests/                       # 테스트 코드
```

---

## 3. 설치 및 검증 (Setup Verification)

### 3-1. Python 환경

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install anthropic      # Claude API
pip install chromadb       # Vector DB
pip install fastapi        # Web framework
pip install uvicorn        # ASGI server
pip install redis          # Module communication
pip install discord.py     # Discord bot
pip install pyyaml         # Config loader
pip install python-dotenv  # .env loader
```

`requirements.txt`:
```
anthropic>=0.40.0
chromadb>=0.5.0
fastapi>=0.115.0
uvicorn>=0.32.0
redis>=5.0.0
discord.py>=2.4.0
pyyaml>=6.0
python-dotenv>=1.0.0
httpx>=0.27.0
```

### 3-2. Docker Compose (선택)

```yaml
# docker-compose.yml
version: "3.8"
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  chroma:
    image: chromadb/chroma:latest
    ports: ["8000:8000"]
    volumes:
      - ./data/chroma:/chroma/chroma

  cs-bot:
    build: ./module_cs
    env_file: .env
    depends_on: [redis, chroma]

  qa-monitor:
    build: ./module_qa
    env_file: .env
    depends_on: [redis]

  ops-auto:
    build: ./module_ops
    env_file: .env
    depends_on: [redis]

  analytics:
    build: ./module_analytics
    env_file: .env
    depends_on: [redis]

  admin:
    build: ./module_admin
    ports: ["8080:8080"]
    env_file: .env
    depends_on: [redis, cs-bot, qa-monitor, ops-auto, analytics]
```

### 3-3. 검증 체크리스트

| # | 검증 항목 | 명령어 | 기대 결과 |
|---|----------|--------|-----------|
| 1 | Python 버전 | `python --version` | 3.11+ |
| 2 | Claude API 연결 | `python -c "import anthropic; c=anthropic.Anthropic(); print(c.messages.create(model='claude-sonnet-4-6',max_tokens=10,messages=[{'role':'user','content':'ping'}]).content[0].text)"` | 응답 텍스트 출력 |
| 3 | ChromaDB 작동 | `python -c "import chromadb; c=chromadb.Client(); print(c.heartbeat())"` | timestamp 출력 |
| 4 | Redis 연결 (Docker 시) | `redis-cli ping` | `PONG` |
| 5 | Game config 로드 | `python -c "import yaml; print(yaml.safe_load(open('games/mygame/config.yaml')))"` | config dict 출력 |
| 6 | .env 로드 | `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:10])"` | API 키 앞 10자 |

---

## 4. Phase 0 완료 조건

| # | Deliverable | 확인 방법 |
|---|-------------|-----------|
| 1 | 프로젝트 디렉토리 생성 완료 | `ls qa_manager/` 에서 전체 구조 확인 |
| 2 | `.env` 파일에 API 키 설정 | Claude API 호출 성공 |
| 3 | 1개 이상 게임 config 작성 | `games/{name}/config.yaml` 존재 |
| 4 | `shared/` 공통 모듈 작동 | `llm_client.py` 테스트 통과 |
| 5 | Docker 또는 로컬 환경 구동 | 서비스 시작 확인 |

---

## 5. Phase 0 → Phase 1 연결

Phase 0이 완료되면 다음 데이터를 준비하여 Phase 1로 진행:

| 다음 Phase에 필요한 것 | Phase 0에서 준비 | 비고 |
|-----------------------|-----------------|------|
| FAQ 문서 | `games/{name}/faq/` 폴더에 작성 시작 | Phase 1에서 상세 |
| 정책 문서 | `games/{name}/policies/` 폴더에 작성 시작 | Phase 1에서 상세 |
| 에스컬레이션 규칙 | `games/{name}/escalation_rules.yaml` 작성 | Phase 1에서 상세 |
| CS 채널 선택 및 봇 생성 | Discord Bot 또는 KakaoTalk 채널 생성 | API 키를 .env에 추가 |
