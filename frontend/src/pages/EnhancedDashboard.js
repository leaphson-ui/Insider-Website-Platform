import React, { useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import Navigation from '../components/Navigation';
import Pagination from '../components/Pagination';

const EnhancedDashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [itemsPerPage, setItemsPerPage] = useState(50);
  const [allTransactions, setAllTransactions] = useState([]);
  
  // Analytics state
  const [analytics, setAnalytics] = useState({
    flowSentiment: 'Neutral',
    buySellRatio: '50% / 50%',
    buyFlow: 0,
    sellFlow: 0
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

    const buyTransactions = transactionData.filter(t => 
      t.transaction_code === 'P' || 
      t.transaction_code === 'A' || 
      t.transaction_code === 'D' ||
      t.transaction_code === 'F' ||
      t.transaction_code === 'G' ||
      t.transaction_code === 'H' ||
      t.transaction_code === 'I' ||
      t.transaction_code === 'J' ||
      t.transaction_code === 'K' ||
      t.transaction_code === 'L' ||
      t.transaction_code === 'M' ||
      t.transaction_code === 'N' ||
      t.transaction_code === 'O' ||
      t.transaction_code === 'Q' ||
      t.transaction_code === 'R' ||
      t.transaction_code === 'T' ||
      t.transaction_code === 'U' ||
      t.transaction_code === 'V' ||
      t.transaction_code === 'W' ||
      t.transaction_code === 'X' ||
      t.transaction_code === 'Y' ||
      t.transaction_code === 'Z'
    );

    const sellTransactions = transactionData.filter(t => 
      t.transaction_code === 'S' || 
      t.transaction_code === 'C' || 
      t.transaction_code === 'E'
    );

    const totalTransactions = transactionData.length;
    const buyCount = buyTransactions.length;
    const sellCount = sellTransactions.length;
    
    const buyPercentage = totalTransactions > 0 ? Math.round((buyCount / totalTransactions) * 100) : 0;
    const sellPercentage = totalTransactions > 0 ? Math.round((sellCount / totalTransactions) * 100) : 0;

    // Calculate total values
    const buyFlow = buyTransactions.reduce((sum, t) => sum + (t.calculated_transaction_value || 0), 0);
    const sellFlow = sellTransactions.reduce((sum, t) => sum + (t.calculated_transaction_value || 0), 0);

    // Determine sentiment
    let sentiment = 'Neutral';
    if (buyPercentage > 60) sentiment = 'Bullish';
    else if (sellPercentage > 60) sentiment = 'Bearish';

    setAnalytics({
      flowSentiment: sentiment,
      buySellRatio: `${buyPercentage}% / ${sellPercentage}%`,
      buyFlow: buyFlow,
      sellFlow: sellFlow
    });
  }, []);
  
  // Filter states
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    companyName: '',
    companyTicker: '',
    insiderName: '',
    transactionType: 'all'
  });

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
      console.log('📊 Executing search query...');
      const { data: allData, count, error } = await query;
      
      if (error) {
        console.error('Supabase query error:', error);
        throw error;
      }
      
      console.log('📈 Search results:', {
        dataLength: allData?.length || 0,
        count: count,
        searchTerm: trimmedTerm
      });
      
      console.log('🔄 Setting state...');
      setAllTransactions(allData || []);
      setTotalItems(count || 0);
      console.log('✅ State set - allTransactions:', allData?.length || 0, 'totalItems:', count || 0);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setAllTransactions([]);
      setTotalItems(0);
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);

  // Reset to page 1 when search or filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filters]);

  // Fetch all data when search term changes
  useEffect(() => {
    fetchAllTransactions();
  }, [fetchAllTransactions]);

  // Apply filters to data
  const applyFilters = useCallback((data) => {
    console.log('Current filters:', filters);
    
    const filtered = data.filter(transaction => {
      // Date range filter
      if (filters.startDate && transaction.transaction_date < filters.startDate) return false;
      if (filters.endDate && transaction.transaction_date > filters.endDate) return false;
      
      // Company name filter
      if (filters.companyName && !transaction.company_name.toLowerCase().includes(filters.companyName.toLowerCase())) return false;
      
      // Company ticker filter
      if (filters.companyTicker && !transaction.company_ticker.toLowerCase().includes(filters.companyTicker.toLowerCase())) return false;
      
      // Insider name filter
      if (filters.insiderName && !transaction.insider_name.toLowerCase().includes(filters.insiderName.toLowerCase())) return false;
      
      // Transaction type filter
      if (filters.transactionType !== 'all' && transaction.transaction_code !== filters.transactionType) return false;
      
      return true;
    });
    
    console.log(`Filtered ${data.length} transactions down to ${filtered.length}`);
    return filtered;
  }, [filters]);

  // Process and paginate the data
  const processTransactions = useCallback(() => {
    console.log('🔄 Processing transactions...', {
      allTransactionsLength: allTransactions.length,
      currentPage: currentPage,
      itemsPerPage: itemsPerPage
    });
    
    if (allTransactions.length === 0) {
      console.log('❌ No allTransactions data');
      setTransactions([]);
      setTotalPages(0);
      return;
    }

    // Apply filters first
    const filteredData = applyFilters(allTransactions);
    console.log('📊 Filtered data length:', filteredData.length);
    
    // Calculate pagination
    const totalFilteredItems = filteredData.length;
    const totalPages = Math.ceil(totalFilteredItems / itemsPerPage);
    setTotalPages(totalPages);
    
    // Get current page data
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentPageData = filteredData.slice(startIndex, endIndex);
    
    console.log('📄 Pagination results:', {
      totalFilteredItems,
      totalPages,
      currentPage,
      startIndex,
      endIndex,
      currentPageDataLength: currentPageData.length
    });
    
    setTransactions(currentPageData);
    
    // Calculate analytics from filtered data
    calculateAnalytics(filteredData);
  }, [allTransactions, currentPage, itemsPerPage, applyFilters, calculateAnalytics]);

  // Process data when sorting or pagination changes
  useEffect(() => {
    processTransactions();
  }, [processTransactions]);

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

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

        {/* Search Interface - Hero Section Styling */}
        {!searchTerm || !searchTerm.trim() ? (
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
                    />
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
                      onClick={() => setSearchTerm(term)}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-full text-sm text-white transition-colors"
                    >
                      {term}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>
        ) : (
          /* Show search bar and filters when searching */
          <div className="mb-6 space-y-4">
            {/* Search Bar */}
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
                />
                {searchTerm && (
                  <button 
                    onClick={() => setSearchTerm('')}
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

            {/* Filter Controls - Compact */}
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
          </div>
        )}

        {/* Show table and pagination only when searching */}
        {searchTerm && searchTerm.trim() && (
          <>
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
          </>
        )}
      </div>
    </div>
  );
};

export default EnhancedDashboard;