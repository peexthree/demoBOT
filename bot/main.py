import asyncio
import logging
import os
import sys

# Добавляем корневую папку bot в sys.path, чтобы python находил модули
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv

from middlewares import ShadowTrackingMiddleware
from handlers import base, client, admin

load_dotenv()

logging.basicConfig(level=logging.INFO)


async def health_check(request):
    return web.Response(text="OK")

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    is_mock = False
    if not bot_token:
        # Для локальных тестов
        logging.warning("BOT_TOKEN не найден, используем моковый токен.")
        bot_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi" # valid format
        is_mock = True

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    # Регистрация Middlewares
    dp.update.middleware(ShadowTrackingMiddleware())

    # Регистрация роутеров
    dp.include_router(base.router)
    dp.include_router(client.router)
    dp.include_router(admin.router)

    logging.info("Starting bot...")

    if is_mock:
         logging.info("Mock mode, skipping polling but starting health check...")
         # Запускаем минимальный сервер для health checks (Render требует порт)
         app = web.Application()
         app.router.add_get("/healthz", health_check)
         port = int(os.getenv("PORT", 10000))
         runner = web.AppRunner(app)
         await runner.setup()
         site = web.TCPSite(runner, host="0.0.0.0", port=port)
         await site.start()

         logging.info(f"Health check server running on 0.0.0.0:{port} in mock mode")
         await asyncio.Event().wait()
         return

    webhook_url = os.getenv("WEBHOOK_URL")

    if webhook_url:
        webhook_path = "/webhook"
        full_webhook_url = f"{webhook_url.rstrip('/')}{webhook_path}"
        logging.info(f"Setting webhook to {full_webhook_url}")

        # Устанавливаем вебхук
        await bot.set_webhook(full_webhook_url)

        # Настраиваем aiohttp приложение
        app = web.Application()

        # Регистрируем хэндлер для вебхука
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=webhook_path)

        # Добавляем health check (Render часто требует этого)
        app.router.add_get("/healthz", health_check)

        # Настраиваем приложение (добавляет стартап/шаттдаун коллбэки)
        setup_application(app, dp, bot=bot)

        # Запускаем aiohttp сервер
        port = int(os.getenv("PORT", 10000))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=port)
        await site.start()

        logging.info(f"Webhook server running on 0.0.0.0:{port}")

        # Бесконечный цикл, чтобы программа не завершилась
        await asyncio.Event().wait()
    else:
        logging.info("WEBHOOK_URL not set, using long polling")
        # Удаляем вебхук на всякий случай
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception as e:
            logging.error(f"Could not delete webhook: {e}")

        # Запускаем минимальный сервер для health checks (Render требует порт)
        app = web.Application()
        app.router.add_get("/healthz", health_check)
        port = int(os.getenv("PORT", 10000))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=port)
        await site.start()

        logging.info(f"Health check server running on 0.0.0.0:{port}")

        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Error during polling: {e}")

if __name__ == "__main__":
    asyncio.run(main())
