import React from 'react';
import { motion } from 'framer-motion';
import { Lock } from 'lucide-react';

interface BlurredPaywallProps {
  onUnlock: () => void;
  title?: string;
}

export const BlurredPaywall = ({ onUnlock, title = "Разблокируйте PRO доступ" }: BlurredPaywallProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative w-full rounded-lg overflow-hidden border border-eidos-gray/20 shadow-[0_0_15px_rgba(69,162,158,0.2)]"
    >
      <div className="absolute inset-0 bg-eidos-bg/40 z-0"></div>

      {/* Фейковый контент для создания эффекта размытия */}
      <div className="p-6 opacity-30 blur-sm flex flex-col gap-4 filter pointer-events-none select-none">
        <div className="h-6 w-3/4 bg-gray-500/50 rounded animate-pulse"></div>
        <div className="h-4 w-full bg-gray-500/30 rounded"></div>
        <div className="h-4 w-5/6 bg-gray-500/30 rounded"></div>
        <div className="h-32 w-full border border-gray-500/30 rounded"></div>
        <div className="h-4 w-1/2 bg-gray-500/30 rounded"></div>
      </div>

      <div className="absolute inset-0 z-10 flex flex-col items-center justify-center p-6 text-center bg-gradient-to-t from-eidos-bg via-eidos-bg/80 to-transparent">
        <Lock className="w-12 h-12 text-eidos-cyan mb-4 animate-pulse drop-shadow-[0_0_8px_rgba(102,252,241,0.8)]" />
        <h3 className="text-xl font-bold font-mono text-white mb-2">{title}</h3>
        <p className="text-sm text-eidos-text mb-6">Получите полный доступ к глубокой аналитике, стратегиям роста и безлимитным ИИ-генерациям.</p>

        <button
          onClick={() => {
            if (window.Telegram?.WebApp?.HapticFeedback) {
              window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
            }
            onUnlock();
          }}
          className="eidos-btn w-full max-w-[200px]"
        >
          Оформить PRO
        </button>
      </div>
    </motion.div>
  );
};
