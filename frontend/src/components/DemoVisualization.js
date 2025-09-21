import React from 'react';
import { ChartBarIcon, ArrowTrendingUpIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';

const DemoVisualization = () => {
  return (
    <div className="relative">
      {/* Main Dashboard Mockup */}
      <div className="bg-secondary rounded-2xl p-6 border border-default shadow-2xl">
        <div className="grid grid-cols-3 gap-4 mb-6">
          {/* Mini stat cards */}
          <div className="bg-tertiary rounded-lg p-3 text-center">
            <ArrowTrendingUpIcon className="h-6 w-6 text-green-500 mx-auto mb-1" />
            <div className="text-lg font-bold text-primary">+24%</div>
            <div className="text-xs text-secondary">Returns</div>
          </div>
          <div className="bg-tertiary rounded-lg p-3 text-center">
            <ChartBarIcon className="h-6 w-6 text-blue-500 mx-auto mb-1" />
            <div className="text-lg font-bold text-primary">419K</div>
            <div className="text-xs text-secondary">Trades</div>
          </div>
          <div className="bg-tertiary rounded-lg p-3 text-center">
            <CurrencyDollarIcon className="h-6 w-6 text-purple-500 mx-auto mb-1" />
            <div className="text-lg font-bold text-primary">94%</div>
            <div className="text-xs text-secondary">Accuracy</div>
          </div>
        </div>

        {/* Chart Area */}
        <div className="bg-tertiary rounded-lg p-4 h-32 flex items-end justify-between">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="bg-gradient-to-t from-blue-500 to-purple-600 rounded-sm"
              style={{
                width: '8px',
                height: `${Math.random() * 80 + 20}%`,
                animation: `float 3s ease-in-out infinite`,
                animationDelay: `${i * 0.2}s`
              }}
            />
          ))}
        </div>

        {/* Trade List */}
        <div className="mt-4 space-y-2">
          {[
            { name: 'Tim Cook', action: 'BUY', amount: '$2.4M', change: '+12%' },
            { name: 'Elon Musk', action: 'SELL', amount: '$1.8M', change: '-5%' },
            { name: 'Jeff Bezos', action: 'BUY', amount: '$3.1M', change: '+18%' }
          ].map((trade, i) => (
            <div key={i} className="flex items-center justify-between bg-tertiary rounded-lg p-2 text-xs">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${trade.action === 'BUY' ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-primary font-medium">{trade.name}</span>
                <span className={`px-2 py-1 rounded ${trade.action === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {trade.action}
                </span>
              </div>
              <div className="text-right">
                <div className="text-primary font-bold">{trade.amount}</div>
                <div className={`${trade.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                  {trade.change}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Floating Elements */}
      <div className="absolute -top-2 -right-2 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold float-animation">
        Live
      </div>
      <div className="absolute -bottom-2 -left-2 bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-semibold float-animation" style={{animationDelay: '1s'}}>
        Real-time
      </div>
    </div>
  );
};

export default DemoVisualization;
