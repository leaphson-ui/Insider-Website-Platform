/**
 * Universal FilterBar Component
 * Standardized filter styling across all pages
 */
import React from 'react';
import { cn } from '../../utils/cn';
import { Card } from './index';

const FilterBar = ({ 
 filters = [],
 className,
 ...props 
}) => {
 return (
  <Card className={cn("mb-6", className)} {...props}>
   <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
    {filters.map((filter, index) => (
     <div key={index}>
      <label className="block text-sm font-medium text-secondary mb-1">
       {filter.label}
      </label>
      {filter.type === 'select' ? (
       <select
        value={filter.value}
        onChange={filter.onChange}
        className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary text-sm focus:outline-none focus:ring-2 focus:ring-blue focus:border-blue"
       >
        {filter.options.map((option) => (
         <option key={option.value} value={option.value}>
          {option.label}
         </option>
        ))}
       </select>
      ) : filter.type === 'input' ? (
       <input
        type={filter.inputType || 'text'}
        value={filter.value}
        onChange={filter.onChange}
        placeholder={filter.placeholder}
        className="w-full px-3 py-2 bg-tertiary border border-primary rounded-lg text-primary text-sm focus:outline-none focus:ring-2 focus:ring-blue focus:border-blue"
       />
      ) : (
       <div className="text-tertiary text-sm">
        {filter.customComponent || 'Unsupported filter type'}
       </div>
      )}
     </div>
    ))}
   </div>
  </Card>
 );
};

export default FilterBar;


