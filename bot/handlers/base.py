import os
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.demo import get_demo_keyboard

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    # Убрали внешние ссылки на WebApp, делаем все нативно в Telegram.
    welcome_text = (
        "🤖 *Eidos System* — премиальная система автоматизации бизнеса внутри Telegram.\n\n"
        "Мы перенесли весь функционал прямо в чат, без сторонних сайтов!\n\n"
        "Выберите роль, чтобы протестировать систему в действии:"
    )

    markup = get_demo_keyboard("guest")

    await message.answer(welcome_text, reply_markup=markup, parse_mode="Markdown")
