import asyncio
import logging
import os
import sys

# Добавляем корневую папку bot в sys.path, чтобы python находил модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from middlewares import ShadowTrackingMiddleware
from handlers import base, client, admin

load_dotenv()

logging.basicConfig(level=logging.INFO)

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        # Для локальных тестов
        logging.warning("BOT_TOKEN не найден, используем моковый токен.")
        bot_token = "mock"

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    # Регистрация Middlewares
    dp.update.middleware(ShadowTrackingMiddleware())

    # Регистрация роутеров
    dp.include_router(base.router)
    dp.include_router(client.router)
    dp.include_router(admin.router)

    logging.info("Starting bot...")
    try:
        if bot_token == "mock":
             logging.info("Mock mode, stopping...")
             return
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error during polling: {e}")

if __name__ == "__main__":
    asyncio.run(main())
