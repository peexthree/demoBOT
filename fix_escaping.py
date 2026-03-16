import re

with open("bot/handlers/client.py", "r") as f:
    content = f.read()

# Add html escaping to client.py user inputs
old_checkout = """f"🎉 Вы успешно оформили заказ: <b>{item.get('title')}</b>.\\n\""""
new_checkout = """import html
            f"🎉 Вы успешно оформили заказ: <b>{html.escape(str(item.get('title')))}</b>.\\n\""""
content = content.replace(old_checkout, new_checkout)

old_checkout_admin = """f"👤 Пользователь: {user_link}\\n\"\n                        f"📦 Товар: <b>{item.get('title')}</b>\\n\""""
new_checkout_admin = """f"👤 Пользователь: {html.escape(user_link)}\\n\"\n                        f"📦 Товар: <b>{html.escape(str(item.get('title')))}</b>\\n\""""
content = content.replace(old_checkout_admin, new_checkout_admin)

old_broadcast = """response_text = f"📢 <b>Демо-рассылка</b>\\n\\n{text}\\n\\n(Всем пользователям якобы ушло это сообщение)\""""
new_broadcast = """response_text = f"📢 <b>Демо-рассылка</b>\\n\\n{html.escape(str(text))}\\n\\n(Всем пользователям якобы ушло это сообщение)\""""
content = content.replace(old_broadcast, new_broadcast)

with open("bot/handlers/client.py", "w") as f:
    f.write(content)

with open("bot/handlers/demo.py", "r") as f:
    content = f.read()

# Escape AI history text that could have arbitrary symbols
old_history = """history += f" User: {message.text}. You: {answer_text}.\""""
new_history = """import html
             history += f" User: {html.escape(message.text)}. You: {html.escape(answer_text)}.\""""
content = content.replace(old_history, new_history)

with open("bot/handlers/demo.py", "w") as f:
    f.write(content)
