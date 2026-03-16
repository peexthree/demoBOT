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
        [InlineKeyboardButton(text="⚙️ [ДЕМО-РЕЖИМ: АВТОМАТИЗАЦИЯ]", callback_data="demo_client_path")],
        [InlineKeyboardButton(text="📑 [ИНВЕСТИЦИОННЫЙ ЧЕК-ЛИСТ]", callback_data="demo_pricing")],
        [InlineKeyboardButton(text="💬 [ОБСУДИТЬ ПРОЕКТ]", url=f"tg://user?id={os.getenv('ADMIN_ID', '0')}")]
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
    await callback.message.answer(
        "Для расчета стоимости (Калькулятор Архитектора) используйте кнопку в меню ниже:",
        reply_markup=get_twa_reply_keyboard()
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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]),
        parse_mode="HTML"
    )
    await callback.answer()

# Feature 1: Dynamic Niche Selection
from states import DemoStates

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
            [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
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
            [InlineKeyboardButton(text="⚙️ Сменить нишу", callback_data="demo_client_path")]
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
            [InlineKeyboardButton(text="⚙️ Сменить нишу", callback_data="demo_client_path")]
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
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚙️ Вернуться в Демо", callback_data="demo_client_path")]]),
        parse_mode="HTML"
    )
    await state.set_state(DemoStates.in_niche)

# Feature 3: Voice Message Recognition
@router.callback_query(F.data == "demo_voice")
async def demo_voice(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎤 <b>Голосовой ассистент</b>\n\n"
        "Клиенты не любят писать. Запишите короткое голосовое сообщение с любым вопросом.",
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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚙️ Вернуться в Демо", callback_data="demo_client_path")]]),
        parse_mode="HTML"
    )
    await state.set_state(DemoStates.in_niche)

# Feature 4: Interactive Quiz / Calculator
@router.callback_query(F.data.startswith("demo_calc"))
async def demo_calculator(callback: types.CallbackQuery, state: FSMContext):
    # dynamic edit
    step = callback.data.split("_")[-1] if "_" in callback.data else "start"

    if step == "start" or step == "calculator":
        text = "🧮 <b>Интерактивный Квиз (Калькулятор)</b>\n\nОтветьте на 2 вопроса, чтобы узнать стоимость:\n\nКакой объем работ?"
        keyboard = [
            [InlineKeyboardButton(text="Маленький", callback_data="demo_calc_step2_small")],
            [InlineKeyboardButton(text="Большой", callback_data="demo_calc_step2_big")]
        ]
    elif step.startswith("step2"):
        volume = step.split("_")[1]
        await state.update_data(calc_volume=volume)
        text = "🧮 <b>Интерактивный Квиз</b>\n\nВопрос 2/2: Как срочно?"
        keyboard = [
            [InlineKeyboardButton(text="Не к спеху", callback_data="demo_calc_result_slow")],
            [InlineKeyboardButton(text="Горит!", callback_data="demo_calc_result_fast")]
        ]
    elif step.startswith("result"):
        text = "🧮 <b>Расчет завершен!</b>\n\nВаша предварительная стоимость: <b>от 15 000 до 35 000 рублей.</b>\n\nХотите оформить заявку?"
        keyboard = [
            [InlineKeyboardButton(text="🎯 Оформить", callback_data="demo_leave_lead")],
            [InlineKeyboardButton(text="⚙️ Назад в меню", callback_data="demo_client_path")]
        ]

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
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⚙️ Вернуться в Демо", callback_data="demo_client_path")]]),
        parse_mode="HTML"
    )
    await callback.answer()
