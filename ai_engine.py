"""
ai_engine.py - QER 공유 AI 창작 엔진
app.py(Streamlit), telegram_bot.py, sns_server.py 가 모두 이 모듈을 공유합니다.
"""
import os
import re
import json
import base64
import random
import urllib.parse
import urllib.request
from groq import Groq


def load_groq_key() -> str:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GROQ_API_KEY="):
                    return re.sub(r"[^\x00-\x7F]+", "", line.split("=", 1)[1].strip())
    return os.getenv("GROQ_API_KEY", "")


def clean_korean_only(t: str) -> str:
    """한글 + ASCII + 기본 구두점만 허용, 나머지(한자·러·일) 전부 제거"""
    pattern = re.compile(
        r"[^\uAC00-\uD7A3"    # 한글 완성형
        r"\u1100-\u11FF"       # 한글 자모
        r"\u3130-\u318F"       # 한글 호환 자모
        r"\u0020-\u007E"       # ASCII 출력 문자
        r"\u00B7"              # 가운뎃점
        r"\u2018\u2019"        # 작은따옴표
        r"\u201C\u201D"        # 큰따옴표
        r"\n\r\t]+"
    )
    return pattern.sub("", t)


def fetch_image_b64(prompt_text: str, seed: int) -> str:
    """Pollinations → LoremFlickr 순으로 시도, Base64 반환"""
    urls = [
        ("https://image.pollinations.ai/prompt/"
         + urllib.parse.quote(prompt_text)
         + f"?width=800&height=450&nologo=true&seed={seed}&model=flux"),
        (f"https://loremflickr.com/800/450/"
         + urllib.parse.quote(prompt_text.split()[0])
         + f"?lock={seed}"),
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
            if len(data) > 5000:
                return "data:image/jpeg;base64," + base64.b64encode(data).decode("utf-8")
        except Exception:
            continue
    return ""


def generate_post(raw_text: str, images_b64: list[str] | None = None,
                  groq_key: str = "") -> dict:
    """
    핵심 파이프라인: 텍스트 + 이미지 → HTML 포스팅

    Returns:
        {
            "title": str,
            "html": str,           # 전체 HTML 문서
            "essay_html": str,     # 본문만 (embed용)
        }
    """
    if images_b64 is None:
        images_b64 = []
    if not groq_key:
        groq_key = load_groq_key()
    if not raw_text.strip():
        raw_text = "오늘 하루도 감사합니다"

    images_to_use = list(images_b64)
    captions = ["📸 기록의 순간", "📸 감정의 결", "📸 기억의 빛"]
    novel_title = "오늘, 나의 이야기"
    essay_html = ""
    img_prompts = [
        "beautiful cinematic nature photography",
        "emotional peaceful photography",
        "hope sunrise landscape"
    ]

    # ── Groq LLaMA 창작 ────────────────────────────────────────────
    if groq_key:
        try:
            client = Groq(api_key=groq_key)
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

            novel_title = clean_korean_only(ai_data.get("title", novel_title))
            ch1_t = clean_korean_only(ai_data.get("ch1_title", "첫 번째 이야기"))
            ch1_b = clean_korean_only(ai_data.get("ch1_text", ""))
            ch2_t = clean_korean_only(ai_data.get("ch2_title", "두 번째 이야기"))
            ch2_b = clean_korean_only(ai_data.get("ch2_text", ""))
            ch3_t = clean_korean_only(ai_data.get("ch3_title", "세 번째 이야기"))
            ch3_b = clean_korean_only(ai_data.get("ch3_text", ""))
            img_prompts = [
                ai_data.get("img1_prompt", img_prompts[0]),
                ai_data.get("img2_prompt", img_prompts[1]),
                ai_data.get("img3_prompt", img_prompts[2]),
            ]

            # Liquid Glass inline styling for H3 and P
            H3 = ("color:#fff;font-weight:900;font-size:27px;margin:55px 0 16px;"
                  "border-left:5px solid rgba(255,107,107,0.8);padding-left:18px;line-height:1.3;"
                  "text-shadow: 0 4px 16px rgba(255,107,107,0.3);")
            P  = "font-size:19px;line-height:2.15;color:rgba(255,255,255,0.9);margin-bottom:28px;"
            essay_html = (
                f"<h3 style='{H3}'>Chapter 1. {ch1_t}</h3>"
                f"<p style='{P}'>{ch1_b}</p>[IMG_1]"
                f"<h3 style='{H3}'>Chapter 2. {ch2_t}</h3>"
                f"<p style='{P}'>{ch2_b}</p>[IMG_2]"
                f"<h3 style='{H3}'>Chapter 3. {ch3_t}</h3>"
                f"<p style='{P}'>{ch3_b}</p>[IMG_3]"
            )
        except Exception as e:
            essay_html = f"<p style='color:red;'>[AI 오류] {e}</p>"
    else:
        essay_html = "<p style='color:red;'>GROQ_API_KEY가 없습니다.</p>"

    # ── 이미지 보충 (Liquid Glass 스타일 부착) ────────────────────────
    while len(images_to_use) < 3:
        idx  = len(images_to_use)
        seed = random.randint(1, 99999)
        p    = img_prompts[idx] if idx < len(img_prompts) else "cinematic nature"
        b64  = fetch_image_b64(p, seed)
        images_to_use.append(b64)
        captions[idx] = "✨ 문맥 기반 AI 시각화"

    def img_block(src, cap):
        if not src:
            return ""
        return (
            "<div style='text-align:center;margin:48px 0;'>"
            f"<img src='{src}' style='max-width:100%;border-radius:24px;"
            "box-shadow: 0 20px 60px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1);'>"
            f"<p style='margin-top:16px;font-size:14px;color:rgba(255,255,255,0.5);font-style:italic;'>{cap}</p>"
            "</div>"
        )

    img_tags = [
        img_block(images_to_use[i], captions[i]) if i < len(images_to_use) else ""
        for i in range(3)
    ]
    for extra in images_to_use[3:]:
        img_tags[2] += img_block(extra, "📸 추가 기록")

    final_essay = (essay_html
                   .replace("[IMG_1]", img_tags[0])
                   .replace("[IMG_2]", img_tags[1])
                   .replace("[IMG_3]", img_tags[2]))

    # ── 최종 HTML 조립 (Liquid Glass Aesthetic) ───────────────────
    import datetime
    pub_date = datetime.datetime.now().strftime("%Y년 %m월 %d일")
    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{novel_title} | QER MEDIA</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap" rel="stylesheet">
<style>
body {{
    margin:0; padding:0; font-family:'Noto Sans KR',sans-serif;
    background-color: #0c0f1a;
    background-image: 
        radial-gradient(at 0% 0%, #1a1025 0px, transparent 50%),
        radial-gradient(at 100% 100%, #152036 0px, transparent 50%),
        radial-gradient(at 100% 0%, #2a1532 0px, transparent 50%);
    background-attachment: fixed;
    color: #ffffff;
}}
.wrap {{
    max-width:860px; margin:50px auto; padding:70px 60px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(40px) saturate(200%);
    -webkit-backdrop-filter: blur(40px) saturate(200%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 32px;
    box-shadow: 0 32px 80px rgba(0,0,0,0.5);
}}
.badge {{
    background: rgba(255, 107, 107, 0.15);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 107, 107, 0.3);
    color: #ff8787; padding: 10px 24px; border-radius: 30px;
    font-weight: 800; font-size: 13px; letter-spacing: 2px; display: inline-block;
    box-shadow: 0 8px 24px rgba(255, 107, 107, 0.15);
}}
h1 {{
    color: #fff; text-align: center; font-size: 42px; font-weight: 900;
    margin: 40px 0 70px; line-height: 1.4;
    text-shadow: 0 4px 20px rgba(255,255,255,0.2);
}}
.footer {{
    text-align: center; margin-top: 80px; padding-top: 36px;
    border-top: 1px solid rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.4); font-size: 13px;
}}
</style>
</head>
<body>
<div class="wrap">
  <div style="text-align:center;margin-bottom:36px;">
    <span class="badge">QER MEDIA &middot; 총괄 Antigravity x 집필 Paul</span>
    <div style="color:rgba(255,255,255,0.5);font-size:13px;margin-top:16px;">{pub_date}</div>
  </div>
  <h1>{novel_title}</h1>
  {final_essay}
  <div class="footer">
    General Manager Antigravity &middot; Editor Paul &middot; Groq AI (LLaMA 3.3) &middot; Liquid Glass Design
  </div>
</div>
</body>
</html>"""

    return {
        "title":      novel_title,
        "html":       full_html,
        "essay_html": final_essay,
    }
