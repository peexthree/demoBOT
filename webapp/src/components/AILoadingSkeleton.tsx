import React from 'react';
import { motion } from 'framer-motion';

export const AILoadingSkeleton = () => {
  return (
    <div className="flex flex-col gap-4 w-full animate-pulse">
      <div className="h-4 w-1/3 bg-eidos-gray/20 rounded"></div>

      <div className="relative overflow-hidden w-full h-32 bg-eidos-surface border border-eidos-gray/20">
        <div className="absolute inset-0 bg-cyber-gradient animate-pulse opacity-50"></div>

        {/* Анимация сканирования/глитча */}
        <div className="absolute inset-0 bg-eidos-cyan-dim h-full w-full animate-scanline"
             style={{ backgroundImage: 'linear-gradient(transparent 50%, rgba(102, 252, 241, 0.1) 50%)', backgroundSize: '100% 4px' }}>
        </div>

        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-eidos-cyan animate-bounce"></div>
          <div className="w-2 h-2 rounded-full bg-eidos-cyan animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-2 h-2 rounded-full bg-eidos-cyan animate-bounce" style={{ animationDelay: '0.4s' }}></div>
        </div>
      </div>

      <div className="flex justify-between mt-2">
        <div className="h-4 w-1/4 bg-eidos-gray/20 rounded"></div>
        <div className="h-4 w-1/4 bg-eidos-gray/20 rounded"></div>
      </div>
    </div>
  );
};
