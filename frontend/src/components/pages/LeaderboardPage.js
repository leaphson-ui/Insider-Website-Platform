import React, { useState, useEffect } from 'react';
import { 
  TrophyIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  UserIcon,
  CurrencyDollarIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

const LeaderboardPage = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortField, setSortField] = useState('performance_score');
  const [sortDirection, setSortDirection] = useState('desc');
  const [filterSector, setFilterSector] = useState('all');
  const [filterMinTrades, setFilterMinTrades] = useState(0);
  const [sectors, setSectors] = useState([]);

  useEffect(() => {
    fetchLeaderboardData();
    fetchSectors();
  }, [sortField, sortDirection, filterSector, filterMinTrades]);

  const fetchLeaderboardData = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        sort: sortField,
        direction: sortDirection,
        limit: 100
      });
      
      if (filterSector !== 'all') {
        params.append('sector', filterSector);
      }
      
      if (filterMinTrades > 0) {
        params.append('min_trades', filterMinTrades);
      }

      const response = await fetch(`/api/leaderboard?${params}`);
      if (!response.ok) throw new Error('Failed to fetch leaderboard data');
      const data = await response.json();
      
      setLeaderboard(data.leaderboard || []);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSectors = async () => {
    try {
      const response = await fetch('/api/sectors');
      if (response.ok) {
        const data = await response.json();
        setSectors(data.sectors || []);
      }
    } catch (err) {
      console.error('Failed to fetch sectors:', err);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const getRankIcon = (index) => {
    if (index === 0) return <TrophyIcon className="w-6 h-6 text-yellow-500" />;
    if (index === 1) return <TrophyIcon className="w-6 h-6 text-gray-400" />;
    if (index === 2) return <TrophyIcon className="w-6 h-6 text-orange-500" />;
    return <span className="text-lg font-bold text-gray-400">#{index + 1}</span>;
  };

  const getPerformanceColor = (score) => {
    if (score > 1000) return 'text-green-600';
    if (score > 500) return 'text-blue-600';
    if (score > 100) return 'text-yellow-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">⚠️</div>
          <p className="text-gray-600">Error loading data: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center">
                <TrophyIcon className="w-8 h-8 text-yellow-600" />
              </div>
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Insider Trading Leaderboard
              </h1>
              <p className="text-gray-600">
                Top performing corporate insiders ranked by their trading performance
              </p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sort by
              </label>
              <select
                value={sortField}
                onChange={(e) => setSortField(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="performance_score">Performance Score</option>
                <option value="win_rate">Win Rate</option>
                <option value="total_profit_loss">Total Profit/Loss</option>
                <option value="total_trades">Total Trades</option>
                <option value="avg_return_30d">30-Day Return</option>
                <option value="avg_return_90d">90-Day Return</option>
                <option value="avg_return_1y">1-Year Return</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sector
              </label>
              <select
                value={filterSector}
                onChange={(e) => setFilterSector(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Sectors</option>
                {sectors.map((sector) => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Trades
              </label>
              <select
                value={filterMinTrades}
                onChange={(e) => setFilterMinTrades(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={0}>All</option>
                <option value={10}>10+ trades</option>
                <option value={50}>50+ trades</option>
                <option value={100}>100+ trades</option>
                <option value={500}>500+ trades</option>
              </select>
            </div>
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Top Performers</h2>
            <p className="text-sm text-gray-600 mt-1">
              {leaderboard.length} insiders ranked by {sortField.replace('_', ' ')}
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('name')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Insider</span>
                      {sortField === 'name' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('company_ticker')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Company</span>
                      {sortField === 'company_ticker' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('performance_score')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Score</span>
                      {sortField === 'performance_score' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('win_rate')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Win Rate</span>
                      {sortField === 'win_rate' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('total_trades')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Trades</span>
                      {sortField === 'total_trades' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('total_profit_loss')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>P&L</span>
                      {sortField === 'total_profit_loss' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('avg_return_30d')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>30d Return</span>
                      {sortField === 'avg_return_30d' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {leaderboard.map((trader, index) => (
                  <tr key={trader.trader_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getRankIcon(index)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                            <UserIcon className="h-6 w-6 text-gray-500" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {trader.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {trader.title}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {trader.company_ticker}
                      </div>
                      <div className="text-sm text-gray-500">
                        {trader.company_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-lg font-bold ${getPerformanceColor(trader.performance_score)}`}>
                        {trader.performance_score?.toFixed(0) || 0}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-900">
                          {formatPercentage(trader.win_rate)}%
                        </span>
                        {trader.win_rate > 80 && (
                          <ArrowTrendingUpIcon className="w-4 h-4 text-green-500 ml-1" />
                        )}
                        {trader.win_rate < 20 && (
                          <ArrowTrendingDownIcon className="w-4 h-4 text-red-500 ml-1" />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {trader.total_trades?.toLocaleString() || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${
                        trader.total_profit_loss > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatCurrency(trader.total_profit_loss)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${
                        trader.avg_return_30d > 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {trader.avg_return_30d ? formatPercentage(trader.avg_return_30d) : 'N/A'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeaderboardPage;
