import os
import requests
import telegram
import replicate
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

# Настройка токенов
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

bot = telegram.Bot(token=BOT_TOKEN)
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
app = Flask(__name__)
last_prompts = {}

# --- Генерация текста от ChatGPT ---
def ask_openrouter(prompt):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] OpenRouter: {e}")
        return "Ошибка при обращении к ChatGPT."

# --- Генерация изображения через Replicate ---
def generate_image(prompt):
    print(f"[LOG] Генерация изображения: {prompt}")
    try:
        output = replicate_client.run(
            "stability-ai/sdxl:latest",
            input={"prompt": prompt}
        )
        if isinstance(output, list) and output:
            print(f"[LOG] Ссылка на изображение: {output[0]}")
            return output[0]
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Replicate: {e}")
        return None

# --- Обработка запроса Telegram ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text

        if any(word in message.lower() for word in ["карт", "рис", "нарисуй", "сгенерируй"]):
            image_url = generate_image(message)
            if image_url:
                last_prompts[chat_id] = message
                send_image_with_button(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.", reply_markup=ReplyKeyboardRemove())
        else:
            reply = ask_openrouter(message)
            bot.send_message(chat_id=chat_id, text=reply, reply_markup=ReplyKeyboardRemove())

    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
        if chat_id in last_prompts:
            bot.send_message(chat_id=chat_id, text="Генерирую ещё...", reply_markup=ReplyKeyboardRemove())
            prompt = last_prompts[chat_id]
            image_url = generate_image(prompt)
            if image_url:
                send_image_with_button(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Не удалось сгенерировать новое изображение.")
        else:
            bot.send_message(chat_id=chat_id, text="Я не помню, что ты просил нарисовать.")

    return "ok", 200

# --- Отправка изображения с кнопкой ---
def send_image_with_button(chat_id, image_url):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Сгенерировать ещё", callback_data="more")]
    ])
    bot.send_photo(chat_id=chat_id, photo=image_url, caption="Готово!", reply_markup=keyboard)

# --- Главная страница ---
@app.route("/")
def index():
    return "Бот работает!"

# --- Запуск ---
if __name__ == "__main__":
    render_url = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_url:
        bot.set_webhook(url=f"https://{render_url}/{BOT_TOKEN}")
        print(f"[LOG] Webhook установлен: {render_url}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
