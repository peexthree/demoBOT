import os
import asyncio
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.demo import get_main_menu_keyboard, get_twa_reply_keyboard

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message, command: CommandObject):
    # Deep Linking
    if command.args:
        args = command.args
        if args == "demo_stomatology":
             await message.answer(
                 "🦷 <b>Запуск персонального демо: Стоматология</b>\n\n"
                 "Инициализация процессов...",
                 parse_mode="HTML"
             )
             await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
             await asyncio.sleep(2)
             await message.answer(
                 "Приветствую! Я умный ассистент клиники 'Здоровая Улыбка'.\n\n"
                 "Могу записать вас на прием, рассказать о ценах или перевести на врача.\n"
                 "Что вас интересует?",
                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="Записаться на чистку (Демо)", callback_data="demo_stoma_booking")],
                     [InlineKeyboardButton(text="🔙 В главное меню системы", callback_data="main_menu")]
                 ]),
                 parse_mode="HTML"
             )
             return

    # Обычный старт
    # Feature 9: Rich Media Greeting
    from datetime import datetime
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"

    welcome_text = (
        f"🌆 <b>{greeting}, {message.from_user.first_name}!</b>\n\n"
        "<b>Eidos System</b> — цифровой шоурум Архитектора систем автоматизации.\n\n"
        "💡 <i>Я не просто бот, я — демонстрация того, как ваш бизнес может работать 24/7 без участия человека.</i>\n\n"
        "<b>Мои возможности:</b>\n"
        "🔹 Генерация лидов и сбор заявок\n"
        "🔹 Умный ИИ-ассистент с пониманием голоса и фото\n"
        "🔹 Интеграция с CRM и аналитикой\n\n"
        "👇 <b>Выберите раздел для погружения:</b>"
    )

    markup = get_main_menu_keyboard()

    # If the user has a profile photo or we just send an HTML message (simulating a banner with rich text)
    await message.answer(welcome_text, reply_markup=markup, parse_mode="HTML")
