// Utility functions for formatting data

export const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'N/A';
  
  const num = parseFloat(value);
  if (isNaN(num)) return 'N/A';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
};

export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return 'N/A';
  
  const num = parseFloat(value);
  if (isNaN(num)) return 'N/A';
  
  return `${num.toFixed(decimals)}%`;
};

export const formatNumber = (value, decimals = 0) => {
  if (value === null || value === undefined) return 'N/A';
  
  const num = parseFloat(value);
  if (isNaN(num)) return 'N/A';
  
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
};

export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (error) {
    return 'N/A';
  }
};

export const getReturnColor = (value) => {
  if (value === null || value === undefined || isNaN(parseFloat(value))) {
    return 'text-gray-500';
  }
  
  const num = parseFloat(value);
  if (num > 0) return 'text-green-600';
  if (num < 0) return 'text-red-600';
  return 'text-gray-500';
};

export const getPerformanceScoreColor = (score) => {
  if (score === null || score === undefined || isNaN(parseFloat(score))) {
    return 'text-gray-500';
  }
  
  const num = parseFloat(score);
  if (num >= 20) return 'text-green-600 font-semibold';
  if (num >= 10) return 'text-green-500';
  if (num >= 0) return 'text-yellow-500';
  return 'text-red-500';
};
