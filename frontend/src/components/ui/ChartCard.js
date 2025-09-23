import React from 'react';
import { cn } from '../../utils/cn';

const ChartCard = ({ 
 title, 
 subtitle,
 icon: Icon,
 iconColor = 'text-orange-400',
 children,
 className,
 ...props 
}) => {
 return (
  <div
   className={cn(
    'card [1.02] transition-all duration-200',
    className
   )}
   {...props}
  >
   <div className="p-6">
    <div className="flex items-center justify-between mb-4">
     <div>
      <h2 className="text-lg font-semibold text-primary">{title}</h2>
      {subtitle && (
       <p className="text-sm text-secondary mt-1">{subtitle}</p>
      )}
     </div>
     {Icon && <Icon className={cn('h-5 w-5', iconColor)} />}
    </div>
    {children}
   </div>
  </div>
 );
};

export default ChartCard;


