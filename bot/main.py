import asyncio
import logging
import os
import sys

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Роутеры и API
from bot.handlers import client, payments
from bot.api import api_crm, api_get_profile, api_save_profile, api_generate_content, cors_middleware, options_handler

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Например: https://eidos-bot.onrender.com
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_PATH = f"/webhook/{TOKEN}"
APP_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

async def on_startup(bot: Bot):
    if WEBHOOK_URL:
        await bot.set_webhook(APP_URL, drop_pending_updates=True)
        logger.info(f"Вэбхук установлен на: {APP_URL}")
    else:
        logger.info("Вэбхук отключен, запуск через Long Polling...")

async def health_check(request):
    return web.Response(text="OK", status=200)

async def main():
    if not TOKEN:
        logger.error("BOT_TOKEN не установлен!")
        return

    # Инициализация бота и диспетчера
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(client.router)
    dp.include_router(payments.router)

    # Настройка aiohttp приложения
    app = web.Application(middlewares=[cors_middleware])
    app['bot'] = bot # Пробрасываем бота для фоновых задач

    # API endpoints для TWA
    app.router.add_options('/api/crm', options_handler)
    app.router.add_get('/api/crm', api_crm)

    app.router.add_options('/api/profile', options_handler)
    app.router.add_get('/api/profile', api_get_profile)
    app.router.add_post('/api/profile', api_save_profile)

    app.router.add_options('/api/generate', options_handler)
    app.router.add_post('/api/generate', api_generate_content)

    # Health check endpoint для Render
    app.router.add_get('/', health_check)
    app.router.add_get('/healthz', health_check)

    if WEBHOOK_URL:
        # Настройка вэбхуков
        dp.startup.register(on_startup)
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        # Запуск aiohttp сервера
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
        logger.info(f"Запуск aiohttp сервера (Webhook) на порту {PORT}...")
        await site.start()

        # Поддерживаем работу скрипта
        await asyncio.Event().wait()
    else:
        # Запуск в режиме Long Polling (для локальной разработки)
        # Параллельно запускаем веб-сервер aiohttp для health_check и API
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
        logger.info(f"Запуск aiohttp сервера на порту {PORT}...")
        await site.start()

        logger.info("Запуск бота в режиме Polling...")
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot, handle_signals=False)
        finally:
            await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
