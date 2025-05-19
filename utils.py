import os

def setup_webhook(bot):
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if hostname:
        url = f"https://{hostname}/{os.getenv('BOT_TOKEN')}"
        bot.set_webhook(url=url)
        print(f"[LOG] Webhook установлен на {url}")