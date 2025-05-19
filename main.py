import os
import requests
from flask import Flask, request
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")

app = Flask(__name__)

last_prompts = {}

def ask_chatgpt(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT: {e}"

def generate_image(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/images/generations",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/dall-e-3",
                "prompt": prompt
            }
        )
        result = response.json()
        return result["data"][0]["url"]
    except Exception as e:
        print(f"[ERROR] Ошибка генерации изображения: {e}")
        return None

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text

        if any(word in message.lower() for word in ["карт", "рис", "нарисуй"]):
            image_url = generate_image(message)
            if image_url:
                last_prompts[chat_id] = message
                send_image_with_button(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.")
        else:
            reply = ask_chatgpt(message)
            bot.send_message(chat_id=chat_id, text=reply)

    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
        if chat_id in last_prompts:
            prompt = last_prompts[chat_id]
            bot.send_message(chat_id=chat_id, text="Генерирую ещё...")
            image_url = generate_image(prompt)
            if image_url:
                send_image_with_button(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.")
        else:
            bot.send_message(chat_id=chat_id, text="Я не помню, что ты просил нарисовать.")

    return "ok", 200

def send_image_with_button(chat_id, image_url):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Сгенерировать ещё", callback_data="more")]
    ])
    bot.send_photo(chat_id=chat_id, photo=image_url, caption="Готово!", reply_markup=keyboard)

@app.route("/")
def index():
    return "Бот работает!"

if __name__ == "__main__":
    render_url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_url:
        bot.set_webhook(url=f"https://{render_url}/{os.getenv('BOT_TOKEN')}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)