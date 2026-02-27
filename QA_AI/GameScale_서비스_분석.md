# GameScale (developers.gamescale.io) 분석

> **분석일**: 2026-02-27
> **대상**: https://developers.gamescale.io/ko/services

## 한 줄 요약
> **넥슨 인텔리전스랩스(~700명)가 만든 AI 기반 게임 서비스 솔루션 플랫폼.** 50+ 게임에 적용 중.

---

## 1. 플랫폼 구조

| 사이트 | 역할 |
|--------|------|
| gamescale.io | 비즈니스 소개 (퍼블리셔/파트너 대상) |
| developers.gamescale.io | 개발자 포털 (API 문서, 연동 가이드) |

> 두 사이트 모두 SPA(React/Next 계열)로 구축되어 서버 사이드 렌더링 없이 JS로 콘텐츠를 로드.

---

## 2. 서비스 규모

**7개 패키지, 73개 제품**으로 구성

### 7개 패키지 카테고리

| # | 패키지 | 주요 기능 |
|---|--------|-----------|
| 1 | **보안 (Security)** | 핵/치트 탐지, 봇 감지, 비인가 프로그램 차단. 던파모바일 출시 3시간 만에 어뷰저 탐지한 사례 |
| 2 | **마케팅 (Marketing)** | 게임 내 개인화 광고, 타겟 푸시, 이탈 예측 기반 재접속 유도 (리텐션 164% 향상) |
| 3 | **커뮤니티 (Community)** | 소셜/커뮤니티 관리 도구 |
| 4 | **데이터/분석 (Analytics)** | 정량+정성 데이터 분석, UX 분석, 아이템 시세 이상 탐지, 결제 구간 분석 |
| 5 | **플랫폼 (Platform)** | 인증, 결제, 쿠폰, 인게임 스토어 관리 |
| 6 | **QA/운영 (Operation)** | 게임 운영 자동화, 라이브 서비스 지원 |
| 7 | **AI/매칭 (AI & Matching)** | AI 매칭 알고리즘(유저 선호도/플레이스타일 기반), 추천 시스템, LLM 기반 NPC |

---

## 3. 핵심 AI 기능 상세

| 기능 | 설명 |
|------|------|
| **개인화 매칭** | 유저 선호도+플레이스타일 기반 매칭 (기존 스킬 기반 대체) |
| **이탈 예측** | 이탈 가능성 높은 유저 40% 선별 → 재접속 유도 (카트라이더 러쉬플러스 사례) |
| **개인화 광고** | 게임 내 맞춤 광고 → 리텐션 164%+ 향상 |
| **이상 탐지** | 아이템 시세 이상, 경제 불균형 자동 감지 |
| **결제 분석** | 최초 결제 구간, 다수 결제 구간 분석 → 맞춤 운영 방안 제시 |
| **LLM NPC** | 생성형 AI 기반 인게임 NPC (V4Romance, Hack 등 적용) |
| **핵/봇 탐지** | 실시간 비인가 프로그램 + 봇 탐지 |

---

## 4. 개발자 포털 (developers.gamescale.io)

- 서비스 번호로 구분된 API 문서 구조 (`/ko/services/5`, `/ko/services/9` 등)
- 각 서비스별 API 스펙, 연동 가이드, 개발 프로세스 문서 제공

---

## 5. 실적 및 규모

| 지표 | 수치 |
|------|------|
| 적용 게임 수 | 50+ |
| 조직 규모 | ~700명 (인텔리전스랩스) |
| 리텐션 효과 | 164%+ |
| FC 온라인 | 3년 연속 최고 매출 경신 (GameScale 기여) |
| 던파모바일 | 출시 3시간 내 어뷰저 탐지 |

---

## 6. CS/운영 AI 기획안과의 연관성

| GameScale | 우리 기획안 |
|-----------|-------------|
| 데이터 분석 / 이상 탐지 | 밸런스 이상 탐지 모듈 |
| 이탈 예측 / 재접속 유도 | CS AI의 유저 이력 분석 |
| QA/운영 자동화 | CS AI 에이전트 전체 |
| 커뮤니티 관리 | 버그 리포트 집계, 공지 자동 작성 |

GameScale은 **넥슨 내부 + 외부 퍼블리셔 대상 B2B SaaS**이고, 우리 기획안은 **자사 서비스에 특화된 CS/운영 AI**라는 차이가 있다. GameScale API를 활용하면 분석/보안 부분은 직접 구축하지 않고 연동하는 것도 가능.

---

## 참고 자료
- [GameScale 공식](https://www.gamescale.io/ko)
- [GameScale Developers](https://developers.gamescale.io/ko/services)
- [넥슨 AI 솔루션 외부 공개 기사](https://news.nate.com/view/20250225n35882)
- [인텔리전스랩스 기사 (파이낸셜뉴스)](https://www.fnnews.com/news/202401050910101767)
- [GameScale 브랜딩 (River + Wolf)](https://riverandwolf.com/projects/gamescale/)
- [넥슨 GDC 2023 발표](https://www.marketscreener.com/quote/stock/NEXON-CO-LTD-10016656/news/Nexon-Unveils-New-Games-and-Services-at-the-2023-Game-Developers-Conference-43362394/)
