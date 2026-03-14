# Eidos System — Демонстрационный проект

Премиальный Telegram бот и TWA (Telegram Web App) витрина для тестирования системы "Я — Клиент" и "Я — Владелец бизнеса", с теневым трекингом действий пользователя.

---

## 🛠 Архитектура

- **Бэкенд (bot)**: Чистый Python, aiogram 3.x, FSM, Middlewares.
- **Фронтенд (webapp)**: TWA SDK, Vite, React, Zustand, React Query, Tailwind CSS. Стилизация в Gothic Tech-RPG / Cyberpunk (backdrop-blur, clip-path).
- **База Данных**: Supabase (PostgreSQL).
- **Деплой**: Render.com (через `render.yaml`).

---

## 🚀 Деплой на Render

Для развертывания системы используется инфраструктурный файл `render.yaml`.
Вам потребуется подключить этот GitHub-репозиторий в панель Render (Blueprint Deploy).

### Секретные переменные окружения (Environment Variables)

В Render (в настройках Worker сервиса `eidos-bot`) необходимо добавить следующие секреты:

1. `BOT_TOKEN`: Токен вашего бота (получите у [@BotFather](https://t.me/BotFather)).
2. `ADMIN_ID`: Ваш Telegram ID (цифры), куда будут приходить скрытые алерты ("🔥 Лид @username сейчас тестирует админ-панель"). Получите, например, у @getmyid_bot.
3. `WEBAPP_URL`: Ссылка на ваш задеплоенный статический сайт (например: `https://eidos-webapp.onrender.com`).
4. `SUPABASE_URL`: Ссылка на ваш проект Supabase (см. раздел "База Данных").
5. `SUPABASE_KEY`: Ваш анонимный `anon` ключ Supabase.

> **Примечание:** Если `SUPABASE_URL` или `SUPABASE_KEY` не указаны, бот запустится в моковом режиме (заявки не будут сохраняться, только логироваться в консоли).

---

## 🗄 Настройка Базы Данных (Supabase)

Система использует облачную БД [Supabase](https://supabase.com).
Чтобы бот мог корректно сохранять лиды, вам необходимо:

1. Зарегистрироваться в Supabase и создать новый проект.
2. Перейти в **SQL Editor** (слева в меню панели).
3. Выполнить следующий SQL запрос для создания таблицы `leads`:

```sql
CREATE TABLE public.leads (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    username TEXT,
    user_id BIGINT,
    item_title TEXT,
    item_price TEXT
);

-- Настройка политик безопасности (RLS)
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;

-- Разрешаем чтение и запись (для демо-проекта)
CREATE POLICY "Enable read access for all users" ON public.leads FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON public.leads FOR INSERT WITH CHECK (true);
```

4. Скопировать `Project URL` и `anon public API Key` (в разделе Settings -> API) и вставить их в Render как переменные `SUPABASE_URL` и `SUPABASE_KEY`.

---

## 💻 Локальный запуск (Разработка)

### Фронтенд (TWA)
```bash
cd webapp
npm install
npm run dev # (Не забудьте запустить это в фоне или в отдельном терминале)
```

### Бэкенд (Bot)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r bot/requirements.txt
# Создайте файл .env внутри папки bot с необходимыми секретами
python bot/main.py
```
