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

async def save_chat_history(user_id: int, role: str, content: str):
    from bot.db import supabase
    if not supabase:
        return
    try:
        def _save():
            supabase.table("dialog_history").insert({
                "user_id": user_id,
                "role": role,
                "content": content
            }).execute()
        await asyncio.to_thread(_save)
    except Exception as e:
        logging.error(f"Failed to save chat history: {e}")

async def get_chat_history(user_id: int, limit: int = 10):
    from bot.db import supabase
    if not supabase:
        return []
    try:
        def _fetch():
            resp = supabase.table("dialog_history").select("*").eq("user_id", user_id).order("created_at", desc=False).limit(limit).execute()
            return resp.data
        return await asyncio.to_thread(_fetch)
    except Exception as e:
        logging.error(f"Failed to fetch chat history: {e}")
        return []

async def generate_with_fallback(prompt, image_parts=None, file_part=None, user_id=None, system_prompt=None):
    if not os.getenv("API_KEY"):
        raise Exception("API_KEY not set")

    history = []
    if user_id and not image_parts and not file_part:
        raw_history = await get_chat_history(user_id, limit=5)
        for msg in raw_history:
            history.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})

    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            logging.info(f"Attempting generate_content with model {model_name}")
            model = genai.GenerativeModel(model_name, system_instruction=system_prompt) if system_prompt else genai.GenerativeModel(model_name)

            contents = history.copy()
            user_parts = [{"text": prompt}]

            if image_parts:
                user_parts.extend(image_parts)
            if file_part:
                user_parts.append(file_part)

            contents.append({"role": "user", "parts": user_parts})

            response = await model.generate_content_async(contents)

            if user_id:
                asyncio.create_task(save_chat_history(user_id, "user", prompt))
                asyncio.create_task(save_chat_history(user_id, "model", response.text))
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
