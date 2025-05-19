import os
import requests
from flask import Flask, request
import telegram

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")

bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Генерация изображения через DeepAI
def generate_image_deepai(prompt):
    api_url = 'https://api.deepai.org/api/text2img'
    try:
        response = requests.post(
            api_url,
            data={'text': prompt},
            headers={'api-key': DEEPAI_API_KEY}
        )
        result = response.json()
        return result.get('output_url')
    except Exception as e:
        print(f"[ERROR] Ошибка DeepAI: {e}")
        return None

# Обработка Webhook от Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    if message:
        if any(word in message.lower() for word in ["карт", "рис", "нарисуй"]):
            image_url = generate_image_deepai(message)
            if image_url:
                bot.send_photo(chat_id=chat_id, photo=image_url, caption="Вот твоё изображение!")
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.")
        else:
            bot.send_message(chat_id=chat_id, text="Напиши, что нарисовать. Например: нарисуй кота в очках.")

    return "ok", 200

@app.route("/")
def index():
    return "Бот запущен!"

if __name__ == "__main__":
    render_url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_url:
        bot.set_webhook(url=f"https://{render_url}/{BOT_TOKEN}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
