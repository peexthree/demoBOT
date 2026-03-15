with open('bot/main.py', 'r') as f:
    content = f.read()

old_startup = """
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
"""

new_startup = """
        async def delayed_polling(app):
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

        async def on_startup_polling(app):
            app['delayed_task'] = asyncio.create_task(delayed_polling(app))

        app.on_startup.append(on_startup_polling)

        async def on_shutdown_polling(app):
            logging.info("Stopping polling task...")
            if 'delayed_task' in app:
                app['delayed_task'].cancel()
            if 'polling_task' in app:
                app['polling_task'].cancel()
            await bot.session.close()
"""

if old_startup in content:
    print("Found exact block, replacing...")
    content = content.replace(old_startup, new_startup)
else:
    print("Exact block not found! Reverting to robust replacement.")
    content = content.replace(
        "        async def on_startup_polling(app):",
        "        async def delayed_polling(app):"
    )
    content = content.replace(
        "        app.on_startup.append(on_startup_polling)",
        "        async def on_startup_polling(app):\n            app['delayed_task'] = asyncio.create_task(delayed_polling(app))\n\n        app.on_startup.append(on_startup_polling)"
    )
    content = content.replace(
        "            if 'polling_task' in app:\n                app['polling_task'].cancel()",
        "            if 'delayed_task' in app:\n                app['delayed_task'].cancel()\n            if 'polling_task' in app:\n                app['polling_task'].cancel()"
    )

with open('bot/main.py', 'w') as f:
    f.write(content)
