#!/bin/bash
# Запуск Telegram-бота и FastAPI одновременно
uvicorn app.fastapi_crypto_webhook:app --host 0.0.0.0 --port 8000 &
python3 app/bot.py
