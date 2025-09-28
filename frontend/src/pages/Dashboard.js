import React, { useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import Navigation from '../components/Navigation';
import Pagination from '../components/Pagination';

const Dashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const itemsPerPage = 20;

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      
      // Calculate offset for pagination
      const offset = (currentPage - 1) * itemsPerPage;
      
      let transactions = [];
      let totalCount = 0;
      
      if (searchTerm && searchTerm.trim()) {
        // Search in the consolidated insider_transactions table
        const searchPattern = `%${searchTerm.trim()}%`;
        
        // Search across company name, ticker, and insider name
        const { data: transactionData, count } = await supabase
          .from('insider_transactions')
          .select('*', { count: 'exact' })
          .or(`company_name.ilike.${searchPattern},company_ticker.ilike.${searchPattern},insider_name.ilike.${searchPattern}`)
          .order('transaction_date', { ascending: false })
          .range(offset, offset + itemsPerPage - 1);
        
        transactions = transactionData || [];
        totalCount = count || 0;
      } else {
        // No search - get all transactions from consolidated table
        const { data: transactionData, count } = await supabase
          .from('insider_transactions')
          .select('*', { count: 'exact' })
          .order('transaction_date', { ascending: false })
          .range(offset, offset + itemsPerPage - 1);
        
        transactions = transactionData || [];
        totalCount = count || 0;
      }
      
      setTotalItems(totalCount);
      setTotalPages(Math.ceil(totalCount / itemsPerPage));
      setTransactions(transactions);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, currentPage, itemsPerPage]);

  // Reset to page 1 when search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  // Fetch transactions from Supabase
  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const clearSearch = () => {
    setSearchTerm('');
  };



  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
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

  const formatInsiderRole = (relationship, title) => {
    if (title) return title;
    if (relationship === 'Director') return 'Director';
    if (relationship === 'Officer') return 'Officer';
    if (relationship === 'TenPercentOwner') return '10% Owner';
    return relationship || 'N/A';
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

  const getTransactionType = (code) => {
    switch (code) {
      case 'P': return 'BUY';
      case 'S': return 'SELL';
      case 'A': return 'AWARD';
      case 'G': return 'GIFT';
      case 'M': return 'EXERCISE';
      case 'C': return 'CONVERT';
      case 'J': return 'OTHER';
      default: return code;
    }
  };

  const getValueClass = (code, value) => {
    if (code === 'P') return 'positive';
    if (code === 'S') return 'negative';
    if (code === 'A' || code === 'G') return '';
    return '';
  };

  return (
    <div className="min-h-screen bg-primary">
      <Navigation />
      
      <div className="container py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">Insider Trading Dashboard</h1>
          <p className="text-secondary">
            Real-time insider trading data from SEC Form 4 filings
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
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
                  onClick={clearSearch}
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


        {/* Trades Table - Using EXACT same structure as homepage */}
        <div className="trades-table">
          <div className="table-header">
            <div className="header-cell">TIME</div>
            <div className="header-cell">INSIDER</div>
            <div className="header-cell">COMPANY</div>
            <div className="header-cell">SHARES</div>
            <div className="header-cell">VALUE</div>
            <div className="header-cell">TYPE</div>
            <div className="header-cell">SECURITY</div>
            <div className="header-cell">ROLE</div>
            <div className="header-cell">SIGNATURE DATE</div>
          </div>
          
          {loading ? (
            <div className="table-row">
              <div className="cell">Loading...</div>
              <div className="cell"></div>
              <div className="cell"></div>
              <div className="cell"></div>
              <div className="cell"></div>
              <div className="cell"></div>
              <div className="cell"></div>
              <div className="cell"></div>
              <div className="cell"></div>
            </div>
          ) : (
            transactions.map((transaction) => (
              <div key={transaction.id} className="table-row">
                <div className="cell">{formatTime(transaction.transaction_date)}</div>
                <div className="cell">{transaction.insider_name || 'N/A'}</div>
                <div className="cell">{transaction.company_name || transaction.company_ticker || 'N/A'}</div>
                <div className="cell">{formatShares(transaction.transaction_shares)}</div>
                <div className={`cell ${getValueClass(transaction.transaction_code, transaction.calculated_transaction_value)}`}>
                  {formatCurrency(transaction.calculated_transaction_value)}
                </div>
                <div className="cell">{getTransactionType(transaction.transaction_code)}</div>
                <div className="cell">{transaction.security_title || 'N/A'}</div>
                <div className="cell">{formatInsiderRole(transaction.insider_relationship, transaction.insider_title)}</div>
                <div className="cell">{formatSignatureDate(transaction.owner_signature_date)}</div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
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
  );
};

export default Dashboard;