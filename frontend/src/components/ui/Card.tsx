import { ReactNode } from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export default function Card({ 
  children, 
  className, 
  hover = false,
  padding = 'md' 
}: CardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <div
      className={clsx(
        'bg-white rounded-2xl shadow-lg border border-gray-100 transition-shadow duration-300',
        hover && 'hover:shadow-xl',
        paddingStyles[padding],
        className
      )}
    >
      {children}
    </div>
  );
}
