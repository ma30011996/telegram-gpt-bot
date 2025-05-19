import os
import requests
from flask import Flask, request
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import replicate

bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

app = Flask(__name__)
last_prompts = {}

def generate_image(prompt):
    try:
        output = replicate_client.run(
            "stability-ai/sdxl:latest",
            input={"prompt": prompt}
        )
        return output[0] if output else None
    except Exception as e:
        print(f"Ошибка генерации изображения: {str(e)}")
        return None

def ask_chatgpt(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Ошибка ChatGPT: {e}")
        return "Ошибка при обращении к ChatGPT."

def send_image(chat_id, image_url, prompt):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Сгенерировать ещё", callback_data="more")]
    ])
    bot.send_photo(chat_id=chat_id, photo=image_url, caption="Вот изображение!", reply_markup=keyboard)

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text
        print(f"Получено сообщение: {message}")

        if any(word in message.lower() for word in ["карт", "рис", "нарисуй", "создай"]):
            image_url = generate_image(message)
            if image_url:
                last_prompts[chat_id] = message
                send_image(chat_id, image_url, message)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.")
        else:
            reply = ask_chatgpt(message)
            bot.send_message(chat_id=chat_id, text=reply)

    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
        if chat_id in last_prompts:
            bot.send_message(chat_id=chat_id, text="Секунду... Генерирую ещё.")
            image_url = generate_image(last_prompts[chat_id])
            if image_url:
                send_image(chat_id, image_url, last_prompts[chat_id])
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.")
        else:
            bot.send_message(chat_id=chat_id, text="Я не помню, что рисовать. Напиши заново.")

    return "ok", 200

@app.route("/")
def index():
    return "Бот работает!"

if __name__ == "__main__":
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{os.getenv('BOT_TOKEN')}"
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
