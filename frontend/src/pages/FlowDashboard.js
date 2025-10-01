import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Navigation from '../components/Navigation';
import Pagination from '../components/Pagination';

const FlowDashboard = () => {
  const location = useLocation();
  
  // Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Data state
  const [allTransactions, setAllTransactions] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  
  // Analytics state
  const [analytics, setAnalytics] = useState({
    flowSentiment: 'Neutral',
    buySellRatio: '50% / 50%',
    buyFlow: 0,
    sellFlow: 0
  });
  
  // Filter states
  const [filters, setFilters] = useState({
    timePeriod: '30d', // 7d, 30d, 90d, ytd, custom
    startDate: '',
    endDate: '',
    transactionValue: 'all', // all, 100k, 1m, 10m, 50m, 100m, custom
    minValue: '',
    maxValue: '',
    companyName: '',
    companyTicker: '',
    insiderName: '',
    transactionType: 'all'
  });

  // Filter panel state
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  // Calculate analytics from transaction data
  const calculateAnalytics = useCallback((transactionData) => {
    if (!transactionData || transactionData.length === 0) {
      setAnalytics({
        flowSentiment: 'Neutral',
        buySellRatio: '50% / 50%',
        buyFlow: 0,
        sellFlow: 0
      });
      return;
    }

    // Comprehensive buy transactions - include all bullish transaction codes
    const buyTransactions = transactionData.filter(t => 
      t.transaction_code === 'P' ||  // Purchase
      t.transaction_code === 'A' ||  // Award
      t.transaction_code === 'G' ||  // Grant
      t.transaction_code === 'I' ||  // Incentive
      t.transaction_code === 'M' ||  // Exercise
      t.transaction_code === 'Q' ||  // Qualified
      t.transaction_code === 'R' ||  // Return
      t.transaction_code === 'T' ||  // Transfer
      t.transaction_code === 'U' ||  // Underlying
      t.transaction_code === 'V' ||  // Vesting
      t.transaction_code === 'W' ||  // Warrant
      t.transaction_code === 'X' ||  // Exchange
      t.transaction_code === 'Y' ||  // Yield
      t.transaction_code === 'Z'     // Zero
    );

    const sellTransactions = transactionData.filter(t => 
      t.transaction_code === 'S' ||  // Sale
      t.transaction_code === 'D' ||  // Disposition
      t.transaction_code === 'E'     // Expiration
    );

    // Calculate total values
    const buyFlow = buyTransactions.reduce((sum, t) => sum + (t.calculated_transaction_value || 0), 0);
    const sellFlow = sellTransactions.reduce((sum, t) => sum + (t.calculated_transaction_value || 0), 0);

    // Debug logging
    console.log('🔍 Transaction Debug:', {
      totalTransactions: transactionData.length,
      buyTransactions: buyTransactions.length,
      sellTransactions: sellTransactions.length,
      buyFlow,
      sellFlow,
      sampleBuyCodes: buyTransactions.slice(0, 3).map(t => ({ code: t.transaction_code, value: t.calculated_transaction_value })),
      sampleSellCodes: sellTransactions.slice(0, 3).map(t => ({ code: t.transaction_code, value: t.calculated_transaction_value })),
      allCodes: [...new Set(transactionData.map(t => t.transaction_code))]
    });

    // Simple ratio calculation
    const totalFlow = buyFlow + sellFlow;
    const buyRatio = totalFlow > 0 ? Math.round((buyFlow / totalFlow) * 100) : 0;
    const sellRatio = totalFlow > 0 ? Math.round((sellFlow / totalFlow) * 100) : 0;
    
    // Simple sentiment based on which flow is higher
    let sentiment = 'Neutral';
    if (buyFlow > sellFlow) {
      sentiment = 'Bullish';
    } else if (sellFlow > buyFlow) {
      sentiment = 'Bearish';
    }

    setAnalytics({
      flowSentiment: sentiment,
      buySellRatio: `${buyRatio}% / ${sellRatio}%`,
      buyFlow: buyFlow,
      sellFlow: sellFlow
    });
  }, []);

  // Search-first approach: Only load data when user searches
  const fetchAllTransactions = useCallback(async () => {
    try {
      setLoading(true);
      
      // If no search term, don't load any data
      if (!searchTerm || !searchTerm.trim()) {
        console.log('🔍 No search term - showing empty state');
        setAllTransactions([]);
        setTotalItems(0);
        return;
      }
      
      const trimmedTerm = searchTerm.trim();
      console.log('🔍 Search triggered:', trimmedTerm);
      
      let query = supabase
        .from('insider_transactions')
        .select('*', { count: 'exact' });
      
      // Use targeted queries for major companies
      if (trimmedTerm.toUpperCase() === 'AAPL' || trimmedTerm.toLowerCase() === 'apple') {
        query = query.eq('company_ticker', 'AAPL');
        console.log('🍎 Searching for Apple transactions...');
      } else if (trimmedTerm.toUpperCase() === 'MSFT' || trimmedTerm.toLowerCase() === 'microsoft') {
        query = query.eq('company_ticker', 'MSFT');
        console.log('🏢 Searching for Microsoft transactions...');
      } else if (trimmedTerm.toUpperCase() === 'TSLA' || trimmedTerm.toLowerCase() === 'tesla') {
        query = query.eq('company_ticker', 'TSLA');
        console.log('🚗 Searching for Tesla transactions...');
      } else if (trimmedTerm.toUpperCase() === 'AMZN' || trimmedTerm.toLowerCase() === 'amazon') {
        query = query.eq('company_ticker', 'AMZN');
        console.log('📦 Searching for Amazon transactions...');
      } else if (trimmedTerm.toUpperCase() === 'GOOGL' || trimmedTerm.toLowerCase() === 'google') {
        query = query.eq('company_ticker', 'GOOGL');
        console.log('🔍 Searching for Google transactions...');
      } else if (trimmedTerm.toUpperCase() === 'META' || trimmedTerm.toLowerCase() === 'meta') {
        query = query.eq('company_ticker', 'META');
        console.log('📘 Searching for Meta transactions...');
      } else {
        // For other searches, use company name or insider name search
        query = query.or(`company_name.ilike.%${trimmedTerm}%,insider_name.ilike.%${trimmedTerm}%`);
        console.log(`🔍 Searching for "${trimmedTerm}" in company names and insider names...`);
      }
      
      // Order by most recent first
      query = query.order('transaction_date', { ascending: false });
      
      // Fetch data
      const { data, error, count } = await query;
      
      if (error) {
        console.error('❌ Supabase error:', error);
        setAllTransactions([]);
        setTotalItems(0);
        return;
      }
      
      console.log(`✅ Found ${data?.length || 0} transactions (Total: ${count})`);
      
      if (data && data.length > 0) {
        setAllTransactions(data);
        setTotalItems(count || data.length);
        calculateAnalytics(data);
      } else {
        setAllTransactions([]);
        setTotalItems(0);
        setAnalytics({
          flowSentiment: 'Neutral',
          buySellRatio: '50% / 50%',
          buyFlow: 0,
          sellFlow: 0
        });
      }
      
    } catch (error) {
      console.error('❌ Fetch error:', error);
      setAllTransactions([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, calculateAnalytics]);

  // Process transactions with filters and pagination
  const processTransactions = useCallback(() => {
    let filtered = [...allTransactions];

    // Apply filters
    if (filters.startDate) {
      filtered = filtered.filter(t => new Date(t.transaction_date) >= new Date(filters.startDate));
    }
    if (filters.endDate) {
      filtered = filtered.filter(t => new Date(t.transaction_date) <= new Date(filters.endDate));
    }
    if (filters.companyName) {
      filtered = filtered.filter(t => 
        t.company_name.toLowerCase().includes(filters.companyName.toLowerCase())
      );
    }
    if (filters.companyTicker) {
      filtered = filtered.filter(t => 
        t.company_ticker.toLowerCase().includes(filters.companyTicker.toLowerCase())
      );
    }
    if (filters.insiderName) {
      filtered = filtered.filter(t => 
        t.insider_name.toLowerCase().includes(filters.insiderName.toLowerCase())
      );
    }
    
    // Apply time period filter
    if (filters.timePeriod && filters.timePeriod !== 'custom') {
      const now = new Date();
      let cutoffDate;
      
      if (filters.timePeriod === '7d') {
        cutoffDate = new Date(now.setDate(now.getDate() - 7));
      } else if (filters.timePeriod === '30d') {
        cutoffDate = new Date(now.setDate(now.getDate() - 30));
      } else if (filters.timePeriod === '90d') {
        cutoffDate = new Date(now.setDate(now.getDate() - 90));
      } else if (filters.timePeriod === 'ytd') {
        cutoffDate = new Date(now.getFullYear(), 0, 1); // Jan 1 of current year
      }
      
      if (cutoffDate) {
        filtered = filtered.filter(t => new Date(t.transaction_date) >= cutoffDate);
      }
    }

    // Apply transaction value filter
    if (filters.transactionValue && filters.transactionValue !== 'all') {
      if (filters.transactionValue === 'custom') {
        if (filters.minValue) {
          filtered = filtered.filter(t => (t.calculated_transaction_value || 0) >= parseFloat(filters.minValue));
        }
        if (filters.maxValue) {
          filtered = filtered.filter(t => (t.calculated_transaction_value || 0) <= parseFloat(filters.maxValue));
        }
      } else {
        const thresholds = {
          '100k': 100000,
          '1m': 1000000,
          '10m': 10000000,
          '50m': 50000000,
          '100m': 100000000
        };
        const threshold = thresholds[filters.transactionValue];
        if (threshold) {
          filtered = filtered.filter(t => (t.calculated_transaction_value || 0) >= threshold);
        }
      }
    }
    
    // Apply transaction type filter
    if (filters.transactionType && filters.transactionType !== 'all') {
      filtered = filtered.filter(t => t.transaction_code === filters.transactionType);
    }

    // Calculate pagination
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginated = filtered.slice(startIndex, endIndex);

    setTransactions(paginated);
    
    // Recalculate analytics with filtered data
    calculateAnalytics(filtered);
  }, [allTransactions, filters, currentPage, itemsPerPage, calculateAnalytics]);

  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      timePeriod: '30d',
      startDate: '',
      endDate: '',
      transactionValue: 'all',
      minValue: '',
      maxValue: '',
      companyName: '',
      companyTicker: '',
      insiderName: '',
      transactionType: 'all'
    });
    setCurrentPage(1);
  };

  // Handle page changes
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Handle items per page changes
  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1);
  };

  // Smooth scroll to results when search is triggered
  const scrollToResults = () => {
    setTimeout(() => {
      const resultsSection = document.getElementById('results-section');
      if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  // Handle search with smooth scroll
  const handleSearch = useCallback((term) => {
    setSearchTerm(term);
    fetchAllTransactions();
    scrollToResults();
  }, [fetchAllTransactions]);

  // Handle URL search parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const searchParam = urlParams.get('search');
    if (searchParam) {
      setSearchTerm(searchParam);
      handleSearch(searchParam);
    }
  }, [location.search, handleSearch]);

  // Effects
  useEffect(() => {
    fetchAllTransactions();
  }, [fetchAllTransactions]);

  useEffect(() => {
    processTransactions();
  }, [processTransactions]);

  // Format functions
  const formatSignatureDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const formatCurrency = (value) => {
    if (!value || value === 0) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatShares = (shares) => {
    if (!shares) return 'N/A';
    return new Intl.NumberFormat('en-US').format(shares);
  };

  // Color logic based on transaction type
  const getTransactionColor = (transaction_code) => {
    // Green for purchases/acquisitions (bullish)
    if (['P', 'A', 'G', 'I', 'M'].includes(transaction_code)) {
      return 'text-green-400';
    }
    
    // Red for sales/dispositions (bearish)
    if (['S', 'D', 'F', 'C'].includes(transaction_code)) {
      return 'text-red-400';
    }
    
    // Yellow for neutral/other
    return 'text-yellow-400';
  };

  return (
    <div className="min-h-screen bg-primary">
      <Navigation />
      
      <div className="container py-8">
        <div className="space-y-6">
            {/* Search Bar with Filter Button */}
            <div className="mb-6 relative">
              <div className="search-container">
                <div className="search-input-wrapper">
                  <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <input 
                    type="text" 
                    placeholder="Search for insider trades, executives, or companies..." 
                    className="search-input"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSearch(searchTerm);
                      }
                    }}
                  />
                  <div className="flex items-center gap-2 mr-4">
                    {searchTerm && (
                      <button 
                        onClick={() => {
                          setSearchTerm('');
                          setAllTransactions([]);
                          setTotalItems(0);
                        }}
                        className="search-clear-btn"
                        aria-label="Clear search"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M18 6L6 18M6 6L18 18"/>
                        </svg>
                      </button>
                    )}
                    <button 
                      onClick={() => setIsFilterOpen(!isFilterOpen)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors ${
                        isFilterOpen ? 'bg-accent-blue text-white' : 'bg-gray-700 text-secondary hover:bg-gray-600'
                      }`}
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 6h18M7 12h10M10 18h4"/>
                      </svg>
                      <span className="text-xs font-medium">Filters</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Filter Dropdown Box */}
              {isFilterOpen && (
                <div className="absolute top-full right-0 mt-2 w-80 bg-gray-700 rounded-lg shadow-xl p-4 z-50">
                  {/* Time Range Section */}
                  <div className="mb-4">
                    <label className="text-xs font-medium text-secondary uppercase block mb-2">Time Range</label>
                    <div className="flex gap-2">
                      <select
                        value={filters.timePeriod === 'custom' ? '30d' : filters.timePeriod}
                        onChange={(e) => handleFilterChange('timePeriod', e.target.value)}
                        className="pagination-select flex-1"
                        disabled={filters.timePeriod === 'custom'}
                      >
                        <option value="7d">Last 7 days</option>
                        <option value="30d">Last 30 days</option>
                        <option value="90d">Last 90 days</option>
                        <option value="ytd">Year to date</option>
                      </select>
                      <button
                        onClick={() => handleFilterChange('timePeriod', filters.timePeriod === 'custom' ? '30d' : 'custom')}
                        className="px-3 py-1 rounded text-xs font-medium bg-yellow-500 text-black hover:bg-yellow-600"
                      >
                        Custom
                      </button>
                    </div>
                    {filters.timePeriod === 'custom' && (
                      <div className="mt-2 space-y-2">
                        <input
                          type="date"
                          value={filters.startDate}
                          onChange={(e) => handleFilterChange('startDate', e.target.value)}
                          className="input w-full"
                          placeholder="Start date"
                        />
                        <input
                          type="date"
                          value={filters.endDate}
                          onChange={(e) => handleFilterChange('endDate', e.target.value)}
                          className="input w-full"
                          placeholder="End date"
                        />
                      </div>
                    )}
                  </div>

                  {/* Transaction Value Section */}
                  <div className="mb-4">
                    <label className="text-xs font-medium text-secondary uppercase block mb-2">Transaction Value</label>
                    <div className="flex gap-2">
                      <select
                        value={filters.transactionValue === 'custom' ? 'all' : filters.transactionValue}
                        onChange={(e) => handleFilterChange('transactionValue', e.target.value)}
                        className="pagination-select flex-1"
                        disabled={filters.transactionValue === 'custom'}
                      >
                        <option value="all">All amounts</option>
                        <option value="100k">Over $100K</option>
                        <option value="1m">Over $1M</option>
                        <option value="10m">Over $10M</option>
                        <option value="50m">Over $50M</option>
                        <option value="100m">Over $100M</option>
                      </select>
                      <button
                        onClick={() => handleFilterChange('transactionValue', filters.transactionValue === 'custom' ? 'all' : 'custom')}
                        className="px-3 py-1 rounded text-xs font-medium bg-yellow-500 text-black hover:bg-yellow-600"
                      >
                        Custom
                      </button>
                    </div>
                    {filters.transactionValue === 'custom' && (
                      <div className="mt-2 space-y-2">
                        <input
                          type="number"
                          value={filters.minValue}
                          onChange={(e) => handleFilterChange('minValue', e.target.value)}
                          className="input w-full"
                          placeholder="Min value ($)"
                        />
                        <input
                          type="number"
                          value={filters.maxValue}
                          onChange={(e) => handleFilterChange('maxValue', e.target.value)}
                          className="input w-full"
                          placeholder="Max value ($)"
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Pagination Controls */}
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <label className="text-sm font-medium text-secondary">
                    Records per page:
                  </label>
                  <select 
                    value={itemsPerPage} 
                    onChange={(e) => handleItemsPerPageChange(parseInt(e.target.value))}
                    className="pagination-select"
                    style={{ width: '100px' }}
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                    <option value={500}>500</option>
                  </select>
                </div>
              </div>

              <div className="pagination-controls">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                  itemsPerPage={itemsPerPage}
                  totalItems={totalItems}
                  loading={loading}
                />
              </div>
            </div>

            {/* Analytics Cards */}
            <div className="analytics-grid mb-6">
              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Flow Sentiment</span>
                </div>
                <div className={`analytics-value ${analytics.flowSentiment === 'Bullish' ? 'text-green-400' : analytics.flowSentiment === 'Bearish' ? 'text-red-400' : 'text-gray-400'}`}>
                  {analytics.flowSentiment}
                </div>
                <div className="analytics-progress">
                  <div 
                    className={`analytics-progress-bar ${analytics.flowSentiment === 'Bullish' ? 'bg-green-400' : analytics.flowSentiment === 'Bearish' ? 'bg-red-400' : 'bg-gray-400'}`}
                    style={{ 
                      width: analytics.flowSentiment === 'Bullish' ? '75%' : analytics.flowSentiment === 'Bearish' ? '25%' : '50%' 
                    }}
                  ></div>
                </div>
              </div>

              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Buy vs Sell Ratio</span>
                </div>
                <div className="analytics-value text-white">
                  {analytics.buySellRatio}
                </div>
                <div className="analytics-progress">
                  <div 
                    className="analytics-progress-bar bg-green-400"
                    style={{ 
                      width: analytics.buySellRatio.split(' / ')[0] || '50%'
                    }}
                  ></div>
                  <div 
                    className="analytics-progress-bar bg-red-400"
                    style={{ 
                      width: analytics.buySellRatio.split(' / ')[1] || '50%',
                      marginLeft: '2px'
                    }}
                  ></div>
                </div>
              </div>

              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Buy Flow</span>
                </div>
                <div className="analytics-value text-green-400">
                  ${analytics.buyFlow > 1000000 
                    ? (analytics.buyFlow / 1000000).toFixed(1) + 'M' 
                    : analytics.buyFlow > 1000 
                    ? (analytics.buyFlow / 1000).toFixed(1) + 'K' 
                    : analytics.buyFlow.toLocaleString()}
                </div>
              </div>

              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Sell Flow</span>
                </div>
                <div className="analytics-value text-red-400">
                  ${analytics.sellFlow > 1000000 
                    ? (analytics.sellFlow / 1000000).toFixed(1) + 'M' 
                    : analytics.sellFlow > 1000 
                    ? (analytics.sellFlow / 1000).toFixed(1) + 'K' 
                    : analytics.sellFlow.toLocaleString()}
                </div>
              </div>
            </div>

            {/* New Analytics Row - 4 cards */}
            <div className="analytics-grid mb-6">
              {/* 1. Average Transaction Size */}
              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Avg Transaction Size</span>
                </div>
                <div className="analytics-value text-white">
                  $2.4M
                </div>
              </div>

              {/* 2. Largest Transaction */}
              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Largest Transaction</span>
                </div>
                <div className="analytics-value text-yellow-400">
                  $125M
                </div>
                <div className="text-xs text-secondary mt-1">TSLA - Elon Musk</div>
              </div>

              {/* 7. Transaction Type Breakdown */}
              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Transaction Types</span>
                </div>
                <div className="flex gap-2 mt-2">
                  <div className="flex-1">
                    <div className="text-xs text-secondary">Purchase</div>
                    <div className="analytics-value text-green-400">45%</div>
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-secondary">Sale</div>
                    <div className="analytics-value text-red-400">35%</div>
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-secondary">Other</div>
                    <div className="analytics-value text-gray-400">20%</div>
                  </div>
                </div>
              </div>

              {/* 8. Insider Role Distribution */}
              <div className="analytics-card">
                <div className="analytics-header">
                  <span className="analytics-label">Top Insider Roles</span>
                </div>
                <div className="space-y-1 mt-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-secondary">CEO</span>
                    <span className="text-white font-semibold">32%</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-secondary">Director</span>
                    <span className="text-white font-semibold">28%</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-secondary">CFO</span>
                    <span className="text-white font-semibold">18%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Enhanced Trades Table */}
            <div className="trades-table">
              <div className="table-header">
                <div className="header-cell">
                  TICKER
                </div>
                <div className="header-cell">
                  <div>TRANSACTION</div>
                  <div>VALUE</div>
                </div>
                <div className="header-cell">
                  INSIDER NAME
                </div>
                <div className="header-cell">
                  INSIDER TITLE
                </div>
                <div className="header-cell">
                  COMPANY NAME
                </div>
                <div className="header-cell">
                  TRANSACTION CODE
                </div>
                <div className="header-cell">
                  SHARES
                </div>
                <div className="header-cell">
                  PRICE PER SHARE
                </div>
                <div className="header-cell">
                  SHARES OWNED AFTER
                </div>
                <div className="header-cell">
                  TRANSACTION DATE
                </div>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                  <p className="mt-2 text-white">Loading transactions...</p>
                </div>
              ) : transactions.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-white">No transactions found. Try adjusting your filters or search terms.</p>
                </div>
              ) : (
                transactions.map((transaction, index) => (
                  <div key={`${transaction.id}-${index}`} className="table-row">
                    <div className="cell">
                      <span className={`font-mono text-sm ${getTransactionColor(transaction.transaction_code)}`}>
                        {transaction.company_ticker}
                      </span>
                    </div>
                    <div className="cell">
                      <div className={`font-medium ${getTransactionColor(transaction.transaction_code)}`}>
                        {formatCurrency(transaction.calculated_transaction_value)}
                      </div>
                    </div>
                    <div className="cell">
                      <div className="font-medium text-white">{transaction.insider_name}</div>
                    </div>
                    <div className="cell">
                      <div className="text-sm text-gray-300">{transaction.insider_title || 'N/A'}</div>
                    </div>
                    <div className="cell">
                      <div className={`font-medium ${getTransactionColor(transaction.transaction_code)}`}>
                        {transaction.company_name}
                      </div>
                    </div>
                    <div className="cell">
                      <span className="font-mono text-sm text-white">
                        {transaction.transaction_code}
                      </span>
                    </div>
                    <div className="cell">
                      <div className={`text-sm ${getTransactionColor(transaction.transaction_code)}`}>
                        {formatShares(transaction.transaction_shares)}
                      </div>
                    </div>
                    <div className="cell">
                      <div className="text-sm text-white">{formatCurrency(transaction.transaction_price_per_share)}</div>
                    </div>
                    <div className="cell">
                      <div className={`text-sm ${getTransactionColor(transaction.transaction_code)}`}>
                        {formatShares(transaction.shares_owned_following_transaction)}
                      </div>
                    </div>
                    <div className="cell">
                      <div className="text-sm text-white">{formatSignatureDate(transaction.transaction_date)}</div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Pagination */}
            <div className="pagination-container">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                itemsPerPage={itemsPerPage}
                totalItems={totalItems}
                loading={loading}
              />
            </div>
        </div>
      </div>
    </div>
  );
};

export default FlowDashboard;
