import re

with open("bot/main.py", "r") as f:
    content = f.read()

# Register the global error handler right before logging.info("Starting bot...")
content = content.replace('logging.info("Starting bot...")', 'dp.errors.register(global_error_handler)\n\n    logging.info("Starting bot...")')

with open("bot/main.py", "w") as f:
    f.write(content)
