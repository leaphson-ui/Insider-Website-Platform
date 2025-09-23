import React from 'react';
import { cn } from '../../utils/cn';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

const Select = React.forwardRef(({ 
 className,
 children,
 placeholder,
 ...props 
}, ref) => {
 return (
  <div className="relative">
   <select
    ref={ref}
    className={cn(
     'w-full px-4 py-2.5 pr-10 bg-card/30 backdrop-blur-sm border border-tertiary/50 rounded-lg text-primary text-sm font-medium',
     'focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50',
     ' transition-all duration-200',
     'appearance-none cursor-pointer',
     'bg-gradient-to-r from-card/20 to-card/30',
     className
    )}
    {...props}
   >
    {placeholder && (
     <option value="" disabled>
      {placeholder}
     </option>
    )}
    {children}
   </select>
   <ChevronDownIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary pointer-events-none" />
  </div>
 );
});
Select.displayName = 'Select';

const SelectOption = ({ children, value, ...props }) => {
 return (
  <option 
   value={value} 
   className="bg-card text-primary font-medium"
   {...props}
  >
   {children}
  </option>
 );
};

export { Select, SelectOption };
