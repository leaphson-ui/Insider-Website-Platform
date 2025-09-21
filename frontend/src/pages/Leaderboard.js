import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getLeaderboard } from '../utils/api';
import { formatCurrency, formatPercentage, getReturnColor, getPerformanceScoreColor } from '../utils/formatters';

const Leaderboard = () => {
  const [traders, setTraders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    minTrades: 1,
    limit: 50
  });

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        const data = await getLeaderboard(filters.limit, filters.minTrades);
        setTraders(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching leaderboard:', err);
        setError('Failed to load leaderboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Insider Trading Leaderboard</h1>
        <p className="mt-2 text-gray-600">
          Top performing corporate insiders ranked by their trading performance.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Minimum Trades
            </label>
            <select
              value={filters.minTrades}
              onChange={(e) => handleFilterChange('minTrades', parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
            >
              <option value={1}>1+</option>
              <option value={3}>3+</option>
              <option value={5}>5+</option>
              <option value={10}>10+</option>
              <option value={20}>20+</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Results Limit
            </label>
            <select
              value={filters.limit}
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trader
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trades
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  30d Return
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  90d Return
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  1Y Return
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Win Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  P&L
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {traders.map((trader, index) => (
                <tr key={trader.trader_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{index + 1}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <Link
                        to={`/traders/${trader.trader_id}`}
                        className="text-sm font-medium text-brand-600 hover:text-brand-500"
                      >
                        {trader.name}
                      </Link>
                      <div className="text-sm text-gray-500">{trader.title}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{trader.company_ticker}</div>
                      <div className="text-sm text-gray-500">{trader.company_name}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {trader.total_trades}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trader.avg_return_30d)}`}>
                    {formatPercentage(trader.avg_return_30d)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trader.avg_return_90d)}`}>
                    {formatPercentage(trader.avg_return_90d)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trader.avg_return_1y)}`}>
                    {formatPercentage(trader.avg_return_1y)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatPercentage(trader.win_rate)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trader.total_profit_loss)}`}>
                    {formatCurrency(trader.total_profit_loss)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${getPerformanceScoreColor(trader.performance_score)}`}>
                    {trader.performance_score?.toFixed(1) || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {traders.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No traders found matching your criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
