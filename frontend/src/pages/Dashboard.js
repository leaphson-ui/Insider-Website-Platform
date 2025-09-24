import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import Navigation from '../components/Navigation';

const Dashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch transactions from Supabase
  useEffect(() => {
    fetchTransactions();
  }, [searchTerm]);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      
      let query = supabase
        .from('transactions')
        .select(`
          *,
          companies(name, ticker),
          insiders(name, is_director, is_officer)
        `)
        .order('transaction_date', { ascending: false })
        .limit(50);

      // Apply search filter
      if (searchTerm) {
        query = query.or(`companies.name.ilike.%${searchTerm}%,insiders.name.ilike.%${searchTerm}%`);
      }

      const { data, error } = await query;
      
      if (error) {
        console.error('Error fetching transactions:', error);
      } else {
        setTransactions(data || []);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
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
      </div>
    </div>
  );
};

export default Dashboard;