import React, { useState, useEffect } from 'react';
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon, 
  FireIcon,
  BoltIcon,
  ChartBarIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';
import { getLeaderboard, getRecentTrades } from '../utils/api';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const RiskProfiles = () => {
  const [riskData, setRiskData] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRiskData = async () => {
      try {
        setLoading(true);
        
        const [tradersData, tradesData] = await Promise.all([
          getLeaderboard(200, 5), // Top 200 with at least 5 trades
          getRecentTrades(3000, null, 730) // 2 years of trades
        ]);

        const riskAnalysis = analyzeRiskProfiles(tradersData, tradesData);
        setRiskData(riskAnalysis);
        
      } catch (error) {
        console.error('Error fetching risk data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRiskData();
  }, []);

  const analyzeRiskProfiles = (traders, trades) => {
    // Create comprehensive risk profiles for each trader
    const riskProfiles = traders.map(trader => {
      const traderTrades = trades.filter(t => t.trader_name === trader.name);
      
      if (traderTrades.length < 3) return null;

      // Calculate risk metrics
      const tradeSizes = traderTrades.map(t => t.total_value);
      const avgTradeSize = tradeSizes.reduce((sum, size) => sum + size, 0) / tradeSizes.length;
      const maxTradeSize = Math.max(...tradeSizes);
      const minTradeSize = Math.min(...tradeSizes);
      
      // Trade size consistency (lower = more consistent)
      const tradeSizeVariance = calculateVariance(tradeSizes);
      const consistencyScore = 100 - Math.min((tradeSizeVariance / avgTradeSize) * 100, 100);
      
      // Trading frequency
      const daysBetweenTrades = calculateDaysBetweenTrades(traderTrades);
      const avgDaysBetween = daysBetweenTrades.reduce((sum, days) => sum + days, 0) / daysBetweenTrades.length;
      
      // Risk tolerance indicators
      const largeTradeCount = traderTrades.filter(t => t.total_value > avgTradeSize * 2).length;
      const riskTolerance = (largeTradeCount / traderTrades.length) * 100;
      
      // Market timing (simplified)
      const recentTrades = traderTrades.filter(t => {
        const tradeDate = new Date(t.transaction_date);
        const sixMonthsAgo = new Date();
        sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
        return tradeDate > sixMonthsAgo;
      });
      
      const marketTimingScore = recentTrades.length > 0 ? 
        (recentTrades.filter(t => t.transaction_type === 'BUY').length / recentTrades.length) * 100 : 50;

      // Overall risk classification
      const riskClass = classifyRiskProfile(consistencyScore, riskTolerance, avgTradeSize, trader.win_rate);

      return {
        ...trader,
        riskMetrics: {
          avgTradeSize,
          maxTradeSize,
          minTradeSize,
          consistencyScore,
          avgDaysBetween,
          riskTolerance,
          marketTimingScore,
          tradeCount: traderTrades.length
        },
        riskClass
      };
    }).filter(profile => profile !== null);

    // Group by risk class
    const riskGroups = {
      'Conservative': riskProfiles.filter(p => p.riskClass === 'Conservative'),
      'Moderate': riskProfiles.filter(p => p.riskClass === 'Moderate'),
      'Aggressive': riskProfiles.filter(p => p.riskClass === 'Aggressive'),
      'High-Risk': riskProfiles.filter(p => p.riskClass === 'High-Risk')
    };

    return {
      riskProfiles: riskProfiles.sort((a, b) => b.performance_score - a.performance_score),
      riskGroups,
      summary: {
        totalAnalyzed: riskProfiles.length,
        avgConsistency: riskProfiles.reduce((sum, p) => sum + p.riskMetrics.consistencyScore, 0) / riskProfiles.length,
        avgRiskTolerance: riskProfiles.reduce((sum, p) => sum + p.riskMetrics.riskTolerance, 0) / riskProfiles.length
      }
    };
  };

  const calculateVariance = (values) => {
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
    return squaredDiffs.reduce((sum, diff) => sum + diff, 0) / values.length;
  };

  const calculateDaysBetweenTrades = (trades) => {
    if (trades.length < 2) return [0];
    
    const sortedTrades = trades.sort((a, b) => new Date(a.transaction_date) - new Date(b.transaction_date));
    const daysBetween = [];
    
    for (let i = 1; i < sortedTrades.length; i++) {
      const prevDate = new Date(sortedTrades[i-1].transaction_date);
      const currDate = new Date(sortedTrades[i].transaction_date);
      const diffDays = Math.abs((currDate - prevDate) / (1000 * 60 * 60 * 24));
      daysBetween.push(diffDays);
    }
    
    return daysBetween;
  };

  const classifyRiskProfile = (consistency, riskTolerance, avgTradeSize, winRate) => {
    // Sophisticated risk classification algorithm
    if (consistency > 70 && riskTolerance < 20 && avgTradeSize < 1000000) {
      return 'Conservative';
    } else if (consistency > 50 && riskTolerance < 40 && winRate > 60) {
      return 'Moderate';
    } else if (riskTolerance > 40 || avgTradeSize > 5000000) {
      return 'Aggressive';
    } else {
      return 'High-Risk';
    }
  };

  const getRiskColor = (riskClass) => {
    const colors = {
      'Conservative': 'text-green-600 bg-green-100',
      'Moderate': 'text-blue-600 bg-blue-100', 
      'Aggressive': 'text-yellow-600 bg-yellow-100',
      'High-Risk': 'text-red-600 bg-red-100'
    };
    return colors[riskClass] || 'text-gray-600 bg-gray-100';
  };

  const getRiskIcon = (riskClass) => {
    const icons = {
      'Conservative': ShieldCheckIcon,
      'Moderate': ChartBarIcon,
      'Aggressive': BoltIcon,
      'High-Risk': FireIcon
    };
    return icons[riskClass] || ShieldCheckIcon;
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
        <h1 className="text-3xl font-bold text-gray-900">Insider Risk Profiles</h1>
        <p className="mt-2 text-gray-600">
          Behavioral analysis and risk classification of corporate insiders
        </p>
      </div>

      {/* Risk Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {Object.entries(riskData.riskGroups || {}).map(([riskClass, traders]) => {
          const Icon = getRiskIcon(riskClass);
          return (
            <div key={riskClass} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <Icon className={`h-6 w-6 ${getRiskColor(riskClass).split(' ')[0]}`} />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-500">{riskClass}</p>
                    <p className="text-lg font-semibold text-gray-900">{traders.length}</p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Risk Profile Details */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Detailed Risk Profiles
          </h3>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Insider
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk Class
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Consistency
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Trade Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Risk Tolerance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Frequency
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {riskData.riskProfiles?.slice(0, 50).map((profile) => (
                  <tr key={profile.trader_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{profile.name}</div>
                        <div className="text-sm text-gray-500">{profile.company_ticker}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(profile.riskClass)}`}>
                        {profile.riskClass}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <div className="flex items-center">
                        <span>{profile.riskMetrics?.consistencyScore?.toFixed(1)}%</span>
                        <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${profile.riskMetrics?.consistencyScore || 0}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(profile.riskMetrics?.avgTradeSize || 0)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {profile.riskMetrics?.riskTolerance?.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {profile.riskMetrics?.avgDaysBetween?.toFixed(0)} days
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className={`${profile.performance_score > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {profile.performance_score?.toFixed(1) || 'N/A'}
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

export default RiskProfiles;
