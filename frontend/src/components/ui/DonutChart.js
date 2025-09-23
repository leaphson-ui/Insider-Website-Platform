import React from 'react';
import { cn } from '../../utils/cn';

const DonutChart = ({ 
 data = [],
 size = 128,
 strokeWidth = 8,
 className,
 ...props 
}) => {
 const radius = (size - strokeWidth) / 2;
 const circumference = 2 * Math.PI * radius;
 
 // Calculate total for percentages
 const total = data.reduce((sum, item) => sum + item.value, 0);
 
 let cumulativePercentage = 0;
 
 return (
  <div className={cn('flex items-center justify-center', className)} {...props}>
   <div className="relative" style={{ width: size, height: size }}>
    <svg 
     className="transform -rotate-90" 
     width={size} 
     height={size} 
     viewBox={`0 0 ${size} ${size}`}
    >
     {/* Background circle */}
     <circle
      cx={size / 2}
      cy={size / 2}
      r={radius}
      fill="none"
      stroke="var(--color-border-primary)"
      strokeWidth={strokeWidth}
      className="opacity-30"
     />
     
     {/* Data segments */}
     {data.map((item, index) => {
      const percentage = (item.value / total) * 100;
      const strokeDasharray = `${(percentage / 100) * circumference} ${circumference}`;
      const strokeDashoffset = -(cumulativePercentage / 100) * circumference;
      
      cumulativePercentage += percentage;
      
      return (
       <circle
        key={index}
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={item.color}
        strokeWidth={strokeWidth}
        strokeDasharray={strokeDasharray}
        strokeDashoffset={strokeDashoffset}
        className="transition-all duration-1000 ease-in-out"
        strokeLinecap="round"
       />
      );
     })}
    </svg>
    
    {/* Center content */}
    <div className="absolute inset-0 flex items-center justify-center">
     <div className="text-center">
      <div className="text-xl font-bold text-primary">
       {data[0]?.percentage || 0}%
      </div>
      <div className="text-xs text-secondary">
       {data[0]?.label || 'Primary'}
      </div>
     </div>
    </div>
   </div>
  </div>
 );
};

export default DonutChart;


