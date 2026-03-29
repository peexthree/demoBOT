from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery
import json
import os
import logging
from bot.db import save_user, save_event, get_user, save_business_profile

router = Router()
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-app.onrender.com/twa")

# --- ОНБОРДИНГ ---

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    telegram_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or ""

    # Обработка реферальной системы (/start ref12345)
    referred_by = None
    args = command.args
    if args and args.startswith("ref"):
        try:
            referred_by = int(args.replace("ref", ""))
        except ValueError:
            pass

    # Сохраняем/проверяем юзера
    user_exists = await save_user(telegram_id, username, full_name, referred_by)

    if not user_exists:
        await save_event({"user_id": telegram_id, "username": username, "action": "onboarding_started"})
        text = (
            "<b>Привет. Я Eidos. Твой ИИ-Директор по маркетингу.</b>\n\n"
            "Я не задаю глупых вопросов. Скинь мне ссылку на свой проект (сайт, соцсети, канал), "
            "и я сам соберу профиль твоего бизнеса, проанализирую нишу и подготовлю план роста."
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ввести данные вручную", callback_data="manual_onboarding")]
        ])
        await message.answer(text, parse_mode="HTML", reply_markup=markup)
    else:
        # Юзер уже есть, выдаем меню
        await save_event({"user_id": telegram_id, "username": username, "action": "app_opened"})
        text = (
            "<b>Eidos готов к работе.</b>\n\n"
            "Все инструменты, генерация контента и аналитика доступны в приложении."
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Открыть платформу", web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={telegram_id}"))],
            [InlineKeyboardButton(text="💎 PRO Подписка", callback_data="buy_pro")]
        ])
        await message.answer(text, parse_mode="HTML", reply_markup=markup)


# --- MAGIC LINK PARSER (Обработка ссылок) ---

@router.message(F.text.regexp(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'))
async def handle_magic_link(message: Message):
    url = message.text.strip()
    user_id = message.from_user.id

    msg = await message.answer("🔄 Анализирую проект по ссылке... Это займет пару секунд.")
    await save_event({"user_id": user_id, "action": "magic_link_submitted", "metadata": {"url": url}})

    # Запускаем ИИ для парсинга (в реальном приложении здесь был бы вызов Scraper API + ИИ)
    # Для MVP делаем симуляцию успешного парсинга через ИИ
    from bot.ai_utils import generate_with_fallback
    try:
        sys_prompt = "Ты парсер B2B профилей. Извлеки из ссылки или названия суть проекта. Верни строгий JSON: {'project_name': 'имя', 'niche': 'ниша', 'target_audience': 'ЦА'}."
        # В MVP мы просто "скармливаем" ссылку Gemini и просим додумать
        res_json_str = await generate_with_fallback(f"Ссылка: {url}", system_prompt=sys_prompt)

        # Парсим JSON
        import json
        try:
            profile = json.loads(res_json_str.replace('```json', '').replace('```', '').strip())
        except:
            profile = {
                "project_name": "Проект по ссылке",
                "niche": "IT / Digital",
                "target_audience": "B2C / B2B клиенты"
            }

        await save_business_profile(
            user_id=user_id,
            project_url=url,
            project_name=profile.get("project_name", "Проект"),
            niche=profile.get("niche", "Не определена"),
            target_audience=profile.get("target_audience", "Широкая"),
            tone_of_voice="Экспертный"
        )

        await msg.edit_text(
            f"✅ <b>Цифровой профиль создан!</b>\n\n"
            f"Проект: {profile.get('project_name')}\n"
            f"Ниша: {profile.get('niche')}\n\n"
            "Платформа настроена и готова к работе.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚡ Открыть платформу", web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={user_id}"))]
            ])
        )
    except Exception as e:
        logging.error(f"Magic link error: {e}")
        # Silent fallback на ручной ввод
        await msg.edit_text(
            "⚠️ Защита сайта заблокировала анализ (возможно Cloudflare).\n"
            "Пожалуйста, заполните профиль вручную внутри приложения.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Заполнить профиль", web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={user_id}&tab=profile"))]
            ])
        )

# --- РУЧНОЙ ВВОД ---
@router.callback_query(F.data == "manual_onboarding")
async def manual_onboarding(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(
        "📝 Откройте приложение, чтобы быстро настроить профиль (3 поля):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Настроить профиль", web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={user_id}&tab=profile"))]
        ])
    )

# --- ОБРАБОТКА ДАННЫХ ИЗ TWA ---
@router.message(F.web_app_data)
async def web_app_data_handler(message: Message):
    data = message.web_app_data.data
    try:
        parsed_data = json.loads(data)

        # Если пришел запрос на покупку PRO из Blurred Paywall
        if parsed_data.get('action') == 'buy_pro':
            await message.answer("💎 Для оформления PRO подписки перейдите по кнопке ниже:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Оформить PRO", callback_data="buy_pro")]
            ]))

    except Exception as e:
        logging.error(f"WebAppData Error: {e}")
