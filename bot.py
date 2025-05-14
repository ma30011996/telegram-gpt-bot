import os
from flask import Flask, request
import telegram
import requests

TOKEN = os.getenv("BOT_TOKEN")  # Задай переменную окружения с токеном бота
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

# Функция генерации изображения
def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    return url

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id

    if update.message.text.startswith("/image"):
        prompt = update.message.text.replace("/image", "").strip()
        if not prompt:
            bot.send_message(chat_id=chat_id, text="Напиши описание после команды. Пример: /image робот на пляже")
        else:
            image_url = generate_image(prompt)
            bot.send_photo(chat_id=chat_id, photo=image_url, caption=f"Вот изображение по запросу: {prompt}")
    else:
        bot.send_message(chat_id=chat_id, text="Используй команду /image чтобы сгенерировать картинку.")

    return 'ok', 200

@app.route('/')
def index():
    return 'бот работает'

if __name__ == '__main__':
    render_url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_url:
        webhook_url = f"https://{render_url}/{TOKEN}"
        bot.set_webhook(url=webhook_url)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
