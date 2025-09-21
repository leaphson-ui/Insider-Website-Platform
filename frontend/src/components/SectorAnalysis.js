import React from 'react';
import { 
  BuildingOfficeIcon, 
  ArrowUpIcon, 
  ArrowDownIcon 
} from '@heroicons/react/24/outline';
import { formatCurrency } from '../utils/formatters';

const SectorAnalysis = ({ trades = [] }) => {
  // Group trades by sector
  const getSectorFromTicker = (ticker) => {
    const sectorMap = {
      'AAPL': 'Technology',
      'MSFT': 'Technology', 
      'GOOGL': 'Technology',
      'NVDA': 'Technology',
      'META': 'Technology',
      'TSLA': 'Automotive',
      'AMZN': 'E-commerce',
      'JPM': 'Financial',
      'BAC': 'Financial',
      'JNJ': 'Healthcare',
      'PFE': 'Healthcare',
      'XOM': 'Energy',
      'CVX': 'Energy'
    };
    return sectorMap[ticker] || 'Other';
  };

  const sectorData = trades.reduce((acc, trade) => {
    const sector = getSectorFromTicker(trade.company_ticker);
    
    if (!acc[sector]) {
      acc[sector] = {
        buys: 0,
        sells: 0,
        totalVolume: 0,
        trades: [],
        netFlow: 0
      };
    }
    
    acc[sector].trades.push(trade);
    acc[sector].totalVolume += trade.total_value;
    
    if (trade.transaction_type === 'BUY') {
      acc[sector].buys++;
      acc[sector].netFlow += trade.total_value;
    } else if (trade.transaction_type === 'SELL') {
      acc[sector].sells++;
      acc[sector].netFlow -= trade.total_value;
    }
    
    return acc;
  }, {});

  // Sort sectors by volume
  const sortedSectors = Object.entries(sectorData)
    .sort(([,a], [,b]) => b.totalVolume - a.totalVolume)
    .slice(0, 8);

  const getSectorColor = (sector) => {
    const colors = {
      'Technology': 'bg-blue-500',
      'Healthcare': 'bg-green-500',
      'Financial': 'bg-yellow-500',
      'Energy': 'bg-red-500',
      'Automotive': 'bg-purple-500',
      'E-commerce': 'bg-orange-500',
      'Other': 'bg-gray-500'
    };
    return colors[sector] || 'bg-gray-500';
  };

  const getSentiment = (data) => {
    if (data.netFlow > 0) return { text: 'Bullish', color: 'text-green-600', icon: ArrowUpIcon };
    if (data.netFlow < 0) return { text: 'Bearish', color: 'text-red-600', icon: ArrowDownIcon };
    return { text: 'Neutral', color: 'text-gray-600', icon: BuildingOfficeIcon };
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-medium text-gray-900">Sector Analysis</h3>
        <BuildingOfficeIcon className="h-5 w-5 text-gray-400" />
      </div>

      <div className="space-y-4">
        {sortedSectors.map(([sector, data]) => {
          const sentiment = getSentiment(data);
          const SentimentIcon = sentiment.icon;
          
          return (
            <div key={sector} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center">
                  <div className={`w-3 h-3 rounded-full ${getSectorColor(sector)} mr-3`}></div>
                  <h4 className="text-sm font-medium text-gray-900">{sector}</h4>
                </div>
                <div className="flex items-center">
                  <SentimentIcon className={`h-4 w-4 mr-1 ${sentiment.color}`} />
                  <span className={`text-sm ${sentiment.color}`}>{sentiment.text}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Total Volume</span>
                  <p className="font-medium">{formatCurrency(data.totalVolume)}</p>
                </div>
                <div>
                  <span className="text-gray-500">Net Flow</span>
                  <p className={`font-medium ${data.netFlow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(Math.abs(data.netFlow))}
                  </p>
                </div>
                <div>
                  <span className="text-gray-500">Buys</span>
                  <p className="font-medium text-green-600">{data.buys}</p>
                </div>
                <div>
                  <span className="text-gray-500">Sells</span>
                  <p className="font-medium text-red-600">{data.sells}</p>
                </div>
              </div>

              {/* Activity Bar */}
              <div className="mt-3">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Buy Activity</span>
                  <span>Sell Activity</span>
                </div>
                <div className="flex h-2 rounded-full overflow-hidden bg-gray-200">
                  <div 
                    className="bg-green-500"
                    style={{ width: `${(data.buys / (data.buys + data.sells)) * 100}%` }}
                  ></div>
                  <div 
                    className="bg-red-500"
                    style={{ width: `${(data.sells / (data.buys + data.sells)) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {sortedSectors.length === 0 && (
        <div className="text-center py-8">
          <BuildingOfficeIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No sector data</h3>
          <p className="mt-1 text-sm text-gray-500">
            Sector analysis will appear when trade data is available.
          </p>
        </div>
      )}
    </div>
  );
};

export default SectorAnalysis;
