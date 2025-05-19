import os
import telegram
import replicate
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
app = Flask(__name__)

last_prompts = {}

def generate_image(prompt):
    print(f"[LOG] Генерация изображения: {prompt}")
    try:
        output = replicate_client.run(
            "stability-ai/sdxl:latest",
            input={"prompt": prompt}
        )
        print(f"[LOG] Ссылка на изображение: {output[0]}")
        return output[0]
    except Exception as e:
        print(f"[ERROR] Ошибка генерации изображения: {str(e)}")
        return None

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Обработка сообщений
    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text
        print(f"[LOG] Получено сообщение от {chat_id}: {message}")

        if message:
            if any(word in message.lower() for word in ["карт", "рис", "нарисуй"]):
                image_url = generate_image(message)
                if image_url:
                    last_prompts[chat_id] = message
                    send_image_with_button(chat_id, image_url)
                else:
                    bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.",
                                     reply_markup=ReplyKeyboardRemove())
            else:
                bot.send_message(chat_id=chat_id, text="Напиши, что нарисовать!",
                                 reply_markup=ReplyKeyboardRemove())

    # Обработка нажатия кнопки "Сгенерировать ещё"
    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
        data = update.callback_query.data
        if data == "more":
            if chat_id in last_prompts:
                prompt = last_prompts[chat_id]
                bot.answer_callback_query(update.callback_query.id, text="Генерирую ещё изображение...")
                image_url = generate_image(prompt)
                if image_url:
                    send_image_with_button(chat_id, image_url)
                else:
                    bot.send_message(chat_id=chat_id, text="Не удалось сгенерировать новое изображение.")
            else:
                bot.send_message(chat_id=chat_id, text="Я не помню, что ты просил нарисовать.")
        else:
            bot.answer_callback_query(update.callback_query.id)

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
        print("[LOG] Webhook установлен")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
11:37







