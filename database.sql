-- Инициализация расширения pgvector для семантического поиска
CREATE EXTENSION IF NOT EXISTS vector;

-- Устанавливаем часовой пояс
SET TIME ZONE 'UTC';

-----------------------------------------
-- 1. ТАБЛИЦА: users (Пользователи)
-----------------------------------------
CREATE TABLE public.users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    pro_status BOOLEAN DEFAULT FALSE,
    pro_expires_at TIMESTAMP WITH TIME ZONE,
    tokens_used BIGINT DEFAULT 0,
    free_requests_left INT DEFAULT 5, -- Фримиум (Трипвайер)
    referred_by BIGINT, -- ID пригласившего
    total_referrals INT DEFAULT 0
);

-----------------------------------------
-- 2. ТАБЛИЦА: business_profiles (Профили бизнеса)
-----------------------------------------
CREATE TABLE public.business_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(telegram_id) ON DELETE CASCADE,
    project_url TEXT,
    project_name TEXT NOT NULL,
    niche TEXT,
    target_audience TEXT,
    tone_of_voice TEXT DEFAULT 'Экспертный', -- Заботливый, Агрессивный, Ироничный
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-----------------------------------------
-- 3. ТАБЛИЦА: ai_cache_vector (Семантический кэш)
-----------------------------------------
CREATE TABLE public.ai_cache_vector (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_text TEXT NOT NULL,
    prompt_embedding vector(768), -- Размерность зависит от модели (для Google text-embedding-004: 768)
    response_json JSONB NOT NULL,
    tool_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    hit_count INT DEFAULT 0
);

-- Индекс для быстрого векторного поиска (HNSW)
CREATE INDEX ON public.ai_cache_vector USING hnsw (prompt_embedding vector_cosine_ops);

-----------------------------------------
-- 4. ТАБЛИЦА: transactions (Платежи)
-----------------------------------------
CREATE TABLE public.transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(telegram_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'RUB', -- RUB или STARS
    provider TEXT NOT NULL, -- yookassa, telegram_stars
    payment_id TEXT UNIQUE,
    status TEXT DEFAULT 'pending', -- success, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-----------------------------------------
-- 5. ТАБЛИЦА: leads (Для совместимости с текущим кодом)
-----------------------------------------
CREATE TABLE IF NOT EXISTS public.leads (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    username TEXT,
    user_id BIGINT,
    item_title TEXT,
    item_price TEXT
);

-----------------------------------------
-- 6. ТАБЛИЦА: events (Аналитика/События)
-----------------------------------------
CREATE TABLE IF NOT EXISTS public.events (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    user_id BIGINT,
    username TEXT,
    action TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-----------------------------------------
-- НАСТРОЙКА БЕЗОПАСНОСТИ (RLS - Row Level Security)
-----------------------------------------
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_cache_vector ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;

-- Разрешаем сервисному ключу (бота) делать что угодно (он использует anon key, если не настроен service_role)
-- Для демо-запуска открываем доступ
CREATE POLICY "Enable all for users" ON public.users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for profiles" ON public.business_profiles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for cache" ON public.ai_cache_vector FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for transactions" ON public.transactions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for leads" ON public.leads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for events" ON public.events FOR ALL USING (true) WITH CHECK (true);

-----------------------------------------
-- RPC Функция для семантического поиска
-----------------------------------------
CREATE OR REPLACE FUNCTION match_prompts (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  p_tool_name text
)
RETURNS TABLE (
  id uuid,
  prompt_text text,
  response_json jsonb,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    ai_cache_vector.id,
    ai_cache_vector.prompt_text,
    ai_cache_vector.response_json,
    1 - (ai_cache_vector.prompt_embedding <=> query_embedding) AS similarity
  FROM ai_cache_vector
  WHERE 1 - (ai_cache_vector.prompt_embedding <=> query_embedding) > match_threshold
    AND ai_cache_vector.tool_name = p_tool_name
  ORDER BY similarity DESC
  LIMIT match_count;
$$;
