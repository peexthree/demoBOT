import os
import logging
import asyncio
import time
from datetime import datetime
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update

from bot.db import save_event

# Глобальный словарь для отслеживания пути пользователя
# Структура: { user_id: { "username": str, "path": ["action1", "action2"], "last_activity": timestamp } }
user_sessions: Dict[int, Dict[str, Any]] = {}

# Time to live for a session in seconds (e.g., 2 hours)
SESSION_TTL = 7200

class SmartStalkerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:

        self._cleanup_sessions()

        user_id = None
        username = None
        action = None

        # Определяем пользователя и действие
        if event.callback_query:
            user_id = event.callback_query.from_user.id
            username = event.callback_query.from_user.username
            action = f"кнопка: {event.callback_query.data}"
        elif event.message:
            user_id = event.message.from_user.id
            username = event.message.from_user.username
            # Фильтруем системные сообщения и просто текст
            if event.message.text and event.message.text.startswith('/'):
                action = f"команда: {event.message.text}"
            elif event.message.web_app_data:
                 action = f"web_app_data: {event.message.web_app_data.data}"
            elif event.message.text:
                action = f"сообщение: {event.message.text[:20]}..."

        if user_id and action:
             # 1. Сохраняем в Supabase (сырые данные для аналитики)
             event_data = {
                 "user_id": user_id,
                 "username": username or "Unknown",
                 "action": action
             }

             # Отправляем в БД асинхронно через to_thread, не блокируя event loop
             asyncio.create_task(self._safe_save_event(event_data))

             # 2. Обновляем сессию в памяти для умных алертов
             now = time.time()

             if user_id not in user_sessions:
                 user_sessions[user_id] = {
                     "username": username or str(user_id),
                     "path": [],
                     "last_activity": now,
                     "alert_sent": False
                 }

             session = user_sessions[user_id]
             session["path"].append(action)
             session["last_activity"] = now

             # Ограничиваем длину сохраняемого пути
             if len(session["path"]) > 50:
                 session["path"] = session["path"][-50:]

             # 3. Проверка триггеров
             bot = data.get("bot")
             if bot:
                 await self._check_triggers(user_id, session, bot)

        return await handler(event, data)

    def _cleanup_sessions(self):
        """Removes inactive sessions to prevent memory leaks."""
        now = time.time()
        # Create a list of keys to delete to avoid dictionary changed size during iteration error
        stale_users = [
            uid for uid, session in user_sessions.items()
            if now - session.get("last_activity", 0) > SESSION_TTL
        ]
        for uid in stale_users:
            del user_sessions[uid]

    async def _safe_save_event(self, data: dict):
         # Обертка для вызова синхронного Supabase в фоне,
         # чтобы не блокировать event loop
         try:
             await save_event(data)
         except Exception as e:
             logging.error(f"Failed to save event to DB: {e}")

    async def _check_triggers(self, user_id: int, session: dict, bot):
        admin_id = os.getenv("ADMIN_ID")
        if not admin_id:
            return

        # Триггер: Пользователь смотрит цены или контакты
        last_action = session["path"][-1] if session["path"] else ""

        trigger_hit = False
        interest_level = "Обычный"

        if "demo_pricing" in last_action:
            trigger_hit = True
            interest_level = "Высокий (Смотрит Цены 💸)"
        elif "demo_contact" in last_action:
            trigger_hit = True
            interest_level = "Критический (Хочет связаться 📞)"

        if trigger_hit and not session.get("alert_sent"):
             # Формируем цепочку пути (последние 5 действий)
             recent_path = " -> ".join([a.replace("кнопка: ", "") for a in session["path"][-5:]])

             username_display = f"@{session['username']}" if not session['username'].isdigit() else f"ID:{session['username']}"

             message_text = (
                 f"⚠️ <b>Умный Алерт (Stalker)</b>\n\n"
                 f"Лид {username_display} активировал важный триггер!\n"
                 f"Уровень интереса: <b>{interest_level}</b>\n\n"
                 f"Последние действия:\n`{recent_path}`"
             )

             try:
                 await bot.send_message(chat_id=admin_id, text=message_text, parse_mode="HTML")
                 # Флаг, чтобы не спамить при повторном клике на ту же кнопку подряд
                 session["alert_sent"] = True
             except Exception as e:
                 logging.error(f"Не удалось отправить уведомление админу: {e}")

        # Сбрасываем алерт, если он ушел с важных кнопок (чтобы при возврате снова уведомить)
        if not trigger_hit and session.get("alert_sent"):
             session["alert_sent"] = False
