import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  UsersIcon, 
  ChartBarIcon, 
  CurrencyDollarIcon,
  ClockIcon,
  BuildingOfficeIcon,
  FireIcon,
  BellIcon,
  EyeIcon,
  ChevronUpIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';
import { getLeaderboard, getPlatformStats, getRecentTrades } from '../utils/api';
import { formatCurrency, formatPercentage, formatDate, getReturnColor, getPerformanceScoreColor } from '../utils/formatters';

const EnhancedDashboard = () => {
  const [stats, setStats] = useState(null);
  const [topTraders, setTopTraders] = useState([]);
  const [recentTrades, setRecentTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('365d');
  const [sortField, setSortField] = useState('performance_score');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const days = selectedTimeframe === '7d' ? 7 : 
                     selectedTimeframe === '30d' ? 30 : 
                     selectedTimeframe === '90d' ? 90 :
                     selectedTimeframe === '180d' ? 180 :
                     selectedTimeframe === '365d' ? 365 :
                     selectedTimeframe === '730d' ? 730 : 
                     3650; // All time = 10 years
        
        const [statsData, leaderboardData, tradesData] = await Promise.all([
          getPlatformStats(),
          getLeaderboard(50, 1), // Get top 50 traders
          getRecentTrades(50, null, days) // Reasonable amount for loading
        ]);

        setStats(statsData);
        setTopTraders(leaderboardData);
        setRecentTrades(tradesData);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedTimeframe]);

  // Calculate advanced metrics
  const calculateAdvancedMetrics = () => {
    if (!topTraders.length || !recentTrades.length) return {};

    // Sector analysis
    const sectorData = {};
    recentTrades.forEach(trade => {
      const sector = getSectorFromTicker(trade.company_ticker);
      if (!sectorData[sector]) {
        sectorData[sector] = { buys: 0, sells: 0, volume: 0 };
      }
      if (trade.transaction_type === 'BUY') {
        sectorData[sector].buys++;
      } else if (trade.transaction_type === 'SELL') {
        sectorData[sector].sells++;
      }
      sectorData[sector].volume += trade.total_value;
    });

    // Buy/sell ratio
    const buyTrades = recentTrades.filter(t => t.transaction_type === 'BUY').length;
    const sellTrades = recentTrades.filter(t => t.transaction_type === 'SELL').length;
    const buySellRatio = sellTrades > 0 ? (buyTrades / sellTrades).toFixed(2) : 'N/A';

    // Average trade size
    const avgTradeSize = recentTrades.reduce((sum, t) => sum + t.total_value, 0) / recentTrades.length;

    // Top performing sectors
    const topSectors = Object.entries(sectorData)
      .sort(([,a], [,b]) => b.volume - a.volume)
      .slice(0, 8);

    return {
      sectorData,
      buySellRatio,
      avgTradeSize,
      topSectors,
      buyTrades,
      sellTrades
    };
  };

  const getSectorFromTicker = (ticker) => {
    const sectorMap = {
      'AAPL': 'Technology',
      'MSFT': 'Technology', 
      'GOOGL': 'Technology',
      'NVDA': 'Technology',
      'TSLA': 'Automotive',
      'AMZN': 'E-commerce',
      'META': 'Technology'
    };
    return sectorMap[ticker] || 'Other';
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const getSortedTraders = () => {
    return [...topTraders].sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];
      
      // Handle null/undefined values
      if (aVal == null) aVal = sortDirection === 'desc' ? -Infinity : Infinity;
      if (bVal == null) bVal = sortDirection === 'desc' ? -Infinity : Infinity;
      
      if (sortDirection === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });
  };

  const SortableHeader = ({ field, children }) => (
    <th 
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortField === field && (
          sortDirection === 'desc' ? 
            <ChevronDownIcon className="h-4 w-4" /> : 
            <ChevronUpIcon className="h-4 w-4" />
        )}
      </div>
    </th>
  );

  const metrics = calculateAdvancedMetrics();

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
    <div className="space-y-8">
      {/* Enhanced Header with Alerts */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Insider Alpha Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Advanced insider trading analytics and market intelligence
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button className="flex items-center px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700">
            <BellIcon className="h-5 w-5 mr-2" />
            Alerts
          </button>
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="rounded-lg border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="180d">Last 6 Months</option>
            <option value="365d">Last Year</option>
            <option value="730d">Last 2 Years</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      {/* Enhanced Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UsersIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Active Insiders</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.active_traders}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Trades</dt>
                    <dd className="text-lg font-medium text-gray-900">{stats.total_trades.toLocaleString()}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ArrowUpIcon className="h-6 w-6 text-green-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Buy/Sell Ratio</dt>
                    <dd className="text-lg font-medium text-gray-900">{metrics.buySellRatio}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CurrencyDollarIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Avg Trade Size</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {formatCurrency(metrics.avgTradeSize || 0)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Market Sentiment & Activity Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Insider Sentiment */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Insider Sentiment</h2>
            <FireIcon className="h-5 w-5 text-orange-500" />
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Bullish Trades (Buys)</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div 
                    className="bg-green-500 h-2 rounded-full" 
                    style={{ width: `${(metrics.buyTrades / (metrics.buyTrades + metrics.sellTrades)) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-green-600">{metrics.buyTrades}</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Bearish Trades (Sells)</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                  <div 
                    className="bg-red-500 h-2 rounded-full" 
                    style={{ width: `${(metrics.sellTrades / (metrics.buyTrades + metrics.sellTrades)) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-red-600">{metrics.sellTrades}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Top Sectors */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Top Sectors by Volume</h2>
            <BuildingOfficeIcon className="h-5 w-5 text-blue-500" />
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {metrics.topSectors?.slice(0, 8).map(([sector, data], index) => (
              <div key={sector} className="flex justify-between items-center py-1">
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    index === 0 ? 'bg-blue-500' :
                    index === 1 ? 'bg-green-500' :
                    index === 2 ? 'bg-yellow-500' :
                    index === 3 ? 'bg-purple-500' :
                    index === 4 ? 'bg-red-500' :
                    index === 5 ? 'bg-indigo-500' :
                    index === 6 ? 'bg-pink-500' : 'bg-gray-500'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-700">{sector}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">{formatCurrency(data.volume)}</span>
                  <div className="flex items-center space-x-1">
                    <span className="text-xs text-green-600">+{data.buys}</span>
                    <span className="text-xs text-red-600">-{data.sells}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Enhanced Top Performers with Conviction Scores */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Top Performers by Conviction Score</h2>
            <Link to="/leaderboard" className="text-brand-600 hover:text-brand-500 text-sm font-medium">
              View full leaderboard →
            </Link>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Insider</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                  <SortableHeader field="performance_score">Conviction</SortableHeader>
                  <SortableHeader field="avg_return_90d">90d Return</SortableHeader>
                  <SortableHeader field="win_rate">Win Rate</SortableHeader>
                  <SortableHeader field="total_profit_loss">Total P&L</SortableHeader>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {getSortedTraders().slice(0, 10).map((trader, index) => (
                  <tr key={trader.trader_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-900">#{index + 1}</span>
                        {index < 3 && (
                          <FireIcon className={`ml-2 h-4 w-4 ${
                            index === 0 ? 'text-yellow-500' : 
                            index === 1 ? 'text-gray-400' : 'text-orange-600'
                          }`} />
                        )}
                      </div>
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
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {trader.company_ticker}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`text-sm font-bold ${getPerformanceScoreColor(trader.performance_score)}`}>
                          {trader.performance_score?.toFixed(1) || 'N/A'}
                        </div>
                        <div className="ml-2">
                          {trader.performance_score > 30 ? (
                            <ArrowUpIcon className="h-4 w-4 text-green-500" />
                          ) : trader.performance_score > 0 ? (
                            <ArrowUpIcon className="h-4 w-4 text-yellow-500" />
                          ) : (
                            <ArrowDownIcon className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                      </div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trader.avg_return_90d)}`}>
                      {formatPercentage(trader.avg_return_90d)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <span>{formatPercentage(trader.win_rate)}</span>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full" 
                            style={{ width: `${trader.win_rate}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trader.total_profit_loss)}`}>
                      {formatCurrency(trader.total_profit_loss)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center space-x-2">
                        <button className="text-brand-600 hover:text-brand-500">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button className="text-gray-400 hover:text-gray-500">
                          <BellIcon className="h-4 w-4" />
                        </button>
                      </div>
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

export default EnhancedDashboard;
