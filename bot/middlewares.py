import os
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, CallbackQuery, Message

class ShadowTrackingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        # Перехватываем CallbackQuery (клики по инлайн кнопкам)
        if event.callback_query:
            await self._notify_admin(event.callback_query.from_user.username, data.get("bot"))

        # Перехватываем WebApp данные (если лид тестирует TWA)
        elif event.message and event.message.web_app_data:
            await self._notify_admin(event.message.from_user.username, data.get("bot"))

        return await handler(event, data)

    async def _notify_admin(self, username: str, bot):
        admin_id = os.getenv("ADMIN_ID")
        if not admin_id:
            return

        username_display = f"@{username}" if username else "Неизвестный пользователь"
        message_text = f"🔥 Лид {username_display} сейчас тестирует админ-панель или систему!"

        try:
            await bot.send_message(chat_id=admin_id, text=message_text)
        except Exception as e:
            logging.error(f"Не удалось отправить уведомление админу: {e}")
