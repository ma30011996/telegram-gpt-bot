import os
import requests
from flask import Flask, request
import telegram

bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

app = Flask(__name__)

# Генерация ответа на вопрос
def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Ошибка при обращении к OpenRouter: {str(e)}"

# Генерация изображения
def generate_image(prompt):
    try:
        # Бесплатный генератор от Pollinations
        return f"https://image.pollinations.ai/prompt/{prompt}"
    except:
        return None

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    if message:
        if "карт" in message.lower() or "рис" in message.lower() or "нарисуй" in message.lower():
            # Генерация изображения
            img_url = generate_image(message)
            bot.send_photo(chat_id=chat_id, photo=img_url, caption="Вот изображение!")
        else:
            # Ответ на вопрос
            reply = ask_openrouter(message)
            bot.send_message(chat_id=chat_id, text=reply)

    return "ok", 200

@app.route("/")
def index():
    return "Бот запущен!"

if __name__ == "__main__":
    render_url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_url:
        bot.set_webhook(url=f"https://{render_url}/{os.getenv('BOT_TOKEN')}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
