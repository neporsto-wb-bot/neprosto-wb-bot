import os
import logging
import openai
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь ссылку на карточку WB, и я всё проанализирую!")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "wildberries.ru" not in url:
        await update.message.reply_text("Пришли корректную ссылку на товар с Wildberries.")
        return

    await update.message.reply_text("🔍 Анализ начался, подожди 20–30 секунд...")

    try:
        result = run_analysis_v2(url)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

def run_analysis_v2(card_url: str) -> str:
    # 🔧 Здесь будет вся логика анализа карточки: фото, отзывы, вопросы, рейтинг, фото-отзывы за 14 дней
    # Сейчас — просто заглушка:
    return (
        "🛒 Анализ карточки Wildberries (v2)\n\n"
        "✅ Отражены:\n"
        "- Удобство в носке\n"
        "- Эффект на осанку\n\n"
        "❌ Не отражены:\n"
        "- Запах при открытии\n"
        "- Вопросы по липучкам\n\n"
        "📊 Рейтинг: 4.7\n"
        "🖼️ Отзывов с фото за 14 дней: 17"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze))
    app.run_polling()


if __name__ == "__main__":
    main()
