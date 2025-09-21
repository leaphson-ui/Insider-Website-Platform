import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ClockIcon, 
  TrendingUpIcon,
  CalendarIcon,
  UserGroupIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';
import { getRecentTrades, getLeaderboard } from '../utils/api';
import SectorAnalysis from '../components/SectorAnalysis';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const Analytics = () => {
  const [trades, setTrades] = useState([]);
  const [traders, setTraders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('30d');
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const days = timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : 90;
        
        const [tradesData, tradersData] = await Promise.all([
          getRecentTrades(500, null, days),
          getLeaderboard(50, 1)
        ]);

        setTrades(tradesData);
        setTraders(tradersData);
        
        // Calculate advanced analytics
        const analyticsData = calculateAdvancedAnalytics(tradesData, tradersData);
        setAnalytics(analyticsData);
        
      } catch (error) {
        console.error('Error fetching analytics data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeframe]);

  const calculateAdvancedAnalytics = (trades, traders) => {
    if (!trades.length) return {};

    // Timing analysis
    const tradesByDay = trades.reduce((acc, trade) => {
      const day = new Date(trade.transaction_date).getDay();
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      const dayName = dayNames[day];
      
      if (!acc[dayName]) acc[dayName] = { count: 0, volume: 0 };
      acc[dayName].count++;
      acc[dayName].volume += trade.total_value;
      
      return acc;
    }, {});

    // Size distribution
    const sizeDistribution = {
      small: trades.filter(t => t.total_value < 100000).length,
      medium: trades.filter(t => t.total_value >= 100000 && t.total_value < 1000000).length,
      large: trades.filter(t => t.total_value >= 1000000).length
    };

    // Top companies by insider activity
    const companyActivity = trades.reduce((acc, trade) => {
      if (!acc[trade.company_ticker]) {
        acc[trade.company_ticker] = { 
          count: 0, 
          volume: 0, 
          buys: 0, 
          sells: 0,
          insiders: new Set()
        };
      }
      
      acc[trade.company_ticker].count++;
      acc[trade.company_ticker].volume += trade.total_value;
      acc[trade.company_ticker].insiders.add(trade.trader_name);
      
      if (trade.transaction_type === 'BUY') {
        acc[trade.company_ticker].buys++;
      } else if (trade.transaction_type === 'SELL') {
        acc[trade.company_ticker].sells++;
      }
      
      return acc;
    }, {});

    // Convert insider sets to counts
    Object.keys(companyActivity).forEach(ticker => {
      companyActivity[ticker].uniqueInsiders = companyActivity[ticker].insiders.size;
      delete companyActivity[ticker].insiders;
    });

    // Top companies sorted by volume
    const topCompanies = Object.entries(companyActivity)
      .sort(([,a], [,b]) => b.volume - a.volume)
      .slice(0, 10);

    // Conviction analysis (based on trade frequency and size)
    const highConvictionTrades = trades.filter(trade => {
      const traderData = traders.find(t => t.name === trade.trader_name);
      return traderData && traderData.performance_score > 30 && trade.total_value > 500000;
    });

    return {
      tradesByDay,
      sizeDistribution,
      topCompanies,
      highConvictionTrades,
      totalVolume: trades.reduce((sum, t) => sum + t.total_value, 0),
      avgTradeSize: trades.reduce((sum, t) => sum + t.total_value, 0) / trades.length,
      buyVsSell: {
        buys: trades.filter(t => t.transaction_type === 'BUY').length,
        sells: trades.filter(t => t.transaction_type === 'SELL').length
      }
    };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
          <p className="mt-2 text-gray-600">
            Deep insights into insider trading patterns and market behavior
          </p>
        </div>
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
          className="rounded-lg border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
        >
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Volume</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(analytics.totalVolume || 0)}
                  </dd>
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
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Trade Size</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(analytics.avgTradeSize || 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUpIcon className="h-6 w-6 text-green-500" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Buy/Sell Ratio</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.buyVsSell ? 
                      (analytics.buyVsSell.buys / Math.max(analytics.buyVsSell.sells, 1)).toFixed(2) : 
                      'N/A'
                    }
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">High Conviction</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.highConvictionTrades?.length || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trade Size Distribution */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Trade Size Distribution</h3>
          <div className="space-y-4">
            {analytics.sizeDistribution && (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Small (&lt;$100K)</span>
                  <div className="flex items-center">
                    <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ 
                          width: `${(analytics.sizeDistribution.small / trades.length) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{analytics.sizeDistribution.small}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Medium ($100K-$1M)</span>
                  <div className="flex items-center">
                    <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                      <div 
                        className="bg-yellow-500 h-2 rounded-full" 
                        style={{ 
                          width: `${(analytics.sizeDistribution.medium / trades.length) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{analytics.sizeDistribution.medium}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">Large (&gt;$1M)</span>
                  <div className="flex items-center">
                    <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                      <div 
                        className="bg-red-500 h-2 rounded-full" 
                        style={{ 
                          width: `${(analytics.sizeDistribution.large / trades.length) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{analytics.sizeDistribution.large}</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Trading Day Patterns */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Trading Day Patterns</h3>
          <div className="space-y-3">
            {analytics.tradesByDay && Object.entries(analytics.tradesByDay)
              .sort(([,a], [,b]) => b.count - a.count)
              .map(([day, data]) => (
                <div key={day} className="flex justify-between items-center">
                  <span className="text-sm text-gray-700">{day}</span>
                  <div className="flex items-center space-x-3">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-brand-500 h-2 rounded-full" 
                        style={{ 
                          width: `${(data.count / Math.max(...Object.values(analytics.tradesByDay).map(d => d.count))) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium w-8">{data.count}</span>
                    <span className="text-sm text-gray-500">{formatCurrency(data.volume)}</span>
                  </div>
                </div>
              ))
            }
          </div>
        </div>
      </div>

      {/* Sector Analysis */}
      <SectorAnalysis trades={trades} />

      {/* Top Companies by Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Most Active Companies</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Volume</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trade Count</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unique Insiders</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Buy/Sell</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sentiment</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {analytics.topCompanies?.map(([ticker, data]) => (
                  <tr key={ticker} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {ticker}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {formatCurrency(data.volume)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {data.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {data.uniqueInsiders}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className="text-green-600">+{data.buys}</span>
                      {' / '}
                      <span className="text-red-600">-{data.sells}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {data.buys > data.sells ? (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          Bullish
                        </span>
                      ) : data.sells > data.buys ? (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                          Bearish
                        </span>
                      ) : (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                          Neutral
                        </span>
                      )}
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

export default Analytics;
