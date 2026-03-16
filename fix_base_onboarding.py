import re

with open("bot/handlers/base.py", "r") as f:
    content = f.read()

# Replace the analytics code with code that checks if user exists
old_analytics = """    # User analytics
    try:
        from bot.db import save_user
        await save_user(
            message.from_user.id,
            message.from_user.username or "",
            message.from_user.first_name or "",
            message.from_user.last_name or ""
        )
    except Exception as e:
        print(f"User analytics error: {e}")"""

new_analytics = """    # User analytics
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
        print(f"User analytics error: {e}")"""

content = content.replace(old_analytics, new_analytics)

# Conditionally show the onboarding if user does NOT exist
old_welcome = """    welcome_text = (
        f"🌆 <b>{greeting}, {message.from_user.first_name}!</b>\\n\\n"
        "<b>Eidos System</b> — цифровой шоурум Архитектора систем автоматизации.\\n\\n"
        "Для того, чтобы показать вам наиболее релевантные возможности, подскажите, <b>в какой сфере вы работаете?</b>"
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Услуги (Юристы, Консалтинг)", callback_data="onboard_lawyer")],
        [InlineKeyboardButton(text="🏥 Медицина и Стоматология", callback_data="onboard_dentist")],
        [InlineKeyboardButton(text="🚗 Автобизнес (СТО, Продажи)", callback_data="onboard_auto")],
        [InlineKeyboardButton(text="💇‍♀️ Бьюти-сфера (Салоны)", callback_data="onboard_beauty")],
        [InlineKeyboardButton(text="🏢 Другое (Показать всё меню)", callback_data="main_menu")]
    ])

    await message.answer(welcome_text, reply_markup=markup, parse_mode="HTML")"""

new_welcome = """    if not user_exists:
        welcome_text = (
            f"🌆 <b>{greeting}, {message.from_user.first_name}!</b>\\n\\n"
            "<b>Eidos System</b> — цифровой шоурум Архитектора систем автоматизации.\\n\\n"
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
            f"🌆 <b>С возвращением, {message.from_user.first_name}!</b>\\n\\n"
            "<b>Eidos System</b> — цифровой шоурум Архитектора систем автоматизации.\\n\\n"
            "Выберите раздел для изучения:"
        )
        markup = get_main_menu_keyboard()

    # If the user has a profile photo or we just send an HTML message (simulating a banner with rich text)
    await message.answer(welcome_text, reply_markup=markup, parse_mode="HTML")"""

content = content.replace(old_welcome, new_welcome)

with open("bot/handlers/base.py", "w") as f:
    f.write(content)
