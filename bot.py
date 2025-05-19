
    import os
import requests
import telegram
import replicate
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
app = Flask(__name__)

# Словарь для запоминания последних запросов
last_prompts = {}

# Генерация изображения через Replicate (Stable Diffusion)
def generate_image(prompt):
    print(f"[LOG] Генерация изображения: {prompt}")
    try:
        output = replicate_client.run(
            "stability-ai/sdxl:latest",
            input={"prompt": prompt}
        )
        print(f"[LOG] Ссылка на изображение: {output[0]}")
        return output[0]  # URL изображения
    except Exception as e:
        print(f"[ERROR] Ошибка генерации изображения: {str(e)}")
        return None

# Обработка команды Webhook
@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text

        print(f"[LOG] Получено сообщение от {chat_id}: {message}")

        if any(word in message.lower() for word in ["карт", "рис", "нарисуй"]):
            image_url = generate_image(message)
            if image_url:
                last_prompts[chat_id] = message  # Сохраняем запрос
                send_image_with_button(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.")
        else:
            bot.send_message(chat_id=chat_id, text="Напиши, что нарисовать!")

    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
        if chat_id in last_prompts:
            prompt = last_prompts[chat_id]
            bot.send_message(chat_id=chat_id, text="Генерирую ещё...")
            image_url = generate_image(prompt)
            if image_url:
                send_image_with_button(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Не удалось сгенерировать новое изображение.")
        else:
            bot.send_message(chat_id=chat_id, text="Я не помню, что ты просил нарисовать.")

    return "ok", 200

# Отправка изображения с кнопкой "Сгенерировать ещё"
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
        print("[LOG] Webhook установлен")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
