import React, { useState, useEffect } from 'react';
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

  // Reset to page 1 when search term changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  // Fetch transactions from Supabase
  useEffect(() => {
    fetchTransactions();
  }, [searchTerm, currentPage]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      
      // Calculate offset for pagination
      const offset = (currentPage - 1) * itemsPerPage;
      
      let transactions = [];
      let totalCount = 0;
      
      if (searchTerm && searchTerm.trim()) {
        // Simple search approach: Search companies first, then get their transactions
        const searchPattern = `%${searchTerm.trim()}%`;
        
        // Get matching companies
        const { data: companies } = await supabase
          .from('companies')
          .select('id')
          .or(`name.ilike.${searchPattern},ticker.ilike.${searchPattern}`);
        
        if (companies && companies.length > 0) {
          const companyIds = companies.map(c => c.id);
          
          // Get transactions for matching companies with proper joins
          const { data: transactionData, count } = await supabase
            .from('transactions')
            .select(`
              *,
              companies(id, name, ticker),
              insiders(id, name, is_director, is_officer)
            `, { count: 'exact' })
            .in('company_id', companyIds)
            .not('insider_id', 'is', null)
            .order('transaction_date', { ascending: false })
            .range(offset, offset + itemsPerPage - 1);
          
          transactions = transactionData || [];
          totalCount = count || 0;
        }
      } else {
        // No search - get all transactions with valid foreign keys
        const { data: transactionData, count } = await supabase
          .from('transactions')
          .select(`
            *,
            companies(id, name, ticker),
            insiders(id, name, is_director, is_officer)
          `, { count: 'exact' })
          .not('company_id', 'is', null)
          .not('insider_id', 'is', null)
          .order('transaction_date', { ascending: false })
          .range(offset, offset + itemsPerPage - 1);
        
        transactions = transactionData || [];
        totalCount = count || 0;
      }
      
      setTotalItems(totalCount);
      setTotalPages(Math.ceil(totalCount / itemsPerPage));
      
      if (!transactions || transactions.length === 0) {
        setTransactions([]);
        return;
      }

      // Data is already joined from the query, just format it
      const enrichedTransactions = transactions.map(transaction => ({
        ...transaction,
        companies: transaction.companies,
        insiders: transaction.insiders
      }));

      setTransactions(enrichedTransactions);
    } catch (error) {
      console.error('Error:', error);
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  };

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
          </div>
          
          {loading ? (
            <div className="table-row">
              <div className="cell">Loading...</div>
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
                <div className="cell">{transaction.insiders?.name || 'N/A'}</div>
                <div className="cell">{transaction.companies?.ticker || 'N/A'}</div>
                <div className="cell">{formatShares(transaction.transaction_shares)}</div>
                <div className={`cell ${getValueClass(transaction.transaction_code, transaction.calculated_transaction_value)}`}>
                  {formatCurrency(transaction.calculated_transaction_value)}
                </div>
                <div className="cell">{getTransactionType(transaction.transaction_code)}</div>
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