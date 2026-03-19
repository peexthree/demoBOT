from aiohttp import web

async def api_crm(request):
    from bot.db import supabase
    import logging
    try:
        if not supabase:
            return web.json_response({"error": "No database connection"}, status=500, headers={"Access-Control-Allow-Origin": "*"})

        import asyncio

        def fetch_data():
            leads = supabase.table("leads").select("*").order("created_at", desc=True).limit(10).execute()
            return leads.data

        data = await asyncio.to_thread(fetch_data)

        total_revenue = 0
        formatted_leads = []

        for idx, row in enumerate(data):
            try:
                price_val = str(row.get('item_price', '0')).replace(' ', '').replace('₽', '')
                price = int(price_val)
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

        return web.json_response({"totalRevenue": total_revenue, "leadsCount": len(data), "leads": formatted_leads}, headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        logging.error(f"CRM API Error: {e}")
        return web.json_response({"error": str(e)}, status=500, headers={"Access-Control-Allow-Origin": "*"})
