with open("bot/handlers/demo.py", "r") as f:
    content = f.read()

content = content.replace('],\n        \n    ])', ']\n    ])')
content = content.replace('url=f"tg://user?id={os.getenv(\'ADMIN_ID\', \'0\')}")],\n    ])', 'url=f"tg://user?id={os.getenv(\'ADMIN_ID\', \'0\')}")]\n    ])')

with open("bot/handlers/demo.py", "w") as f:
    f.write(content)
