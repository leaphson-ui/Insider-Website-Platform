import React, { useState, useEffect, useCallback } from 'react';
import DataTable from '../components/ui/DataTable';
import { getPortfolioLeaderboard } from '../utils/api';
import { formatCurrency } from '../utils/formatters';

const PortfolioLeaderboard = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [minHoldingsValue, setMinHoldingsValue] = useState(100000);

  const fetchPortfolios = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getPortfolioLeaderboard(100, minHoldingsValue);
      setPortfolios(data);
    } catch (error) {
      console.error('Error fetching portfolio leaderboard:', error);
    } finally {
      setLoading(false);
    }
  }, [minHoldingsValue]);

  useEffect(() => {
    fetchPortfolios();
  }, [fetchPortfolios]);

  const columns = [
    { 
      key: 'name', 
      header: 'Trader',
      render: (value, row) => (
        <div 
          onClick={() => window.location.href = `/traders/${row.trader_id}`}
          className="cursor-pointer hover:text-blue transition-colors"
        >
          <div className="font-medium">{value}</div>
          <div className="text-sm text-secondary">{row.title}</div>
        </div>
      )
    },
    { 
      key: 'company_name', 
      header: 'Company',
      render: (value) => (
        <span className="font-medium">{value}</span>
      )
    },
    { 
      key: 'total_portfolio_value', 
      header: 'Portfolio Value',
      render: (value) => (
        <span className="font-bold text-green">{formatCurrency(value)}</span>
      )
    },
    { 
      key: 'companies_held', 
      header: 'Companies',
      render: (value) => (
        <span className="font-medium">{value}</span>
      )
    },
    { 
      key: 'total_trades', 
      header: 'Total Trades',
      render: (value) => formatCurrency(value)
    },
    { 
      key: 'performance_score', 
      header: 'Score',
      render: (value) => (
        <span className="font-bold text-blue">{value?.toFixed(2)}</span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-primary">Portfolio Leaderboard</h1>
        <div className="flex items-center gap-4">
          <label className="text-sm text-secondary">Min Portfolio Value:</label>
          <select 
            value={minHoldingsValue} 
            onChange={(e) => setMinHoldingsValue(Number(e.target.value))}
            className="input w-32"
          >
            <option value={0}>$0+</option>
            <option value={100000}>$100K+</option>
            <option value={500000}>$500K+</option>
            <option value={1000000}>$1M+</option>
            <option value={5000000}>$5M+</option>
          </select>
        </div>
      </div>

      <DataTable
        data={portfolios}
        columns={columns}
        loading={loading}
      />
    </div>
  );
};

export default PortfolioLeaderboard;