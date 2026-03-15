import os
import logging
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client | None = None

if url and key:
    try:
        supabase = create_client(url, key)
        logging.info("Успешное подключение к Supabase.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации Supabase: {e}")
else:
    logging.warning("SUPABASE_URL или SUPABASE_KEY не установлены. База данных отключена (моковый режим).")

def save_lead_request(data: dict):
    if not supabase:
        logging.warning(f"Моковое сохранение лида: {data}")
        return

    try:
        response = supabase.table("leads").insert(data).execute()
        logging.info(f"Лид успешно сохранен: {response.data}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении лида: {e}")

def save_event(data: dict):
    if not supabase:
        logging.warning(f"Моковое сохранение события: {data}")
        return


    try:
        # Temporary fix: event logging to DB disabled to avoid missing table error
        # response = supabase.table("events").insert(data).execute()
        # logging.info(f"Событие успешно сохранено: {response.data}")
        logging.info(f"Событие сохранено локально (БД отключена для events): {data}")
    except Exception as e:

        logging.error(f"Ошибка при сохранении события: {e}")
