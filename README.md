<div align="center">
  <img src="https://img.shields.io/badge/Korea%20Code%20Fair-2025-00b894?style=for-the-badge&logo=" alt="KCF 2025" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Groq-API-blue?style=for-the-badge&logo=ai&logoColor=white" alt="Groq" />
  <img src="https://img.shields.io/badge/Release-V7.2-orange?style=for-the-badge" alt="Version" />
</div>

<br>

<h1 align="center">🏢 QER Company: 모두를 위한 무인 출판 파이프라인 (AI Agentic Publishing)</h1>

<p align="center">
  <b>"카카오톡으로 대충 던진 한 줄의 메모가, AI 요원들에 의해 한 편의 감동적인 서사시(STORYBOOK)로 완성됩니다."</b><br><br>
  QER Company(중학생 CEO 기획)는 디지털 소외계층(노년층, 청소년 등)의 AI 리터러시 문제를 해결하기 위해<br>가장 친근한 SNS(카카오톡, 텔레그램)를 활용한 <b>100% 무인 AI 출판 자동화 시스템</b>을 구축했습니다.
</p>

---

## ✨ 핵심 철학 및 특징 (Key Features)

- 👵 **배리어 프리 (Barrier-Free) UI/UX**
  - 새로운 앱을 설치하거나 배울 필요가 없습니다. 익숙한 **카카오톡 챗봇**에 메모를 남기면, 알아서 웹 포스팅이 완성되어 답장 링크로 전달됩니다.
- 🤖 **멀티 에이전트 파이프라인 (Multi-Agent Architecture)**
  - `Manager (Agile Captain)`: 파이프라인 총괄 및 이벤트 트리거 관리
  - `Extractor (분석 요원)`: 짧은 단어를 감동적인 1인칭 서사(서론-본론-결론)로 확장 및 구조화
  - `Editor Paul (집필 및 디자인 요원)`: 본문 문맥을 읽고 부족한 이미지를 AI로 즉석 생성하여 웹진 형태의 완성된 HTML 배포
- ⚡ **비동기 이벤트 트리거 시스템 (Event-Triggered)**
  - 과거의 무한 대기(Watchdog) 방식을 탈피하여 FastAPI의 BackgroundTasks와 Webhook을 활용해 즉각적으로 응답합니다. 카카오톡의 '5초 타임아웃' 제약을 완벽하게 우회합니다.
- 💎 **Liquid Glass (액체 유리) 디자인 시스템**
  - Streamlit 대시보드 관제 웹에 프리미엄 iOS 느낌의 **'Liquid Glass' 글래스모피즘(Glassmorphism) CSS**를 전면 도입하여 극강의 시각적 경험을 제공합니다.
- 🔐 **초강력 복붙 호환성 (Base64 인베딩)**
  - 생성된 모든 결과물은 외부 CSS나 외부 이미지 링크에 의존하지 않는 100% Inline-CSS + Base64 인코딩 방식을 사용합니다. 어디에 복사+붙여넣기를 해도 이미지가 유실되지 않습니다.

---

## 🛠️ 기술 스택 (Tech Stack)

### **Core AI Engine**
- **LLM**: Groq (Llama-3.3-70B-Versatile) - 초고속 추론 및 CJK 주입 방어형 화이트리스트 필터링
- **Image Gen**: Pollinations AI (Fallback: LoremFlickr) — Base64 인코딩 내장
- **Knowledge System**: `knowledge/` 폴더 기반 Single Source of Truth — 브랜드 사실·금칙어·톤 가이드를 코드 외부에서 관리

### **Quality & History**
- **품질 검증**: `quality_check.py` — HTML 태그 닫힘·이미지 수·한글 비율 등 7항목 자동 검사
- **히스토리 트래킹**: `output/_index.json` — 포스팅 생성 이력 자동 기록, 반복 테마 자동 회피

### **Agent Architecture**
- **에이전트 역할 분리**: `.claude/agents/` — analyzer(분석)·writer(집필)·validator(검증) 독립 파일로 관리

### **Backend & Framework**
- **Web Dashboard**: Streamlit (KCF 시연 및 관제용)
- **SNS Webhook**: FastAPI, Uvicorn, Python-Multipart
- **Bot Integration**: python-telegram-bot

---

## 📂 프로젝트 구조 (Repository Structure)

```text
📦 QER-AI-Publisher
 ┣ 📂 0_Input/              # 사용자 테스트 업로드/메모 (로컬 전용)
 ┣ 📂 1_Output/             # 생성된 Base64 삽입형 HTML 저장 공간
 ┣ 📂 output/               # 포스팅 히스토리 인덱스 (_index.json)
 ┃  ┗ 📜 _index.json        # 생성 이력 자동 기록 — 반복 테마 방지용
 ┣ 📂 knowledge/            # ⭐ Single Source of Truth (브랜드 사실 저장소)
 ┃  ┣ 📜 brand-facts.md     # QER 브랜드 정체성, AI 직원 명칭, 기술 스택
 ┃  ┣ 📜 banned-words.json  # AI 클리셰·금지 표현 목록
 ┃  ┗ 📜 tone-guide.md      # 감성 에세이 문장 스타일 가이드
 ┣ 📂 .claude/
 ┃  ┗ 📂 agents/            # Claude Code 서브에이전트 역할 정의
 ┃     ┣ 📜 analyzer.md     # Extractor: 메모 → JSON 분석
 ┃     ┣ 📜 writer.md       # Editor Paul: JSON → HTML 집필
 ┃     ┗ 📜 validator.md    # 품질 검증 지시서
 ┣ 📜 AGENTS.md             # QER 에이전트 전술 지침서 (System Prompt Core)
 ┣ 📜 ai_engine.py          # 공유 AI 창작 엔진 (knowledge 연동, 히스토리 기록)
 ┣ 📜 app.py                # Streamlit 관제 웹 (Liquid Glass 디자인)
 ┣ 📜 quality_check.py      # 포스팅 품질 자동 검증기 (7항목)
 ┣ 📜 sns_server.py         # 카카오톡 FastAPI Webhook 서버
 ┣ 📜 telegram_bot.py       # 텔레그램 봇
 ┗ 📜 .gitignore            # API Key 및 민감 파일 차단
```

---

## 🚀 시작하기 (Getting Started)

본 프로젝트는 환경 변수(`.env`) 세팅이 필수입니다.

### 1. 환경 변수 설정
최상단 디렉토리에 `.env` 파일을 만들고 아래의 키들을 입력해 주세요:
```env
# 필수: 초고속 추론 엔진 API
GROQ_API_KEY=your_groq_api_key_here

# 선택: 텔레그램 봇 연동 시
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# 선택: 카카오톡 웹훅 외부 라우팅 시 (Ngrok 등 사용)
BASE_URL=https://your-server-url.com
```

### 2. 패키지 설치
```bash
pip install streamlit fastapi uvicorn groq python-telegram-bot httpx python-multipart
```

### 3. 브랜드 정보 설정 (선택, 최초 1회)
`knowledge/brand-facts.md`를 열어 프로젝트에 맞게 수정하세요.
코드를 건드리지 않고도 브랜드 이름·AI 직원 명칭·금칙어를 변경할 수 있습니다.

### 3. 텔레그램 봇 생성 가이드 (Telegram Bot Setup)
텔레그램 봇 연동을 위해 다음 절차에 따라 봇을 생성하고 토큰을 발급받아야 합니다:
1. 스마트폰/PC 텔레그램 앱에서 **`BotFather`**를 검색하여 대화방에 입장합니다.
2. 채팅창에 **`/newbot`**을 전송하고, 로봇 이름과 아이디(반드시 `bot`으로 끝나는 영어)를 지정합니다.
3. 화면에 발급되는 긴 문자열의 **`HTTP API Token`**을 복사합니다.
4. 최상단 디렉토리의 `.env` 파일에 `TELEGRAM_BOT_TOKEN=발급받은토큰` 형태로 저장합니다.

### 4. 품질 검증 (선택)
포스팅 생성 후 7항목 자동 검사:
```bash
python quality_check.py --file shared/current_post.html
```

### 5. 서비스별 실행 방법

**A. 관제용 웹 대시보드 (Streamlit) 실행:**
```bash
streamlit run app.py
```
*(웹 브라우저에서 `http://localhost:8501`로 즉시 시연 가능합니다)*

**B. 카카오톡 웹훅 (FastAPI) 백엔드 실행:**
```bash
uvicorn sns_server:app --host 0.0.0.0 --port 8000
```

**C. 텔레그램 봇 실행:**
```bash
python telegram_bot.py
```

---

## 🏆 KCF 한국코드페어 지향점
이 프로젝트는 "어떻게 하면 최신 AI 기술을 모르는 사람도 AI가 주는 혜택을 100% 누리게 할 수 있을까?"에 대한 고민에서 출발했습니다. 
'디바이스 학습'이라는 장벽을 허물기 위해, 가장 대중적인 **카카오톡 챗봇 하나로 모든 블로그 마케팅과 출판/저작 활동이 자동화되는 세상**을 시연합니다.

✒️ *Designed & Engineered for Everyone, by QER Company.*
