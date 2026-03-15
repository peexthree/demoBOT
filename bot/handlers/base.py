import os
import asyncio
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.demo import get_main_menu_keyboard

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message, command: CommandObject):
    # Deep Linking
    if command.args:
        args = command.args
        if args == "demo_stomatology":
             await message.answer(
                 "🦷 *Запуск персонального демо: Стоматология*\n\n"
                 "Инициализация процессов...",
                 parse_mode="Markdown"
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
                 parse_mode="Markdown"
             )
             return

    # Обычный старт
    welcome_text = (
        "🤖 *Eidos System* — цифровой шоурум Архитектора.\n\n"
        "Вы находитесь в демо-версии премиальной системы автоматизации бизнеса.\n\n"
        "Выберите уровень доступа:"
    )

    markup = get_main_menu_keyboard()

    await message.answer(welcome_text, reply_markup=markup, parse_mode="Markdown")
