from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    await callback.message.answer("📊 Статистика:\n\nПользователей: 142\nЗаказов: 12\n\n(Данные мокаются, но система работает)")
    await callback.answer()
