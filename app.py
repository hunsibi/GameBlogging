import streamlit as st
import time
import os
import base64
import random
import re
import json
import urllib.parse
import urllib.request
from groq import Groq
import streamlit.components.v1 as components

st.set_page_config(
    page_title="QER 컴퍼니 | 무인 출판사",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

INPUT_DIR = "0_Input"
OUTPUT_DIR = "1_Output"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── .env 자동 로딩 ───────────────────────────────────────────────────
env_path = os.path.join(os.path.dirname(__file__), ".env")
groq_api_key = ""
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GROQ_API_KEY="):
                groq_api_key = re.sub(r"[^\x00-\x7F]+", "", line.split("=", 1)[1].strip())

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&family=Inter:wght@400;600;800&display=swap");

html, body, [class*="css"] {
    font-family: "Noto Sans KR", "Inter", sans-serif;
}

/* ── 스트림릿 네이티브 배경 덮어쓰기 (핵심) ── */
[data-testid="stAppViewContainer"] {
    /* 복합 매시 그라데이션으로 유리에 비치는 색상 제공 */
    background-color: #0b0f19;
    background-image: 
        radial-gradient(at 0% 0%, #301b3f 0px, transparent 50%),
        radial-gradient(at 50% 100%, #172a45 0px, transparent 50%),
        radial-gradient(at 100% 0%, #3b185f 0px, transparent 50%);
    background-attachment: fixed;
    background-size: cover;
}

[data-testid="stHeader"] {
    background-color: rgba(0,0,0,0) !important;
}

[data-testid="stSidebar"] {
    background: rgba(20, 20, 35, 0.4) !important;
    backdrop-filter: blur(40px) saturate(200%);
    -webkit-backdrop-filter: blur(40px) saturate(200%);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* 액체 유리(Liquid Glass) 메인 버튼 */
.stButton > button {
    background: rgba(255, 107, 107, 0.15) !important;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    color: #ff8787 !important; 
    border: 1px solid rgba(255, 107, 107, 0.3) !important;
    padding: 16px 32px !important; 
    border-radius: 16px !important;
    font-size: 17px !important; 
    font-weight: 800 !important;
    width: 100% !important; 
    letter-spacing: 1px !important;
    box-shadow: 0 8px 32px 0 rgba(255, 107, 107, 0.15) !important;
    transition: all .3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    background: rgba(255, 107, 107, 0.25) !important;
    box-shadow: 0 12px 40px rgba(255, 107, 107, 0.3) !important;
    border: 1px solid rgba(255, 107, 107, 0.6) !important;
    color: #fff !important;
}

/* 액체 유리(Liquid Glass) 다운로드 버튼 */
.stDownloadButton > button {
    background: rgba(0, 184, 148, 0.15) !important;
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    color: #55efc4 !important; 
    border: 1px solid rgba(0, 184, 148, 0.3) !important;
    padding: 14px 28px !important; 
    border-radius: 14px !important;
    font-size: 16px !important; 
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 8px 32px 0 rgba(0, 184, 148, 0.15) !important;
    transition: all .3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    background: rgba(0, 184, 148, 0.25) !important;
    box-shadow: 0 12px 40px rgba(0, 184, 148, 0.3) !important;
    border: 1px solid rgba(0, 184, 148, 0.6) !important;
    color: #fff !important;
}

/* Liquid Glass 카드 컨테이너 */
.card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(40px) saturate(200%);
    -webkit-backdrop-filter: blur(40px) saturate(200%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 30px 32px;
    margin-bottom: 24px;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
    transition: all .3s ease;
}
.card:hover {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 업로드 안내 라벨 */
.upload-label {
    color: rgba(255, 255, 255, 0.95);
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 4px;
    display: block;
    letter-spacing: 0.5px;
}
.upload-hint {
    color: rgba(255, 255, 255, 0.6);
    font-size: 13px;
    margin-bottom: 12px;
    display: block;
}

/* Before 박스 (딥 글래스) */
.before-box {
    background: rgba(0, 0, 0, 0.25);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid rgba(255, 255, 255, 0.3);
    padding: 24px 28px;
    border-radius: 16px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 15px;
    line-height: 1.9;
    white-space: pre-wrap;
}

/* 에이전트 스텝 박스 (반투명 모핑 베이스) */
.step-card {
    background: rgba(255, 107, 107, 0.08);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid rgba(255, 107, 107, 0.2);
    border-left: 4px solid #ff6b6b;
    padding: 16px 20px;
    border-radius: 16px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
.step-icon { font-size: 24px; text-shadow: 0 2px 10px rgba(255,255,255,0.3); }
.step-text { color: rgba(255, 255, 255, 0.9); font-size: 15px; font-weight: 700; }

/* 배지 */
.badge-success {
    background: rgba(0, 184, 148, 0.25);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 184, 148, 0.5);
    color: #55efc4; padding: 6px 16px;
    border-radius: 30px; font-size: 13px; font-weight: 800;
    display: inline-block; box-shadow: 0 4px 12px rgba(0,184,148,0.3);
}
.badge-kcode {
    background: rgba(108, 92, 231, 0.25);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(108, 92, 231, 0.5);
    color: #a29bfe; padding: 5px 14px;
    border-radius: 30px; font-size: 12px; font-weight: 800;
    letter-spacing: 1px; display: inline-block; box-shadow: 0 4px 12px rgba(108,92,231,0.3);
}

/* 공유 박스 (투명 글래스) */
.share-box {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(30px) saturate(200%);
    -webkit-backdrop-filter: blur(30px) saturate(200%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 26px 30px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.2);
}
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="text-align:center;padding:20px 0 24px;">
    <div style="font-size:44px;margin-bottom:8px;">🏢</div>
    <div style="font-size:21px;font-weight:900;color:#ffffff;">QER 컴퍼니</div>
    <div style="font-size:11px;color:#ff6b6b;font-weight:700;letter-spacing:3px;margin-top:6px;">
        UNMANNED PUBLISHING HOUSE
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    if groq_api_key:
        st.markdown("""
<div style="background:#0d3b2e;border:1px solid #00b894;border-radius:10px;padding:12px 16px;text-align:center;">
    <span style="color:#00b894;font-weight:700;font-size:14px;">⚡ Groq AI 엔진 연결됨</span><br>
    <span style="color:#888;font-size:12px;">LLaMA 3.3 70B · 초고속 추론</span>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="background:#3b0d0d;border:1px solid #d63031;border-radius:10px;padding:12px 16px;text-align:center;">
    <span style="color:#ff6b6b;font-weight:700;font-size:14px;">❌ API 키 없음</span><br>
    <span style="color:#888;font-size:12px;">.env 파일에 GROQ_API_KEY 추가 필요</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🤖 AI 직원 소개**")
    for agent in [
        ("🧭", "Agent 0", "Antigravity (총괄)", "전체 파이프라인 지휘"),
        ("🔎", "Agent 1", "분석 요원", "스토리 뼈대 구성"),
        ("✍️", "Agent 2", "집필 요원 Paul", "감성 에세이 창작 및 디자인"),
    ]:
        st.markdown(f"""
<div style="background:#141428;border-radius:10px;padding:10px 14px;margin-bottom:8px;border:1px solid #2d2d44;">
    <span style="font-size:18px;">{agent[0]}</span>
    <span style="color:#ff6b6b;font-size:12px;font-weight:700;margin-left:6px;">{agent[1]}</span><br>
    <span style="color:#ffffff;font-size:14px;font-weight:700;">{agent[2]}</span><br>
    <span style="color:#888;font-size:12px;">{agent[3]}</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style="text-align:center;color:#666;font-size:12px;line-height:1.7;">
    중학생 CEO & AI Agent의 협업<br>
    짧은 메모 → 완성된 블로그 포스팅
</div>
""", unsafe_allow_html=True)

# ── 메인 헤더 ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:52px 0 36px;">
    <span class="badge-kcode">KOREA CODE FAIR 2025</span>
    <h1 style="font-size:46px;font-weight:900;color:#ffffff;line-height:1.35;margin:20px 0 14px;">
        중학생 CEO와 AI Agent가 만드는<br>
        <span style="background:linear-gradient(135deg,#ff6b6b,#ee5a24);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            무인 출판사
        </span>
    </h1>
    <p style="color:#888;font-size:16px;max-width:580px;margin:0 auto;line-height:2.0;">
        어르신과 청소년의 짧은 메모 한 줄이<br>
        3명의 AI 직원에 의해 완벽한 감성 블로그 포스팅으로 자동 변환됩니다
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── 업로드 카드 ───────────────────────────────────────────────────────
st.markdown("### 📁 Step 1 &nbsp;·&nbsp; 원본 자료 업로드", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown("""
<div class="card">
    <span class="upload-label">📝 텍스트 메모</span>
    <span class="upload-hint">일기, 메모, 짧은 생각을 .txt 파일로 저장해 올려주세요</span>
</div>
""", unsafe_allow_html=True)
    uploaded_txt = st.file_uploader("텍스트 메모", type=["txt"], label_visibility="collapsed")

with col2:
    st.markdown("""
<div class="card">
    <span class="upload-label">🖼️ 사진 파일 (선택, 여러 장 가능)</span>
    <span class="upload-hint">부족한 이미지는 AI가 문맥에 맞게 자동 생성합니다</span>
</div>
""", unsafe_allow_html=True)
    uploaded_images = st.file_uploader(
        "사진", type=["jpg","jpeg","png","webp"],
        accept_multiple_files=True, label_visibility="collapsed"
    )

# ── 세션 초기화 ───────────────────────────────────────────────────────
for k, default in [("pipeline_started", False), ("raw_text", ""),
                   ("images_base64", []), ("final_html_bytes", b""),
                   ("novel_title", "")]:
    if k not in st.session_state:
        st.session_state[k] = default

# ── 가동 버튼 ─────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🚀 Step 2 &nbsp;·&nbsp; 파이프라인 가동", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀  AI 직원 3명 소집 — 출판 파이프라인 가동!"):
    if not uploaded_txt and not uploaded_images:
        st.warning("📂 텍스트 파일이나 이미지를 최소 하나 이상 업로드해주세요!")
    else:
        raw_text = ""
        if uploaded_txt:
            raw_text = uploaded_txt.read().decode("utf-8", errors="replace").strip()
        st.session_state.raw_text = raw_text

        images_base64 = []
        for img_file in (uploaded_images or []):
            img_bytes = img_file.read()
            ext = img_file.name.split(".")[-1].lower()
            mime = "image/jpeg" if ext in ["jpg","jpeg"] else f"image/{ext}"
            b64 = "data:" + mime + ";base64," + base64.b64encode(img_bytes).decode("utf-8")
            images_base64.append(b64)
        st.session_state.images_base64 = images_base64
        st.session_state.pipeline_started = True
        st.session_state.final_html_bytes = b""

# ── 파이프라인 실행 ───────────────────────────────────────────────────
if st.session_state.pipeline_started:
    raw_text      = st.session_state.get("raw_text", "")
    images_base64 = st.session_state.get("images_base64", [])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Step 3 &nbsp;·&nbsp; AI 직원 파이프라인 실행 중...", unsafe_allow_html=True)
    progress_bar = st.progress(0)

    for icon, agent, desc, pct in [
        ("🧭", "Agent 0 — 총괄 매니저", "멀티미디어 융합 워크플로우 설계 중...", 20),
        ("🔎", "Agent 1 — 데이터 분석 요원", "단문 → 3챕터 스토리라인 기획 중...", 40),
    ]:
        st.markdown(f"""
<div class="step-card">
    <span class="step-icon">{icon}</span>
    <span class="step-text">{agent}</span>
</div>""", unsafe_allow_html=True)
        with st.spinner(desc):
            time.sleep(0.6)
            progress_bar.progress(pct)
        st.caption(f"✅ 완료")

    st.markdown("""
<div class="step-card">
    <span class="step-icon">✍️</span>
    <span class="step-text">Agent 2 — 집필 요원 Paul &nbsp;·&nbsp; Groq ⚡ 초고속 AI</span>
</div>""", unsafe_allow_html=True)

    with st.spinner("Groq AI가 감성 에세이를 창작하는 중... ⚡"):

        if not raw_text.strip():
            raw_text = "오늘 하루도 감사합니다"

        images_to_use = images_base64.copy()
        captions      = ["📸 기록의 순간", "📸 감정의 결", "📸 기억의 빛"]
        novel_title   = "오늘, 나의 이야기"
        essay_html    = ""
        img_prompts   = ["beautiful nature cinematic", "emotional moment photography", "hope sunrise peaceful"]

        # ── Groq 창작 ─────────────────────────────────────────────────
        if groq_api_key:
            try:
                client = Groq(api_key=groq_api_key)
                system_msg = (
                    "You are a master Korean emotional essay writer. "
                    "Write ONLY in pure Korean Hangul. "
                    "No Chinese characters, no Japanese, no HTML tags in your text. "
                    "Return ONLY valid JSON, no markdown fences."
                )
                user_msg = (
                    "아래 사용자의 일기 메모를 바탕으로 감성 에세이 3챕터를 창작하세요.\n\n"
                    "[사용자 메모]\n" + raw_text.strip() + "\n\n"
                    "[규칙]\n"
                    "- 순수 한국어(한글)만 사용. 한자·영어 단어 혼용 금지.\n"
                    "- 원본 텍스트를 그대로 반복하지 말고 감성적으로 재해석.\n"
                    "- 1인칭 시점(나는, 내가, 저는)으로 작성.\n"
                    "- 각 챕터는 서로 다른 감성과 시각으로 최소 5문장 이상.\n"
                    "- HTML 태그 절대 금지. 아래 JSON 형식만 출력.\n\n"
                    '{"title":"15자 이내 감성적 제목",'
                    '"ch1_title":"챕터1 소제목","ch1_text":"챕터1 본문 5문장+",'
                    '"ch2_title":"챕터2 소제목","ch2_text":"챕터2 본문 5문장+",'
                    '"ch3_title":"챕터3 소제목","ch3_text":"챕터3 본문 5문장+",'
                    '"img1_prompt":"ch1 mood English image prompt (specific, cinematic)",'
                    '"img2_prompt":"ch2 mood English image prompt",'
                    '"img3_prompt":"ch3 mood English image prompt"}'
                )

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user",   "content": user_msg},
                    ],
                    temperature=0.9,
                    max_tokens=2500,
                    response_format={"type": "json_object"},
                )

                ai_data = json.loads(completion.choices[0].message.content.strip())

                def clean_korean_only(t):
                    """
                    한글(가-힣, 자모) + ASCII 출력 가능 문자 + 기본 한국어 구두점만 남기고
                    러시아어(Cyrillic), 일본어(히라가나/가타카나), 한자(CJK) 등 모두 제거
                    """
                    allowed = re.compile(
                        r"[^\uAC00-\uD7A3"   # 한글 완성형 (가-힣)
                        r"\u1100-\u11FF"      # 한글 자모
                        r"\u3130-\u318F"      # 한글 호환 자모
                        r"\u0020-\u007E"      # ASCII 출력 가능 문자 (영어/숫자/기호)
                        r"\u00B7"             # 가운뎃점 ·
                        r"\u2019\u2018"       # 영문 따옴표
                        r"\u201C\u201D"       # 영문 쌍따옴표
                        r"\uFF01-\uFF60"      # 전각 문자 (느낌표 등)
                        r"\u3000-\u303F"      # CJK 기호·구두점 (…, 。등)
                        r"\n\r\t]+"
                    )
                    return allowed.sub("", t)


                novel_title = clean_korean_only(ai_data.get("title", novel_title))
                ch1_title   = clean_korean_only(ai_data.get("ch1_title", "첫 번째 이야기"))
                ch1_text    = clean_korean_only(ai_data.get("ch1_text", ""))
                ch2_title   = clean_korean_only(ai_data.get("ch2_title", "두 번째 이야기"))
                ch2_text    = clean_korean_only(ai_data.get("ch2_text", ""))
                ch3_title   = clean_korean_only(ai_data.get("ch3_title", "세 번째 이야기"))
                ch3_text    = clean_korean_only(ai_data.get("ch3_text", ""))
                img_prompts = [
                    ai_data.get("img1_prompt", "baseball stadium night dramatic cinematic"),
                    ai_data.get("img2_prompt", "crowd cheering excitement photography"),
                    ai_data.get("img3_prompt", "victory celebration emotion photography"),
                ]

                H3 = "color:#d63031;font-weight:900;font-size:27px;margin:55px 0 16px;border-left:5px solid #ff6b6b;padding-left:16px;line-height:1.3;"
                P  = "font-size:19px;line-height:2.15;color:#333;margin-bottom:28px;"
                essay_html = (
                    f"<h3 style='{H3}'>Chapter 1. {ch1_title}</h3>"
                    f"<p style='{P}'>{ch1_text}</p>[IMG_1_PLACEHOLDER]"
                    f"<h3 style='{H3}'>Chapter 2. {ch2_title}</h3>"
                    f"<p style='{P}'>{ch2_text}</p>[IMG_2_PLACEHOLDER]"
                    f"<h3 style='{H3}'>Chapter 3. {ch3_title}</h3>"
                    f"<p style='{P}'>{ch3_text}</p>[IMG_3_PLACEHOLDER]"
                )

            except Exception as e:
                essay_html = f"<p style='color:red;font-weight:bold;'>[오류] {str(e)}</p>"
        else:
            essay_html = "<p style='color:red;'>.env 파일에 GROQ_API_KEY를 입력해주세요.</p>"

        # ── 이미지 다운로드 → Base64 ──────────────────────────────────
        def fetch_image_b64(prompt_text, seed):
            urls = [
                ("https://image.pollinations.ai/prompt/"
                 + urllib.parse.quote(prompt_text)
                 + f"?width=800&height=450&nologo=true&seed={seed}&model=flux"),
                f"https://loremflickr.com/800/450/{urllib.parse.quote(prompt_text.split()[0])}?lock={seed}",
            ]
            for url in urls:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=40) as resp:
                        data = resp.read()
                    if len(data) > 5000:
                        return "data:image/jpeg;base64," + base64.b64encode(data).decode("utf-8")
                except Exception:
                    continue
            return ""

        while len(images_to_use) < 3:
            idx  = len(images_to_use)
            seed = random.randint(1, 99999)
            p    = img_prompts[idx] if idx < len(img_prompts) else "cinematic nature photography"
            st.caption(f"⏳ Chapter {idx+1} 이미지 생성 중... ({p[:45]})")
            b64 = fetch_image_b64(p, seed)
            images_to_use.append(b64)
            captions[idx] = "✨ 문맥 기반 AI 시각화"

        # ── 이미지 HTML 블록 ──────────────────────────────────────────
        def img_block(src, cap):
            if not src:
                return ""
            return (
                "<div style='text-align:center;margin:48px 0;'>"
                f"<img src='{src}' style='max-width:100%;border-radius:18px;"
                "box-shadow:0 16px 40px rgba(0,0,0,0.13);'>"
                f"<p style='margin-top:12px;font-size:14px;color:#aaa;font-style:italic;'>{cap}</p>"
                "</div>"
            )

        img1 = img_block(images_to_use[0], captions[0]) if len(images_to_use) > 0 else ""
        img2 = img_block(images_to_use[1], captions[1]) if len(images_to_use) > 1 else ""
        img3 = img_block(images_to_use[2], captions[2]) if len(images_to_use) > 2 else ""
        for extra in images_to_use[3:]:
            img3 += img_block(extra, "📸 추가 기록")

        essay_html = (essay_html
                      .replace("[IMG_1_PLACEHOLDER]", img1)
                      .replace("[IMG_2_PLACEHOLDER]", img2)
                      .replace("[IMG_3_PLACEHOLDER]", img3))

        # ── 최종 HTML 조립 ────────────────────────────────────────────
        import datetime
        pub_date = datetime.datetime.now().strftime("%Y년 %m월 %d일")
        final_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{novel_title} | QER MEDIA</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap" rel="stylesheet">
<style>
  body{{margin:0;padding:0;background:#f0f0f5;font-family:'Noto Sans KR',sans-serif;}}
  .wrap{{background:#fff;max-width:860px;margin:40px auto;padding:70px 60px;
         border-radius:24px;box-shadow:0 24px 64px rgba(0,0,0,.08);}}
  .badge{{background:#ffe0e0;color:#d63031;padding:9px 20px;border-radius:30px;
          font-weight:900;font-size:13px;letter-spacing:2px;display:inline-block;}}
  h1{{color:#111;text-align:center;font-size:38px;font-weight:900;
      margin:40px 0 70px;line-height:1.5;}}
  .footer{{text-align:center;margin-top:80px;padding-top:36px;
           border-top:1px dashed #e0e0e0;color:#bbb;font-size:13px;}}
</style>
</head>
<body>
<div class="wrap">
  <div style="text-align:center;margin-bottom:36px;">
    <span class="badge">QER MEDIA &middot; AI 집필 요원 Paul</span>
    <div style="color:#bbb;font-size:13px;margin-top:12px;">{pub_date}</div>
  </div>
  <h1>{novel_title}</h1>
  <div style="font-family:'Noto Sans KR',sans-serif;">
    {essay_html}
  </div>
  <div class="footer">
    QER 집필 요원 Paul &middot; Groq AI (LLaMA 3.3 70B) &middot; Multi-Agent 무인 출판 파이프라인
  </div>
</div>
</body>
</html>"""

        out_path = os.path.join(OUTPUT_DIR, "post_generated_combined.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        st.session_state.final_html_bytes = final_html.encode("utf-8")
        st.session_state.novel_title      = novel_title

        progress_bar.progress(100)
        st.caption("✅ AI 창작 완료 · 이미지 배치 완료 · HTML 렌더링 완료")

    st.balloons()

    # ── 결과 섹션 ─────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
    <h2 style="color:#fff;margin:0;">✨ 출판 완료!</h2>
    <span class="badge-success">경험 자산화 성공</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # Before / After 비교
    col_b, col_a = st.columns(2, gap="large")
    with col_b:
        st.markdown("#### 🌱 Before — 원본 메모")
        st.markdown(
            "<div class='before-box'>"
            + (raw_text or "(텍스트 없음)")
            + f"\n\n📸 첨부 이미지: {len(images_base64)}장</div>",
            unsafe_allow_html=True
        )
    with col_a:
        st.markdown("#### 📊 변환 결과 요약")
        st.markdown(f"""
<div class="card" style="height:100%;box-sizing:border-box;">
    <div style="font-size:13px;color:#888;margin-bottom:6px;">제목</div>
    <div style="font-size:18px;font-weight:900;color:#ff6b6b;margin-bottom:20px;">
        {st.session_state.novel_title}
    </div>
    <div style="color:#888;font-size:13px;margin-bottom:4px;">구성</div>
    <div style="color:#e0e0e0;font-size:15px;margin-bottom:20px;">3개 챕터 · 이미지 3장</div>
    <div style="color:#888;font-size:13px;margin-bottom:4px;">AI 엔진</div>
    <div style="color:#e0e0e0;font-size:15px;">Groq · LLaMA 3.3 70B</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 다운로드 & 공유
    st.markdown("#### 📥 다운로드 & 공유")
    st.markdown("""
<div class="share-box">
    <p style="color:#888;font-size:14px;margin:0 0 20px;">
        생성된 HTML 파일은 네이버 블로그, 카카오뷰, 브런치 등 모든 플랫폼에
        <b style="color:#e0e0e0;">복사·붙여넣기</b>로 즉시 업로드 가능합니다.<br>
        이미지도 Base64로 내장되어 있어 어디서나 완벽하게 표시됩니다.
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    dcol1, dcol2 = st.columns(2, gap="medium")
    with dcol1:
        if st.session_state.final_html_bytes:
            fname = f"QER_{st.session_state.novel_title}_{time.strftime('%Y%m%d_%H%M')}.html"
            st.download_button(
                label="⬇️  HTML 파일 다운로드",
                data=st.session_state.final_html_bytes,
                file_name=fname,
                mime="text/html",
                use_container_width=True,
            )
    with dcol2:
        out_path = os.path.join(OUTPUT_DIR, "post_generated_combined.html")
        st.info(f"📂 저장 위치: `{os.path.abspath(out_path)}`")

    st.markdown("<br>", unsafe_allow_html=True)

    # 미리보기
    st.markdown("#### 👁️ After — AI 완성 포스팅 미리보기")

    out_path = os.path.join(OUTPUT_DIR, "post_generated_combined.html")
    if os.path.exists(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            html_out = f.read()
        html_out += f"<!-- TS:{time.time()} -->"
        components.html(html_out, height=1700, scrolling=True)
    else:
        st.error("HTML 결과물을 로드할 수 없습니다.")
