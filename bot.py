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

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        response_json = response.json()

        if 'choices' in response_json:
            reply = response_json['choices'][0]['message']['content']
        else:
            reply = "Ошибка: " + str(response_json.get("error", "Неизвестная ошибка"))
    except Exception as e:
        reply = f"Произошла ошибка при обращении к OpenRouter: {str(e)}"

    bot.send_message(chat_id=chat_id, text=reply)
    return 'ok', 200

@app.route('/')
def index():
    return 'Бот работает.'

if __name__ == '__main__':
    render_url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_url:
        webhook_url = f"https://{render_url}/{TELEGRAM_TOKEN}"
        bot.set_webhook(url=webhook_url)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
