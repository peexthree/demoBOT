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

from middlewares import SmartStalkerMiddleware
from handlers import base, client, admin, demo

load_dotenv()

logging.basicConfig(level=logging.INFO)

async def health_check(request):
    return web.Response(text="OK")

def main():
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
    dp.update.middleware(SmartStalkerMiddleware())

    # Регистрация роутеров
    dp.include_router(base.router)
    dp.include_router(client.router)
    dp.include_router(admin.router)
    dp.include_router(demo.router)

    logging.info("Starting bot...")

    app = web.Application()
    app.router.add_get("/healthz", health_check)
    app.router.add_get("/health", health_check) # Добавлено для монитора
    app.router.add_get("/", health_check)
    port = int(os.getenv("PORT", 10000))

    if is_mock:
         logging.info("Mock mode, skipping polling but starting health check...")
         logging.info(f"Health check server running on 0.0.0.0:{port} in mock mode")
         web.run_app(app, host="0.0.0.0", port=port)
         return

    webhook_url = os.getenv("WEBHOOK_URL")

    if webhook_url:
        webhook_path = "/webhook"
        full_webhook_url = f"{webhook_url.rstrip('/')}{webhook_path}"
        logging.info(f"Setting webhook to {full_webhook_url}")

        # Регистрируем хэндлер для вебхука
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=webhook_path)

        # Настраиваем приложение (добавляет стартап/шаттдаун коллбэки)
        setup_application(app, dp, bot=bot)

        # Добавляем синхронный вызов bot.set_webhook() в startup
        async def on_startup_webhook(app):
            await bot.set_webhook(full_webhook_url)
        app.on_startup.append(on_startup_webhook)

        logging.info(f"Webhook server running on 0.0.0.0:{port}")
        web.run_app(app, host="0.0.0.0", port=port)

    else:
        logging.info("WEBHOOK_URL not set, using long polling")

        async def on_startup_polling(app):
            # Задержка для предотвращения TelegramConflictError при zero-downtime деплоях
            # Старая инстанция бота завершает работу не сразу.
            logging.info("Delaying polling start for 15 seconds to avoid conflicts with stopping instances...")
            await asyncio.sleep(15)

            # Удаляем вебхук на всякий случай
            try:
                await bot.delete_webhook(drop_pending_updates=True)
            except Exception as e:
                logging.error(f"Could not delete webhook: {e}")

            # Запускаем поллинг как фоновую задачу
            logging.info("Starting polling task...")
            app['polling_task'] = asyncio.create_task(dp.start_polling(bot))

        app.on_startup.append(on_startup_polling)

        async def on_shutdown_polling(app):
            logging.info("Stopping polling task...")
            if 'polling_task' in app:
                app['polling_task'].cancel()
            await bot.session.close()

        app.on_shutdown.append(on_shutdown_polling)


        logging.info(f"Health check server running on 0.0.0.0:{port}")
        web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
