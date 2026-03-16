with open("bot/handlers/client.py", "r") as f:
    content = f.read()

# Replace message.answer with appropriate menu return
old_ans_checkout = """await message.answer(response_text, parse_mode="HTML")"""
new_ans_checkout = """from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await message.answer(
                response_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]])
            )"""

content = content.replace(old_ans_checkout, new_ans_checkout, 1) # Only first one for checkout

old_ans_broadcast = """await message.answer(response_text, parse_mode="HTML")"""
new_ans_broadcast = """from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await message.answer(
                response_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]])
            )"""
content = content.replace(old_ans_broadcast, new_ans_broadcast, 1)

old_ans_base = """await message.answer(response_text, parse_mode="HTML")"""
new_ans_base = """from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            await message.answer(
                response_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Главное меню (/start)", callback_data="main_menu")]])
            )"""
content = content.replace(old_ans_base, new_ans_base, 1)

with open("bot/handlers/client.py", "w") as f:
    f.write(content)
