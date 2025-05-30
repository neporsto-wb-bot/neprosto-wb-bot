import os
import logging
import requests
import openai
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Настройка логов
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь ссылку на карточку WB, и я всё проанализирую!")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text.strip()
        await update.message.reply_text("\U0001F9E0 Анализ начался, подожди 20–30 секунд...")

        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Не удалось загрузить страницу. Код: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Без названия"

        reviews_block = soup.find_all("span", class_="feedback__text")
        questions_block = soup.find_all("div", class_="question__text")
        reviews = [r.get_text(strip=True) for r in reviews_block][:20]
        questions = [q.get_text(strip=True) for q in questions_block][:10]

        reviews_text = "\n".join(reviews)
        questions_text = "\n".join(questions)

        prompt = f"Вот отзывы покупателей:\n{reviews_text}\n\nВот вопросы:\n{questions_text}\n\n" \
                 f"На основе этого укажи, какие плюсы и минусы отражены в карточке товара, а какие нет. " \
                 f"Просто выдай \"✅ Отражены:...\" и \"❌ Не отражены:...\" без рекомендаций."

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты помощник, делаешь сухой анализ карточки Wildberries."},
                {"role": "user", "content": prompt},
            ]
        )

        result = completion.choices[0].message.content

        await update.message.reply_text(f"\U0001F6D2 Анализ карточки Wildberries (v2):\n{result}")

    except Exception as e:
        logging.exception("Ошибка при анализе карточки")
        await update.message.reply_text("Произошла ошибка при анализе карточки. Попробуй позже.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling()
