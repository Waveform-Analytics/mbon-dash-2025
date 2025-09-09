import React from 'react';
import { motion } from 'framer-motion';

interface NarrativeSectionProps {
  title?: string;
  emoji?: string;
  children: React.ReactNode;
  className?: string;
  variant?: 'info' | 'insight' | 'tip' | 'warning';
  delay?: number;
}

const variantStyles = {
  info: 'bg-blue-50 border-l-4 border-blue-400 text-blue-800',
  insight: 'bg-green-50 border-l-4 border-green-400 text-green-800', 
  tip: 'bg-purple-50 border-l-4 border-purple-400 text-purple-800',
  warning: 'bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800'
};

const titleStyles = {
  info: 'text-blue-900',
  insight: 'text-green-900',
  tip: 'text-purple-900', 
  warning: 'text-yellow-900'
};

export default function NarrativeSection({
  title,
  emoji,
  children,
  className = '',
  variant = 'info',
  delay = 0.6
}: NarrativeSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      className={`mb-8 ${className}`}
    >
      <div className="space-y-4">
        {title ? (
          <div className={`${variantStyles[variant]} p-6 rounded-r-lg`}>
            {title && (
              <h3 className={`text-lg font-semibold ${titleStyles[variant]} mb-2`}>
                {emoji && `${emoji} `}{title}
              </h3>
            )}
            <div className="space-y-2">
              {children}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {children}
          </div>
        )}
      </div>
    </motion.div>
  );
}