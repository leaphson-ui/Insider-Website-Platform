import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRecentTrades } from '../utils/api';
import { formatCurrency, formatDate, getReturnColor } from '../utils/formatters';

const RecentTrades = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    limit: 500,
    ticker: '',
    days: 365
  });

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setLoading(true);
        const data = await getRecentTrades(
          filters.limit, 
          filters.ticker || null, 
          filters.days
        );
        setTrades(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching trades:', err);
        setError('Failed to load trades data');
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
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
        <h1 className="text-3xl font-bold text-gray-900">Recent Insider Trades</h1>
        <p className="mt-2 text-gray-600">
          Latest insider trading activity across all tracked companies.
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Company Ticker
            </label>
            <input
              type="text"
              value={filters.ticker}
              onChange={(e) => handleFilterChange('ticker', e.target.value.toUpperCase())}
              placeholder="e.g., AAPL"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Time Period
            </label>
            <select
              value={filters.days}
              onChange={(e) => handleFilterChange('days', parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={180}>Last 6 months</option>
              <option value={365}>Last year</option>
              <option value={730}>Last 2 years</option>
              <option value={1095}>Last 3 years</option>
              <option value={3650}>All time</option>
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
              <option value={100}>100</option>
              <option value={250}>250</option>
              <option value={500}>500</option>
              <option value={1000}>1,000</option>
              <option value={2500}>2,500</option>
            </select>
          </div>
        </div>
      </div>

      {/* Trades Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Trader
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Shares
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  30d Return
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Filing Date
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {trades.map((trade) => (
                <tr key={trade.trade_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(trade.transaction_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {trade.trader_name}
                      </div>
                      <div className="text-sm text-gray-500">{trade.trader_title}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {trade.company_ticker}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      trade.transaction_type.includes('BUY') || trade.transaction_type === 'P' || trade.transaction_type === 'A'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {trade.transaction_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {trade.shares_traded.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${trade.price_per_share.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {formatCurrency(trade.total_value)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {trade.current_price ? `$${trade.current_price.toFixed(2)}` : 'N/A'}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trade.return_30d)}`}>
                    {trade.return_30d !== null && trade.return_30d !== undefined 
                      ? `${trade.return_30d.toFixed(1)}%` 
                      : 'N/A'
                    }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(trade.filing_date)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {trades.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No trades found matching your criteria.</p>
          </div>
        )}
      </div>

      {/* Summary */}
      {trades.length > 0 && (
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">
            Showing {trades.length} trades from the last {filters.days} days
            {filters.ticker && ` for ${filters.ticker}`}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecentTrades;
