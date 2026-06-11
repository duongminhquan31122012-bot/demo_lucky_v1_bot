import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from google import genai

TELEGRAM_TOKEN = os.getenv("")
GEMINI_API_KEY = os.getenv("")

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Gemini đã sẵn sàng.\n\n"
        "Gửi tin nhắn bất kỳ để trò chuyện."
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 Không có lịch sử được lưu, đã reset."
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    thinking_msg = await update.message.reply_text(
        "🤔 Đang suy nghĩ..."
    )

    try:
        response = None

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=user_text,
                )
                break
            except Exception:
                if attempt < 2:
                    await asyncio.sleep(2)

        if response is None:
            await thinking_msg.edit_text(
                "⚠️ Gemini đang quá tải, thử lại sau."
            )
            return

        answer = getattr(response, "text", None) or "Không có phản hồi."

        if len(answer) > 4000:
            answer = answer[:4000] + "\n\n...(rút gọn)"

        await thinking_msg.edit_text(answer)

    except Exception as e:
        print("ERROR:", e)
        await thinking_msg.edit_text(
            "❌ Đã xảy ra lỗi khi gọi Gemini."
        )

app = Application.builder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat,
    )
)

print("Bot đang chạy...")
app.run_polling()
