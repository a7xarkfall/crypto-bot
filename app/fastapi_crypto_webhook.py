from fastapi import FastAPI, Request
from telegram import Bot, InputFile
import os

# Токен Telegram-бота (тот же, что и в основном боте)
API_TOKEN = "8162219271:AAEhKmeNRLzORbDwXyLKH4tbUMMmtU-ypsw"
FILE_PATH = "example.txt"
LOG_FILE = "paid_users.txt"
EXPECTED_PAYLOAD = "IVHvWARX9rfE"  # из ссылки CryptoBot

bot = Bot(token=API_TOKEN)
app = FastAPI()

def user_already_received(user_id):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r') as f:
        return str(user_id) in f.read()

def log_user(user_id):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{user_id}\n")

@app.post("/crypto-webhook")
async def crypto_webhook(request: Request):
    data = await request.json()
    print("🔥 Получено от CryptoBot:", data)

    if data.get("event") == "payment" and data.get("status") == "success":
        payload = data.get("invoice_payload")
        telegram_id = data.get("user", {}).get("telegram_id")

        if payload == EXPECTED_PAYLOAD and telegram_id:
            if user_already_received(telegram_id):
                await bot.send_message(chat_id=telegram_id, text="📁 Вы уже получали файл. Спасибо за оплату!")
            else:
                if os.path.exists(FILE_PATH):
                    await bot.send_document(chat_id=telegram_id, document=InputFile(FILE_PATH),
                                            caption="📄 Ваш файл — спасибо за оплату!")

                    gif_path = "success.gif"
                    if os.path.exists(gif_path):
                        with open(gif_path, "rb") as gif:
                            await bot.send_animation(chat_id=telegram_id, animation=gif, caption="🎉 Великий успех!")

                    log_user(telegram_id)
                else:
                    await bot.send_message(chat_id=telegram_id, text="❌ Файл не найден. Обратитесь в поддержку.")

    return {"ok": True}

