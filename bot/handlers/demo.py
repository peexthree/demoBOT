import os
import asyncio
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
        [InlineKeyboardButton(text="🌟 [10 ИННОВАЦИЙ ДЛЯ БИЗНЕСА]", callback_data="demo_innovations")],
        [InlineKeyboardButton(text="⚙️ [ДЕМО-РЕЖИМ: АВТОМАТИЗАЦИЯ]", callback_data="demo_client_path")],
        [InlineKeyboardButton(text="📑 [ИНВЕСТИЦИОННЫЙ ЧЕК-ЛИСТ]", callback_data="demo_pricing")],
        [InlineKeyboardButton(text="💬 [ОБСУДИТЬ ПРОЕКТ]", url=f"tg://user?id={os.getenv('ADMIN_ID', '0')}")],
        [InlineKeyboardButton(text="🔄 Меню (/start)", callback_data="main_menu")]
    ])

def get_twa_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 ОТКРЫТЬ КАЛЬКУЛЯТОР", web_app=types.WebAppInfo(url=os.getenv("WEBAPP_URL", "https://lid-flow.vercel.app/twa")))],
            [KeyboardButton(text="Скрыть меню")]
        ],
        resize_keyboard=True,
        is_persistent=False
    )

@router.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🤖 <b>Eidos System</b> — цифровой шоурум Архитектора.\n\n"
        "Вы находитесь в демо-версии премиальной системы автоматизации бизнеса.\n\n"
        "Выберите раздел для изучения:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(F.text == "Скрыть меню")
async def hide_keyboard_handler(message: types.Message):
    await message.answer("Меню скрыто. Чтобы вернуть его, перезапустите бота командой /start.", reply_markup=ReplyKeyboardRemove())

@router.callback_query(F.data == "demo_portfolio")
async def demo_portfolio(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🚀 <b>Наши Решения и Кейсы</b>\n\n"
        "Мы внедряем автономные цифровые активы, которые окупаются за 2-3 месяца.\n\n"
        "🔹 <b>Lizing-Phi</b> — Автоматизация скоринга и заявок.\n"
        "   <i>Результат:</i> Снизили нагрузку на админа на 70%.\n\n"
        "🔹 <b>FermerHub</b> — Платформа-маркетплейс в Telegram.\n"
        "   <i>Результат:</i> Увеличение конверсии на 40% за счет отсутствия регистраций.\n\n"
        "🔹 <b>Акуленок</b> — Автоворонка и ИИ-ассистент.\n"
        "   <i>Результат:</i> Круглосуточная обработка лидов, рост LTV.\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]]),
        parse_mode="HTML"
    )
    await callback.answer()

# Feature 1: Dynamic Niche Selection
from bot.states import DemoStates

@router.callback_query(F.data == "demo_client_path")
async def demo_client_path(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(DemoStates.choosing_niche)
    await callback.message.edit_text(
        "⚙️ <b>Выберите нишу для демонстрации</b>\n\n"
        "Я моментально адаптируюсь под любой бизнес. Выберите отрасль, чтобы увидеть, как бот общается с клиентами:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚖️ Юрист", callback_data="niche_lawyer")],
            [InlineKeyboardButton(text="🦷 Стоматология", callback_data="niche_dentist")],
            [InlineKeyboardButton(text="🚗 Автосервис / СТО", callback_data="niche_auto")],
            [InlineKeyboardButton(text="💅 Салон красоты", callback_data="niche_beauty")],
            [InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(DemoStates.choosing_niche, F.data.startswith("niche_"))
async def niche_selected(callback: types.CallbackQuery, state: FSMContext):
    niche = callback.data.split("_")[1]

    niche_data = {
        "lawyer": ("⚖️ Юридическая компания 'Право и Закон'", "оформлении документов и защите прав"),
        "dentist": ("🦷 Стоматология 'Здоровая Улыбка'", "записи на прием и ценах на лечение"),
        "auto": ("🚗 Автосервис 'Драйв'", "ремонте, запчастях и записи на диагностику"),
        "beauty": ("💅 Салон красоты 'Элеганс'", "услугах, мастерах и записи на процедуры")
    }

    name, spec = niche_data.get(niche, ("Ваш бизнес", "ваших услугах"))
    await state.update_data(niche=niche, niche_name=name)
    await state.set_state(DemoStates.in_niche)

    await callback.message.edit_text(
        f"<i>(Вы вошли в роль клиента)</i>\n\n"
        f"<b>Добро пожаловать в {name}!</b>\n\n"
        f"Я ваш виртуальный помощник. Я могу проконсультировать вас по {spec}, а также записать на удобное время.\n\n"
        "Что вас интересует?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Задать вопрос ИИ (FAQ & Консультация)", callback_data="demo_ai_ask")],
            [InlineKeyboardButton(text="📷 Анализ по фото (Vision ИИ)", callback_data="demo_vision")],
            [InlineKeyboardButton(text="🎤 Записать аудио (Голосовой ИИ)", callback_data="demo_voice")],
            [InlineKeyboardButton(text="🧮 Калькулятор стоимости", callback_data="demo_calculator")],
            [InlineKeyboardButton(text="🎁 Получить промокод", callback_data="demo_promo")],
            [InlineKeyboardButton(text="🔙 Сменить нишу", callback_data="demo_client_path")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

# Feature 6: Smart FAQ and Memory
@router.callback_query(F.data == "demo_ai_ask")
async def demo_ai_ask(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🧠 <b>ИИ-Консультант (Демо)</b>\n\n"
        "Напишите любой вопрос, связанный с вашей выбранной нишей (или общей автоматизацией). "
        "Попробуйте спросить: 'Какие у вас цены?' или 'Запишите меня на завтра'.\n\n"
        "Жду ваш вопрос:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]),
        parse_mode="HTML"
    )
    await state.set_state(DemoStates.waiting_for_question)
    await callback.answer()

@router.message(DemoStates.waiting_for_question, F.text)
async def handle_ai_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес Архитектор")
    history = data.get("history", "")

    status_msg = await message.answer(f"🔄 <i>{niche_name}:</i> Анализирую запрос...", parse_mode="HTML")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if model:
        try:
             prompt = f"Действуй профессионально в роли ассистента компании {niche_name}. Ответь клиенту на вопрос: {message.text}. Если это запрос на запись или покупку - соглашайся и проси оставить контакт. История: {history}. Ответ должен быть кратким и по делу, не более 50-100 слов. ОТВЕЧАЙ ПРОСТЫМ ТЕКСТОМ БЕЗ MARKDOWN (без звездочек)."
             response = await model.generate_content_async(prompt)
             answer_text = response.text

             # Save history
             history += f" User: {message.text}. You: {answer_text}."
             await state.update_data(history=history[-1000:])
        except Exception as e:
             answer_text = "❌ Ошибка при обращении к ИИ-серверу: " + str(e)
    else:
        await asyncio.sleep(2)
        answer_text = f"В реальности ИИ проанализирует запрос '{message.text}' для бизнеса {niche_name} и выдаст ответ, подводящий к продаже или записи."

    final_text = f"🤖 <b>Ответ ассистента ({niche_name}):</b>\n\n{answer_text}"

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
    await callback.message.edit_text(
        f"✅ <b>Заявка в {niche_name} успешно оформлена!</b>\n\n"
        "<i>(Вы как клиент получили это подтверждение)</i>\n\n"
        "А теперь посмотрите, что в эту же секунду придет владельцу бизнеса в отдельный канал или личку 👇",
        parse_mode="HTML"
    )

    # Admin notification (Lead Card)
    admin_id = os.getenv("ADMIN_ID", callback.from_user.id)
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
    await callback.message.edit_text(
        "🛍 <b>Оформление заказа</b>\n\n"
        "Клиент нажимает пару кнопок, выбирает товар и оплачивает внутри Telegram.\n"
        "Весь процесс занимает 30 секунд. Вы мгновенно получаете деньги и уведомление в свою CRM.\n\n"
        "<b>Это сильно повышает конверсию по сравнению с сайтом.</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="demo_client_path")]]),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "demo_pricing")
async def demo_pricing(callback: types.CallbackQuery):
    text = (
        "📑 <b>Инвестиционный Чек-лист</b>\n\n"
        "Прозрачный расчет стоимости разработки вашего цифрового актива.\n\n"
        "📦 <b>База [от 15k]</b> - Идеально для старта. Меню, воронка, сбор лидов.\n"
        "📦 <b>Стандарт [от 50k]</b> - Интеграция БД, ИИ, полноценная мини-CRM.\n"
        "📦 <b>Индивидуальный [от 150k]</b> - Сложные интеграции, WebApp (TWA), уникальный дизайн.\n\n"
        "<i>Свяжитесь со мной для точного расчета под ваши задачи.</i>"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Обсудить проект", url=f"tg://user?id={os.getenv('ADMIN_ID', '0')}")],
        [InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "demo_stoma_booking")
async def demo_stoma_booking(callback: types.CallbackQuery):
    await callback.answer("✅ (Демо) Заявка на чистку принята. Врач скоро свяжется с вами!", show_alert=True)

# Feature 2: Photo Analysis (Gemini Vision)
@router.callback_query(F.data == "demo_vision")
async def demo_vision(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📷 <b>Анализ по фото (Vision ИИ)</b>\n\n"
        "Отправьте фото (например, разбитое авто для СТО, товар на полке, зубной снимок). ИИ проанализирует его моментально.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]),
        parse_mode="HTML"
    )
    await state.set_state(DemoStates.waiting_for_photo)
    await callback.answer()

@router.message(DemoStates.waiting_for_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес Архитектор")

    status_msg = await message.answer("🔄 <i>Загружаю зрение терминатора...</i>", parse_mode="HTML")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if model:
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

            response = await model.generate_content_async([prompt, image_parts[0]])
            answer_text = response.text
        except Exception as e:
            answer_text = "❌ Ошибка при анализе изображения ИИ: " + str(e)
    else:
        answer_text = "Демонстрация зрения: ИИ распознал объекты на фото и готов выдать предварительную оценку стоимости."

    await status_msg.edit_text(
        f"📷 <b>Результат анализа (Vision ИИ):</b>\n\n{answer_text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]]),
        parse_mode="HTML"
    )
    await state.set_state(DemoStates.in_niche)

# Feature 3: Voice Message Recognition
@router.callback_query(F.data == "demo_voice")
async def demo_voice(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎤 <b>Голосовой ассистент</b>\n\n"
        "Клиенты не любят писать. Запишите короткое голосовое сообщение с любым вопросом.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]),
        parse_mode="HTML"
    )
    await state.set_state(DemoStates.waiting_for_voice)
    await callback.answer()

@router.message(DemoStates.waiting_for_voice, F.voice)
async def handle_voice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    niche_name = data.get("niche_name", "Бизнес Архитектор")

    status_msg = await message.answer("🔄 <i>Перевожу голос в текст и анализирую...</i>", parse_mode="HTML")
    await message.bot.send_chat_action(chat_id=message.chat.id, action="record_voice")

    if model:
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
                uploaded_file = genai.upload_file(tmp_path)

                prompt = f"Ты экспертный ассистент компании {niche_name}. Прослушай аудиосообщение клиента. Дай четкий, полезный ответ, подходящий для ниши (согласись на запись или проконсультируй по услугам). Ответ должен быть кратким и по делу, не более 50-100 слов. ОТВЕЧАЙ ПРОСТЫМ ТЕКСТОМ БЕЗ MARKDOWN."

                response = await model.generate_content_async([prompt, uploaded_file])
                answer_text = response.text

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

    if callback.data == "demo_calc":
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

        status_msg = await callback.message.edit_text(
            "🔄 <i>Передаю данные ИИ для индивидуального расчета...</i>",
            parse_mode="HTML"
        )

        # Determine actual text answers based on keys
        text_ans1 = next((item[0] for item in niche_q['a1'] if item[1] == ans1), ans1)
        text_ans2 = next((item[0] for item in niche_q['a2'] if item[1] == ans2), ans2)

        if model:
             try:
                 prompt = f"Ты ИИ-ассистент компании {niche_name}. Клиент прошел квиз. Вопрос 1: {niche_q['q1']} Ответ: {text_ans1}. Вопрос 2: {niche_q['q2']} Ответ: {text_ans2}. Сделай примерный расчет стоимости и времени, и предложи записаться/оставить заявку. Напиши 1 короткий, привлекательный абзац. ОТВЕЧАЙ ПРОСТЫМ ТЕКСТОМ БЕЗ MARKDOWN."
                 response = await model.generate_content_async(prompt)
                 ai_text = response.text
             except Exception as e:
                 ai_text = f"Ваша предварительная стоимость: от 15 000 до 35 000 рублей. ({str(e)})"
        else:
             ai_text = f"ИИ проанализировал ваши ответы ({text_ans1}, {text_ans2}) и подготовил бы персональное коммерческое предложение с ценой и сроками."

        text = f"🧮 <b>Расчет завершен!</b>\n\n{ai_text}\n\nХотите оформить заявку?"
        keyboard = [
            [InlineKeyboardButton(text="🎯 Оформить", callback_data="demo_leave_lead")],
            [InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]
        ]
        await status_msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )
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
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню ниши", callback_data="demo_niche_back")]]),
        parse_mode="HTML"
    )
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
    await callback.message.edit_text(
        f"<i>(Вы вошли в роль клиента)</i>\n\n"
        f"<b>Добро пожаловать в {niche_name}!</b>\n\n"
        f"Я ваш виртуальный помощник. Я могу проконсультировать вас по {spec}, а также записать на удобное время.\n\n"
        "Что вас интересует?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Задать вопрос ИИ (FAQ & Консультация)", callback_data="demo_ai_ask")],
            [InlineKeyboardButton(text="📷 Анализ по фото (Vision ИИ)", callback_data="demo_vision")],
            [InlineKeyboardButton(text="🎤 Записать аудио (Голосовой ИИ)", callback_data="demo_voice")],
            [InlineKeyboardButton(text="🧮 Калькулятор стоимости", callback_data="demo_calculator")],
            [InlineKeyboardButton(text="🎁 Получить промокод", callback_data="demo_promo")],
            [InlineKeyboardButton(text="🔙 Сменить нишу", callback_data="demo_client_path")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


# Creative improvements showcase

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
    await callback.message.edit_text(
        f"<i>(Вы вошли в роль клиента)</i>\n\n"
        f"<b>Добро пожаловать в {niche_name}!</b>\n\n"
        f"Я ваш виртуальный помощник. Я могу проконсультировать вас по {spec}, а также записать на удобное время.\n\n"
        "Что вас интересует?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Задать вопрос ИИ (FAQ & Консультация)", callback_data="demo_ai_ask")],
            [InlineKeyboardButton(text="📷 Анализ по фото (Vision ИИ)", callback_data="demo_vision")],
            [InlineKeyboardButton(text="🎤 Записать аудио (Голосовой ИИ)", callback_data="demo_voice")],
            [InlineKeyboardButton(text="🧮 Калькулятор стоимости", callback_data="demo_calculator")],
            [InlineKeyboardButton(text="🎁 Получить промокод", callback_data="demo_promo")],
            [InlineKeyboardButton(text="🔙 Сменить нишу", callback_data="demo_client_path")]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()

# Creative improvements showcase
@router.callback_query(F.data == "demo_innovations")
async def demo_innovations(callback: types.CallbackQuery):
    text = (
        "🌟 <b>Топ-10 B2B Инноваций для Вашего Бизнеса</b> 🌟\n\n"
        "<i>Превратите Telegram в полноценную корпоративную экосистему и опередите конкурентов. Вот чем мы можем удивить ваших клиентов:</i>\n\n"
        "1️⃣ <b>Генератор Коммерческих Предложений (PDF)</b>\n"
        "▪️ <b>Что это:</b> Бот задает клиенту 3 уточняющих вопроса и мгновенно формирует стильный PDF-документ с расчетом, вашим логотипом и контактами менеджера.\n"
        "▪️ <b>Зачем:</b> Сокращает цикл сделки. Пока конкуренты берут время на расчет, вы уже отправляете готовое КП, удерживая горячего лида.\n\n"
        "2️⃣ <b>DeepFake-Аватары и Видео-Презентации</b>\n"
        "▪️ <b>Что это:</b> Генерация персонализированных видео на лету. Цифровой аватар руководителя обращается к клиенту по имени и кратко презентует нужный продукт.\n"
        "▪️ <b>Зачем:</b> Вау-эффект и радикальное повышение доверия. Персональное внимание в B2B ценится крайне высоко и повышает конверсию.\n\n"
        "3️⃣ <b>Умный Парсинг Смет и Спецификаций</b>\n"
        "▪️ <b>Что это:</b> Клиент загружает фото спецификации или Excel. Нейросеть распознает позиции, сопоставляет их с вашей базой 1С/МойСклад и выдает готовый счет.\n"
        "▪️ <b>Зачем:</b> Экономит часы рутинной работы менеджеров. Снижает риск человеческой ошибки при вводе сложных номенклатур.\n\n"
        "4️⃣ <b>Интеграция с ERP/CRM (Реал-тайм склад)</b>\n"
        "▪️ <b>Что это:</b> Клиент прямо в боте может проверить наличие товара на складе, статус отгрузки, трек-номер логистики или баланс взаиморасчетов.\n"
        "▪️ <b>Зачем:</b> Снижает нагрузку на колл-центр до 60%. Клиенты получают нужную информацию 24/7 без ожидания ответа живого человека.\n\n"
        "5️⃣ <b>Предиктивная Аналитика Закупок</b>\n"
        "▪️ <b>Что это:</b> Нейросеть анализирует историю заказов контрагента и проактивно пишет: <i>«Иван, по нашим данным вам пора пополнить запасы материала X. Сформировать счет со скидкой 5%?»</i>\n"
        "▪️ <b>Зачем:</b> Увеличение LTV (пожизненной ценности). Бот сам делает допродажи и напоминает о регулярных закупках, не давая клиенту уйти к конкурентам.\n\n"
        "6️⃣ <b>AI-Скоринг Контрагентов</b>\n"
        "▪️ <b>Что это:</b> Клиент (или ваш менеджер) отправляет ИНН, а бот выдает экспресс-отчет о надежности компании (суды, долги, финансы) через интеграцию с сервисами проверки.\n"
        "▪️ <b>Зачем:</b> Моментальная оценка рисков перед заключением сделки или предоставлением отсрочки платежа прямо в мессенджере.\n\n"
        "7️⃣ <b>AR-Каталог Оборудования (Web 3D)</b>\n"
        "▪️ <b>Что это:</b> По клику из бота открывается Web App (TWA), где клиент может покрутить 3D-модель станка/продукта, рассмотреть узлы или «примерить» его габариты в своем цеху через камеру.\n"
        "▪️ <b>Зачем:</b> Заменяет физический шоурум. Идеально для демонстрации сложного, дорогого или крупногабаритного оборудования удаленным клиентам.\n\n"
        "8️⃣ <b>Voice-to-Task (Голосовые Заказы)</b>\n"
        "▪️ <b>Что это:</b> Клиент наговаривает аудио: <i>«Повтори прошлый заказ на 10 тонн арматуры, доставка на вторник»</i>. ИИ расшифровывает голос, находит заказ и создает заявку в CRM.\n"
        "▪️ <b>Зачем:</b> Максимальное удобство для ЛПР (лиц, принимающих решения), которые часто находятся в дороге или на производстве и не имеют времени печатать.\n\n"
        "9️⃣ <b>Геймифицированный Онбординг Партнеров</b>\n"
        "▪️ <b>Что это:</b> Интерактивные квесты для обучения дилеров или франчайзи. За изучение материалов и прохождение тестов прямо в боте они получают баллы лояльности или повышенную скидку.\n"
        "▪️ <b>Зачем:</b> Резко ускоряет адаптацию новых партнеров. Геймификация заставляет их быстрее изучить ваш продукт и начать продавать.\n\n"
        "🔟 <b>Виртуальная Переговорка (WebRTC внутри TG)</b>\n"
        "▪️ <b>Что это:</b> По нажатию одной кнопки в боте начинается защищенный видеозвонок с закрепленным менеджером или техподдержкой — без перехода в Zoom или Skype.\n"
        "▪️ <b>Зачем:</b> Бесшовный клиентский опыт. Вы всегда на связи в привычной для клиента среде, что повышает лояльность и ускоряет решение сложных вопросов.\n\n"
        "💡 <i>Любая из этих функций может стать киллер-фичей вашего проекта!</i>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]]),
        parse_mode="HTML"
    )
    await callback.answer()
