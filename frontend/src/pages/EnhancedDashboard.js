import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
 ArrowUpIcon, 
 ArrowDownIcon,
 UsersIcon, 
 ChartBarIcon, 
 CurrencyDollarIcon,
 FireIcon,
 BellIcon,
 EyeIcon,
 ChevronUpIcon,
 ChevronDownIcon,
 ArrowPathIcon
} from '@heroicons/react/24/outline';
import { getLeaderboard, getPlatformStats, getRecentTrades, getSectorAnalytics } from '../utils/api';
import { formatCurrency, formatPercentage, formatDate, getReturnColor, getPerformanceScoreColor } from '../utils/formatters';
import { StatsCard, ChartCard, DonutChart, Legend, Button, Select, SelectOption } from '../components/ui';

const EnhancedDashboard = () => {
 const [stats, setStats] = useState(null);
 const [topTraders, setTopTraders] = useState([]);
 const [recentTrades, setRecentTrades] = useState([]);
 const [sectorData, setSectorData] = useState(null);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [selectedTimeframe, setSelectedTimeframe] = useState('365d');
 const [sortField, setSortField] = useState('performance_score');
 const [sortDirection, setSortDirection] = useState('desc');
 const [sectorSortField, setSectorSortField] = useState('total_volume');
 const [sectorSortDirection, setSectorSortDirection] = useState('desc');

 // Sort sectors function
 const sortSectors = (field) => {
  if (sectorSortField === field) {
   setSectorSortDirection(sectorSortDirection === 'asc' ? 'desc' : 'asc');
  } else {
   setSectorSortField(field);
   setSectorSortDirection('desc');
  }
 };

 // Get sorted sectors
 const getSortedSectors = () => {
  if (!sectorData?.top_sectors) return [];
  
  return [...sectorData.top_sectors].sort((a, b) => {
   let aValue, bValue;
   
   switch (sectorSortField) {
    case 'total_volume':
     aValue = a.total_volume;
     bValue = b.total_volume;
     break;
    case 'trade_count':
     aValue = a.buy_count + a.sell_count;
     bValue = b.buy_count + b.sell_count;
     break;
    case 'buy_count':
     aValue = a.buy_count;
     bValue = b.buy_count;
     break;
    case 'sell_count':
     aValue = a.sell_count;
     bValue = b.sell_count;
     break;
    default:
     aValue = a.total_volume;
     bValue = b.total_volume;
   }
   
   if (sectorSortDirection === 'asc') {
    return aValue - bValue;
   } else {
    return bValue - aValue;
   }
  });
 };

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
    
    const [statsData, leaderboardData, tradesData, sectorAnalytics] = await Promise.all([
     getPlatformStats(),
     getLeaderboard(50, 1), // Get top 50 traders
     getRecentTrades(50, null, days), // Reasonable amount for loading
     getSectorAnalytics()
    ]);

    setStats(statsData);
    setTopTraders(leaderboardData);
    setRecentTrades(tradesData);
    setSectorData(sectorAnalytics);
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

  // Top performing sectors - limit to exactly 5
  const topSectors = Object.entries(sectorData)
   .sort(([,a], [,b]) => b.volume - a.volume)
   .slice(0, 5);

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
   // Technology
   'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'GOOG': 'Technology',
   'NVDA': 'Technology', 'META': 'Technology', 'NFLX': 'Technology', 'CRM': 'Technology',
   'ORCL': 'Technology', 'IBM': 'Technology', 'INTC': 'Technology', 'AMD': 'Technology',
   'ADBE': 'Technology', 'NOW': 'Technology', 'SNOW': 'Technology', 'PLTR': 'Technology',
   
   // Healthcare & Pharmaceuticals
   'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
   'MRK': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare', 'DHR': 'Healthcare',
   'BMY': 'Healthcare', 'AMGN': 'Healthcare', 'GILD': 'Healthcare', 'BIIB': 'Healthcare',
   
   // Financial Services
   'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial', 'GS': 'Financial',
   'MS': 'Financial', 'C': 'Financial', 'BRK': 'Financial', 'V': 'Financial',
   'MA': 'Financial', 'AXP': 'Financial', 'COF': 'Financial', 'USB': 'Financial',
   
   // Consumer & Retail
   'AMZN': 'Consumer', 'WMT': 'Consumer', 'HD': 'Consumer', 'PG': 'Consumer',
   'KO': 'Consumer', 'PEP': 'Consumer', 'NKE': 'Consumer', 'SBUX': 'Consumer',
   'MCD': 'Consumer', 'DIS': 'Consumer', 'COST': 'Consumer', 'TGT': 'Consumer',
   
   // Energy & Oil
   'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'SLB': 'Energy',
   'EOG': 'Energy', 'KMI': 'Energy', 'OKE': 'Energy', 'PSX': 'Energy',
   
   // Automotive & Transportation
   'TSLA': 'Automotive', 'F': 'Automotive', 'GM': 'Automotive', 'RIVN': 'Automotive',
   'LCID': 'Automotive', 'NIO': 'Automotive', 'UPS': 'Transportation', 'FDX': 'Transportation',
   
   // Industrial & Manufacturing
   'GE': 'Industrial', 'CAT': 'Industrial', 'BA': 'Industrial', 'MMM': 'Industrial',
   'HON': 'Industrial', 'UNP': 'Industrial', 'LMT': 'Industrial', 'RTX': 'Industrial',
   
   // Real Estate & REITs
   'AMT': 'Real Estate', 'PLD': 'Real Estate', 'CCI': 'Real Estate', 'EQIX': 'Real Estate',
   'SPG': 'Real Estate', 'O': 'Real Estate', 'WELL': 'Real Estate', 'AVB': 'Real Estate',
   
   // Telecommunications
   'VZ': 'Telecom', 'T': 'Telecom', 'TMUS': 'Telecom', 'CMCSA': 'Telecom',
   
   // Utilities
   'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities', 'D': 'Utilities'
  };
  
  // Try exact match first
  if (sectorMap[ticker]) return sectorMap[ticker];
  
  // Try to infer from ticker patterns for unknown tickers
  if (ticker.includes('TECH') || ticker.includes('SOFT') || ticker.includes('DATA')) return 'Technology';
  if (ticker.includes('BANK') || ticker.includes('FIN') || ticker.includes('CRED')) return 'Financial';
  if (ticker.includes('HEALTH') || ticker.includes('MED') || ticker.includes('PHARM')) return 'Healthcare';
  if (ticker.includes('ENERGY') || ticker.includes('OIL') || ticker.includes('GAS')) return 'Energy';
  if (ticker.includes('AUTO') || ticker.includes('CAR')) return 'Automotive';
  if (ticker.includes('REAL') || ticker.includes('REIT')) return 'Real Estate';
  
  return 'Other';
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
   className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider cursor-pointer select-none transition-colors duration-200"
   onClick={() => handleSort(field)}
  >
   <div className="flex items-center space-x-1">
    <span>{children}</span>
    {sortField === field && (
     sortDirection === 'desc' ? 
      <ChevronDownIcon className="h-4 w-4 text-primary" /> : 
      <ChevronUpIcon className="h-4 w-4 text-primary" />
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
   <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
    <p className="text-red-800 dark:text-red-200">{error}</p>
   </div>
  );
 }

 return (
  <div className="space-y-8">
   {/* Enhanced Header with Alerts */}
   <div className="flex justify-between items-start">
    <div>
     <h1 className="text-3xl font-bold text-primary">Insider Alpha Dashboard</h1>
     <p className="mt-2 text-secondary">
      Advanced insider trading analytics and market intelligence
     </p>
    </div>
    <div className="flex items-center space-x-4">
     <Button variant="primary" icon={BellIcon}>
      Alerts
     </Button>
     <Select
      value={selectedTimeframe}
      onChange={(e) => setSelectedTimeframe(e.target.value)}
      className="min-w-[150px]"
     >
      <SelectOption value="7d">Last 7 Days</SelectOption>
      <SelectOption value="30d">Last 30 Days</SelectOption>
      <SelectOption value="90d">Last 90 Days</SelectOption>
      <SelectOption value="180d">Last 6 Months</SelectOption>
      <SelectOption value="365d">Last Year</SelectOption>
      <SelectOption value="730d">Last 2 Years</SelectOption>
      <SelectOption value="all">All Time</SelectOption>
     </Select>
    </div>
   </div>

   {/* Ultra Compact Stats Cards */}
   {stats && (
    <div className="flex gap-2">
     <div className="bg-card/30 backdrop-blur-sm rounded-lg p-3 flex-1 border border-tertiary/50">
      <div className="text-center">
       <UsersIcon className="h-5 w-5 text-blue-400 mx-auto mb-2" />
       <p className="text-xs text-secondary font-medium mb-1">Active Insiders</p>
       <p className="text-sm font-bold text-white">{stats.active_traders}</p>
      </div>
     </div>
     
     <div className="bg-card/30 backdrop-blur-sm rounded-lg p-3 flex-1 border border-tertiary/50">
      <div className="text-center">
       <ChartBarIcon className="h-5 w-5 text-green-400 mx-auto mb-2" />
       <p className="text-xs text-secondary font-medium mb-1">Total Trades</p>
       <p className="text-sm font-bold text-white">{stats.total_trades.toLocaleString()}</p>
      </div>
     </div>
     
     <div className="bg-card/30 backdrop-blur-sm rounded-lg p-3 flex-1 border border-tertiary/50">
      <div className="text-center">
       <ArrowUpIcon className="h-5 w-5 text-purple-400 mx-auto mb-2" />
       <p className="text-xs text-secondary font-medium mb-1">Buy/Sell Ratio</p>
       <p className="text-sm font-bold text-white">{metrics.buySellRatio}</p>
      </div>
     </div>
     
     <div className="bg-card/30 backdrop-blur-sm rounded-lg p-3 flex-1 border border-tertiary/50">
      <div className="text-center">
       <CurrencyDollarIcon className="h-5 w-5 text-yellow-400 mx-auto mb-2" />
       <p className="text-xs text-secondary font-medium mb-1">Avg Trade Size</p>
       <p className="text-sm font-bold text-white">{formatCurrency(metrics.avgTradeSize || 0)}</p>
      </div>
     </div>

     <div className="bg-card/30 backdrop-blur-sm rounded-lg p-3 flex-1 border border-tertiary/50">
      <div className="text-center">
       <FireIcon className="h-5 w-5 text-orange-400 mx-auto mb-2" />
       <p className="text-xs text-secondary font-medium mb-1">Insider Sentiment</p>
       <p className="text-sm font-bold text-white">{`${sectorData?.insider_sentiment?.bullish_percentage || 0}%`}</p>
       <p className="text-xs text-tertiary mt-1">{`${(sectorData?.insider_sentiment?.buy_trades || 0).toLocaleString()} buys / ${(sectorData?.insider_sentiment?.sell_trades || 0).toLocaleString()} sells`}</p>
      </div>
     </div>
    </div>
   )}

   {/* Sectors Analysis - Filterable */}
   <ChartCard
    title="Sectors Analysis"
    icon={ChartBarIcon}
    iconColor="text-blue-400"
   >
    <div className="space-y-4">
     {/* Sectors Table */}
     <div className="overflow-x-auto">
      <table className="w-full">
       <thead>
        <tr className="border-b border-tertiary">
         <th className="text-left py-3 px-2 text-xs font-medium text-secondary uppercase tracking-wider">Sector</th>
         <th 
          className="text-right py-3 px-2 text-xs font-medium text-secondary uppercase tracking-wider cursor-pointer transition-colors"
          onClick={() => sortSectors('total_volume')}
         >
          Volume {sectorSortField === 'total_volume' && (sectorSortDirection === 'desc' ? '↓' : '↑')}
         </th>
         <th 
          className="text-right py-3 px-2 text-xs font-medium text-secondary uppercase tracking-wider cursor-pointer transition-colors"
          onClick={() => sortSectors('trade_count')}
         >
          Trades {sectorSortField === 'trade_count' && (sectorSortDirection === 'desc' ? '↓' : '↑')}
         </th>
         <th 
          className="text-right py-3 px-2 text-xs font-medium text-secondary uppercase tracking-wider cursor-pointer transition-colors"
          onClick={() => sortSectors('buy_count')}
         >
          Buys {sectorSortField === 'buy_count' && (sectorSortDirection === 'desc' ? '↓' : '↑')}
         </th>
         <th 
          className="text-right py-3 px-2 text-xs font-medium text-secondary uppercase tracking-wider cursor-pointer transition-colors"
          onClick={() => sortSectors('sell_count')}
         >
          Sells {sectorSortField === 'sell_count' && (sectorSortDirection === 'desc' ? '↓' : '↑')}
         </th>
        </tr>
       </thead>
       <tbody>
        {getSortedSectors().map((sector, index) => (
         <tr key={sector.sector} className="border-b border-tertiary transition-colors">
          <td className="py-3 px-2">
           <span className="text-sm font-medium text-primary">{sector.sector}</span>
          </td>
          <td className="py-3 px-2 text-right">
           <div className="text-sm font-semibold text-primary">{formatCurrency(sector.total_volume)}</div>
          </td>
          <td className="py-3 px-2 text-right">
           <div className="text-sm text-primary">{(sector.buy_count + sector.sell_count).toLocaleString()}</div>
          </td>
          <td className="py-3 px-2 text-right">
           <div className="text-sm text-green-400">+{sector.buy_count.toLocaleString()}</div>
          </td>
          <td className="py-3 px-2 text-right">
           <div className="text-sm text-red-400">-{sector.sell_count.toLocaleString()}</div>
          </td>
         </tr>
        )) || (
         <tr>
          <td colSpan="5" className="text-center text-secondary py-8">
           <ChartBarIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
           <p>No sector data available</p>
          </td>
         </tr>
        )}
       </tbody>
      </table>
     </div>

     {/* Summary Stats */}
     <div className="mt-4 pt-4 border-t border-tertiary">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
       <div className="text-center">
        <div className="text-xs text-secondary">Total Volume</div>
        <div className="text-lg font-semibold text-primary">
         {formatCurrency(sectorData?.top_sectors?.reduce((sum, s) => sum + s.total_volume, 0) || 0)}
        </div>
       </div>
       <div className="text-center">
        <div className="text-xs text-secondary">Total Trades</div>
        <div className="text-lg font-semibold text-primary">
         {sectorData?.top_sectors?.reduce((sum, s) => sum + s.buy_count + s.sell_count, 0)?.toLocaleString() || '0'}
        </div>
       </div>
       <div className="text-center">
        <div className="text-xs text-secondary">Total Buys</div>
        <div className="text-lg font-semibold text-green-400">
         {sectorData?.top_sectors?.reduce((sum, s) => sum + s.buy_count, 0)?.toLocaleString() || '0'}
        </div>
       </div>
       <div className="text-center">
        <div className="text-xs text-secondary">Total Sells</div>
        <div className="text-lg font-semibold text-red-400">
         {sectorData?.top_sectors?.reduce((sum, s) => sum + s.sell_count, 0)?.toLocaleString() || '0'}
        </div>
       </div>
      </div>
     </div>
    </div>
   </ChartCard>

   {/* Enhanced Top Performers with Conviction Scores */}
   <div className="bg-secondary border border-default shadow-lg rounded-lg transition-colors duration-300">
    <div className="px-4 py-5 sm:p-6">
     <div className="flex items-center justify-between mb-4">
      <h2 className="text-lg font-medium text-primary">Top Performers by Conviction Score</h2>
      <Link to="/leaderboard" className="text-brand-600 text-sm font-medium">
       View full leaderboard →
      </Link>
     </div>
     
     <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-default">
       <thead className="bg-tertiary">
        <tr>
         <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Rank</th>
         <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Insider</th>
         <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Company</th>
         <SortableHeader field="performance_score">Conviction</SortableHeader>
         <SortableHeader field="avg_return_90d">90d Return</SortableHeader>
         <SortableHeader field="win_rate">Win Rate</SortableHeader>
         <SortableHeader field="total_profit_loss">Total P&L</SortableHeader>
         <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Actions</th>
        </tr>
       </thead>
       <tbody className="bg-secondary divide-y divide-default">
        {getSortedTraders().slice(0, 10).map((trader, index) => (
         <tr key={trader.trader_id}>
          <td className="px-6 py-4 whitespace-nowrap">
           <div className="flex items-center">
            <span className="text-sm font-medium text-primary">#{index + 1}</span>
            {index < 3 && (
             <FireIcon className={`ml-2 h-4 w-4 ${
              index === 0 ? 'text-yellow-500' : 
              index === 1 ? 'text-tertiary' : 'text-orange'
             }`} />
            )}
           </div>
          </td>
          <td className="px-6 py-4 whitespace-nowrap">
           <div>
            <Link
             to={`/traders/${trader.trader_id}`}
             className="text-sm font-medium text-brand-600 "
            >
             {trader.name}
            </Link>
            <div className="text-sm text-secondary">{trader.title}</div>
           </div>
          </td>
          <td className="px-6 py-4 whitespace-nowrap">
           <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
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
          <td className="px-6 py-4 whitespace-nowrap text-sm text-primary">
           <div className="flex items-center">
            <span>{formatPercentage(trader.win_rate)}</span>
            <div className="ml-2 w-16 bg-tertiary rounded-full h-2">
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
          <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary">
           <div className="flex items-center space-x-2">
            <button className="text-brand-600">
             <EyeIcon className="h-4 w-4" />
            </button>
            <button className="text-secondary">
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
