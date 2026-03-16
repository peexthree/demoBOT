import ast
with open("bot/handlers/demo.py", "r") as f:
    ast.parse(f.read())
print("Syntax OK")
