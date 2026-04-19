# 🎮 QER 무인 출판 파이프라인 개발 지침서 (Master Development Guidelines)

> *"위대한 게임은 플레이어의 행동(Input)에 대한 즉각적이고 환상적인 피드백(Output)에서 완성됩니다. 우리의 AI 파이프라인 역시 유저의 작은 메모 하나를 감동적인 서사와 완벽한 웹진 형태의 마법으로 되돌려주는 AAA급 작품이 될 것입니다." - 수석 게임 디렉터(Antigravity)*

## 1. 프로젝트 개요 (Project Overview: The "Game")
- **프로젝트 명:** QER Company: 무인 출판 파이프라인 (AI Agentic Publishing)
- **장르 (Category):** B2C / 배리어 프리(Barrier-Free) AI 자동화 플랫폼
- **핵심 플레이 타겟 (Target Audience):** 노년층, 청소년 등 AI 사용과 블로그 포스팅이 낯선 디지털 소외계층
- **플랫폼 (Platform):** 카카오톡 챗봇, 텔레그램, Streamlit 대시보드

## 2. 디자인 철학 및 핵심 재미 요소 (Design Philosophy & Core Mechanics)
- **원-버튼 액션 (Barrier-Free UX):** 유저는 새로운 튜토리얼을 배울 필요가 없습니다. 익숙한 카카오톡에 한 줄 메모를 던지는 것만으로(Input) 본문 작성, 이미지 생성, 퍼블리싱까지 모든 모험이 자동으로 클리어(Output)됩니다.
- **멀티 에이전트 레이드 (Multi-Agent Architecture):**
  - **Manager (탱커/조율자):** 이벤트 트리거 및 비동기 파이프라인 총괄
  - **Extractor (딜러/마법사):** 거친 단어들을 1인칭 서사시로 폭발적으로 확장 및 구조화
  - **Editor Paul (서포터/아티스트):** 문맥을 읽어 필요한 이미지를 즉석 생성하고, HTML을 폴리싱하여 최상의 비주얼 완성

## 3. 아트 및 레벨 디자인 (Art & Level Design)
- **비주얼 스타일 (Liquid Glass UI):** 대시보드는 칙칙한 관리자 페이지가 아닙니다. 최상급 iOS 느낌의 프리미엄 **'Liquid Glass(액체 유리)' 글래스모피즘 CSS**를 전면 도입하여, 모니터링하는 내내 시각적 황홀함을 제공합니다.
- **렌더링 최적화 (Base64 Embedding):** 생성된 결과물은 외부 링크나 외부 CSS 종속성으로 인해 깨지지 않아야 합니다. HTML 안에 모든 요소가 "100% Base64 + Inline-CSS"로 인베딩되어 어디든 완벽히 복붙되는 무결점을 지향합니다.

## 4. 기술 스택 및 아키텍처 (Tech Stack & Engine)
- **AI Core Engine:** Groq (Llama-3.3-70B) - 빠른 응답 속도 확보 및 CJK 화이트리스트 필터링 방어
- **Asset Gen Engine:** Pollinations AI (이미지 생성)
- **UI/Web 엔진:** Streamlit (관제 대시보드)
- **Backend 망:** FastAPI (Webhook), BackgroundTasks (카카오톡 5초 타임아웃 우회, 비동기 시스템)

## 5. 단계별 퀘스트 및 마일스톤 (Milestones)
- **알파 빌드 (Core Logic):** LLM 연동 및 프롬프트 개선, 멀티 에이전트 간의 데이터 전달(파이프라인) 완료
- **베타 빌드 (UX & Visuals):** Liquid Glass 대시보드 구현 완성, 이미지 생성 로직 및 Base64 HTML 빌더 통합
- **RC 빌드 (Integration & Sync):** 카카오톡/텔레그램 비동기 Webhook 실시간 연동 테스트, 예외 처리 강화
- **출시 (Release):** 한국코드페어(KCF) 2025 라이브 시연 - "한 줄의 카톡, 하나의 완벽한 블로그 포스팅"

---

### 🔥 디렉터의 다음 지시 대기 중
> **엔진과 설계도는 완벽하게 파악했습니다.** 
> 현재 마일스톤 중 어떤 파트를 가장 먼저 디버깅하거나, 기능을 추가해야 할까요? 
> `ai_engine.py`의 구조 개선, `app.py`의 UI 고도화, 또는 새로운 에이전트 추가 등 원하시는 다음 퀘스트를 지정해 주십시오!
