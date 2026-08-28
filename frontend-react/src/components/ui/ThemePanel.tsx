import React from 'react';
import { useTheme } from '../../context/ThemeContext';
import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';
import Paper from '@mui/material/Paper';
import { cn } from '../../utils/cn';

interface ThemePanelProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export function ThemePanel({ children, className, delay = 0, ...props }: ThemePanelProps) {
  const { theme } = useTheme();

  const animationProps = {
    initial: { opacity: 0, y: 15 },
    animate: { opacity: 1, y: 0 },
    transition: { type: "spring" as const, stiffness: 350, damping: 25, delay },
    ...props
  };

  if (theme === 'glass-ios') {
    return (
      <motion.div 
        className={cn("glass-panel rounded-3xl p-6", className)} 
        {...animationProps}
      >
        {children}
      </motion.div>
    );
  }

  // Material Theme
  return (
    <motion.div {...animationProps}>
      <Paper 
        elevation={3} 
        className={cn("rounded-3xl p-6 bg-[var(--bg-card)]", className)} 
      >
        {children}
      </Paper>
    </motion.div>
  );
}
