with open("bot/handlers/demo.py", "r") as f:
    content = f.read()

# Replace the direct generate_content_async calls with the new fallback logic
# Remove the old import block
old_import = """try:
    import google.generativeai as genai
    API_KEY = os.getenv("API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        model = None
except ImportError:
    model = None"""

content = content.replace(old_import, "from bot.ai_utils import generate_with_fallback, API_KEY")

# Replace `if model:` with `if API_KEY:`
content = content.replace("if model:", "if API_KEY:")

# Replace in demo_ai_ask
content = content.replace(
    "response = await model.generate_content_async(prompt)\n             answer_text = response.text",
    "answer_text = await generate_with_fallback(prompt)"
)

# Replace in demo_vision
content = content.replace(
    "response = await model.generate_content_async([prompt, image_parts[0]])\n            answer_text = response.text",
    "answer_text = await generate_with_fallback(prompt, image_parts=[image_parts[0]])"
)

# Replace in demo_voice
content = content.replace(
    "response = await model.generate_content_async([prompt, uploaded_file])\n                answer_text = response.text",
    "answer_text = await generate_with_fallback(prompt, file_part=uploaded_file)"
)
# Make sure genai is still accessible for the file upload
content = content.replace("uploaded_file = genai.upload_file(tmp_path)", "import google.generativeai as genai\n                uploaded_file = genai.upload_file(tmp_path)")

# Replace in demo_calculator
content = content.replace(
    "response = await model.generate_content_async(prompt)\n                 ai_text = response.text",
    "ai_text = await generate_with_fallback(prompt)"
)

with open("bot/handlers/demo.py", "w") as f:
    f.write(content)
