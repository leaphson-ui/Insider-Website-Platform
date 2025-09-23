import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const api = axios.create({
 baseURL: API_BASE_URL,
 timeout: 10000, // 10 second timeout
 headers: {
  'Content-Type': 'application/json',
 },
});

// Request interceptor for logging and error handling
api.interceptors.request.use(
 (config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
 },
 (error) => {
  console.error('API Request Error:', error);
  return Promise.reject(error);
 }
);

// Response interceptor for centralized error handling
api.interceptors.response.use(
 (response) => {
  return response;
 },
 (error) => {
  console.error('API Response Error:', error);
  
  // Handle different error types with user-friendly messages
  if (error.response) {
   // Server responded with error status
   const message = error.response.data?.detail || error.response.data?.message || 'Server error';
   throw new Error(`${error.response.status}: ${message}`);
  } else if (error.request) {
   // Request was made but no response received
   throw new Error('Network error: Unable to connect to server');
  } else {
   // Something else happened
   throw new Error(`Request error: ${error.message}`);
  }
 }
);

// Utility function for consistent error handling
// const handleApiError = (error, operation) => {
//   console.error(`Error ${operation}:`, error);
//   throw error;
// };

// API functions - simplified with centralized error handling
export const getLeaderboard = async (limit = 50, minTrades = 5) => {
 const response = await api.get('/leaderboard', {
  params: { limit, min_trades: minTrades }
 });
 return response.data;
};

export const getTrader = async (traderId) => {
 const response = await api.get(`/traders/${traderId}`);
 return response.data;
};

export const getTraderTrades = async (traderId, page = 1, limit = 50) => {
 const response = await api.get(`/traders/${traderId}/trades`, {
  params: { page, limit }
 });
 return response.data;
};

export const getTraderTradesCount = async (traderId) => {
 const response = await api.get(`/traders/${traderId}/trades/count`);
 return response.data;
};

export const searchSuggestions = async (query, limit = 10) => {
 const response = await api.get(`/search?q=${encodeURIComponent(query)}&limit=${limit}`);
 return response.data;
};

export const getRecentTrades = async (limit = 100, ticker = null, days = 30) => {
 const params = { limit, days };
 if (ticker) params.ticker = ticker;
 
 const response = await api.get('/trades/recent', { params });
 return response.data;
};

export const getCompanyTrades = async (ticker, limit = 100) => {
 const response = await api.get(`/companies/${ticker}/insider-trades`, {
  params: { limit }
 });
 return response.data;
};

export const getPlatformStats = async () => {
 const response = await api.get('/stats/summary');
 return response.data;
};

export const getNetworkAnalysis = async () => {
 const response = await api.get('/analytics/networks');
 return response.data;
};

export const getTimingAnalysis = async () => {
 const response = await api.get('/analytics/timing');
 return response.data;
};

export const getPortfolioLeaderboard = async (limit = 50, minHoldingsValue = 100000) => {
 const response = await api.get('/portfolio/leaderboard', {
  params: { limit, min_holdings_value: minHoldingsValue }
 });
 return response.data;
};

export const getTraderHoldings = async (traderId) => {
 const response = await api.get(`/traders/${traderId}/holdings`);
 return response.data;
};

export const getSectorAnalytics = async () => {
 const response = await api.get('/analytics/sectors');
 return response.data;
};

// Utility functions for error handling
export const isNetworkError = (error) => error.message.includes('Network error');
export const isServerError = (error) => error.message.includes(':');
export const getErrorMessage = (error) => {
 if (isNetworkError(error)) {
  return 'Unable to connect to server. Please check your internet connection.';
 }
 if (isServerError(error)) {
  return 'Server error. Please try again later.';
 }
 return error.message || 'An unexpected error occurred.';
};

// API groups for better organization
export const dashboardAPI = {
 getStats: getPlatformStats,
 getSectorAnalytics,
 getLeaderboard,
 getRecentTrades,
};

export const traderAPI = {
 getTrader,
 getTraderTrades,
 getTraderTradesCount,
 getTraderHoldings,
};

export const searchAPI = {
 getSuggestions: searchSuggestions,
};

export const companyAPI = {
 getCompanyTrades,
};

export const analyticsAPI = {
 getNetworkAnalysis,
 getTimingAnalysis,
 getSectorAnalytics,
};

export const portfolioAPI = {
 getPortfolioLeaderboard,
};

export default api;
