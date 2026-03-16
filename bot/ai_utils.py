import os
import logging
import asyncio

try:
    import google.generativeai as genai
    API_KEY = os.getenv("API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
except ImportError:
    pass

# List of models to fallback to in case of rate limits or errors
# Ordered from most cost-efficient/fastest to most capable/heaviest
GEMINI_MODELS = [
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash"
]

async def generate_with_fallback(prompt, image_parts=None, file_part=None):
    if not os.getenv("API_KEY"):
        raise Exception("API_KEY not set")

    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            logging.info(f"Attempting generate_content with model {model_name}")
            model = genai.GenerativeModel(model_name)

            contents = [prompt]
            if image_parts:
                contents.extend(image_parts)
            if file_part:
                contents.append(file_part)

            response = await model.generate_content_async(contents)
            return response.text

        except Exception as e:
            error_msg = str(e).lower()
            logging.warning(f"Model {model_name} failed: {e}")
            last_error = e

            # If rate limit or resource exhausted, try next model
            if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                continue

            # For 500 errors, give a small delay and try next
            if "500" in error_msg or "internal" in error_msg:
                await asyncio.sleep(1)
                continue

            # If it's another error (like blocked content), don't fallback, just return
            raise e

    # If all models failed, raise the last rate limit error
    raise Exception(f"All fallback models failed. Last error: {last_error}")
