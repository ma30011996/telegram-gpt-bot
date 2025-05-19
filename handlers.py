import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from image_generator import generate_image
from chatgpt import ask_chatgpt

last_prompts = {}

def handle_update(update, bot):
    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text

        if any(word in message.lower() for word in ["карт", "рис", "нарисуй"]):
            image_url = generate_image(message)
            if image_url:
                last_prompts[chat_id] = message
                send_image_with_button(bot, chat_id, image_url)
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
                send_image_with_button(bot, chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации.")
        else:
            bot.send_message(chat_id=chat_id, text="Нечего повторять.")

def send_image_with_button(bot, chat_id, image_url):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Сгенерировать ещё", callback_data="more")]])
    bot.send_photo(chat_id=chat_id, photo=image_url, caption="Готово!", reply_markup=keyboard)