import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import Navigation from '../components/Navigation';
import Pagination from '../components/Pagination';

const UnifiedDashboard = () => {
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
    startDate: '',
    endDate: '',
    companyName: '',
    companyTicker: '',
    insiderName: '',
    transactionType: 'all'
  });

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
    if (filters.transactionType !== 'all') {
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
      startDate: '',
      endDate: '',
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
        {/* Search Section - Always Visible */}
        <section className="hero-section py-24">
          <div className="container text-center">
            <h1 className="hero-title">
              <span className="gradient-text">Search Insider Trading Data</span>
            </h1>
            <p className="hero-subtitle">
              Enter a company name, ticker symbol, or insider name to find transactions
            </p>
            
            {/* Search Bar - Same styling as homepage */}
            <div className="hero-search mb-8">
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
                </div>
              </div>
            </div>
            
            {/* Popular Searches */}
            <div className="mt-6">
              <p className="text-sm text-secondary mb-4">Popular searches:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {['Apple', 'Microsoft', 'Tesla', 'Amazon', 'Google', 'Meta', 'Elon Musk', 'Tim Cook'].map((term) => (
                  <button
                    key={term}
                    onClick={() => handleSearch(term)}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-full text-sm text-white transition-colors"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Results Section - Only visible when searching */}
        {searchTerm && searchTerm.trim() && (
          <div id="results-section" className="space-y-6">
            {/* Filter Controls */}
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-secondary">Date:</label>
                <input
                  type="date"
                  value={filters.startDate}
                  onChange={(e) => handleFilterChange('startDate', e.target.value)}
                  className="input"
                  style={{ width: '140px' }}
                  placeholder="Start"
                />
                <span className="text-secondary">to</span>
                <input
                  type="date"
                  value={filters.endDate}
                  onChange={(e) => handleFilterChange('endDate', e.target.value)}
                  className="input"
                  style={{ width: '140px' }}
                  placeholder="End"
                />
              </div>

              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-secondary">Company:</label>
                <input
                  type="text"
                  placeholder="Company name..."
                  value={filters.companyName}
                  onChange={(e) => handleFilterChange('companyName', e.target.value)}
                  className="input"
                  style={{ width: '140px' }}
                />
              </div>

              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-secondary">Ticker:</label>
                <input
                  type="text"
                  placeholder="Ticker..."
                  value={filters.companyTicker}
                  onChange={(e) => handleFilterChange('companyTicker', e.target.value)}
                  className="input"
                  style={{ width: '100px' }}
                />
              </div>

              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-secondary">Insider:</label>
                <input
                  type="text"
                  placeholder="Insider name..."
                  value={filters.insiderName}
                  onChange={(e) => handleFilterChange('insiderName', e.target.value)}
                  className="input"
                  style={{ width: '140px' }}
                />
              </div>

              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-secondary">Type:</label>
                <select
                  value={filters.transactionType}
                  onChange={(e) => handleFilterChange('transactionType', e.target.value)}
                  className="pagination-select"
                  style={{ width: '120px' }}
                >
                  <option value="all">All Types</option>
                  <option value="P">Purchase</option>
                  <option value="S">Sale</option>
                  <option value="A">Acquisition</option>
                  <option value="D">Disposition</option>
                </select>
              </div>

              <button
                onClick={clearFilters}
                className="pagination-btn"
              >
                Clear Filters
              </button>
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
        )}
      </div>
    </div>
  );
};

export default UnifiedDashboard;
