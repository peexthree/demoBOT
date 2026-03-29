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


# --- Базовые методы (Лиды и События) ---

async def save_lead_request(data: dict):
    if not supabase: return
    try:
        await asyncio.to_thread(lambda: supabase.table("leads").insert(data).execute())
    except Exception as e:
        logging.error(f"Ошибка при сохранении лида: {e}")

async def save_event(data: dict):
    if not supabase: return
    try:
        await asyncio.to_thread(lambda: supabase.table("events").insert(data).execute())
    except Exception as e:
        logging.error(f"Ошибка при сохранении события: {e}")


# --- Пользователи (users) ---

async def save_user(telegram_id: int, username: str, full_name: str, referred_by: int = None):
    """
    Проверяет существование пользователя. Если нет - создает.
    Возвращает True, если пользователь УЖЕ существовал, и False, если это новый.
    """
    if not supabase: return False
    try:
        def _save_user():
            existing = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
            if not existing.data:
                data = {
                    "telegram_id": telegram_id,
                    "username": username,
                    "full_name": full_name
                }
                if referred_by and referred_by != telegram_id:
                    data["referred_by"] = referred_by
                    # Обновляем счетчик у пригласившего
                    try:
                        referrer = supabase.table("users").select("total_referrals").eq("telegram_id", referred_by).execute()
                        if referrer.data:
                            new_count = referrer.data[0].get("total_referrals", 0) + 1
                            supabase.table("users").update({"total_referrals": new_count}).eq("telegram_id", referred_by).execute()
                    except Exception as ref_e:
                        logging.error(f"Ошибка обновления рефералки: {ref_e}")

                supabase.table("users").insert(data).execute()
                return False
            else:
                # Обновляем last_active
                supabase.table("users").update({"last_active": "now()"}).eq("telegram_id", telegram_id).execute()
                return True
        return await asyncio.to_thread(_save_user)
    except Exception as e:
        logging.error(f"Ошибка при сохранении пользователя: {e}")
        return False

async def get_user(telegram_id: int):
    if not supabase: return None
    try:
        res = await asyncio.to_thread(lambda: supabase.table("users").select("*").eq("telegram_id", telegram_id).execute())
        return res.data[0] if res.data else None
    except Exception as e:
        logging.error(f"Ошибка получения пользователя: {e}")
        return None

async def use_free_request(telegram_id: int) -> bool:
    """Уменьшает счетчик бесплатных запросов. Возвращает True, если запрос разрешен."""
    user = await get_user(telegram_id)
    if not user: return False
    if user.get("pro_status", False): return True # У PRO нет лимитов

    left = user.get("free_requests_left", 0)
    if left > 0:
        await asyncio.to_thread(
            lambda: supabase.table("users").update({"free_requests_left": left - 1}).eq("telegram_id", telegram_id).execute()
        )
        return True
    return False


# --- Профили бизнеса (business_profiles) ---

async def save_business_profile(user_id: int, project_url: str, project_name: str, niche: str, target_audience: str, tone_of_voice: str = 'Экспертный'):
    if not supabase: return
    try:
        def _save():
            existing = supabase.table("business_profiles").select("id").eq("user_id", user_id).execute()
            data = {
                "user_id": user_id,
                "project_url": project_url,
                "project_name": project_name,
                "niche": niche,
                "target_audience": target_audience,
                "tone_of_voice": tone_of_voice,
                "updated_at": "now()"
            }
            if existing.data:
                supabase.table("business_profiles").update(data).eq("user_id", user_id).execute()
            else:
                supabase.table("business_profiles").insert(data).execute()
        await asyncio.to_thread(_save)
    except Exception as e:
        logging.error(f"Ошибка при сохранении профиля: {e}")

async def get_business_profile(user_id: int):
    if not supabase: return None
    try:
        res = await asyncio.to_thread(lambda: supabase.table("business_profiles").select("*").eq("user_id", user_id).execute())
        return res.data[0] if res.data else None
    except Exception as e:
        return None


# --- Семантическое кэширование (pgvector) ---

async def search_semantic_cache(prompt_embedding: list[float], tool_name: str, match_threshold: float = 0.95):
    """Ищет похожий промпт через RPC вызов."""
    if not supabase: return None
    try:
        res = await asyncio.to_thread(
            lambda: supabase.rpc("match_prompts", {
                "query_embedding": prompt_embedding,
                "match_threshold": match_threshold,
                "match_count": 1,
                "p_tool_name": tool_name
            }).execute()
        )
        if res.data and len(res.data) > 0:
            # Увеличиваем hit_count
            cache_id = res.data[0]["id"]
            await asyncio.to_thread(
                lambda: supabase.table("ai_cache_vector").update({
                    "hit_count": supabase.table("ai_cache_vector").select("hit_count").eq("id", cache_id).execute().data[0]["hit_count"] + 1
                }).eq("id", cache_id).execute()
            )
            return res.data[0]["response_json"]
        return None
    except Exception as e:
        logging.error(f"Ошибка поиска в векторном кэше: {e}")
        return None

async def save_to_semantic_cache(prompt_text: str, prompt_embedding: list[float], response_json: dict, tool_name: str):
    if not supabase: return
    try:
        await asyncio.to_thread(
            lambda: supabase.table("ai_cache_vector").insert({
                "prompt_text": prompt_text,
                "prompt_embedding": prompt_embedding,
                "response_json": response_json,
                "tool_name": tool_name
            }).execute()
        )
    except Exception as e:
        logging.error(f"Ошибка сохранения в кэш: {e}")


# --- Платежи (transactions) ---

async def save_transaction(user_id: int, amount: float, currency: str, provider: str, payment_id: str, status: str = 'pending'):
    if not supabase: return
    try:
        await asyncio.to_thread(
            lambda: supabase.table("transactions").insert({
                "user_id": user_id,
                "amount": amount,
                "currency": currency,
                "provider": provider,
                "payment_id": payment_id,
                "status": status
            }).execute()
        )
    except Exception as e:
        logging.error(f"Ошибка сохранения транзакции: {e}")

async def update_transaction_status(payment_id: str, status: str):
    if not supabase: return
    try:
        await asyncio.to_thread(
            lambda: supabase.table("transactions").update({"status": status}).eq("payment_id", payment_id).execute()
        )
    except Exception as e:
        logging.error(f"Ошибка обновления статуса транзакции: {e}")

async def grant_pro_status(user_id: int, days: int = 30):
    """Выдает PRO статус на указанное количество дней."""
    if not supabase: return
    try:
        # Для простоты в MVP ставим pro_status = True без сложного расчета pro_expires_at,
        # но если надо - можно добавить интервал времени.
        await asyncio.to_thread(
            lambda: supabase.table("users").update({"pro_status": True}).eq("telegram_id", user_id).execute()
        )
    except Exception as e:
        logging.error(f"Ошибка выдачи PRO статуса: {e}")
