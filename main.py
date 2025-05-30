import os
import logging
import openai
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получение переменных среды
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Функция анализа карточки
async def analyze_wb_card(text_data):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты помощник, который анализирует карточки товаров на Wildberries. На основе отзывов, вопросов и фотографий скажи, какие преимущества отражены, а какие нет. Не давай советов. Просто раздели как 'Отражены' и 'Не отражены'. В конце выведи рейтинг и число отзывов с фото за 14 дней."},
                {"role": "user", "content": text_data}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка при запросе к OpenAI: {e}")
        return "Произошла ошибка при анализе карточки. Попробуй позже."

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь ссылку на карточку WB, и я всё проанализирую!")

# Обработка сообщений с ссылками
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "wildberries.ru" not in url:
        await update.message.reply_text("Это не похоже на ссылку Wildberries. Попробуй ещё раз.")
        return

    await update.message.reply_text("🧠 Анализ начался, подожди 20–30 секунд...")

    try:
        # Получение текста страницы (условно — заменить на парсинг отзывов/вопросов позже)
        response = requests.get(url)
        response.encoding = 'utf-8'
        page_text = response.text[:4000]  # Ограничим длину запроса

        result = await analyze_wb_card(page_text)
        await update.message.reply_text("🛒 Анализ карточки Wildberries (v2):\n\n" + result)
    except Exception as e:
        logging.error(f"Ошибка при анализе ссылки: {e}")
        await update.message.reply_text("Ошибка при загрузке карточки. Попробуй позже.")

# Основная функция запуска
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    app.run_polling()

if __name__ == "__main__":
    main()
