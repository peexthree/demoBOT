import os
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    # Получаем URL статического сайта из Render Environment
    web_app_url = os.getenv("WEBAPP_URL", "https://render.com")

    # Имитация AI видео аватара (мы отправляем эффектный текст или гифку, но так как гифки нет - эмодзи)
    welcome_text = (
        "🤖 *Eidos System* — премиальная система автоматизации.\n\n"
        "Выберите режим, чтобы протестировать систему в действии:"
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Я — Клиент", web_app=WebAppInfo(url=f"{web_app_url}?start_param=client"))],
        [InlineKeyboardButton(text="👑 Я — Владелец бизнеса", web_app=WebAppInfo(url=f"{web_app_url}?start_param=admin"))]
    ])

    await message.answer(welcome_text, reply_markup=markup, parse_mode="Markdown")
