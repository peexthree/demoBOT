import os
import logging
import asyncio
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client | None = None

if url and key:
    try:
        if url.startswith("postgresql://"):
            parts = url.split("postgres.")[1].split(":")
            project_ref = parts[0]
            url = f"https://{project_ref}.supabase.co"
        supabase = create_client(url, key)
        logging.info("Успешное подключение к Supabase.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации Supabase: {e}")
else:
    logging.warning("SUPABASE_URL или SUPABASE_KEY не установлены. База данных отключена (моковый режим).")

async def save_lead_request(data: dict):
    if not supabase:
        logging.warning(f"Моковое сохранение лида: {data}")
        return

    try:
        def _save_lead():
            return supabase.table("leads").insert(data).execute()

        await asyncio.to_thread(_save_lead)
        logging.info(f"Лид успешно сохранен")
    except Exception as e:
        logging.error(f"Ошибка при сохранении лида: {e}")

async def save_event(data: dict):
    if not supabase:
        logging.warning(f"Моковое сохранение события: {data}")
        return

    try:
        def _save_event():
            return supabase.table("events").insert(data).execute()

        await asyncio.to_thread(_save_event)
        logging.info(f"Событие успешно сохранено")
    except Exception as e:
        logging.error(f"Ошибка при сохранении события: {e}")

async def save_user(user_id: int, username: str, first_name: str, last_name: str = ""):
    if not supabase:
        logging.warning(f"Моковое сохранение пользователя: {user_id}")
        return False # False means we couldn't check if user existed

    try:
        def _save_user():
            # Check if user exists, if not insert
            existing = supabase.table("users").select("*").eq("id", user_id).execute()
            if not existing.data:
                full_name = f"{first_name} {last_name}".strip()
                supabase.table("users").insert({
                    "id": user_id,
                    "username": username,
                    "full_name": full_name
                }).execute()
                return False # New user
            return True # User already exists

        exists = await asyncio.to_thread(_save_user)
        logging.info(f"Пользователь {user_id} проверен. Существует: {exists}")
        return exists
    except Exception as e:
        # Ignore errors if table doesn't exist yet, as we might only have leads/events
        logging.error(f"Ошибка при сохранении пользователя (возможно нет таблицы users): {e}")
        return False
