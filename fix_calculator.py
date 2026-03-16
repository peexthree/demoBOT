with open("bot/handlers/demo.py", "r") as f:
    content = f.read()

# Fix the condition inside demo_calculator:
# if callback.data == "demo_calc": -> if callback.data == "demo_calculator":
content = content.replace(
    'if callback.data == "demo_calc":\n        step = "start"',
    'if callback.data == "demo_calculator" or callback.data == "demo_calc":\n        step = "start"'
)

with open("bot/handlers/demo.py", "w") as f:
    f.write(content)
