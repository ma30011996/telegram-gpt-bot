import os
from flask import Flask, request
import telegram
from handlers import handle_update
from utils import setup_webhook

app = Flask(__name__)
bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    handle_update(update, bot)
    return "ok", 200

@app.route("/")
def index():
    return "Бот запущен!"

if __name__ == "__main__":
    setup_webhook(bot)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))