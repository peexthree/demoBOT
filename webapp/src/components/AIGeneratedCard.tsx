import React from 'react';
import { motion } from 'framer-motion';
import { CopyButton } from './CopyButton';

interface AICardProps {
  title: string;
  content: any; // JSON object or string
  delay?: number;
}

export const AIGeneratedCard = ({ title, content, delay = 0 }: AICardProps) => {
  const isObject = typeof content === 'object' && content !== null;
  const contentString = isObject ? JSON.stringify(content, null, 2) : String(content);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay, duration: 0.4 }}
      className="eidos-card w-full mb-4 relative overflow-hidden group"
    >
      <div className="absolute top-0 left-0 w-1 h-full bg-eidos-cyan opacity-50 group-hover:opacity-100 transition-opacity"></div>

      <div className="flex justify-between items-center mb-3 pr-8">
        <h3 className="text-lg font-mono font-semibold text-eidos-cyan text-glow truncate">{title}</h3>
      </div>

      <div className="relative text-sm text-gray-300 font-sans leading-relaxed break-words bg-black/20 p-3 rounded border border-white/5">
        {isObject ? (
          <pre className="whitespace-pre-wrap overflow-x-auto text-xs text-eidos-text font-mono">
            {contentString}
          </pre>
        ) : (
          <p className="whitespace-pre-wrap">{content}</p>
        )}
      </div>

      <CopyButton text={contentString} />
    </motion.div>
  );
};
