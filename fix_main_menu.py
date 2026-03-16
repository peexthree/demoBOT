with open("bot/handlers/demo.py", "r") as f:
    content = f.read()

# Add referral button to main menu
old_main_menu = """[InlineKeyboardButton(text="💬 [ОБСУДИТЬ ПРОЕКТ]", url=f"tg://user?id={os.getenv('ADMIN_ID', '0')}")]"""
new_main_menu = """[InlineKeyboardButton(text="💬 [ОБСУДИТЬ ПРОЕКТ]", url=f"tg://user?id={os.getenv('ADMIN_ID', '0')}")],
        [InlineKeyboardButton(text="🤝 [ПАРТНЕРСКАЯ ПРОГРАММА]", callback_data="demo_referral")]"""

content = content.replace(old_main_menu, new_main_menu)

with open("bot/handlers/demo.py", "w") as f:
    f.write(content)
