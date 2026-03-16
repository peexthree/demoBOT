from aiogram import Router, F
from aiogram.types import Message
import json
import os
import logging
from db import save_lead_request

BASE_PLANS = {
    "base": "База (Лидогенерация)",
    "standart": "Стандарт (Управление и БД)",
    "business": "Бизнес (Сложная CRM)"
}

MODULES = {
    "ai": "Интеграция ИИ (ChatGPT/Gemini)",
    "payment": "Модуль приема платежей (Эквайринг)",
    "admin": "Админ-панель с аналитикой",
    "video": "Видео-аватар на входе"
}

router = Router()

# Обработчик данных из TWA (оформление заказа)
@router.message(F.web_app_data)
async def web_app_data_handler(message: Message):
    data = message.web_app_data.data
    try:
        parsed_data = json.loads(data)

        if parsed_data.get('action') == 'checkout':
            item = parsed_data.get('payload')

            # Имитация отправки в CRM (Supabase)
            save_lead_request({
                "username": message.from_user.username,
                "user_id": message.from_user.id,
                "item_title": item.get('title'),
                "item_price": item.get('price')
            })

            response_text = (
                f"🎉 Вы успешно оформили заказ: *{item.get('title')}*.\n"
                f"💳 Стоимость: {item.get('price')} ₽\n\n"
                "Ваша заявка моментально зафиксирована в CRM."
            )
            await message.answer(response_text, parse_mode="Markdown")

            # Уведомление администратора
            admin_id = os.getenv("ADMIN_ID")
            if admin_id:
                try:
                    user_link = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
                    admin_text = (
                        f"🚨 *Новый заказ из TWA*\n\n"
                        f"👤 Пользователь: {user_link}\n"
                        f"📦 Товар: *{item.get('title')}*\n"
                        f"💳 Стоимость: {item.get('price')} ₽"
                    )
                    await message.bot.send_message(admin_id, admin_text, parse_mode="Markdown")
                except Exception as e:
                    logging.error(f"Failed to send admin notification: {e}")

        elif parsed_data.get('action') == 'broadcast':
            text = parsed_data.get('payload')
            response_text = f"📢 *Демо-рассылка*\n\n{text}\n\n(Всем пользователям якобы ушло это сообщение)"
            await message.answer(response_text, parse_mode="Markdown")

        elif 'base' in parsed_data:
            base_id = parsed_data.get('base')
            module_ids = parsed_data.get('modules', [])
            total_price = parsed_data.get('totalPrice', 0)

            base_title = BASE_PLANS.get(base_id, base_id)
            modules_titles = [MODULES.get(m, m) for m in module_ids]

            modules_text = "\n".join([f"- {m}" for m in modules_titles]) if modules_titles else "Нет"

            response_text = (
                "🏗 *Запрос Архитектору сформирован!*\n\n"
                f"📦 *База:* {base_title}\n"
                f"🧩 *Дополнительные модули:*\n{modules_text}\n\n"
                f"💰 *Предварительная оценка:* {total_price:,} ₽\n\n"
                "Ваш запрос передан в разработку. Мы скоро свяжемся с вами!"
            ).replace(',', ' ')

            # Сохранение лида (имитация)
            save_lead_request({
                "username": message.from_user.username,
                "user_id": message.from_user.id,
                "item_title": "Запрос Архитектору: " + base_title,
                "item_price": total_price,
                "metadata": {"modules": module_ids}
            })

            await message.answer(response_text, parse_mode="Markdown")

            # Уведомление администратора
            admin_id = os.getenv("ADMIN_ID")
            if admin_id:
                try:
                    user_link = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"

                    admin_text = (
                        "🚨 *Новый лид из Конфигуратора!*\n\n"
                        f"👤 Контакт: {user_link}\n\n"
                        f"📦 *База:* {base_title}\n"
                        f"🧩 *Дополнительные модули:*\n{modules_text}\n\n"
                        f"💰 *Предварительная оценка:* {total_price:,} ₽"
                    ).replace(',', ' ')

                    await message.bot.send_message(admin_id, admin_text, parse_mode="Markdown")
                except Exception as e:
                    logging.error(f"Failed to send admin notification: {e}")

    except Exception as e:
        await message.answer(f"Ошибка обработки: {e}")
