from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from bot.db import save_transaction, grant_pro_status, save_event
import os
import logging

router = Router()

UKASSA_TOKEN = os.getenv("UKASSA_TOKEN")
STARS_TOKEN = os.getenv("STARS_TOKEN", "") # Если пуст, значит не используется провайдер токена, а напрямую Stars

PRO_PRICE_RUB = 1990
PRO_PRICE_STARS = 1500

@router.callback_query(F.data == "buy_pro")
async def process_buy_pro(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    await save_event({"user_id": user_id, "action": "checkout_started"})

    # Отправляем инвойс в Stars или ЮKassa
    # В MVP приоритет - Telegram Stars, так как это нативно

    title = "Eidos PRO Подписка (30 дней)"
    description = (
        "Разблокирует все PRO-инструменты:\n"
        "- Разведка конкурентов\n"
        "- Growth OS (дерево гипотез)\n"
        "- Маркетинговые стратегии\n"
        "- Безлимитные токены ИИ"
    )
    payload = "eidos_pro_30_days"
    currency = "XTR" # Telegram Stars
    prices = [LabeledPrice(label="PRO (30 дней)", amount=PRO_PRICE_STARS)]

    try:
        await bot.send_invoice(
            chat_id=user_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=STARS_TOKEN, # Пусто для Stars
            currency=currency,
            prices=prices,
            start_parameter="pro-subscription",
            is_flexible=False
        )
        await callback.answer()
    except Exception as e:
        logging.error(f"Error sending invoice: {e}")
        await callback.message.answer("Оплата сейчас недоступна. Попробуйте позже.")


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    payment_info = message.successful_payment

    payment_id = payment_info.telegram_payment_charge_id
    amount = payment_info.total_amount
    currency = payment_info.currency

    # 1. Сохраняем транзакцию
    await save_transaction(
        user_id=user_id,
        amount=amount,
        currency=currency,
        provider="telegram_stars" if currency == "XTR" else "yookassa",
        payment_id=payment_id,
        status="success"
    )

    # 2. Выдаем PRO статус
    await grant_pro_status(user_id, days=30)

    # 3. Событие
    await save_event({"user_id": user_id, "action": "checkout_success", "metadata": {"payment_id": payment_id}})

    await message.answer(
        "💎 <b>Оплата успешно завершена!</b>\n\n"
        "Ваш аккаунт получил статус PRO. Все премиум-инструменты и стратегии разблокированы.\n"
        "Запустите платформу, чтобы начать работу на новом уровне.",
        parse_mode="HTML"
    )
