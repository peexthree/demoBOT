with open("bot/handlers/client.py", "r") as f:
    content = f.read()

content = content.replace('save_lead_request(', 'await save_lead_request(')
content = content.replace('save_event(', 'await save_event(')

with open("bot/handlers/client.py", "w") as f:
    f.write(content)
