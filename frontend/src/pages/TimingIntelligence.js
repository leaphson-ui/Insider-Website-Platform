import React, { useState, useEffect } from 'react';
import { 
  ClockIcon, 
  CalendarIcon, 
  ArrowUpIcon,
  ExclamationTriangleIcon,
  BoltIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { getTimingAnalysis } from '../utils/api';
import { formatCurrency, formatDate, formatPercentage } from '../utils/formatters';

const TimingIntelligence = () => {
  const [timingData, setTimingData] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedAnalysis, setSelectedAnalysis] = useState('day-patterns');

  useEffect(() => {
    const fetchTimingData = async () => {
      try {
        setLoading(true);
        
        const timingAnalysis = await getTimingAnalysis();
        setTimingData(timingAnalysis);
        
      } catch (error) {
        console.error('Error fetching timing data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTimingData();
  }, []);

  const analyzeTimingPatterns = (trades, traders) => {
    // 1. Day of Week Analysis
    const dayPatterns = analyzeDayPatterns(trades);
    
    // 2. Month/Season Analysis  
    const seasonalPatterns = analyzeSeasonalPatterns(trades);
    
    // 3. Market Event Timing
    const marketEventTiming = analyzeMarketEventTiming(trades);
    
    // 4. Insider Timing Consistency
    const timingConsistency = analyzeTimingConsistency(trades, traders);
    
    // 5. Pre-Earnings Activity
    const earningsActivity = analyzeEarningsActivity(trades);

    return {
      dayPatterns,
      seasonalPatterns,
      marketEventTiming,
      timingConsistency,
      earningsActivity
    };
  };

  const analyzeDayPatterns = (trades) => {
    const dayData = {};
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    // Initialize days
    dayNames.forEach(day => {
      dayData[day] = {
        totalTrades: 0,
        totalVolume: 0,
        buyTrades: 0,
        sellTrades: 0,
        avgTradeSize: 0,
        topPerformers: []
      };
    });

    trades.forEach(trade => {
      const date = new Date(trade.transaction_date);
      const dayName = dayNames[date.getDay()];
      
      dayData[dayName].totalTrades++;
      dayData[dayName].totalVolume += trade.total_value;
      
      if (trade.transaction_type === 'BUY') {
        dayData[dayName].buyTrades++;
      } else if (trade.transaction_type === 'SELL') {
        dayData[dayName].sellTrades++;
      }
    });

    // Calculate averages
    Object.keys(dayData).forEach(day => {
      if (dayData[day].totalTrades > 0) {
        dayData[day].avgTradeSize = dayData[day].totalVolume / dayData[day].totalTrades;
      }
    });

    return dayData;
  };

  const analyzeSeasonalPatterns = (trades) => {
    const monthData = {};
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    monthNames.forEach(month => {
      monthData[month] = {
        totalTrades: 0,
        totalVolume: 0,
        buyVsSellRatio: 0,
        avgPerformance: 0
      };
    });

    trades.forEach(trade => {
      const date = new Date(trade.transaction_date);
      const monthName = monthNames[date.getMonth()];
      
      monthData[monthName].totalTrades++;
      monthData[monthName].totalVolume += trade.total_value;
    });

    return monthData;
  };

  const analyzeMarketEventTiming = (trades) => {
    // Define major market events (you could expand this with real market data)
    const marketEvents = [
      { date: '2020-03-01', event: 'COVID Market Crash', type: 'crash' },
      { date: '2020-04-01', event: 'COVID Recovery Start', type: 'recovery' },
      { date: '2021-01-01', event: 'Meme Stock Surge', type: 'bubble' },
      { date: '2022-01-01', event: 'Fed Rate Hikes Begin', type: 'correction' },
      { date: '2023-01-01', event: 'AI Boom Start', type: 'rally' }
    ];

    const eventAnalysis = marketEvents.map(event => {
      const eventDate = new Date(event.date);
      const beforeWindow = new Date(eventDate.getTime() - 30 * 24 * 60 * 60 * 1000); // 30 days before
      const afterWindow = new Date(eventDate.getTime() + 30 * 24 * 60 * 60 * 1000); // 30 days after

      const tradesBeforeEvent = trades.filter(trade => {
        const tradeDate = new Date(trade.transaction_date);
        return tradeDate >= beforeWindow && tradeDate <= eventDate;
      });

      const tradesAfterEvent = trades.filter(trade => {
        const tradeDate = new Date(trade.transaction_date);
        return tradeDate > eventDate && tradeDate <= afterWindow;
      });

      return {
        ...event,
        tradesBeforeCount: tradesBeforeEvent.length,
        tradesAfterCount: tradesAfterEvent.length,
        volumeBefore: tradesBeforeEvent.reduce((sum, t) => sum + t.total_value, 0),
        volumeAfter: tradesAfterEvent.reduce((sum, t) => sum + t.total_value, 0),
        buysBefore: tradesBeforeEvent.filter(t => t.transaction_type === 'BUY').length,
        sellsBefore: tradesBeforeEvent.filter(t => t.transaction_type === 'SELL').length
      };
    });

    return eventAnalysis;
  };

  const analyzeTimingConsistency = (trades, traders) => {
    // Analyze which insiders have consistent timing patterns
    const insiderTiming = {};

    trades.forEach(trade => {
      if (!insiderTiming[trade.trader_name]) {
        insiderTiming[trade.trader_name] = {
          trades: [],
          avgDayOfWeek: 0,
          preferredMonth: null,
          timingScore: 0
        };
      }
      insiderTiming[trade.trader_name].trades.push(trade);
    });

    // Calculate timing patterns for each insider
    const timingAnalysis = Object.entries(insiderTiming)
      .filter(([name, data]) => data.trades.length >= 5) // Need enough trades for pattern
      .map(([name, data]) => {
        const days = data.trades.map(t => new Date(t.transaction_date).getDay());
        const months = data.trades.map(t => new Date(t.transaction_date).getMonth());
        
        // Find most common day and month
        const dayFreq = days.reduce((acc, day) => {
          acc[day] = (acc[day] || 0) + 1;
          return acc;
        }, {});
        
        const monthFreq = months.reduce((acc, month) => {
          acc[month] = (acc[month] || 0) + 1;
          return acc;
        }, {});

        const mostCommonDay = Object.entries(dayFreq).sort(([,a], [,b]) => b - a)[0];
        const mostCommonMonth = Object.entries(monthFreq).sort(([,a], [,b]) => b - a)[0];

        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        return {
          name,
          tradeCount: data.trades.length,
          preferredDay: dayNames[mostCommonDay[0]],
          dayConsistency: (mostCommonDay[1] / data.trades.length) * 100,
          preferredMonth: monthNames[mostCommonMonth[0]],
          monthConsistency: (mostCommonMonth[1] / data.trades.length) * 100,
          avgTradeSize: data.trades.reduce((sum, t) => sum + t.total_value, 0) / data.trades.length
        };
      })
      .sort((a, b) => b.dayConsistency - a.dayConsistency)
      .slice(0, 20);

    return timingAnalysis;
  };

  const analyzeEarningsActivity = (trades) => {
    // Simplified earnings analysis - in reality you'd integrate with earnings calendar
    const quarterEndMonths = [3, 6, 9, 12]; // March, June, September, December
    
    const earningsRelatedTrades = trades.filter(trade => {
      const date = new Date(trade.transaction_date);
      const month = date.getMonth() + 1;
      const dayOfMonth = date.getDate();
      
      // Look for trades in the 2 weeks before quarter end
      return quarterEndMonths.includes(month) && dayOfMonth <= 15;
    });

    const earningsAnalysis = {
      totalEarningsSeasonTrades: earningsRelatedTrades.length,
      earningsSeasonVolume: earningsRelatedTrades.reduce((sum, t) => sum + t.total_value, 0),
      earningsVsRegularRatio: earningsRelatedTrades.length / Math.max(trades.length - earningsRelatedTrades.length, 1),
      topEarningsTraders: {}
    };

    return earningsAnalysis;
  };

  const renderAnalysisContent = () => {
    switch(selectedAnalysis) {
      case 'day-patterns':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Day of Week Trading Patterns
            </h3>
            {timingData.day_patterns?.map((dayData, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="font-medium text-gray-900">{dayData.day_name}</h4>
                  <span className="text-sm text-gray-500">
                    {dayData.trade_count} trades
                  </span>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Total Volume</span>
                    <p className="font-medium">{formatCurrency(dayData.total_volume)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Avg Trade Size</span>
                    <p className="font-medium">{formatCurrency(dayData.avg_trade_size)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Buys</span>
                    <p className="font-medium text-green-600">{dayData.buy_count}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Sells</span>
                    <p className="font-medium text-red-600">{dayData.sell_count}</p>
                  </div>
                </div>

                {/* Visual bar for trade volume */}
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-brand-500 h-2 rounded-full" 
                      style={{ 
                        width: `${Math.min((dayData.total_volume / Math.max(...(timingData.day_patterns || []).map(d => d.total_volume))) * 100, 100)}%` 
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'timing-consistency':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Most Consistent Insider Timing Patterns
            </h3>
            {timingData.timing_consistency?.map((insider, index) => (
              <div key={insider.name} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-medium text-gray-900">{insider.name}</h4>
                    <p className="text-sm text-gray-500">{insider.trade_count} trades analyzed</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      Avg Size: {formatCurrency(insider.avg_trade_size)}
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Preferred Day</span>
                    <div className="flex items-center">
                      <span className="font-medium">
                        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][insider.preferred_day] || 'N/A'}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500">Preferred Month</span>
                    <div className="flex items-center">
                      <span className="font-medium">
                        {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][insider.preferred_month - 1] || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Performance indicator */}
                <div className="mt-3">
                  <div className="text-xs text-gray-500">
                    Performance Score: <span className="font-medium">{insider.performance_score?.toFixed(1) || 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      case 'market-events':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Insider Activity Around Market Events
            </h3>
            {timingData.market_events?.map((event, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-medium text-gray-900">{event.event}</h4>
                    <p className="text-sm text-gray-500">{formatDate(event.date)}</p>
                  </div>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    event.type === 'crash' ? 'bg-red-100 text-red-800' :
                    event.type === 'rally' ? 'bg-green-100 text-green-800' :
                    event.type === 'recovery' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {event.type}
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Trades Before</span>
                    <p className="font-medium">{event.tradesBeforeCount}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Trades After</span>
                    <p className="font-medium">{event.tradesAfterCount}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Volume Before</span>
                    <p className="font-medium">{formatCurrency(event.volumeBefore)}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Buy/Sell Before</span>
                    <p className="font-medium">
                      <span className="text-green-600">{event.buysBefore}</span>
                      {' / '}
                      <span className="text-red-600">{event.sellsBefore}</span>
                    </p>
                  </div>
                </div>

                {/* Sentiment indicator */}
                <div className="mt-3">
                  <div className="flex items-center">
                    {event.buysBefore > event.sellsBefore ? (
                      <div className="flex items-center text-green-600">
                        <ArrowUpIcon className="h-4 w-4 mr-1" />
                        <span className="text-xs">Insiders were bullish before event</span>
                      </div>
                    ) : (
                      <div className="flex items-center text-red-600">
                        <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                        <span className="text-xs">Insiders were cautious before event</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        );

      default:
        return <div>Select an analysis type</div>;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-brand-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Timing Intelligence</h1>
        <p className="mt-2 text-gray-600">
          Advanced behavioral analysis of insider trading timing and patterns
        </p>
      </div>

      {/* Analysis Type Selector */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'day-patterns', name: 'Day Patterns', icon: CalendarIcon },
              { id: 'timing-consistency', name: 'Timing Consistency', icon: ClockIcon },
              { id: 'market-events', name: 'Market Events', icon: BoltIcon }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedAnalysis(tab.id)}
                  className={`${
                    selectedAnalysis === tab.id
                      ? 'border-brand-500 text-brand-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {renderAnalysisContent()}
        </div>
      </div>
    </div>
  );
};

export default TimingIntelligence;
