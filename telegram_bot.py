"""
telegram_bot.py - QER 텔레그램 봇
사용자가 텍스트나 사진을 보내면 AI가 감성 에세이를 생성하여 HTML 파일로 답장합니다.

실행:
    python telegram_bot.py

.env 파일에 추가 필요:
    TELEGRAM_BOT_TOKEN=your_token_here
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import re
import base64
import logging
import tempfile
import time
from pathlib import Path

from telegram import Update, InputFile
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler,
)
from ai_engine import generate_post, load_groq_key

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ── 환경변수 로딩 ──────────────────────────────────────────────────
def load_env():
    env_path = Path(__file__).parent / ".env"
    result = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    result[k.strip()] = re.sub(r"[^\x00-\x7F]+", "", v.strip())
    return result

env = load_env()
BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
GROQ_KEY  = env.get("GROQ_API_KEY", load_groq_key())
OUTPUT_DIR = Path(__file__).parent / "1_Output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 사용자별 상태 저장 (메모리)
user_sessions: dict[int, dict] = {}

# ── 명령어 핸들러 ──────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏢 *QER 무인 출판사* 에 오신 것을 환영합니다!\n\n"
        "📝 짧은 일기나 메모를 텍스트로 보내주세요.\n"
        "🖼️ 사진도 함께 보내시면 글에 포함됩니다.\n"
        "⚡ AI가 감성적인 에세이 포스팅으로 변환해드립니다!\n\n"
        "사용법:\n"
        "1. 텍스트 메모를 입력하세요\n"
        "2. 사진이 있으면 함께 전송 (선택)\n"
        "3. /generate 를 보내면 AI 에세이 생성 시작!\n\n"
        "또는 텍스트만 보내도 자동으로 감지합니다.",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *명령어 목록*\n\n"
        "/start - 시작 안내\n"
        "/generate - 지금까지 입력한 내용으로 AI 생성\n"
        "/reset - 초기화 (새로 시작)\n"
        "/status - 현재 입력된 내용 확인",
        parse_mode="Markdown"
    )

async def reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_sessions[uid] = {"text": "", "images": []}
    await update.message.reply_text("🔄 초기화되었습니다. 새 메모를 입력해주세요!")

async def status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    session = user_sessions.get(uid, {"text": "", "images": []})
    text = session.get("text", "").strip() or "(없음)"
    img_count = len(session.get("images", []))
    await update.message.reply_text(
        f"📋 *현재 입력 상태*\n\n"
        f"📝 텍스트: {text[:100]}{'...' if len(text) > 100 else ''}\n"
        f"🖼️ 이미지: {img_count}장",
        parse_mode="Markdown"
    )

# ── 텍스트 메시지 수신 ─────────────────────────────────────────────
async def receive_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text or ""

    if uid not in user_sessions:
        user_sessions[uid] = {"text": "", "images": []}

    user_sessions[uid]["text"] += ("\n" + text if user_sessions[uid]["text"] else text)

    await update.message.reply_text(
        f"✅ 메모를 받았습니다!\n\n"
        f"📝 입력 내용: {text[:80]}{'...' if len(text) > 80 else ''}\n\n"
        f"📸 사진도 추가하시려면 지금 전송하세요.\n"
        f"준비가 되면 /generate 를 보내주세요!",
    )

# ── 사진 수신 ──────────────────────────────────────────────────────
async def receive_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_sessions:
        user_sessions[uid] = {"text": "", "images": []}

    # 가장 큰 해상도 사진 선택
    photo = update.message.photo[-1]
    file  = await ctx.bot.get_file(photo.file_id)
    img_bytes = await file.download_as_bytearray()
    b64 = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode("utf-8")
    user_sessions[uid]["images"].append(b64)

    # 사진에 캡션이 있으면 텍스트로도 저장
    if update.message.caption:
        user_sessions[uid]["text"] += ("\n" + update.message.caption
                                        if user_sessions[uid]["text"]
                                        else update.message.caption)

    img_count = len(user_sessions[uid]["images"])
    await update.message.reply_text(
        f"🖼️ 사진 {img_count}장 수신 완료!\n"
        f"계속 사진을 추가하거나 /generate 로 생성을 시작하세요."
    )

# ── AI 생성 실행 ───────────────────────────────────────────────────
async def generate(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    session = user_sessions.get(uid, {"text": "", "images": []})
    raw_text = session.get("text", "").strip()
    images   = session.get("images", [])

    if not raw_text and not images:
        await update.message.reply_text(
            "❌ 내용이 없습니다!\n먼저 텍스트 메모나 사진을 보내주세요."
        )
        return

    # 생성 시작 알림
    waiting_msg = await update.message.reply_text(
        "⚡ *QER 전담 요원 3명이 에세이를 창작하는 중입니다...*\n\n"
        "🧭 Agile Captain — 워크플로우 조율 및 통제 중...\n"
        "🔎 Extractor — 메모장 심층 분석 및 스토리 확장 중...\n"
        "✍️ Editor Paul — 감성 에세이 집필 및 웹 포스팅 조립 중...\n\n"
        "_이미지 생성까지 1~2분 소요됩니다. 잠시만 기다려주세요!_",
        parse_mode="Markdown"
    )

    try:
        # AI 생성 (동기 함수 → 스레드 풀)
        import asyncio
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: generate_post(raw_text, images, GROQ_KEY)
        )

        title    = result["title"]
        full_html = result["html"]

        # HTML 파일 저장
        ts = int(time.time())
        out_path = OUTPUT_DIR / f"tg_{uid}_{ts}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        # 완료 메시지
        await ctx.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=waiting_msg.message_id,
            text=f"✅ *에세이 완성!*\n\n📰 제목: *{title}*\n\n아래 HTML 파일을 다운로드하세요.",
            parse_mode="Markdown"
        )

        # HTML 파일 전송
        with open(out_path, "rb") as f:
            await update.message.reply_document(
                document=InputFile(f, filename=f"QER_{title}_{ts}.html"),
                caption=(
                    f"📰 *{title}*\n\n"
                    "✨ 이 HTML 파일을 네이버 블로그, 브런치, 티스토리에\n"
                    "복사·붙여넣기 하면 바로 포스팅됩니다!\n"
                    "이미지도 내장되어 있어 깨지지 않습니다."
                ),
                parse_mode="Markdown"
            )

        # 세션 초기화
        user_sessions[uid] = {"text": "", "images": []}

    except Exception as e:
        logger.error("Generation error: %s", e)
        await update.message.reply_text(
            f"❌ 생성 중 오류가 발생했습니다:\n`{str(e)}`\n\n/reset 후 다시 시도해주세요.",
            parse_mode="Markdown"
        )

# ── 봇 실행 ────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN이 .env 파일에 없습니다!")
        print("   1. https://t.me/BotFather 접속")
        print("   2. /newbot 명령어로 봇 생성")
        print("   3. 발급받은 토큰을 .env 파일에 추가:")
        print("      TELEGRAM_BOT_TOKEN=your_token_here")
        return

    print("🚀 QER 텔레그램 봇 시작!")
    print(f"   Groq API 키: {'✅ 연결됨' if GROQ_KEY else '❌ 없음'}")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("help",     help_cmd))
    app.add_handler(CommandHandler("reset",    reset))
    app.add_handler(CommandHandler("status",   status))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))
    app.add_handler(MessageHandler(filters.PHOTO, receive_photo))

    print("📱 봇이 실행 중입니다. Ctrl+C로 종료합니다.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
