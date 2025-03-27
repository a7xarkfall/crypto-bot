from pathlib import Path

webhook_code = """
from fastapi import FastAPI, Request
from telegram import Bot, InputFile
import os

API_TOKEN = "8162219271:AAEhKmeNRLzORbDwXyLKH4tbUMMmtU-ypsw"
FILE_PATH = "app/example.txt"
GIF_PATH = "app/success.gif"
LOG_FILE = "app/paid_users.txt"
EXPECTED_PAYLOAD = "IVHvWARX9rfE"

bot = Bot(token=API_TOKEN)
app = FastAPI()

def user_already_received(user_id):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r') as f:
        return str(user_id) in f.read()

def log_user(user_id):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{user_id}\\n")

@app.post("/crypto-webhook")
async def crypto_webhook(request: Request):
    try:
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

                        if os.path.exists(GIF_PATH):
                            with open(GIF_PATH, "rb") as gif:
                                await bot.send_animation(chat_id=telegram_id, animation=gif, caption="🎉 Великий успех!")

                        log_user(telegram_id)
                    else:
                        await bot.send_message(chat_id=telegram_id, text="❌ Файл не найден. Обратитесь в поддержку.")

        return {"ok": True}
    except Exception as e:
        print(f"❌ Ошибка в обработчике webhook: {e}")
        return {"error": str(e)}
"""

# Сохраняем обновлённый обработчик
output_path = Path("/mnt/data/fixed_fastapi_crypto_webhook.py")
output_path.write_text(webhook_code)

output_path


