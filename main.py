```python
import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI
import asyncio

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Загрузка токенов из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация клиента OpenAI (v0.27+)
client = OpenAI(api_key=OPENAI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое сообщение"""
    await update.message.reply_text(
        "Отправь ссылку на карточку WB, и я всё проанализирую!"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка входящих ссылок"""
    try:
        url = update.message.text.strip()
        await update.message.reply_text("🧠 Анализ начался, подожди 20–30 секунд...")

        # Получаем страницу карточки WB
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        # Собираем отзывы и вопросы (ограничение на 20/10 штук)
        reviews = [tag.get_text(strip=True) for tag in soup.select(".feedback__text")][:20]
        questions = [tag.get_text(strip=True) for tag in soup.select(".question__text")][:10]

        # Формируем подсказку для AI
        prompt = (
            f"Вот отзывы покупателей:\n" + "\n".join(reviews)
            + f"\n\nВот вопросы:\n" + "\n".join(questions)
            + "\n\nУкажи \"✅ Отражены:...\" и \"❌ Не отражены:...\" без рекомендаций."
        )

        # Запрос к OpenAI через асинхронный клиент
        resp_ai = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты помощник, делаешь сухой анализ карточки Wildberries."},
                {"role": "user", "content": prompt},
            ],
            timeout=60
        )

        answer = resp_ai.choices[0].message.content
        await update.message.reply_text(f"🛒 Анализ карточки Wildberries (v2):\n{answer}")

    except Exception as e:
        logging.exception("Ошибка при анализе карточки")
        await update.message.reply_text("Произошла ошибка при анализе карточки. Попробуй позже.")

async def main():
    """Запуск бота"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # Удаляем старые вебхуки и сбрасываем апдейты
    await app.bot.delete_webhook(drop_pending_updates=True)

    # Обработчики команд и сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # Старт Polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == '__main__':
    asyncio.run(main())
```
