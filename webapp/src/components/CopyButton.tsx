import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { motion } from 'framer-motion';

export const CopyButton = ({ text }: { text: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);

      // Haptic feedback
      if (window.Telegram?.WebApp?.HapticFeedback) {
        window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
      }
    } catch (err) {
      console.error('Failed to copy', err);
    }
  };

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={handleCopy}
      className="absolute top-2 right-2 p-2 bg-eidos-surface/80 rounded-sm border border-eidos-gray/30 hover:border-eidos-cyan transition-colors"
    >
      {copied ? <Check className="w-4 h-4 text-eidos-cyan" /> : <Copy className="w-4 h-4 text-eidos-text hover:text-white" />}
    </motion.button>
  );
};
