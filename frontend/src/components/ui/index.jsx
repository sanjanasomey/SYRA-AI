import React from 'react';

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  disabled = false, 
  loading = false,
  ...props 
}) {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-syra-primary text-white hover:bg-syra-primaryHover focus:ring-syra-primary/40 shadow-sm shadow-syra-primary/20',
    secondary: 'bg-white text-syra-text border border-syra-border hover:bg-syra-bg focus:ring-syra-primary/20',
    lavender: 'bg-syra-lavender text-white hover:bg-syra-lavenderHover focus:ring-syra-lavender/40 shadow-sm shadow-syra-lavender/20',
    ghost: 'text-syra-muted hover:text-syra-text hover:bg-syra-sidebar focus:ring-syra-primary/20'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs font-semibold gap-1.5',
    md: 'px-4 py-2 text-sm gap-2',
    lg: 'px-5 py-2.5 text-base gap-2.5'
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {children}
    </button>
  );
}

export function Card({ children, className = '', hoverable = false, ...props }) {
  return (
    <div
      className={`bg-syra-card border border-syra-border rounded-2xl p-5 shadow-sm transition-all duration-150 ${
        hoverable ? 'hover:shadow-md hover:border-syra-primary/40' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function Badge({ children, variant = 'default', size = 'sm' }) {
  const variants = {
    default: 'bg-syra-bg text-syra-muted border border-syra-border',
    pink: 'bg-syra-bg text-syra-primary border border-syra-border',
    lavender: 'bg-purple-50 text-syra-lavender border border-purple-100',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border border-amber-200'
  };

  const sizes = {
    xs: 'px-2 py-0.5 text-[10px]',
    sm: 'px-2.5 py-1 text-xs'
  };

  return (
    <span className={`inline-flex items-center font-medium rounded-full ${variants[variant]} ${sizes[size]}`}>
      {children}
    </span>
  );
}

export function LoadingSpinner({ size = 'md' }) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <div className="flex items-center justify-center p-4">
      <div className={`${sizes[size]} border-2 border-syra-border border-t-syra-primary rounded-full animate-spin`} />
    </div>
  );
}
