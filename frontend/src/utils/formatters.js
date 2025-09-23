// Simple formatting utilities

export const formatCurrency = (value) => {
  if (!value && value !== 0) return 'N/A';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export const formatNumber = (value) => {
  if (!value && value !== 0) return 'N/A';
  return new Intl.NumberFormat('en-US').format(value);
};

export const formatPercentage = (value, decimals = 2) => {
  if (!value && value !== 0) return 'N/A';
  return `${value.toFixed(decimals)}%`;
};

export const formatDate = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString();
};

export const formatDateTime = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleString();
};

// Color helpers for returns and performance
export const getReturnColor = (value) => {
  if (!value && value !== 0) return 'text-secondary';
  return value > 0 ? 'text-green' : value < 0 ? 'text-red' : 'text-secondary';
};

export const getPerformanceScoreColor = (value) => {
  if (!value && value !== 0) return 'text-secondary';
  if (value >= 8) return 'text-green';
  if (value >= 6) return 'text-blue';
  if (value >= 4) return 'text-yellow';
  return 'text-red';
};