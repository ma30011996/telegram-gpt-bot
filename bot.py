import os
from flask import Flask, request
import telegram

TOKEN = os.getenv("7949631115:AAGlmQs-qdv33QWV7mgQuAkDD1EdC0RGVvU")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text
    bot.send_message(chat_id=chat_id, text=f"Ты написал: {message}")
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
