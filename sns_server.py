"""
sns_server.py - FastAPI 기반의 카카오톡 챗봇 스킬 서버
카카오톡 i 오픈빌더 웹훅(Webhook) 연동용 서버입니다.

실행방법:
    uvicorn sns_server:app --host 0.0.0.0 --port 8000 --reload
"""
import os
import time
from pathlib import Path
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ai_engine import generate_post, load_groq_key

app = FastAPI(title="QER 카카오톡 연동 서버")

GROQ_KEY = os.getenv("GROQ_API_KEY", load_groq_key())
OUTPUT_DIR = Path("1_Output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 메모리 기반 간단한 상태 저장소
# 실제 프로덕션에서는 Redis나 DB를 사용해야 합니다.
user_jobs = {}

def process_ai_task(user_id: str, text: str):
    """백그라운드에서 AI 에세이 생성을 수행하는 워커 함수"""
    try:
        user_jobs[user_id] = {"status": "processing", "title": "", "link": "", "error": ""}
        
        # AI 생성 실행
        result = generate_post(text, [], GROQ_KEY)
        title = result["title"]
        html_content = result["html"]
        
        # 고유 파일명 저장
        ts = int(time.time())
        filename = f"kakao_{user_id}_{ts}.html"
        file_path = OUTPUT_DIR / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # NGrok 등 호스팅된 도메인 URL로 접근할 수 있다고 가정 (여기선 로컬 경로 모방)
        # 실제 배포 시 BASE_URL 환경 변수로 서버 주소를 달아줘야 합니다.
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        link = f"{base_url}/view/{filename}"
        
        user_jobs[user_id] = {
            "status": "completed", 
            "title": title, 
            "link": link, 
            "error": ""
        }
        
    except Exception as e:
        print(f"Error on AI task: {e}")
        user_jobs[user_id] = {"status": "failed", "error": str(e)}

@app.post("/kakao/webhook")
async def kakao_webhook(request: Request, bg_tasks: BackgroundTasks):
    """
    카카오 i 오픈빌더에서 넘어오는 스킬 요청을 처리합니다.
    (주의: 카카오톡 웹훅은 5초 내에 응답해야 합니다.)
    """
    payload = await request.json()
    
    # 카카오톡 Request 포맷 분석
    user_id = payload.get("userRequest", {}).get("user", {}).get("id", "test_user")
    utterance = payload.get("userRequest", {}).get("utterance", "").strip()
    
    # 1. 상태 확인 명령어 처리
    if utterance in ["결과 확인", "확인", "결과", "상태"]:
        job = user_jobs.get(user_id)
        if not job:
            return kakao_simple_text("진행 중인 작업이 없습니다. 일기를 먼저 입력해주세요!")
            
        status = job["status"]
        if status == "processing":
            return kakao_simple_text("⏳ 아직 AI 요원들이 열심히 창작 중입니다! 조금만 더 기다린 후 다시 '결과 확인'을 입력해주세요.")
        elif status == "failed":
            error_msg = job.get('error', '알 수 없는 오류')
            return kakao_simple_text(f"❌ 생성 중 오류가 발생했습니다.\n{error_msg}")
        elif status == "completed":
            title = job["title"]
            link = job["link"]
            # 완료되면 상태 초기화
            del user_jobs[user_id]
            return kakao_basic_card(
                title=f"✨ 완성: {title}",
                desc="QER 무인 출판사가 감성 포스팅을 완성했습니다. 링크를 클릭하여 확인하세요!",
                url=link
            )

    # 2. 새로운 글 생성 요청 처리
    # 이미 처리 중인지 확인
    if user_id in user_jobs and user_jobs[user_id]["status"] == "processing":
        return kakao_simple_text("⏳ 이미 생성 중인 에세이가 있습니다. 창작이 완료될 때까지 잠시 기다려주세요! ('결과 확인' 입력)")

    # 텍스트가 짧으면 무시 또는 추가 입력 유도 가능 (우선 무조건 실행)
    bg_tasks.add_task(process_ai_task, user_id, utterance)
    
    return kakao_simple_text(
        "📝 일기 접수가 완료되었습니다!\n"
        "AI 요원들이 3챕터 감성 에세이와 맞춤형 이미지를 창작하고 있습니다.\n"
        "약 1~2분 후 '결과 확인' 이라고 입력해주세요! 🚀"
    )

# --- 카카오톡 챗봇 응답 포맷 렌더러 ---

def kakao_simple_text(text: str) -> JSONResponse:
    return JSONResponse(content={
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": text
                    }
                }
            ]
        }
    })

def kakao_basic_card(title: str, desc: str, url: str) -> JSONResponse:
    return JSONResponse(content={
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "basicCard": {
                        "title": title,
                        "description": desc,
                        "buttons": [
                            {
                                "action": "webLink",
                                "label": "웹에서 확인하기",
                                "webLinkUrl": url
                            }
                        ]
                    }
                }
            ]
        }
    })

# --- 결과 페이지 제공용 Static File 임시 호스팅 ---
from fastapi.responses import HTMLResponse

@app.get("/view/{filename}")
async def view_post(filename: str):
    file_path = OUTPUT_DIR / filename
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>파일을 찾을 수 없습니다.</h1>", status_code=404)
