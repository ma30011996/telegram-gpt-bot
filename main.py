
def ask_openrouter(prompt):
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
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Ошибка при обращении к ChatGPT: {str(e)}"

def generate_image(prompt):
    try:
        return f"https://image.pollinations.ai/prompt/{prompt}"
    except Exception as e:
        print("[ERROR] Генерация изображения:", e)
        return None

@app.route(f"/{os.getenv('BOT_TOKEN')}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    
    if update.message:
        chat_id = update.message.chat.id
        message = update.message.text
        bot.send_message(chat_id=chat_id, text="...", reply_markup=ReplyKeyboardRemove())
        
        if any(word in message.lower() for word in ["карт", "рис", "нарисуй"]):
            image_url = generate_image(message)
            if image_url:
                last_prompts[chat_id] = message
                send_image(chat_id, image_url)
            else:
                bot.send_message(chat_id=chat_id, text="Ошибка генерации изображения.")
        else:
            reply = ask_openrouter(message)
            bot.send_message(chat_id=chat_id, text=reply)
    
    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
        prompt = last_prompts.get(chat_id)
        if prompt:
            bot.send_message(chat_id=chat_id, text="Генерирую ещё...")
            image_url = generate_image(prompt)
            send_image(chat_id, image_url)

    return "ok", 200

def send_image(chat_id, image_url):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Сгенерировать ещё", callback_data="more")]])
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




