/**
 * Universal ModuleCard Component
 * Standardized module wrapper across all pages
 */
import React from 'react';
import { cn } from '../../utils/cn';

const ModuleCard = ({ 
 title,
 subtitle,
 headerAction,
 children,
 className,
 ...props 
}) => {
 return (
  <div className={cn("card", className)} {...props}>
   {(title || headerAction) && (
    <div className="card-header">
     <div className="flex items-center justify-between">
      <div>
       {title && (
        <h3 className="text-lg font-semibold text-primary">
         {title}
        </h3>
       )}
       {subtitle && (
        <p className="text-sm text-secondary mt-1">
         {subtitle}
        </p>
       )}
      </div>
      {headerAction && (
       <div className="flex-shrink-0">
        {headerAction}
       </div>
      )}
     </div>
    </div>
   )}
   <div className="card-body">
    {children}
   </div>
  </div>
 );
};

export default ModuleCard;


