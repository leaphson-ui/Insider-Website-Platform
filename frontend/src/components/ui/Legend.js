import React from 'react';
import { cn } from '../../utils/cn';

const Legend = ({ 
 items = [],
 className,
 compact = false,
 ...props 
}) => {
 return (
  <div className={cn('space-y-2', className)} {...props}>
   {items.map((item, index) => (
    <div key={index} className="flex items-center justify-between py-1">
     <div className="flex items-center min-w-0 flex-1">
      <div 
       className={cn(
        'rounded-full mr-3 flex-shrink-0',
        compact ? 'w-2.5 h-2.5' : 'w-3 h-3'
       )}
       style={{ backgroundColor: item.color }}
      />
      <span className={cn(
       'text-secondary truncate',
       compact ? 'text-xs' : 'text-sm'
      )}>
       {item.label}
      </span>
     </div>
     <span className={cn(
      'font-semibold ml-3 flex-shrink-0',
      compact ? 'text-xs' : 'text-sm',
      item.valueColor || 'text-primary'
     )}>
      {typeof item.value === 'number' ? item.value.toLocaleString() : item.value}
     </span>
    </div>
   ))}
  </div>
 );
};

export default Legend;
