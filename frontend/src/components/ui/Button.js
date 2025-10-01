import React from 'react';

const Button = ({ children, className = '', variant = 'primary', size = 'md', ...props }) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variantClasses = {
    primary: 'bg-yellow-500 hover:bg-yellow-600 text-black border border-yellow-500 hover:border-yellow-600',
    secondary: 'bg-transparent hover:bg-gray-800 text-white border border-gray-600 hover:border-gray-500',
    outline: 'bg-transparent hover:bg-gray-800 text-white border border-gray-600 hover:border-gray-500',
    ghost: 'bg-transparent hover:bg-gray-800 text-white',
    destructive: 'bg-red-500 hover:bg-red-600 text-white border border-red-500 hover:border-red-600'
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm rounded-md',
    md: 'px-4 py-2 text-sm rounded-md',
    lg: 'px-6 py-3 text-base rounded-lg',
    xl: 'px-8 py-4 text-lg rounded-lg'
  };
  
  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;
  
  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
};

export default Button;