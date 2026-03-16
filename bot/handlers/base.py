import os
import asyncio
from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.states import DemoStates
from bot.db import save_event

from bot.handlers.demo import get_main_menu_keyboard, get_twa_reply_keyboard

router = Router()

@router.message(CommandStart())
async def start_cmd(message: types.Message, command: CommandObject, state: FSMContext):
    # User analytics
    user_exists = False
    try:
        from bot.db import save_user
        user_exists = await save_user(
            message.from_user.id,
            message.from_user.username or "",
            message.from_user.first_name or "",
            message.from_user.last_name or ""
        )
    except Exception as e:
        print(f"User analytics error: {e}")

    await save_event({"user_id": message.from_user.id, "action": "start_cmd"})

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
                     [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
                 ]),
                 parse_mode="HTML"
             )
             return
        elif args.startswith("ref_"):
            ref_id = args.split("_")[1]
            await save_event({"user_id": message.from_user.id, "action": "referral_join", "metadata": {"ref_id": ref_id}})
            await message.answer(
                f"🎉 <b>Добро пожаловать по приглашению!</b>\n\nВам доступен специальный бонус при заказе системы.",
                parse_mode="HTML"
            )

    # Обычный старт - Многоуровневый онбординг (Прогрев)
    from datetime import datetime
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"

    if not user_exists:
        welcome_text = (
            "<b>СТАТУС: СИСТЕМА АКТИВИРОВАНА</b>\n\n"
            "Добро пожаловать в технологический шоурум. Это интерактивный прототип вашей будущей цифровой экосистемы.\n\n"
            "Почему это не «просто бот»:\n\n"
            "▪️ <b>100% Владение:</b> Код принадлежит вам. Никакой абонентской платы разработчику.\n"
            "▪️ <b>Масштабируемость:</b> Система на чистом Python готова к нагрузкам в тысячи заказов.\n"
            "▪️ <b>Интеллект:</b> Возможность интеграции ИИ-менеджеров (Gemini/GPT) для общения с вашими клиентами.\n\n"
            "<b>Протестируйте ключевые узлы инфраструктуры:</b>\n\n"
            f"🌆 <b>{greeting}, {message.from_user.first_name}!</b>\n"
            "Для того, чтобы показать вам наиболее релевантные возможности, подскажите, <b>в какой сфере вы работаете?</b>"
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💼 Услуги (Юристы, Консалтинг)", callback_data="onboard_lawyer")],
            [InlineKeyboardButton(text="🏥 Медицина и Стоматология", callback_data="onboard_dentist")],
            [InlineKeyboardButton(text="🚗 Автобизнес (СТО, Продажи)", callback_data="onboard_auto")],
            [InlineKeyboardButton(text="💇‍♀️ Бьюти-сфера (Салоны)", callback_data="onboard_beauty")],
            [InlineKeyboardButton(text="🏢 Другое (Показать всё меню)", callback_data="main_menu")]
        ])
    else:
        # If user exists, skip the questionnaire and show the main menu
        welcome_text = (
            "<b>СТАТУС: СИСТЕМА АКТИВИРОВАНА</b>\n\n"
            "Добро пожаловать в технологический шоурум. Это интерактивный прототип вашей будущей цифровой экосистемы.\n\n"
            "Почему это не «просто бот»:\n\n"
            "▪️ <b>100% Владение:</b> Код принадлежит вам. Никакой абонентской платы разработчику.\n"
            "▪️ <b>Масштабируемость:</b> Система на чистом Python готова к нагрузкам в тысячи заказов.\n"
            "▪️ <b>Интеллект:</b> Возможность интеграции ИИ-менеджеров (Gemini/GPT) для общения с вашими клиентами.\n\n"
            "<b>Протестируйте ключевые узлы инфраструктуры:</b>\n\n"
            f"🌆 <b>С возвращением, {message.from_user.first_name}!</b>\n"
            "Выберите раздел для изучения:"
        )
        markup = get_main_menu_keyboard()

    # If the user has a profile photo or we just send an HTML message (simulating a banner with rich text)
    # First send the persistent keyboard, then the inline markup
    await message.answer("Инициализация интерфейса...", reply_markup=get_twa_reply_keyboard())
    await message.answer(welcome_text, reply_markup=markup, parse_mode="HTML")

@router.callback_query(F.data.startswith("onboard_"))
async def onboard_niche(callback: types.CallbackQuery, state: FSMContext):
    niche = callback.data.split("_")[1]

    await save_event({"user_id": callback.from_user.id, "action": "onboarding_niche_selected", "metadata": {"niche": niche}})

    from bot.handlers.demo import niche_selected

    # We need to rewrite the callback data to match demo format
    class FakeCallback:
        def __init__(self, data, message, from_user, bot):
            self.data = data
            self.message = message
            self.from_user = from_user
            self.bot = bot

        async def answer(self, *args, **kwargs):
            pass

    fake_cb = FakeCallback(f"niche_{niche}", callback.message, callback.from_user, callback.bot)
    await niche_selected(fake_cb, state)
    await callback.answer()
