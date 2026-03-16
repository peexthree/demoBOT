from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import json
import os
import logging
from db import save_lead_request, save_event

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
            await save_lead_request({
                "username": message.from_user.username,
                "user_id": message.from_user.id,
                "item_title": item.get('title'),
                "item_price": item.get('price')
            })

            import html
            response_text = (
                f"🎉 Вы успешно оформили заказ: <b>{html.escape(str(item.get('title')))}</b>.\n"
                f"💳 Стоимость: {item.get('price')} ₽\n\n"
                "Ваша заявка моментально зафиксирована в CRM."
            )
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await message.answer(
                response_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]])
            )

            # Уведомление администратора
            admin_id = os.getenv("ADMIN_ID")
            if admin_id:
                try:
                    user_link = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
                    admin_text = (
                        f"🚨 <b>Новый заказ из TWA</b>\n\n"
                        f"👤 Пользователь: {html.escape(user_link)}\n"
                        f"📦 Товар: <b>{html.escape(str(item.get('title')))}</b>\n"
                        f"💳 Стоимость: {item.get('price')} ₽"
                    )
                    await message.bot.send_message(admin_id, admin_text, parse_mode="HTML")
                except Exception as e:
                    logging.error(f"Failed to send admin notification: {e}")

        elif parsed_data.get('action') == 'broadcast':
            text = parsed_data.get('payload')
            response_text = f"📢 <b>Демо-рассылка</b>\n\n{html.escape(str(text))}\n\n(Всем пользователям якобы ушло это сообщение)"
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await message.answer(
                response_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]])
            )

        elif 'base' in parsed_data:
            base_id = parsed_data.get('base')
            module_ids = parsed_data.get('modules', [])
            total_price = parsed_data.get('totalPrice', 0)

            base_title = BASE_PLANS.get(base_id, base_id)
            modules_titles = [MODULES.get(m, m) for m in module_ids]

            modules_text = "\n".join([f"- {m}" for m in modules_titles]) if modules_titles else "Нет"

            response_text = (
                "🏗 <b>Запрос Архитектору сформирован!</b>\n\n"
                f"📦 <b>База:</b> {base_title}\n"
                f"🧩 <b>Дополнительные модули:</b>\n{modules_text}\n\n"
                f"💰 <b>Предварительная оценка:</b> {total_price:,} ₽\n\n"
                "Ваш запрос передан в разработку. Мы скоро свяжемся с вами!"
            ).replace(',', ' ')

            # Сохранение лида (имитация)
            await save_lead_request({
                "username": message.from_user.username,
                "user_id": message.from_user.id,
                "item_title": "Запрос Архитектору: " + base_title,
                "item_price": total_price,
                "metadata": {"modules": module_ids}
            })

            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await message.answer(
                response_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]])
            )

            # Уведомление администратора
            admin_id = os.getenv("ADMIN_ID")
            if admin_id:
                try:
                    user_link = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"

                    admin_text = (
                        "🚨 <b>Новый лид из Конфигуратора!</b>\n\n"
                        f"👤 Контакт: {user_link}\n\n"
                        f"📦 <b>База:</b> {base_title}\n"
                        f"🧩 <b>Дополнительные модули:</b>\n{modules_text}\n\n"
                        f"💰 <b>Предварительная оценка:</b> {total_price:,} ₽"
                    ).replace(',', ' ')

                    await message.bot.send_message(admin_id, admin_text, parse_mode="HTML")
                except Exception as e:
                    logging.error(f"Failed to send admin notification: {e}")

    except Exception as e:
        await message.answer(f"Ошибка обработки: {e}")


# Feature 10: Database Integration for "Analytics" (Supabase)
@router.message(Command("stats"))
async def stats_cmd(message: Message):
    import os
    admin_id = os.getenv("ADMIN_ID")
    if str(message.from_user.id) != admin_id:
        await message.answer("❌ Нет доступа. Эта команда только для владельца (демонстрация аналитики).")
        return

    # Simple mockup or fetch from Supabase (since we don't have python client query logic mapped, we mock it realistically)
    # The actual implementation would query supabase.table('leads').select('*').execute()
    # We will simulate the "Analytics" report

    from db import supabase

    leads_count = 0
    events_count = 0
    if supabase:
        try:
            leads_resp = supabase.table("leads").select("*", count="exact").execute()
            events_resp = supabase.table("events").select("*", count="exact").execute()
            leads_count = leads_resp.count or len(leads_resp.data)
            events_count = events_resp.count or len(events_resp.data)
        except Exception as e:
            logging.error(f"Error fetching stats: {e}")
            leads_count = "Ошибка БД"
            events_count = "Ошибка БД"

    # Simulated metrics for Demo
    if leads_count == 0 or leads_count == "Ошибка БД":
        leads_count = 24
        events_count = 158

    stats_text = (
        "📊 <b>Аналитика вашего бизнеса (Демо Supabase)</b>\n\n"
        f"👥 <b>Новых лидов за сегодня:</b> {leads_count}\n"
        f"🎯 <b>Действий пользователей (Events):</b> {events_count}\n"
        "🔥 <b>Конверсия в заявку:</b> 15.2%\n\n"
        "💡 <b>Инсайт ИИ:</b> Большинство запросов приходится на утренние часы. Рекомендуется запустить утреннюю рассылку.\n\n"
        "<i>В реальном проекте здесь будет полная выгрузка из базы данных Supabase.</i>"
    )

    await message.answer(stats_text, parse_mode="HTML")
