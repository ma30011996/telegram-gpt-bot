import os
import requests
from flask import Flask, request
import telegram

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telegram.Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    user_message = update.message.text

    # Запрос к OpenRouter API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",  # Используй модель, поддерживаемую OpenRouter
        "messages": [{"role": "user", "content": user_message}]
    }
    response = requests.post("https://api.openrouter.ai/v1/chat/completions", json=data, headers=headers)
    openrouter_reply = response.json()['choices'][0]['message']['content']

    # Ответ от OpenRouter
    bot.send_message(chat_id=chat_id, text=openrouter_reply)
    return 'ok', 200

@app.route('/')
def index():
    return 'бот работает'

if __name__ == '__main__':
    render_url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_url:
        webhook_url = f"https://{render_url}/{TELEGRAM_TOKEN}"
        bot.set_webhook(url=webhook_url)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
