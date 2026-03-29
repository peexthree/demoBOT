import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AIGeneratedCard } from '../components/AIGeneratedCard';
import { BlurredPaywall } from '../components/BlurredPaywall';
import { AILoadingSkeleton } from '../components/AILoadingSkeleton';
import WebApp from '@twa-dev/sdk';
import { useAppStore } from '../store';

const MOCK_TOOLS_L1 = [
  { id: 'content_ideas', title: 'Посты (5 идей)', icon: '📝' },
  { id: 'ads_copy', title: 'Рекламный креатив', icon: '🎯' },
  { id: 'ab_test', title: 'A/B Заголовки', icon: '🧪' },
  { id: 'week_plan', title: 'Контент-план', icon: '📅' },
];

const MOCK_TOOLS_L2 = [
  { id: 'competitor_intel', title: 'Разведка конкурентов', icon: '🕵️', isPro: true },
  { id: 'growth_os', title: 'Growth OS', icon: '📈', isPro: true },
  { id: 'card_detective', title: 'Аудит карточек WB', icon: '🔍', isPro: true },
];

export const DashboardScreen = () => {
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [promptInput, setPromptInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const { isPro, userId } = useAppStore();

  const handleToolClick = (tool: any) => {
    if (tool.isPro && !isPro) {
      if (WebApp.HapticFeedback) WebApp.HapticFeedback.notificationOccurred('warning');
      setSelectedTool(tool.id);
      return;
    }
    setSelectedTool(tool.id);
    setResult(null);
    setError(null);
    if (WebApp.HapticFeedback) WebApp.HapticFeedback.selectionChanged();
  };

  const generateContent = async () => {
    if (!promptInput.trim() || !selectedTool) return;

    setIsGenerating(true);
    setError(null);
    setResult(null);

    if (WebApp.HapticFeedback) WebApp.HapticFeedback.impactOccurred('light');

    try {
      // Mocking the API call for now. In real app we fetch to /api/generate
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'https://lid-flow.vercel.app/api'}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, tool_name: selectedTool, prompt: promptInput }),
      });

      const data = await response.json();

      if (data.error === "limit_reached") {
        setError("Лимит бесплатных запросов исчерпан. Оформите PRO.");
        if (WebApp.HapticFeedback) WebApp.HapticFeedback.notificationOccurred('error');
      } else if (data.status === "processing") {
        setResult("Задача отправлена агентам ИИ. Вы получите Push-уведомление в Telegram по готовности.");
        if (WebApp.HapticFeedback) WebApp.HapticFeedback.notificationOccurred('success');
      } else {
        setResult(data);
        if (WebApp.HapticFeedback) WebApp.HapticFeedback.notificationOccurred('success');
      }
    } catch (err) {
      console.error(err);
      setError("Ошибка соединения с сервером ИИ.");
      if (WebApp.HapticFeedback) WebApp.HapticFeedback.notificationOccurred('error');
    } finally {
      setIsGenerating(false);
    }
  };

  const triggerProPurchase = () => {
    // Отправляем данные обратно в бота для генерации инвойса
    WebApp.sendData(JSON.stringify({ action: 'buy_pro' }));
    WebApp.close();
  };

  return (
    <div className="p-4 flex flex-col gap-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold font-mono text-eidos-cyan text-glow">Терминал Управления</h1>
          <p className="text-xs text-eidos-text opacity-70 font-mono">Версия: 1.0.0-MVP</p>
        </div>
        {!isPro && (
          <button onClick={triggerProPurchase} className="bg-gradient-to-r from-yellow-600 to-yellow-400 text-black text-xs px-3 py-1 font-bold rounded shadow-[0_0_10px_rgba(252,211,77,0.5)]">
            UPGRADE PRO
          </button>
        )}
      </div>

      <section>
        <h2 className="text-sm font-mono text-eidos-gray mb-3 uppercase tracking-wider">Слой 1: Быстрые инструменты</h2>
        <div className="grid grid-cols-2 gap-3">
          {MOCK_TOOLS_L1.map(tool => (
            <button
              key={tool.id}
              onClick={() => handleToolClick(tool)}
              className={`p-3 rounded border text-left transition-all ${
                selectedTool === tool.id
                  ? 'bg-eidos-cyan/10 border-eidos-cyan shadow-[0_0_10px_rgba(102,252,241,0.2)]'
                  : 'bg-eidos-surface border-eidos-gray/30 hover:border-eidos-gray'
              }`}
            >
              <div className="text-2xl mb-1">{tool.icon}</div>
              <div className="text-xs font-bold text-eidos-text">{tool.title}</div>
            </button>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-sm font-mono text-yellow-500/70 mb-3 uppercase tracking-wider flex items-center gap-2">
          Слой 2: PRO Аналитика
        </h2>
        <div className="grid grid-cols-2 gap-3">
          {MOCK_TOOLS_L2.map(tool => (
            <button
              key={tool.id}
              onClick={() => handleToolClick(tool)}
              className={`p-3 rounded border text-left relative overflow-hidden transition-all ${
                selectedTool === tool.id
                  ? 'bg-yellow-500/10 border-yellow-500'
                  : 'bg-eidos-surface border-eidos-gray/30'
              }`}
            >
              {!isPro && <div className="absolute top-1 right-1 text-[10px] bg-yellow-500/20 text-yellow-500 px-1 rounded font-mono">PRO</div>}
              <div className="text-2xl mb-1 opacity-80">{tool.icon}</div>
              <div className="text-xs font-bold text-gray-400">{tool.title}</div>
            </button>
          ))}
        </div>
      </section>

      {/* Рабочая область выбранного инструмента */}
      {selectedTool && (
        <div className="mt-4 bg-black/40 p-4 border-t border-eidos-gray/30 rounded-t-xl -mx-4 pb-10">
          <h3 className="text-eidos-cyan font-mono mb-4 text-sm flex items-center gap-2">
            <span className="w-2 h-2 bg-eidos-cyan rounded-full animate-pulse"></span>
            АКТИВНЫЙ МОДУЛЬ: {selectedTool.toUpperCase()}
          </h3>

          {MOCK_TOOLS_L2.find(t => t.id === selectedTool)?.isPro && !isPro ? (
            <BlurredPaywall onUnlock={triggerProPurchase} title="Модуль доступен в PRO" />
          ) : (
            <div className="flex flex-col gap-4">
              <textarea
                className="w-full bg-eidos-surface border border-eidos-gray/30 rounded p-3 text-sm text-white focus:outline-none focus:border-eidos-cyan min-h-[100px] font-mono resize-none placeholder-gray-600"
                placeholder="Введите тему, продукт или целевую аудиторию..."
                value={promptInput}
                onChange={e => setPromptInput(e.target.value)}
              />

              <button
                className="eidos-btn w-full"
                onClick={generateContent}
                disabled={isGenerating || !promptInput.trim()}
              >
                {isGenerating ? 'СИНТЕЗ ДАННЫХ...' : 'ЗАПУСТИТЬ АГЕНТА'}
              </button>

              {error && <div className="text-red-400 text-xs font-mono p-2 bg-red-400/10 border border-red-400/20 rounded mt-2">{error}</div>}

              {isGenerating && (
                 <div className="mt-6"><AILoadingSkeleton /></div>
              )}

              {result && !isGenerating && (
                <div className="mt-6">
                  <h4 className="text-xs text-eidos-gray font-mono mb-3 uppercase">Результат:</h4>
                  <AIGeneratedCard title={selectedTool} content={result} />
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
