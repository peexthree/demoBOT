from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def get_demo_keyboard(role="guest"):
    if role == "client":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Каталог товаров", callback_data="demo_catalog")],
            [InlineKeyboardButton(text="📅 Запись на услугу", callback_data="demo_booking")],
            [InlineKeyboardButton(text="💎 Мои бонусы (Лояльность)", callback_data="demo_loyalty")],
            [InlineKeyboardButton(text="🎫 Служба поддержки", callback_data="demo_support")],
            [InlineKeyboardButton(text="🔄 Сменить роль на 'Бизнес'", callback_data="role_admin")]
        ])
    elif role == "admin":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Аналитика продаж", callback_data="demo_analytics")],
            [InlineKeyboardButton(text="👥 Управление лидами (CRM)", callback_data="demo_crm")],
            [InlineKeyboardButton(text="📢 Сделать рассылку", callback_data="demo_broadcast")],
            [InlineKeyboardButton(text="⚙️ Настройки бизнеса", callback_data="demo_settings")],
            [InlineKeyboardButton(text="🔄 Сменить роль на 'Клиент'", callback_data="role_client")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Войти как Клиент", callback_data="role_client")],
            [InlineKeyboardButton(text="👑 Войти как Владелец бизнеса", callback_data="role_admin")]
        ])

@router.callback_query(F.data.startswith("role_"))
async def switch_role(callback: types.CallbackQuery):
    role = callback.data.split("_")[1]
    if role == "client":
        text = "👤 *Режим Клиента*\n\nДобро пожаловать в демо-магазин! Выберите действие:"
    else:
        text = "👑 *Режим Владельца Бизнеса*\n\nДобро пожаловать в панель управления Eidos. Выберите инструмент:"

    await callback.message.edit_text(text, reply_markup=get_demo_keyboard(role), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "demo_catalog")
async def demo_catalog(callback: types.CallbackQuery):
    text = (
        "🛒 *Каталог (Демо)*\n\n"
        "1. Кроссовки Nike Air (5 000 ₽)\n"
        "2. Футболка Базовая (1 200 ₽)\n"
        "3. Худи Оверсайз (3 500 ₽)\n\n"
        "_В реальности здесь будут карточки с фото и кнопкой 'Купить'._"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Положить 1-й товар в корзину", callback_data="demo_buy")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="role_client")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "demo_buy")
async def demo_buy(callback: types.CallbackQuery):
    await callback.answer("✅ Товар добавлен в корзину! (демо)", show_alert=True)

@router.callback_query(F.data == "demo_analytics")
async def demo_analytics(callback: types.CallbackQuery):
    text = (
        "📊 *Аналитика за сегодня (Демо)*\n\n"
        "🔹 Просмотров: 1 245\n"
        "🔹 Новых клиентов: 15\n"
        "🔹 Оформлено заказов: 4\n"
        "💰 *Выручка: 24 500 ₽*\n\n"
        "_Здесь бизнес видит ключевые метрики онлайн._"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="role_admin")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "demo_crm")
async def demo_crm(callback: types.CallbackQuery):
    text = (
        "👥 *Мини-CRM (Демо)*\n\n"
        "Новые заявки:\n"
        "1. Иван (@ivan) — Заказ: Кроссовки Nike (Ожидает звонка)\n"
        "2. Анна (@anna) — Бронь на 18:00 (Подтверждено)\n\n"
        "_Владелец может принимать/отклонять заявки кнопками._"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять заявку Ивана", callback_data="demo_accept")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="role_admin")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "demo_accept")
async def demo_accept(callback: types.CallbackQuery):
    await callback.answer("✅ Заявка принята в работу! Клиенту отправлено уведомление.", show_alert=True)

@router.callback_query(F.data == "demo_booking")
async def demo_booking(callback: types.CallbackQuery):
    text = (
        "📅 *Запись на услугу (Демо)*\n\n"
        "Выберите свободное время на сегодня:\n"
        "12:00 | 14:30 | 18:00"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="12:00", callback_data="demo_book_time"),
            InlineKeyboardButton(text="14:30", callback_data="demo_book_time"),
            InlineKeyboardButton(text="18:00", callback_data="demo_book_time")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="role_client")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "demo_book_time")
async def demo_book_time(callback: types.CallbackQuery):
    await callback.answer("✅ Время забронировано!", show_alert=True)

@router.callback_query(F.data.in_({"demo_loyalty", "demo_support", "demo_broadcast", "demo_settings"}))
async def demo_stub(callback: types.CallbackQuery):
    await callback.answer("🚧 Этот раздел в разработке (Демонстрация возможности)", show_alert=True)
