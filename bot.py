import os
from flask import Flask, request
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import replicate

# Инициализация
bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))
app = Flask(__name__)
last_prompts = {}

# Генерация изображения
def generate_image(prompt):
    try:
        print(f"[LOG] Генерация изображения: {prompt}")
        output = replicate_client.run(
            "stability-ai/sdxl:latest",
            input={"prompt": prompt}
        )
        return output[0]
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

# Отправка изображения с кнопкой
def send_image(chat_id, image_url):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Сгенерировать ещё", callback_data="more")]])
    bot.send_photo(chat_id=chat_id, photo=image_url, caption="Готово!", reply_markup=keyboard)

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text

        if message.lower().startswith("/start"):
            bot.send_message(chat_id=chat_id, text="Привет! Напиши, что нарисовать.")
        elif any(x in message.lower() for x in ["рис", "карт", "нарисуй"]):
            image_url = generate_image(message)
            if image_url:
                last_prompts[chat_id] = message
                send_image(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации.")
        else:
            bot.send_message(chat_id=chat_id, text="Хочешь картинку? Напиши, что нарисовать.")

    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
        prompt = last_prompts.get(chat_id)
        if prompt:
            bot.send_message(chat_id=chat_id, text="Генерирую ещё...")
            image_url = generate_image(prompt)
            if image_url:
                send_image(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации.")
        else:
            bot.send_message(chat_id=chat_id, text="Я не помню, что ты просил.")

    return "ok", 200

@app.route("/")
def home():
    return "Бот работает!"

if __name__ == "__main__":
    url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if url:
        bot.set_webhook(f"https://{url}/{os.getenv('BOT_TOKEN')}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




