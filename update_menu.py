import re

with open("bot/handlers/demo.py", "r") as f:
    content = f.read()

# Remove the menu button from the inline keyboard
content = re.sub(
    r'\s*\[InlineKeyboardButton\(text="🔄 Меню \(/start\)", callback_data="main_menu"\)\]',
    '',
    content
)

# Add the text menu button to the reply keyboard
content = content.replace(
    '            [KeyboardButton(text="Скрыть меню")]',
    '            [KeyboardButton(text="Вызвать меню")],\n            [KeyboardButton(text="Скрыть меню")]'
)

with open("bot/handlers/demo.py", "w") as f:
    f.write(content)
