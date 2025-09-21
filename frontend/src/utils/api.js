import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const getLeaderboard = async (limit = 50, minTrades = 5) => {
  try {
    const response = await api.get('/leaderboard', {
      params: { limit, min_trades: minTrades }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    throw error;
  }
};

export const getTrader = async (traderId) => {
  try {
    const response = await api.get(`/traders/${traderId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching trader:', error);
    throw error;
  }
};

export const getRecentTrades = async (limit = 100, ticker = null, days = 30) => {
  try {
    const params = { limit, days };
    if (ticker) params.ticker = ticker;
    
    const response = await api.get('/trades/recent', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching recent trades:', error);
    throw error;
  }
};

export const getCompanyTrades = async (ticker, limit = 100) => {
  try {
    const response = await api.get(`/companies/${ticker}/insider-trades`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching company trades:', error);
    throw error;
  }
};

export const getPlatformStats = async () => {
  try {
    const response = await api.get('/stats/summary');
    return response.data;
  } catch (error) {
    console.error('Error fetching platform stats:', error);
    throw error;
  }
};

export const getNetworkAnalysis = async () => {
  try {
    const response = await api.get('/analytics/networks');
    return response.data;
  } catch (error) {
    console.error('Error fetching network analysis:', error);
    throw error;
  }
};

export const getTimingAnalysis = async () => {
  try {
    const response = await api.get('/analytics/timing');
    return response.data;
  } catch (error) {
    console.error('Error fetching timing analysis:', error);
    throw error;
  }
};

export const getPortfolioLeaderboard = async (limit = 50, minHoldingsValue = 100000) => {
  try {
    const response = await api.get('/portfolio/leaderboard', {
      params: { limit, min_holdings_value: minHoldingsValue }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching portfolio leaderboard:', error);
    throw error;
  }
};

export const getTraderHoldings = async (traderId) => {
  try {
    const response = await api.get(`/traders/${traderId}/holdings`);
    return response.data;
  } catch (error) {
    console.error('Error fetching trader holdings:', error);
    throw error;
  }
};

export default api;
