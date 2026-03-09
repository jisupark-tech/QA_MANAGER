# QA Manager AI - Implementation Guide

> **Version**: 1.1
> **Last Updated**: 2026-03-09
> **Status**: Planning

---

## Overview

게임 QA 관리 AI 시스템 구현 가이드.
GameScale(넥슨) 아키텍처에서 추출한 핵심 원칙을 소규모 팀(1~2 개발자)에 맞게 적용.

> CS Bot(Module 1) 관련 내용은 [CS_Manager](https://github.com/jisupark-tech/CS_Manager) 레포로 분리되었습니다.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       QA Manager AI                              │
│                    (Game-Agnostic Platform)                       │
├───────────┬───────────┬───────────┬─────────────────────────────┤
│ Module 2  │ Module 3  │ Module 4  │    Module 5                 │
│ QA Monitor│ Ops Auto  │ Analytics │  Admin Portal               │
│           │           │           │                             │
│ Anomaly   │ Announce  │ KPI       │  Config UI                  │
│ Bug Group │ Event     │ Churn     │  Escalation Q               │
│ Cheat Det │ Balance   │ Segment   │  Logs/History               │
│ Alert     │ Report    │ Trend     │  Multi-Game                 │
├───────────┴───────────┴───────────┴─────────────────────────────┤
│                      Shared Infrastructure                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐ │
│  │ Vector DB│ │ Game DB  │ │ LLM API  │ │ Event Bus (Queue)  │ │
│  │ (FAQ/Doc)│ │(User/Pay)│ │ (Claude) │ │ (Module ↔ Module)  │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘

CS Bot (Module 1) → https://github.com/jisupark-tech/CS_Manager
```

## Phase Overview

| Phase | Module | Period | Prerequisite |
|-------|--------|--------|-------------|
| **Phase 0** | Project Foundation | Week 0~1 | None |
| **Phase 2** | QA Monitor | Week 3~5 | Phase 0 + game telemetry |
| **Phase 3** | Ops Automation | Week 5~7 | Phase 0 |
| **Phase 4** | Analytics Dashboard | Week 7~9 | Phase 0 + user data |
| **Phase 5** | Admin Portal | Week 9~10 | Phase 2~4 |

> Phase 1 (CS Bot)은 [CS_Manager](https://github.com/jisupark-tech/CS_Manager) 레포에서 관리합니다.

## Documents

| Document | Description |
|----------|-------------|
| [Phase_0_프로젝트_기반.md](Phase_0_프로젝트_기반.md) | 프로젝트 세팅, 인프라, 공통 설정 |
| [Phase_2_QA_모니터.md](Phase_2_QA_모니터.md) | 이상 탐지, 버그 클러스터링, 치트 감지 |
| [Phase_3_운영_자동화.md](Phase_3_운영_자동화.md) | 공지 생성, KPI 리포트, 핫픽스 우선순위 |
| [Phase_4_분석_대시보드.md](Phase_4_분석_대시보드.md) | 이탈 예측, 매출 분석, 리텐션 추적 |
| [Phase_5_관리자_포털.md](Phase_5_관리자_포털.md) | 웹 대시보드, 권한 관리, 멀티게임 설정 |

## Templates

| Template | Usage |
|----------|-------|
| [game_config.yaml](templates/game_config.yaml) | 게임별 기본 설정 (Phase 0) |
| [telemetry_schema.yaml](templates/telemetry_schema.yaml) | 게임 텔레메트리 스키마 정의 (Phase 2) |
| [kpi_definitions.yaml](templates/kpi_definitions.yaml) | KPI 정의 및 데이터소스 매핑 (Phase 3~4) |
| [env_template.env](templates/env_template.env) | 환경변수 템플릿 (API 키, DB 접속) |

## Tech Stack

| Component | Technology | Note |
|-----------|-----------|------|
| LLM | Claude API (Sonnet 4.6) | Primary AI engine |
| Vector DB | ChromaDB (self-hosted) | FAQ/document search |
| Backend | Python 3.11+ / FastAPI | API server |
| Queue | Redis Pub/Sub | Module communication |
| Admin UI | Streamlit (MVP) → React (Production) | Web dashboard |
| Deployment | Docker Compose | 4 modules + infra |

## Related Repos

| Repo | Description |
|------|-------------|
| [CS_Manager](https://github.com/jisupark-tech/CS_Manager) | CS Bot (Module 1) — FAQ 자동응답, 에스컬레이션 |
| [AI_Company](https://github.com/jisupark-tech/AI_Company) | AI Company 전체 — 12개 역할 페르소나 집합체 |

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/jisupark-tech/QA_MANAGER.git
cd QA_MANAGER

# 2. Fill in templates
cp QA_AI/implementation/templates/env_template.env .env
# Edit .env with your API keys

# 3. Fill game config
cp QA_AI/implementation/templates/game_config.yaml games/my_game/config.yaml
# Edit with your game info

# 4. Follow Phase 0 → Phase 2 → ... sequentially
```
