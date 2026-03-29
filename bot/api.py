from aiohttp import web
import logging
import asyncio
import json
from bot.db import (
    supabase, get_user, save_business_profile, get_business_profile,
    use_free_request, save_event
)
from bot.ai_utils import run_agent_chain

async def cors_middleware(app, handler):
    async def middleware_handler(request):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    return middleware_handler

async def options_handler(request):
    return web.Response()

async def api_crm(request):
    """(Обратная совместимость) API для демо-дашборда CRM"""
    try:
        if not supabase:
            return web.json_response({"error": "No database connection"}, status=500)

        data = await asyncio.to_thread(lambda: supabase.table("leads").select("*").order("created_at", desc=True).limit(10).execute().data)

        total_revenue, formatted_leads = 0, []
        for idx, row in enumerate(data):
            try:
                price = int(str(row.get('item_price', '0')).replace(' ', '').replace('₽', ''))
                total_revenue += price
            except ValueError:
                price = 0

            formatted_leads.append({
                "id": row.get('id'),
                "name": row.get('username') or f"User {row.get('user_id')}",
                "action": row.get('item_title', 'Запрос'),
                "amount": f"₽ {price:,}".replace(',', ' '),
                "status": "new" if idx % 3 == 0 else "active" if idx % 3 == 1 else "completed",
                "time": row.get('created_at', '')[:10]
            })

        return web.json_response({"totalRevenue": total_revenue, "leadsCount": len(data), "leads": formatted_leads})
    except Exception as e:
        logging.error(f"CRM API Error: {e}")
        return web.json_response({"error": str(e)}, status=500)

# --- НОВЫЕ ЭНДПОИНТЫ ДЛЯ MVP МАРКЕТОЛОГА ---

async def api_get_profile(request):
    """Получение цифрового профиля бизнеса"""
    try:
        user_id = int(request.query.get("user_id", 0))
        if not user_id: return web.json_response({"error": "user_id required"}, status=400)

        profile = await get_business_profile(user_id)
        user = await get_user(user_id)

        return web.json_response({
            "profile": profile,
            "user": user
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def api_save_profile(request):
    """Ручное сохранение/обновление профиля"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        if not user_id: return web.json_response({"error": "user_id required"}, status=400)

        await save_business_profile(
            user_id=user_id,
            project_url=data.get("project_url", ""),
            project_name=data.get("project_name", ""),
            niche=data.get("niche", ""),
            target_audience=data.get("target_audience", ""),
            tone_of_voice=data.get("tone_of_voice", "Экспертный")
        )
        await save_event({"user_id": user_id, "action": "profile_updated"})
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# --- ФОНОВЫЕ ЗАДАЧИ ДЛЯ ИИ ---

async def background_ai_task(user_id: int, tool_name: str, prompt: str, profile: dict, bot):
    """Асинхронно выполняет ИИ цепочку и отправляет пуш юзеру"""
    try:
        logging.info(f"Start BG task for {user_id}: {tool_name}")
        tone = profile.get("tone_of_voice", "Экспертный") if profile else "Экспертный"

        # 1. Запуск агентов
        result = await run_agent_chain(prompt, tool_name, tone_of_voice=tone)

        # 2. Сохраняем событие аналитики
        await save_event({"user_id": user_id, "action": f"ai_completed_{tool_name}", "metadata": {"status": "success"}})

        # 3. Отправляем Push (через aiohttp сессию бота или вызов метода)
        # Здесь мы предполагаем, что bot проброшен в request.app
        try:
            import json
            # В MVP мы можем отправить JSON или отформатированный текст прямо в чат
            formatted_text = f"🤖 **Задача готова:** {tool_name}\n\n"
            if "error" in result:
                formatted_text += f"Ошибка: {result['error']}"
            else:
                formatted_text += "Результаты доступны в приложении. Откройте TWA, чтобы посмотреть."

            await bot.send_message(chat_id=user_id, text=formatted_text)
        except Exception as e:
            logging.error(f"Failed to send push to {user_id}: {e}")

    except Exception as e:
        logging.error(f"BG task error for {user_id}: {e}")
        await save_event({"user_id": user_id, "action": f"ai_failed_{tool_name}", "metadata": {"error": str(e)}})


async def api_generate_content(request):
    """Точка входа для инструментов (Слой 1 и 2)"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        tool_name = data.get("tool_name") # Например: 'content_ideas', 'ab_test'
        prompt = data.get("prompt")

        if not all([user_id, tool_name, prompt]):
            return web.json_response({"error": "user_id, tool_name, prompt required"}, status=400)

        user = await get_user(user_id)
        if not user:
            return web.json_response({"error": "user not found"}, status=404)

        # Проверяем лимиты
        is_pro = user.get("pro_status", False)
        if not is_pro and not await use_free_request(user_id):
            return web.json_response({"error": "limit_reached", "paywall": True}, status=403)

        profile = await get_business_profile(user_id)

        # Запускаем ИИ в фоне (для долгих задач)
        bot = request.app.get('bot')
        asyncio.create_task(background_ai_task(user_id, tool_name, prompt, profile, bot))

        # Возвращаем task_id фронтенду (упрощенно)
        return web.json_response({
            "success": True,
            "status": "processing",
            "message": "Задача взята в работу. Вы получите пуш-уведомление по готовности."
        })

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
