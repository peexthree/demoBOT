import html
import os
import asyncio
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from bot.showroom import update_showroom_media
from bot.ai_utils import generate_with_fallback, API_KEY

router = Router()

class AIState(StatesGroup):
    waiting_for_question = State()

def get_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Демонстрация работы с клиентами", callback_data="demo_client_path")],
        [InlineKeyboardButton(text="🌟 ТОЧКИ РОСТА И ИННОВАЦИИ", callback_data="demo_innovations")],
        [InlineKeyboardButton(text="📑 ОЦЕНКА СТОИМОСТИ ВНЕДРЕНИЯ", callback_data="demo_pricing")],
        [InlineKeyboardButton(text="📈 ЛИЧНЫЙ КАБИНЕТ РУКОВОДИТЕЛЯ", callback_data="demo_dashboard")],
        [InlineKeyboardButton(text="🧮 AI-КАЛЬКУЛЯТОР ROI (Окупаемость)", callback_data="demo_roi_start")],
        [InlineKeyboardButton(text="🤝 ПАРТНЕРСКАЯ ПРОГРАММА", callback_data="demo_referral")],
        [InlineKeyboardButton(text="💬 СВЯЗАТЬСЯ С АРХИТЕКТОРОМ", callback_data="contact_architect")]
    ])

def get_twa_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")],
            [KeyboardButton(text="📊 Расчет стоимости внедрения", web_app=types.WebAppInfo(url=os.getenv("WEBAPP_URL", "https://lid-flow.vercel.app/twa")))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery):
    await update_showroom_media(callback, "main_menu",
        "🤖 <b>Eidos System</b> — ваш премиальный цифровой шоурум.\n\n"
        "Добро пожаловать в демо-версию интеллектуальной системы автоматизации бизнеса. Здесь вы на практике увидите, как технологии кратно увеличивают прибыль и снижают издержки.\n\n"
        "Выберите интересующий вас раздел:", get_main_menu_keyboard())
    await callback.answer()

#@router.message(F.text == "Скрыть меню")
async def hide_keyboard_handler(message: types.Message):
    await message.answer("Меню скрыто. Чтобы вернуть его, перезапустите бота командой /start.", reply_markup=ReplyKeyboardRemove())


# Feature 1: Dynamic Niche Selection
from bot.states import DemoStates

@router.callback_query(F.data == "demo_client_path")
async def demo_client_path(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(DemoStates.choosing_niche)
    await update_showroom_media(callback, "demo_client_path", "⚙️ <b>Выберите нишу для демонстрации</b>\n\n"
        "AI моментально адаптируется под любой процесс. Выберите отрасль, чтобы увидеть, как бот общается с клиентами:", InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚖️ Юридические услуги (Консалтинг)", callback_data="niche_lawyer")],
            [InlineKeyboardButton(text="🏥 Медицина и клиники", callback_data="niche_dentist")],
            [InlineKeyboardButton(text="🚗 Автобизнес и СТО", callback_data="niche_auto")],
            [InlineKeyboardButton(text="💅 Сфера услуг и Beauty", callback_data="niche_beauty")],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
        ]))
    await callback.answer()

@router.callback_query(DemoStates.choosing_niche, F.data.startswith("niche_"))
async def niche_selected(callback: types.CallbackQuery, state: FSMContext):

    niche = callback.data.split("_")[1]

    niche_data = {
        "lawyer": ("⚖️ Юридическая компания 'Право и Закон'", "оформлении документов и защите прав"),
        "dentist": ("🏥 Медицина и клиники 'Здоровая Улыбка'", "записи на прием и ценах на лечение"),
        "auto": ("🚗 Автосервис 'Драйв'", "ремонте, запчастях и записи на диагностику"),
        "beauty": ("💅 Сфера услуг и Beauty 'Элеганс'", "услугах, мастерах и записи на процедуры")
    }

    name, spec = niche_data.get(niche, ("Ваш бизнес", "ваших услугах"))
    await state.update_data(niche=niche, niche_name=name)
    await state.set_state(DemoStates.in_niche)

    await update_showroom_media(callback, f"niche_{niche}", f"<i>(Вы вошли в роль клиента)</i>\n\n"
        f"<b>Добро пожаловать в {name}!</b>\n\n"
        f"Я ваш виртуальный помощник. Я могу проконсультировать вас по {spec}, а также записать на удобное время.\n\n"
        "Что вас интересует?", InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Тест ИИ-консультанта (FAQ)", callback_data="demo_ai_ask")],
            [InlineKeyboardButton(text="📷 Распознавание фото (Оценка)", callback_data="demo_vision")],
            [InlineKeyboardButton(text="📄 Авто-обработка документов (PDF)", callback_data="demo_docs")],
            [InlineKeyboardButton(text="🎤 Голосовой прием заявок", callback_data="demo_voice")],
            [InlineKeyboardButton(text="🧮 Интерактивный расчет стоимости", callback_data="demo_calculator")],
            [InlineKeyboardButton(text="🎁 Система лояльности (Промокоды)", callback_data="demo_promo")],
            [InlineKeyboardButton(text="🔙 Сменить нишу", callback_data="demo_client_path")]
        ]))
    await callback.answer()

# Feature 6: Smart FAQ and Memory

@router.callback_query(F.data == "demo_ai_ask")

async def demo_ai_ask(callback: types.CallbackQuery, state: FSMContext):
    await update_showroom_media(callback, "demo_ai_ask", "🧠 <b>ИИ-Консультант (Демо)</b>\n\n"
        "Напишите любой вопрос, связанный с вашей выбранной нишей (или общей автоматизацией). "
        "Попробуйте спросить: 'Какие у вас цены?' или 'Запишите меня на завтра'.\n\n"
        "Жду ваш вопрос:", InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]))
    await state.set_state(DemoStates.waiting_for_question)
    await callback.answer()

@router.message(DemoStates.waiting_for_question, F.text)
async def handle_ai_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес Архитектор")
    history = data.get("history", "")

    status_msg = await message.answer(f"🔄 <i>{niche_name}:</i> Анализирую запрос...", parse_mode="HTML")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if API_KEY:
        try:
             prompt = f"Действуй профессионально в роли ассистента компании {niche_name}. Ответь клиенту на вопрос: {message.text}. Если это запрос на запись или покупку - соглашайся и проси оставить контакт. История: {history}. Ответ должен быть кратким и по делу, не более 50-100 слов. ОТВЕЧАЙ ПРОСТЫМ ТЕКСТОМ БЕЗ MARKDOWN (без звездочек)."
             answer_text = await generate_with_fallback(prompt, user_id=message.from_user.id)

             # Save history
             history += f" User: {html.escape(message.text)}. You: {html.escape(answer_text)}."
             await state.update_data(history=history[-1000:])
        except Exception as e:
             answer_text = "❌ Ошибка при обращении к ИИ-серверу: " + str(e)
    else:
        await asyncio.sleep(2)
        answer_text = f"В реальности ИИ проанализирует запрос '{message.text}' для бизнеса {niche_name} и выдаст ответ, подводящий к продаже или записи."

    final_text = f"🤖 <b>Ответ ассистента ({niche_name}):</b>\n\n{html.escape(answer_text)}"

    if len(final_text) > 4000:
        final_text = final_text[:4000] + "...\n\n[Ответ обрезан]"

    await status_msg.edit_text(
        final_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✍️ Продолжить диалог", callback_data="demo_ai_ask")],
            [InlineKeyboardButton(text="🎯 Оставить заявку (Тест)", callback_data="demo_leave_lead")],
            [InlineKeyboardButton(text="🔙 Сменить нишу", callback_data="demo_client_path")]
        ]),
        parse_mode="HTML"
    )

# Feature 5: Lead Card Demonstration & Feature 8: Automatic Feedback Collection
@router.callback_query(F.data == "demo_leave_lead")
async def demo_leave_lead(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес")

    # User feedback simulation
    text = (
        f"✅ <b>Заявка в {niche_name} успешно оформлена!</b>\n\n"
        "<i>(Вы как клиент получили это подтверждение)</i>\n\n"
        "А теперь посмотрите, что в эту же секунду придет владельцу бизнеса в отдельный канал или личку 👇"
    )
    if callback.message.text:
        await callback.message.edit_text(text, parse_mode="HTML")
    else:
        await callback.message.edit_caption(caption=text, parse_mode="HTML")

    # Admin notification (Lead Card)
    admin_id = callback.message.chat.id
    lead_text = (
        f"🚨 <b>НОВЫЙ ЛИД | {niche_name}</b>\n\n"
        f"👤 Клиент: @{callback.from_user.username or callback.from_user.id}\n"
        f"💬 Запрос: Переведен после ИИ-диалога\n"
        f"🔥 Температура: Высокая\n\n"
        f"Выберите действие в CRM:"
    )

    await callback.bot.send_message(
        chat_id=admin_id,
        text=lead_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Взять в работу", callback_data="crm_accept"),
                InlineKeyboardButton(text="❌ Отказ", callback_data="crm_reject")
            ]
        ]),
        parse_mode="HTML"
    )

    # Schedule NPS feedback
    asyncio.create_task(schedule_nps(callback.message.chat.id, callback.bot))
    await callback.answer()

async def schedule_nps(chat_id, bot):
    await asyncio.sleep(10) # 10 seconds for demo instead of 1 hour
    try:
        await bot.send_message(
            chat_id=chat_id,
            text="⭐ <b>Оцените качество обслуживания!</b>\n\n"
                 "Вы недавно обращались к нам. Насколько вы довольны нашей работой?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="1", callback_data="nps_1"),
                    InlineKeyboardButton(text="2", callback_data="nps_2"),
                    InlineKeyboardButton(text="3", callback_data="nps_3"),
                    InlineKeyboardButton(text="4", callback_data="nps_4"),
                    InlineKeyboardButton(text="5", callback_data="nps_5")
                ]
            ]),
            parse_mode="HTML"
        )
    except:
        pass

@router.callback_query(F.data.startswith("crm_"))
async def crm_action(callback: types.CallbackQuery):
    action = "Принято в работу ✅" if "accept" in callback.data else "Отклонено ❌"
    await callback.message.edit_text(f"{callback.message.text}\n\n<b>Статус:</b> {action}", parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("nps_"))
async def nps_action(callback: types.CallbackQuery):
    score = int(callback.data.split("_")[1])
    if score >= 4:
        text = "Спасибо за высокую оценку! 🥰 Оставьте отзыв на Яндекс.Картах: [ссылка]"
    else:
        text = "Нам жаль, что вы недовольны 😔 Перевожу вас на старшего менеджера для решения проблемы."
    await callback.message.edit_text(text)
    await callback.answer()


@router.callback_query(F.data.startswith("demo_niche_"))
async def demo_niche(callback: types.CallbackQuery):
    text = (
        "🛍 <b>Оформление заказа</b>\n\n"
        "Клиент нажимает пару кнопок, выбирает товар и оплачивает внутри Telegram.\n"
        "Весь процесс занимает 30 секунд. Вы мгновенно получаете деньги и уведомление в свою CRM.\n\n"
        "<b>Это сильно повышает конверсию по сравнению с сайтом.</b>"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="demo_client_path")]])
    await update_showroom_media(callback, "demo_client_path", text, markup)
    await callback.answer()

@router.callback_query(F.data.startswith("demo_pricing"))
async def demo_pricing(callback: types.CallbackQuery):
    # Parse pagination
    data = callback.data
    page = 0
    if "_" in data and data != "demo_pricing":
        parts = data.split("_")
        if len(parts) >= 3 and parts[-1].isdigit():
            page = int(parts[-1])

    tariffs = [
        (
            "<b>1. ТАРИФ «СТАРТ» (от 21 000 ₽) — Базовая лидогенерация</b>\n"
            "Бизнес-цель: Заменить скучный лендинг, автоматизировать сбор контактов и отвечать клиентам 24/7 без участия менеджера.\n\n"
            "<b>Технический стек:</b> Python (aiogram 3.x), база данных Supabase. Размещение на надежных серверах.\n\n"
            "<b>Наполнение (Что внутри):</b>\n"
            "• Многоуровневое меню: Четкая структура кнопок (О компании, Услуги, Прайс, FAQ).\n"
            "• Умная заявка: Пошаговый опрос клиента. Бот не пропустит фейковый номер.\n"
            "• Мгновенные алерты: Заявка моментально пересылается в ваш Telegram.\n"
            "• Пульт управления: Рассылка текста или акций всем пользователям бота."
        ),
        (
            "<b>2. ТАРИФ «БИЗНЕС» (от 45 000 ₽) — Автономный отдел продаж</b>\n"
            "Бизнес-цель: Инструмент для микро-розницы и сферы услуг. Бот сам презентует продукт, продает и принимает деньги.\n\n"
            "<b>Технический стек:</b> Python (aiogram), БД Supabase, интеграция касс (ЮKassa, СБП).\n\n"
            "<b>Наполнение (Что внутри):</b>\n"
            "<i>Включает всё из тарифа «Старт», а также:</i>\n"
            "• Интерактивный каталог: Вывод ваших товаров или услуг по категориям с фото и ценами.\n"
            "• Корзина и чекаут: Бот автоматически считает итоговую сумму с учетом доставки.\n"
            "• Оплата онлайн: Клиент оплачивает прямо в Telegram, деньги идут на счет ИП/ООО.\n"
            "• Система записи (Букинг): Календарь для выбора свободных слотов.\n"
            "• Экспорт данных: Выгрузка базы клиентов в Excel/CSV в один клик."
        ),
        (
            "<b>3. ТАРИФ «МАСШТАБ» (от 120 000 ₽) — Премиальная TWA-экосистема</b>\n"
            "Бизнес-цель: Уровень лидеров рынка. Вместо текстовых кнопок в чате — полноценный сервис внутри мессенджера.\n\n"
            "<b>Технический стек:</b> Backend: Python. Frontend: React / Vite. Архитектура Telegram Web Apps (TWA).\n\n"
            "<b>Наполнение (Что внутри):</b>\n"
            "<i>Включает всё из тарифа «Бизнес», а также:</i>\n"
            "• Web-интерфейс (TWA): Кастомный дизайн, плавные анимации, адаптация под ваш бренд.\n"
            "• Личный Кабинет: Статус заказа, история покупок и накопленные бонусы.\n"
            "• Сложные фильтры: Поиск товаров по характеристикам (как на маркетплейсах).\n"
            "• Интеграция с CRM: Прямая передача лидов и оплат в amoCRM или Битрикс24 по API."
        )
    ]

    # Bounds checking
    if page < 0:
        page = 0
    elif page >= len(tariffs):
        page = len(tariffs) - 1

    text = f"📑 <b>ОЦЕНКА СТОИМОСТИ ВНЕДРЕНИЯ</b> (Тариф {page + 1}/{len(tariffs)})\n\n" + tariffs[page]

    # Navigation buttons
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"demo_pricing_{page - 1}"))
    if page < len(tariffs) - 1:
        nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"demo_pricing_{page + 1}"))

    keyboard = []
    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([InlineKeyboardButton(text="💬 Обсудить проект", web_app=types.WebAppInfo(url=os.getenv("WEBAPP_URL", "https://lid-flow.vercel.app/twa")))])
    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    try:
        await update_showroom_media(callback, "demo_pricing", text, markup)
    except Exception as e:
        # Ignore message not modified error
        pass

    await callback.answer()

@router.callback_query(F.data == "demo_stoma_booking")
async def demo_stoma_booking(callback: types.CallbackQuery):
    await callback.answer("✅ (Демо) Заявка на чистку принята. Врач скоро свяжется с вами!", show_alert=True)

# Feature 2: Photo Analysis (Gemini Vision)
@router.callback_query(F.data == "demo_vision")
async def demo_vision(callback: types.CallbackQuery, state: FSMContext):
    await update_showroom_media(callback, "demo_vision", "📷 <b>Анализ по фото (Vision ИИ)</b>\n\n"
        "Отправьте фото (например, разбитое авто для СТО, товар на полке, зубной снимок). ИИ проанализирует его моментально.", InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]))
    await state.set_state(DemoStates.waiting_for_photo)
    await callback.answer()

@router.message(DemoStates.waiting_for_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес Архитектор")

    status_msg = await message.answer("🔄 <i>Загружаю зрение терминатора...</i>", parse_mode="HTML")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if API_KEY:
        try:
            import io
            photo = message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)
            file_bytes = io.BytesIO()
            await message.bot.download_file(file_info.file_path, file_bytes)

            prompt = f"Действуй профессионально в роли ассистента компании {niche_name}. Проанализируй это фото. Если на нем есть дефекты, документы, зубы (в зависимости от ниши) - опиши их. Предложи решение или запиши на осмотр. Ответ должен быть кратким и по делу, не более 50-100 слов. ОТВЕЧАЙ ПРОСТЫМ ТЕКСТОМ БЕЗ MARKDOWN."

            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": file_bytes.getvalue()
                }
            ]

            answer_text = await generate_with_fallback(prompt, image_parts=[image_parts[0]], user_id=message.from_user.id)
        except Exception as e:
            answer_text = "❌ Ошибка при анализе изображения ИИ: " + str(e)
    else:
        answer_text = "Демонстрация зрения: ИИ распознал объекты на фото и готов выдать предварительную оценку стоимости."

    await status_msg.delete()
    await update_showroom_media(message, "demo_vision", f"📷 <b>Результат анализа (Vision ИИ):</b>\n\n{answer_text}", InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]]))
    await state.set_state(DemoStates.in_niche)

# Feature 3: Voice Message Recognition
@router.callback_query(F.data == "demo_voice")
async def demo_voice(callback: types.CallbackQuery, state: FSMContext):
    await update_showroom_media(callback, "demo_voice", "🎤 <b>Голосовой ассистент</b>\n\n"
        "Клиенты не любят писать. Запишите короткое голосовое сообщение с любым вопросом.", InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]))
    await state.set_state(DemoStates.waiting_for_voice)
    await callback.answer()

@router.message(DemoStates.waiting_for_voice, F.voice)
async def handle_voice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес Архитектор")

    status_msg = await message.answer("🔄 <i>Перевожу голос в текст и анализирую...</i>", parse_mode="HTML")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="record_voice")

    if API_KEY:
        try:
            import io
            import tempfile
            import os

            voice = message.voice
            file_info = await message.bot.get_file(voice.file_id)

            # Create a temporary file to save the .ogg voice message
            # Gemini requires the file to have a recognizable extension/format or pass mime_type
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_file:
                await message.bot.download_file(file_info.file_path, destination=tmp_file.name)
                tmp_path = tmp_file.name

            try:
                # Use Gemini file API
                import google.generativeai as genai
                uploaded_file = genai.upload_file(tmp_path)

                prompt = f"Ты экспертный ассистент компании {niche_name}. Прослушай аудиосообщение клиента. Дай четкий, полезный ответ, подходящий для ниши (согласись на запись или проконсультируй по услугам). Ответ должен быть кратким и по делу, не более 50-100 слов. ОТВЕЧАЙ ПРОСТЫМ ТЕКСТОМ БЕЗ MARKDOWN."

                answer_text = await generate_with_fallback(prompt, file_part=uploaded_file, user_id=message.from_user.id)

                # Cleanup the file from Gemini
                uploaded_file.delete()
            finally:
                # Cleanup local temp file
                os.unlink(tmp_path)

        except Exception as e:
            answer_text = "❌ Ошибка при распознавании голоса ИИ: " + str(e)
    else:
        answer_text = "🎵 Я успешно распознал ваше аудио (в рабочей версии здесь будет точная транскрибация). ИИ понял интент и сформировал ответ."

    await status_msg.edit_text(
        f"🎤 <b>Ответ ассистента ({niche_name}):</b>\n\n{answer_text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]]),
        parse_mode="HTML"
    )
    await state.set_state(DemoStates.in_niche)

# Feature 4: Interactive Quiz / Calculator
@router.callback_query(F.data.startswith("demo_calc"))
async def demo_calculator(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    niche = data.get("niche", "default")
    niche_name = data.get("niche_name", "Ваш бизнес")

    if callback.data == "demo_calculator" or callback.data == "demo_calc":
        step = "start"
    else:
        step = callback.data.replace("demo_calc_", "")

    # Define questions based on niche
    questions = {
        "lawyer": {
            "q1": "Какая отрасль права вас интересует?",
            "a1": [("Гражданское", "civil"), ("Уголовное", "criminal"), ("Арбитраж", "arbitration")],
            "q2": "Какой тип услуги вам нужен?",
            "a2": [("Консультация", "consult"), ("Представление в суде", "court"), ("Составление договора", "contract")]
        },
        "dentist": {
            "q1": "Что вас беспокоит?",
            "a1": [("Боль в зубе", "pain"), ("Эстетика (отбеливание)", "aesthetic"), ("Профилактика (чистка)", "cleaning")],
            "q2": "Когда вы хотите записаться?",
            "a2": [("Как можно скорее", "asap"), ("В течение недели", "week"), ("Плановый осмотр", "plan")]
        },
        "auto": {
            "q1": "Какая услуга требуется вашему авто?",
            "a1": [("Плановое ТО", "maintenance"), ("Ремонт двигателя/ходовой", "repair"), ("Диагностика", "diag")],
            "q2": "У вас свои запчасти или нужны наши?",
            "a2": [("Свои", "own_parts"), ("Нужны ваши", "your_parts"), ("Нужна консультация", "consult_parts")]
        },
        "beauty": {
            "q1": "Какую процедуру вы хотите сделать?",
            "a1": [("Стрижка / Окрашивание", "hair"), ("Маникюр / Педикюр", "nails"), ("Уход за лицом", "face")],
            "q2": "К какому мастеру вы хотите попасть?",
            "a2": [("Топ-мастер", "top"), ("Обычный мастер", "regular"), ("Любой свободный", "any")]
        },
        "default": {
             "q1": "Какой объем работ?",
             "a1": [("Маленький", "small"), ("Большой", "big")],
             "q2": "Как срочно?",
             "a2": [("Не к спеху", "slow"), ("Горит!", "fast")]
        }
    }

    niche_q = questions.get(niche, questions["default"])

    if step == "start" or step == "calculator":
        text = f"🧮 <b>Квиз ({niche_name})</b>\n\nОтветьте на 2 вопроса для расчета стоимости:\n\n{niche_q['q1']}"
        keyboard = []
        for text_btn, data_btn in niche_q['a1']:
            keyboard.append([InlineKeyboardButton(text=text_btn, callback_data=f"demo_calc_step2_{data_btn}")])
        keyboard.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="demo_niche_back")])

    elif step.startswith("step2"):
        # We got answer for Q1
        ans1 = step.split("step2")[-1].strip("_")
        await state.update_data(calc_ans1=ans1)

        text = f"🧮 <b>Квиз ({niche_name})</b>\n\nВопрос 2/2: {niche_q['q2']}"
        keyboard = []
        for text_btn, data_btn in niche_q['a2']:
             keyboard.append([InlineKeyboardButton(text=text_btn, callback_data=f"demo_calc_result_{data_btn}")])
        keyboard.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="demo_niche_back")])

    elif step.startswith("result"):
        # We got answer for Q2
        ans2 = step.split("result")[-1].strip("_")
        ans1 = data.get("calc_ans1", "неизвестно")

        status_msg = await update_showroom_media(callback, "demo_vision", "🔄 <i>Передаю данные ИИ для индивидуального расчета...</i>")


        # Determine actual text answers based on keys
        text_ans1 = next((item[0] for item in niche_q['a1'] if item[1] == ans1), ans1)
        text_ans2 = next((item[0] for item in niche_q['a2'] if item[1] == ans2), ans2)

        if API_KEY:
             try:
                 prompt = f"Ты ИИ-ассистент компании {niche_name}. Клиент прошел квиз. Вопрос 1: {niche_q['q1']} Ответ: {text_ans1}. Вопрос 2: {niche_q['q2']} Ответ: {text_ans2}. Сделай примерный расчет стоимости и времени, и предложи записаться/оставить заявку. Напиши 1 короткий, привлекательный абзац. ОТВЕЧАЙ ПРОСТЫМ ТЕКСТОМ БЕЗ MARKDOWN."
                 ai_text = await generate_with_fallback(prompt, user_id=callback.from_user.id)
             except Exception as e:
                 ai_text = f"Ваша предварительная стоимость: от 15 000 до 35 000 рублей. ({str(e)})"
        else:
             ai_text = f"ИИ проанализировал ваши ответы ({text_ans1}, {text_ans2}) и подготовил бы персональное коммерческое предложение с ценой и сроками."

        text = f"🧮 <b>Расчет завершен!</b>\n\n{ai_text}\n\nХотите оформить заявку?"
        keyboard = [
            [InlineKeyboardButton(text="🎯 Оформить", callback_data="demo_leave_lead")],
            [InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]
        ]
        await update_showroom_media(callback, "demo_calculator", text, InlineKeyboardMarkup(inline_keyboard=keyboard))
        await callback.answer()
        return

    await update_showroom_media(callback, "demo_calculator", text, InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

# Feature 7: Unique Promo Code Generation
import random
import string
@router.callback_query(F.data == "demo_promo")
async def demo_promo(callback: types.CallbackQuery, state: FSMContext):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    text = (
        "🎁 <b>Программа лояльности и Возврат клиентов</b>\n\n"
        "Мы можем автоматически отправлять промокоды клиентам, которые давно не заходили.\n\n"
        "Ваш персональный промокод: <span class='tg-spoiler'><b>" + code + "</b></span>\n\n"
        "<i>Нажмите на него, чтобы скопировать.</i>"
    )
    await update_showroom_media(callback, "demo_promo", text, InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]]))
    await callback.answer()

@router.callback_query(F.data == "demo_niche_back")
async def demo_niche_back(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    niche = data.get("niche")
    niche_name = data.get("niche_name", "Ваш бизнес")

    if not niche:
        # Fallback to main demo selection if no niche selected
        await demo_client_path(callback, state)
        return

    niche_data = {
        "lawyer": "оформлении документов и защите прав",
        "dentist": "записи на прием и ценах на лечение",
        "auto": "ремонте, запчастях и записи на диагностику",
        "beauty": "услугах, мастерах и записи на процедуры"
    }
    spec = niche_data.get(niche, "ваших услугах")

    await state.set_state(DemoStates.in_niche)
    await update_showroom_media(callback, f"niche_{niche}", f"<i>(Вы вошли в роль клиента)</i>\n\n"
        f"<b>Добро пожаловать в {niche_name}!</b>\n\n"
        f"Я ваш виртуальный помощник. Я могу проконсультировать вас по {spec}, а также записать на удобное время.\n\n"
        "Что вас интересует?", InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Тест ИИ-консультанта (FAQ)", callback_data="demo_ai_ask")],
            [InlineKeyboardButton(text="📷 Распознавание фото (Оценка)", callback_data="demo_vision")],
            [InlineKeyboardButton(text="📄 Авто-обработка документов (PDF)", callback_data="demo_docs")],
            [InlineKeyboardButton(text="🎤 Голосовой прием заявок", callback_data="demo_voice")],
            [InlineKeyboardButton(text="🧮 Интерактивный расчет стоимости", callback_data="demo_calculator")],
            [InlineKeyboardButton(text="🎁 Система лояльности (Промокоды)", callback_data="demo_promo")],
            [InlineKeyboardButton(text="🔙 Сменить нишу", callback_data="demo_client_path")]
        ]))
    await callback.answer()




# Creative improvements showcase


INNOVATIONS_LIST = [
    (
        "1️⃣ <b>Генератор Коммерческих Предложений (PDF)</b>\n"
        "▪️ <b>Что это:</b> Бот задает клиенту 3 уточняющих вопроса и мгновенно формирует стильный PDF-документ с расчетом, вашим логотипом и контактами менеджера.\n"
        "▪️ <b>Зачем:</b> Сокращает цикл сделки. Пока конкуренты берут время на расчет, вы уже отправляете готовое КП, удерживая горячего лида."
    ),
    (
        "2️⃣ <b>DeepFake-Аватары и Видео-Презентации</b>\n"
        "▪️ <b>Что это:</b> Генерация персонализированных видео на лету. Цифровой аватар руководителя обращается к клиенту по имени и кратко презентует нужный продукт.\n"
        "▪️ <b>Зачем:</b> Вау-эффект и радикальное повышение доверия. Персональное внимание в B2B ценится крайне высоко и повышает конверсию."
    ),
    (
        "3️⃣ <b>Умный Парсинг Смет и Спецификаций</b>\n"
        "▪️ <b>Что это:</b> Клиент загружает фото спецификации или Excel. Нейросеть распознает позиции, сопоставляет их с вашей базой 1С/МойСклад и выдает готовый счет.\n"
        "▪️ <b>Зачем:</b> Экономит часы рутинной работы менеджеров. Снижает риск человеческой ошибки при вводе сложных номенклатур."
    ),
    (
        "4️⃣ <b>Бесшовная интеграция с ERP/CRM (1С, МойСклад)</b>\n"
        "▪️ <b>Как работает:</b> Контрагент прямо в Telegram проверяет актуальные остатки на складе, статус отгрузки, трек-номер и баланс взаиморасчетов.\n"
        "▪️ <b>Ценность:</b> Снижает нагрузку на клиентский сервис до 60%. Лояльность клиентов растет благодаря моментальному доступу к информации в режиме 24/7."
    ),
    (
        "5️⃣ <b>Предиктивная Аналитика Закупок</b>\n"
        "▪️ <b>Что это:</b> Нейросеть анализирует историю заказов контрагента и проактивно пишет: <i>«Иван, по нашим данным вам пора пополнить запасы материала X. Сформировать счет со скидкой 5%?»</i>\n"
        "▪️ <b>Зачем:</b> Увеличение LTV (пожизненной ценности). Бот сам делает допродажи и напоминает о регулярных закупках, не давая клиенту уйти к конкурентам."
    ),
    (
        "6️⃣ <b>AI-Скоринг Контрагентов</b>\n"
        "▪️ <b>Что это:</b> Клиент (или ваш менеджер) отправляет ИНН, а бот выдает экспресс-отчет о надежности компании (суды, долги, финансы) через интеграцию с сервисами проверки.\n"
        "▪️ <b>Зачем:</b> Моментальная оценка рисков перед заключением сделки или предоставлением отсрочки платежа прямо в мессенджере."
    ),
    (
        "7️⃣ <b>AR-Каталог Оборудования (Web 3D)</b>\n"
        "▪️ <b>Что это:</b> По клику из бота открывается Web App (TWA), где клиент может покрутить 3D-модель станка/продукта, рассмотреть узлы или «примерить» его габариты в своем цеху через камеру.\n"
        "▪️ <b>Зачем:</b> Заменяет физический шоурум. Идеально для демонстрации сложного, дорогого или крупногабаритного оборудования удаленным клиентам."
    ),
    (
        "8️⃣ <b>Voice-to-Task (Голосовые Заказы)</b>\n"
        "▪️ <b>Что это:</b> Клиент наговаривает аудио: <i>«Повтори прошлый заказ на 10 тонн арматуры, доставка на вторник»</i>. ИИ расшифровывает голос, находит заказ и создает заявку в CRM.\n"
        "▪️ <b>Зачем:</b> Максимальное удобство для ЛПР (лиц, принимающих решения), которые часто находятся в дороге или на производстве и не имеют времени печатать."
    ),
    (
        "9️⃣ <b>Геймифицированный Онбординг Партнеров</b>\n"
        "▪️ <b>Что это:</b> Интерактивные квесты для обучения дилеров или франчайзи. За изучение материалов и прохождение тестов прямо в боте они получают баллы лояльности или повышенную скидку.\n"
        "▪️ <b>Зачем:</b> Резко ускоряет адаптацию новых партнеров. Геймификация заставляет их быстрее изучить ваш продукт и начать продавать."
    ),
    (
        "🔟 <b>Виртуальная Переговорка (WebRTC внутри TG)</b>\n"
        "▪️ <b>Что это:</b> По нажатию одной кнопки в боте начинается защищенный видеозвонок с закрепленным менеджером или техподдержкой — без перехода в Zoom или Skype.\n"
        "▪️ <b>Зачем:</b> Бесшовный клиентский опыт. Вы всегда на связи в привычной для клиента среде, что повышает лояльность и ускоряет решение сложных вопросов."
    )
]

def get_innovations_text(page: int, per_page: int = 1):
    start_idx = page * per_page
    end_idx = start_idx + per_page
    items = INNOVATIONS_LIST[start_idx:end_idx]

    text = (
        "🌟 <b>Топ-10 B2B Инноваций для Вашего Бизнеса</b> 🌟\n\n"
        "<i>Превратите Telegram в полноценную цифровую экосистему и навсегда отстройтесь от конкурентов. Вот архитектурные решения, которые выведут ваш бизнес на новый уровень:</i>\n\n"
    )

    for item in items:
        text += item + "\n\n"

    text += f"<i>Страница {page + 1} из {(len(INNOVATIONS_LIST) + per_page - 1) // per_page}</i>\n"
    text += "💡 <i>Любая из этих функций может стать киллер-фичей вашего проекта!</i>"

    return text

def get_innovations_keyboard(page: int, per_page: int = 1):
    total_pages = (len(INNOVATIONS_LIST) + per_page - 1) // per_page

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"demo_innovations_page_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"demo_innovations_page_{page + 1}"))

    keyboard = []
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(F.data == "demo_innovations")
async def demo_innovations(callback: types.CallbackQuery):
    await update_showroom_media(callback, "demo_innovations",
        get_innovations_text(0), get_innovations_keyboard(0))
    await callback.answer()

@router.callback_query(F.data.startswith("demo_innovations_page_"))
async def demo_innovations_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await update_showroom_media(callback, "demo_innovations",
        get_innovations_text(page), get_innovations_keyboard(page))
    await callback.answer()

@router.message(F.text == "🏠 Главное меню")
async def show_menu_handler(message: types.Message):
    # Instead of deleting and starting over, just send the main menu
    from bot.handlers.demo import get_main_menu_keyboard

    welcome_text = (
        "🤖 <b>Eidos System</b> — ваш премиальный цифровой шоурум.\n\n"
        "Добро пожаловать в демо-версию интеллектуальной системы автоматизации бизнеса. Здесь вы на практике увидите, как технологии кратно увеличивают прибыль и снижают издержки.\n\n"
        "Выберите интересующий вас раздел:"
    )

    markup = get_main_menu_keyboard()
    await update_showroom_media(message, "main_menu_photo", welcome_text, markup)

# Feature 2.5: Document Analysis (AI Parsing)
@router.message(DemoStates.in_niche, F.document)
async def handle_document(message: types.Message, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес Архитектор")

    doc = message.document

    # We only process PDFs or Excel for demo
    if not (doc.file_name.endswith('.pdf') or doc.file_name.endswith('.xlsx') or doc.file_name.endswith('.xls')):
        await message.answer("❌ <b>Демо:</b> Пожалуйста, отправьте PDF документ или Excel файл для анализа (смета, спецификация, прайс).", parse_mode="HTML")
        return

    status_msg = await message.answer(
        "🔄 <i>Запускаю умный парсинг документов...</i>\n\n"
        "<code>[||||||||  ] 30% - Извлечение таблиц</code>",
        parse_mode="HTML"
    )
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1.5)

    await status_msg.edit_text(
        "🔄 <i>Запускаю умный парсинг документов...</i>\n\n"
        "<code>[||||||||||||||] 80% - Сопоставление с базой CRM</code>",
        parse_mode="HTML"
    )
    await asyncio.sleep(1.5)

    import random
    total = random.randint(15000, 150000)

    ai_text = (
        f"✅ <b>Смета успешно обработана!</b>\n\n"
        f"<b>ИИ:</b> Я проанализировал файл <i>{doc.file_name}</i>. В нём найдено 14 позиций. \n"
        f"Все они сопоставлены с вашей номенклатурой ({niche_name}).\n\n"
        f"💰 <b>Предварительная сумма:</b> {total:,} ₽\n\n"
        f"<i>В реальной системе здесь будет сгенерирован счет на оплату или коммерческое предложение в формате PDF, готовое к отправке клиенту.</i>"
    ).replace(',', ' ')

    await status_msg.delete()
    await update_showroom_media(message, "demo_docs", ai_text, InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Оформить заявку", callback_data="demo_leave_lead")],
            [InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]
        ]))

@router.callback_query(F.data == "demo_docs")
async def demo_docs(callback: types.CallbackQuery, state: FSMContext):
    await update_showroom_media(callback, "demo_docs", "📄 <b>Умный Парсинг Смет и Документов</b>\n\n"


        "Отправьте мне любой PDF, Excel файл или скан счета. ИИ моментально прочитает его и сопоставит с прайсом CRM.", InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]))
    # We stay in DemoStates.in_niche, the document handler listens there
    await callback.answer()

# Feature 12: Referral System
@router.callback_query(F.data == "demo_referral")
async def demo_referral(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # We create a deep link pointing back to the bot
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"

    text = (
        "🤝 <b>Реферальная система (CPA-модель)</b>\n\n"
        "<i>Превратите лояльных клиентов в амбассадоров вашего бренда с помощью автоматического трекинга рекомендаций.</i>\n\n"
        "Отправьте уникальную ссылку вашим партнерам. Если по вашей рекомендации заключается договор на внедрение системы Eidos, вы гарантированно получаете <b>агентскую комиссию 10%</b> от суммы контракта.\n\n"
        "Полученные дивиденды можно реинвестировать в разработку дополнительных модулей для вашего цифрового актива или вывести любым удобным способом.\n\n"
        f"🔗 <b>Ваша персональная ссылка:</b>\n<code>{ref_link}</code>\n\n"
        "<i>(Нажмите на ссылку, чтобы скопировать)</i>"
    )

    await update_showroom_media(callback, "demo_referral",
        text, InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]]))
    await callback.answer()

# --- Связь с архитектором (прямая) ---
@router.callback_query(F.data == "contact_architect")
async def contact_architect_start(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "🏛 <b>Связь с Архитектором Системы</b>\n\n"
        "Пожалуйста, кратко опишите вашу бизнес-задачу или задайте интересующий вопрос.\n\n"
        "<i>Архитектор лично проанализирует запрос и свяжется с вами для обсуждения концепции и точек роста вашего бизнеса.</i>\n\n"
        "✍️ <i>Жду ваше сообщение в чате... (Нажмите «Отменить», чтобы вернуться в меню)</i>"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="main_menu")]
    ])

    await update_showroom_media(callback, "demo_innovations", text, markup)
    await state.set_state(DemoStates.waiting_for_architect_message)
    await callback.answer()

@router.message(DemoStates.waiting_for_architect_message, F.text)
async def contact_architect_receive(message: types.Message, state: FSMContext):
    user_msg = message.text
    user_link = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    full_name = message.from_user.full_name or "Без имени"

    admin_id = os.getenv("ADMIN_ID", "5178416366") # дефолтный айди для надежности, если env пуст

    admin_text = (
        "🔔 <b>Новый прямой запрос к Архитектору!</b>\n\n"
        f"👤 <b>Клиент:</b> {html.escape(full_name)} ({html.escape(user_link)})\n"
        f"💬 <b>Сообщение:</b>\n"
        f"<i>{html.escape(user_msg)}</i>"
    )

    try:
        await message.bot.send_message(admin_id, admin_text, parse_mode="HTML")
    except Exception as e:
        import logging
        logging.error(f"Failed to send direct message to architect: {e}")

    # Возвращаем пользователя в главное меню
    await state.clear()

    confirm_text = (
        "✅ <b>Запрос успешно доставлен.</b>\n\n"
        "Ваш персональный Архитектор уже получил сообщение и вернется к вам с ответом в ближайшее время.\n\n"
        "🤖 <b>Eidos System</b> — ваш премиальный цифровой шоурум.\n\n"
        "Добро пожаловать в демо-версию интеллектуальной системы автоматизации бизнеса. Здесь вы на практике увидите, как технологии кратно увеличивают прибыль и снижают издержки.\n\n"
        "Выберите интересующий вас раздел:"
    )
    from bot.handlers.demo import get_main_menu_keyboard

    # Сначала удаляем сообщение пользователя, чтобы чат оставался чистым (шоурум подход)
    try:
        await message.delete()
    except:
        pass

    await update_showroom_media(message, "main_menu_photo", confirm_text, get_main_menu_keyboard())

# --- Feature 5: Pseudo-Dashboard (Личный Кабинет Руководителя) ---
@router.callback_query(F.data == "demo_dashboard")
async def demo_dashboard(callback: types.CallbackQuery):
    full_name = callback.from_user.full_name or "Руководитель"

    # Мы генерируем красивый текст-псевдографику.
    # В реальном проекте тут генерируется Pillow картинка с диаграммой matplotlib
    # или подтягивается дашборд из Supabase + TWA.

    text = (
        f"📊 <b>Аналитический Дашборд: {html.escape(full_name)}</b>\n\n"
        "<i>Именно так ваши инвесторы и партнеры могут видеть метрики бизнеса в Telegram 24/7. Данные подтягиваются напрямую из вашей 1С или CRM (API).</i>\n\n"
        "💵 <b>Выручка (Текущий месяц):</b> 12,450,000 ₽ <tg-spoiler>+14% 🟢</tg-spoiler>\n"
        "📉 <b>Издержки на ФОТ (Сейлзы):</b> -35% 🟢 <i>(Благодаря AI)</i>\n"
        "🎯 <b>Конверсия в сделку:</b> 18.2% 📈\n\n"
        "<b>Воронка продаж:</b>\n"
        "▪️ Новые лиды: 1450\n"
        "▪️ Квалифицировано ИИ: 1200\n"
        "▪️ Выставлено счетов (Авто): 840\n"
        "▪️ Оплачено: 260\n\n"
        "<code>[||||||||||||||||||  ] 85% План выполнен</code>\n\n"
        "💡 <b>Инсайт от Нейросети:</b> <i>Замечен спад оплат в сегменте B2C. Рекомендую запустить автоматическую SMS-рассылку со скидкой 5% по отказам. Запустить? (Y/N)</i>"
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Запустить AI-Сценарий (Демо)", callback_data="demo_dashboard_magic")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

    # Используем demo_vision как картинку (там красивый AI визуал)
    await update_showroom_media(callback, "demo_vision", text, markup)
    await callback.answer()

@router.callback_query(F.data == "demo_dashboard_magic")
async def demo_dashboard_magic(callback: types.CallbackQuery):
    text = (
        "🚀 <b>Сценарий активирован!</b>\n\n"
        "<i>Магия автоматизации в действии:</i>\n"
        "1. Нейросеть проанализировала 340 отказников.\n"
        "2. Сгенерировала 340 уникальных писем с персональным оффером.\n"
        "3. Отправила их через WhatsApp/Telegram API.\n\n"
        "💸 <b>Прогноз возврата:</b> +1.2 млн ₽ в течение 48 часов.\n\n"
        "<i>Вы только что заработали деньги нажатием одной кнопки, пока пьете кофе. Хотите такую же систему? Нажмите «Связаться с Архитектором».</i>"
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 СВЯЗАТЬСЯ С АРХИТЕКТОРОМ", callback_data="contact_architect")],
        [InlineKeyboardButton(text="🔙 Назад к Дашборду", callback_data="demo_dashboard")]
    ])

    await update_showroom_media(callback, "demo_vision", text, markup)
    await callback.answer()

# --- Feature 6: Interactive AI ROI Calculator ---
from bot.states import ROICalcStates

@router.callback_query(F.data == "demo_roi_start")
async def demo_roi_start(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "🧮 <b>Интерактивный AI-Калькулятор (ROI)</b>\n\n"
        "<i>Давайте посчитаем, сколько денег вы теряете на рутине и сколько может принести внедрение бота.</i>\n\n"
        "🔹 <b>Шаг 1 из 2:</b>\n"
        "Сколько в среднем новых заявок (лидов) в месяц получает ваш бизнес?\n\n"
        "<i>(Ответьте цифрой в чат, например: 150 или нажмите Отмена)</i>"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить расчет", callback_data="main_menu")]
    ])

    await update_showroom_media(callback, "demo_calculator", text, markup)
    await state.set_state(ROICalcStates.waiting_for_leads)
    await callback.answer()

@router.message(ROICalcStates.waiting_for_leads, F.text)
async def demo_roi_leads(message: types.Message, state: FSMContext):
    try:
        leads = int(''.join(filter(str.isdigit, message.text)))
        if leads <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Пожалуйста, введите количество лидов числом (например, 150):")
        return

    await state.update_data(leads=leads)

    # Удаляем сообщение юзера
    try:
        await message.delete()
    except:
        pass

    text = (
        "🧮 <b>Шаг 2 из 2: Ваш средний чек</b>\n\n"
        f"Отлично, <b>{leads} лидов/мес.</b>\n"
        "Теперь введите ваш примерный средний чек (в рублях).\n\n"
        "<i>(Ответьте цифрой, например: 5000)</i>"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить расчет", callback_data="main_menu")]
    ])

    await update_showroom_media(message, "demo_calculator", text, markup)
    await state.set_state(ROICalcStates.waiting_for_check)

@router.message(ROICalcStates.waiting_for_check, F.text)
async def demo_roi_check(message: types.Message, state: FSMContext):
    try:
        check = int(''.join(filter(str.isdigit, message.text)))
        if check <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Пожалуйста, введите средний чек числом (например, 5000):")
        return

    data = await state.get_data()
    leads = data.get("leads", 100)
    await state.clear()

    try:
        await message.delete()
    except:
        pass

    # Показываем статус загрузки
    status_text = "🔄 <i>Нейросеть Eidos System генерирует финансовый прогноз...</i>\n\n<code>[||||||||||        ] 55% Расчет LTV</code>"
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    # Чтобы обновить showroom, отправляем новое состояние.
    # Так как message.text был получен напрямую, update_showroom_media создаст новое сообщение
    # Мы сохраняем старое сообщение (от бота) не можем, так как нет callback.
    # Поэтому просто отправляем новое сообщение:

    from bot.showroom import SHOWROOM_FILES
    file_id = SHOWROOM_FILES.get("demo_calculator")

    try:
        msg = await message.answer_photo(photo=file_id, caption=status_text, parse_mode="HTML")
    except Exception as e:
        msg = await message.answer(status_text, parse_mode="HTML")

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(2)

    # Формируем промпт для Gemini
    system_prompt = "Ты — финансовый аналитик и маркетолог в B2B IT-студии Архитектора."
    user_prompt = (
        f"Клиент ввел: {leads} лидов в месяц и средний чек {check} руб. \n\n"
        f"Сделай красивый B2B-анализ в формате Telegram HTML (строго до 100 слов).\n"
        f"Покажи:\n"
        f"1. Сколько в месяц он теряет денег из-за того, что менеджеры сливают 20% лидов из-за человеческого фактора (посчитай математику).\n"
        f"2. Как AI-бот спасет эти деньги (вернет эти 20%).\n"
        f"3. Оцени срок окупаемости системы автоматизации за 500,000 руб (ROI).\n"
        f"Будь убедительным, профессиональным."
    )

    ai_response = await generate_with_fallback(user_prompt, system_prompt, user_id=message.from_user.id)
    if not ai_response:
        # Резервный расчет без AI
        lost_leads = int(leads * 0.2)
        lost_money = lost_leads * check
        ai_response = (
            f"<b>Финансовая модель вашей компании</b>\n\n"
            f"Обычно менеджеры теряют до 20% лидов (забыли перезвонить, долго отвечали).\n"
            f"📉 <b>Упущенная выгода:</b> {lost_money:,} ₽ / мес. ({lost_leads} заявок).\n\n"
            f"Робот обрабатывает 100% лидов моментально 24/7. Внедрив систему за 500 000 ₽, вы окупите её всего за {max(1, int(500000/lost_money))} месяцев.\n\n"
            f"<i>Это математика, с которой сложно спорить.</i>"
        ).replace(',', ' ')
    else:
        # Чистим ответ от возможных markdown ```html
        ai_response = ai_response.replace("```html", "").replace("```", "").strip()

    final_text = (
        "📊 <b>Результат Нейро-Анализа вашего бизнеса:</b>\n\n"
        f"{ai_response}\n\n"
        "<i>Хотите забрать эти деньги с рынка быстрее конкурентов?</i>"
    )

    final_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 ОБСУДИТЬ ВНЕДРЕНИЕ", callback_data="contact_architect")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

    try:
        await msg.delete()
    except:
        pass

    await update_showroom_media(message, "demo_calculator", final_text, final_markup)
