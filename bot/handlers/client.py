from aiogram import Router, F
from aiogram.types import Message
import json
from db import save_lead_request

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

        elif parsed_data.get('action') == 'broadcast':
            text = parsed_data.get('payload')
            response_text = f"📢 *Демо-рассылка*\n\n{text}\n\n(Всем пользователям якобы ушло это сообщение)"
            await message.answer(response_text, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"Ошибка обработки: {e}")
