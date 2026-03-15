import os
import asyncio
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

try:
    import google.generativeai as genai
    API_KEY = os.getenv("API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        model = None
except ImportError:
    model = None

router = Router()

class AIState(StatesGroup):
    waiting_for_question = State()

def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 [ПОСМОТРЕТЬ РЕШЕНИЯ]", callback_data="demo_portfolio")],
        [InlineKeyboardButton(text="⚙️ [ДЕМО-РЕЖИМ: АВТОМАТИЗАЦИЯ]", callback_data="demo_client_path")],
        [InlineKeyboardButton(text="📊 [ЛИЧНЫЙ КАБИНЕТ И АДМИН-ПАНЕЛЬ]", web_app=types.WebAppInfo(url=os.getenv("WEBAPP_URL", "https://eidos-webapp.onrender.com")))],
        [InlineKeyboardButton(text="📑 [ИНВЕСТИЦИОННЫЙ ЧЕК-ЛИСТ]", callback_data="demo_pricing")],
        [InlineKeyboardButton(text="💬 [ОБСУДИТЬ ПРОЕКТ]", url=f"tg://user?id={os.getenv('ADMIN_ID', '0')}")]
    ])

@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🤖 *Eidos System* — цифровой шоурум Архитектора.\n\n"
        "Вы находитесь в демо-версии премиальной системы автоматизации бизнеса.\n\n"
        "Выберите раздел для изучения:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "demo_portfolio")
async def demo_portfolio(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🚀 *Наши Решения и Кейсы*\n\n"
        "Мы внедряем автономные цифровые активы, которые окупаются за 2-3 месяца.\n\n"
        "🔹 *Lizing-Phi* — Автоматизация скоринга и заявок.\n"
        "   _Результат:_ Снизили нагрузку на админа на 70%.\n\n"
        "🔹 *FermerHub* — Платформа-маркетплейс в Telegram.\n"
        "   _Результат:_ Увеличение конверсии на 40% за счет отсутствия регистраций.\n\n"
        "🔹 *Акуленок* — Автоворонка и ИИ-ассистент.\n"
        "   _Результат:_ Круглосуточная обработка лидов, рост LTV.\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "demo_client_path")
async def demo_client_path(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "⚙️ *Демо-режим: Как это видит ваш клиент*\n\n"
        "Система позволяет вашим клиентам получать услуги мгновенно, без скачивания приложений и сложных регистраций.\n\n"
        "Попробуйте сами:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Оформить заказ (Магазин)", callback_data="demo_niche_shop")],
            [InlineKeyboardButton(text="🧠 Задать вопрос ИИ-консультанту", callback_data="demo_ai_ask")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
        ]),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "demo_ai_ask")
async def demo_ai_ask(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🧠 *ИИ-Консультант (Демо)*\n\n"
        "Напишите любой вопрос, связанный с вашим бизнесом. "
        "Наш встроенный ИИ сгенерирует экспертный ответ.\n\n"
        "Жду ваш вопрос:",
        parse_mode="Markdown"
    )
    await state.set_state(AIState.waiting_for_question)
    await callback.answer()

@router.message(AIState.waiting_for_question)
async def handle_ai_question(message: types.Message, state: FSMContext):
    await state.clear()

    status_msg = await message.answer("🔄 Анализирую запрос. Загрузка данных из нейросети...", parse_mode="Markdown")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if model:
        try:
             prompt = f"Ответь на вопрос пользователя профессионально и экспертно в роли бизнес-архитектора систем автоматизации: {message.text}"
             response = await model.generate_content_async(prompt)
             answer_text = response.text
        except Exception as e:
             answer_text = "❌ Ошибка при обращении к ИИ-серверу: " + str(e)
    else:
        await asyncio.sleep(3)
        answer_text = (
            "Это демонстрационный ответ. В реальности здесь ИИ проанализирует "
            f"ваш вопрос ('{message.text}') и выдаст структурированный план действий.\n\n"
            "Интеграция ИИ позволяет закрывать возражения клиентов круглосуточно."
        )

    final_text = f"🧠 *Ответ Архитектора:*\n\n{answer_text}"

    await status_msg.edit_text(
        final_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Вернуться в Демо", callback_data="demo_client_path")],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
        ]),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("demo_niche_"))
async def demo_niche(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🛍 *Оформление заказа*\n\n"
        "Клиент нажимает пару кнопок, выбирает товар и оплачивает внутри Telegram.\n"
        "Весь процесс занимает 30 секунд. Вы мгновенно получаете деньги и уведомление в свою CRM.\n\n"
        "*Это сильно повышает конверсию по сравнению с сайтом.*",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="demo_client_path")]]),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "demo_pricing")
async def demo_pricing(callback: types.CallbackQuery):
    text = (
        "📑 *Инвестиционный Чек-лист*\n\n"
        "Прозрачный расчет стоимости разработки вашего цифрового актива.\n\n"
        "📦 *База [от 15k]* - Идеально для старта. Меню, воронка, сбор лидов.\n"
        "📦 *Стандарт [от 50k]* - Интеграция БД, ИИ, полноценная мини-CRM.\n"
        "📦 *Индивидуальный [от 150k]* - Сложные интеграции, WebApp (TWA), уникальный дизайн.\n\n"
        "_Свяжитесь со мной для точного расчета под ваши задачи._"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Обсудить проект", url=f"tg://user?id={os.getenv('ADMIN_ID', '0')}")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "demo_stoma_booking")
async def demo_stoma_booking(callback: types.CallbackQuery):
    await callback.answer("✅ (Демо) Заявка на чистку принята. Врач скоро свяжется с вами!", show_alert=True)
