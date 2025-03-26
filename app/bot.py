from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import logging
import os
import httpx
import asyncio

TOKEN = "8162219271:AAEhKmeNRLzORbDwXyLKH4tbUMMmtU-ypsw"
CRYPTOBOT_LINK = "https://t.me/send?start=IVHvWARX9rfE"
FILE_PATH = "example.txt"
LOG_FILE = "paid_users.txt"
WALLET_ADDRESS = "TUsGgfP9X1QcxmuUjDYCFo89i3Wah6XsZQ"
recent_tx_ids = set()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# === Вспомогательные функции ===
def user_already_received(user_id):
    if not os.path.exists(LOG_FILE):
        return False
    with open(LOG_FILE, 'r') as f:
        return str(user_id) in f.read()

def log_user(user_id):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{user_id}\n")

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здарова, барбос, ну шо ты там 😎")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команды бота:\n/start\n/help\n/about\n/pay\n/check")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("тут мы продаем файные говяжьи анусы, лучшего качества, 5 капиталистических бумажек за килограмм 😎")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ℹ️ О боте", callback_data="about")],
        [InlineKeyboardButton("🛠 Помощь", callback_data="help")],
        [InlineKeyboardButton("💵 Оплата", callback_data="pay")],
        [InlineKeyboardButton("🎨 Вдохнови меня", callback_data="inspire")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)

# === Оплата через CryptoBot ===
async def pay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить 0.01 USDT (ERC-20)", url=CRYPTOBOT_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💰 Отправьте 0.01 USDT через CryptoBot. После оплаты файл будет отправлен автоматически.",
        reply_markup=reply_markup
    )

# === Кнопки из меню ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text("Я бот, созданный чётким аптекарем 🤖")
    elif query.data == "help":
        await query.edit_message_text("Вот список команд:\n/start\n/help\n/about\n/menu\n/pay\n/check")
    elif query.data == "inspire":
        await query.edit_message_text("✨ У тебя nice cock & awesome balls!")
    elif query.data == "pay":
        await pay_command(update, context)

# === Проверка оплаты через Tronscan (альтернатива) ===
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_amount = 0.01
    url = f"https://apilist.tronscanapi.com/api/transaction?address={WALLET_ADDRESS}&limit=10&start=0&sort=-timestamp"

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url)
            data = r.json()

            for tx in data.get("data", []):
                if tx.get("tokenInfo", {}).get("tokenAbbr") == "USDT":
                    sender = tx["ownerAddress"]
                    amount = int(tx["quant"]) / (10 ** int(tx["tokenInfo"]["tokenDecimal"]))

                    if abs(amount - target_amount) < 0.001:
                        await update.message.reply_text(
                            f"✅ Оплата получена!\nОтправитель: `{sender}`\nСумма: {amount:.2f} USDT",
                            parse_mode="Markdown"
                        )
                        return
                    else:
                        await update.message.reply_text(
                            f"⚠️ Обнаружена транзакция на сумму {amount:.2f} USDT, но требуется ровно {target_amount:.2f} USDT."
                        )
                        return
            await update.message.reply_text("⏳ Транзакция не найдена. Попробуй позже.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при проверке транзакций: {e}")

# === Эхо и неизвестные команды ===
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("rickroll.mp4", "rb") as video:
        await update.message.reply_video(video, caption="🎶 Никогда тебя не подведу...")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Извини, я не знаю такой команды 😅")

# === Запуск ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("pay", pay_command))
    app.add_handler(CommandHandler("check", check))

    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("✅ Бот полностью запущен. Жми /menu или /pay в Telegram")
    app.run_polling()