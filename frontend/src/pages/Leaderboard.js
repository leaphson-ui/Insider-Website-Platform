import React, { useState, useEffect, useCallback } from 'react';
import DataTable from '../components/ui/DataTable';
import { getLeaderboard } from '../utils/api';

const Leaderboard = () => {
  const [traders, setTraders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [minTrades, setMinTrades] = useState(5);

  const fetchLeaderboard = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getLeaderboard(100, minTrades);
      setTraders(data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  }, [minTrades]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

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
      key: 'company_ticker', 
      header: 'Company',
      render: (value, row) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-sm text-secondary">{row.company_name}</div>
        </div>
      )
    },
    { 
      key: 'total_trades', 
      header: 'Total Trades',
      render: (value) => (
        <span className="font-medium">{value?.toLocaleString()}</span>
      )
    },
    { 
      key: 'avg_return_30d', 
      header: '30d Return',
      render: (value) => (
        <span className={`font-medium ${value > 0 ? 'text-green' : value < 0 ? 'text-red' : 'text-secondary'}`}>
          {value?.toFixed(2)}%
        </span>
      )
    },
    { 
      key: 'avg_return_90d', 
      header: '90d Return',
      render: (value) => (
        <span className={`font-medium ${value > 0 ? 'text-green' : value < 0 ? 'text-red' : 'text-secondary'}`}>
          {value?.toFixed(2)}%
        </span>
      )
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
        <h1 className="text-3xl font-bold text-primary">Leaderboard</h1>
        <div className="flex items-center gap-4">
          <label className="text-sm text-secondary">Min Trades:</label>
          <select 
            value={minTrades} 
            onChange={(e) => setMinTrades(Number(e.target.value))}
            className="input w-24"
          >
            <option value={1}>1+</option>
            <option value={5}>5+</option>
            <option value={10}>10+</option>
            <option value={25}>25+</option>
          </select>
        </div>
      </div>

        <DataTable
          data={traders}
          columns={columns}
          loading={loading}
        />
    </div>
  );
};

export default Leaderboard;