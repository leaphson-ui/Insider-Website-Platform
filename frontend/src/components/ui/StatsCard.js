import React from 'react';

const StatsCard = ({ title, value, subtitle, trend, trendValue, className = '' }) => {
  const getTrendColor = (trend) => {
    if (trend === 'up') return 'text-green';
    if (trend === 'down') return 'text-red';
    return 'text-secondary';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'up') return '↗';
    if (trend === 'down') return '↘';
    return '';
  };

  return (
    <div className={`stats-card ${className}`}>
      <div className="text-secondary text-sm font-medium mb-2">{title}</div>
      <div className="text-primary text-3xl font-bold mb-2">{value}</div>
      {subtitle && <div className="text-muted text-xs mb-2">{subtitle}</div>}
      {trend && trendValue && (
        <div className={`text-xs font-semibold ${getTrendColor(trend)}`}>
          {getTrendIcon(trend)} {trendValue}
        </div>
      )}
    </div>
  );
};

export default StatsCard;