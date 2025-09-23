import React, { useState, useEffect, useCallback } from 'react';
import DataTable from '../components/ui/DataTable';
import { getRecentTrades } from '../utils/api';

const RecentTrades = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ticker, setTicker] = useState('');

  const fetchTrades = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getRecentTrades(100, ticker || null, 365);
      setTrades(data);
    } catch (error) {
      console.error('Error fetching recent trades:', error);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchTrades();
  }, [fetchTrades]);

  const columns = [
    { 
      key: 'trader_name', 
      header: 'Trader',
      render: (value, row) => (
        <div>
          <div className="font-medium text-primary">{value}</div>
          <div className="text-sm text-secondary">{row.trader_title}</div>
        </div>
      )
    },
    { 
      key: 'company_ticker', 
      header: 'Company',
      render: (value) => (
        <span className="font-medium">{value}</span>
      )
    },
    { 
      key: 'transaction_type', 
      header: 'Type',
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value?.toUpperCase().includes('BUY') ? 'bg-green text-white' : 
          value?.toUpperCase().includes('SELL') ? 'bg-red text-white' : 
          'bg-secondary text-primary'
        }`}>
          {value}
        </span>
      )
    },
    { 
      key: 'shares_traded', 
      header: 'Shares',
      render: (value) => (
        <span className="font-medium">{value?.toLocaleString()}</span>
      )
    },
    { 
      key: 'price_per_share', 
      header: 'Price',
      render: (value) => (
        <span className="font-medium">${value?.toFixed(2)}</span>
      )
    },
    { 
      key: 'total_value', 
      header: 'Value',
      render: (value) => (
        <span className="font-medium">${value?.toLocaleString()}</span>
      )
    },
    { 
      key: 'return_30d', 
      header: '30d Return',
      render: (value) => (
        <span className={`font-medium ${value > 0 ? 'text-green' : value < 0 ? 'text-red' : 'text-secondary'}`}>
          {value ? `${value.toFixed(2)}%` : 'N/A'}
        </span>
      )
    },
    { 
      key: 'transaction_date', 
      header: 'Date',
      render: (value) => (
        <span className="text-sm">{new Date(value).toLocaleDateString()}</span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-primary">Recent Trades</h1>
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Filter by ticker (e.g., AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            className="input w-48"
          />
          <button
            onClick={fetchTrades}
            className="btn btn-primary"
          >
            Refresh
          </button>
        </div>
      </div>

      <DataTable
        data={trades}
        columns={columns}
        loading={loading}
      />
    </div>
  );
};

export default RecentTrades;