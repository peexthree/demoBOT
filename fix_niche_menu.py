with open("bot/handlers/demo.py", "r") as f:
    content = f.read()

# Add a button about sending documents to the niche menu
old_niche_menu = """[InlineKeyboardButton(text="📷 Анализ по фото (Vision ИИ)", callback_data="demo_vision")],"""
new_niche_menu = """[InlineKeyboardButton(text="📷 Анализ по фото (Vision ИИ)", callback_data="demo_vision")],
            [InlineKeyboardButton(text="📄 Парсинг смет (Отправьте PDF)", callback_data="demo_docs")],"""

content = content.replace(old_niche_menu, new_niche_menu)

# Handle the click on the new button
content += """
@router.callback_query(F.data == "demo_docs")
async def demo_docs(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📄 <b>Умный Парсинг Смет и Документов</b>\n\n"
        "Отправьте мне любой PDF, Excel файл или скан счета. ИИ моментально прочитает его и сопоставит с прайсом CRM.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад / Отменить", callback_data="demo_niche_back")]]),
        parse_mode="HTML"
    )
    # We stay in DemoStates.in_niche, the document handler listens there
    await callback.answer()
"""

with open("bot/handlers/demo.py", "w") as f:
    f.write(content)
