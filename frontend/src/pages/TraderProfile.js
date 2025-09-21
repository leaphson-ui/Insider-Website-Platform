import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  CurrencyDollarIcon, 
  BuildingOfficeIcon,
  ChartPieIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';
import { getTrader, getTraderHoldings } from '../utils/api';
import { formatCurrency, formatPercentage, formatDate, getReturnColor, getPerformanceScoreColor } from '../utils/formatters';

const TraderProfile = () => {
  const { traderId } = useParams();
  const [trader, setTrader] = useState(null);
  const [holdings, setHoldings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [traderData, holdingsData] = await Promise.all([
          getTrader(traderId),
          getTraderHoldings(traderId)
        ]);
        setTrader(traderData);
        setHoldings(holdingsData);
        setError(null);
      } catch (err) {
        console.error('Error fetching trader data:', err);
        setError(err.response?.status === 404 ? 'Trader not found' : 'Failed to load trader data');
      } finally {
        setLoading(false);
      }
    };

    if (traderId) {
      fetchData();
    }
  }, [traderId]);

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

  if (!trader) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <p className="text-yellow-800">Trader not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{trader.name}</h1>
            <p className="mt-1 text-lg text-gray-600">{trader.title}</p>
            <p className="mt-1 text-sm text-gray-500">
              {trader.relationship_to_company} at {trader.company_name} ({trader.company_ticker})
            </p>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getPerformanceScoreColor(trader.performance_score)}`}>
              {trader.performance_score?.toFixed(1) || 'N/A'}
            </div>
            <div className="text-sm text-gray-500">Performance Score</div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Trades
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {trader.total_trades}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Win Rate
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatPercentage(trader.win_rate)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    90d Avg Return
                  </dt>
                  <dd className={`text-lg font-medium ${getReturnColor(trader.avg_return_90d)}`}>
                    {formatPercentage(trader.avg_return_90d)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total P&L
                  </dt>
                  <dd className={`text-lg font-medium ${getReturnColor(trader.total_profit_loss)}`}>
                    {formatCurrency(trader.total_profit_loss)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Return Breakdown */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Return Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className={`text-2xl font-bold ${getReturnColor(trader.avg_return_30d)}`}>
              {formatPercentage(trader.avg_return_30d)}
            </div>
            <div className="text-sm text-gray-500">30-Day Average</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${getReturnColor(trader.avg_return_90d)}`}>
              {formatPercentage(trader.avg_return_90d)}
            </div>
            <div className="text-sm text-gray-500">90-Day Average</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${getReturnColor(trader.avg_return_1y)}`}>
              {formatPercentage(trader.avg_return_1y)}
            </div>
            <div className="text-sm text-gray-500">1-Year Average</div>
          </div>
        </div>
      </div>

      {/* Holdings Dashboard */}
      {holdings && (
        <div className="space-y-6">
          {/* Portfolio Summary */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900">Current Holdings Portfolio</h2>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(holdings.total_portfolio_value)}
                </div>
                <div className="text-sm text-gray-500">Total Portfolio Value</div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <BuildingOfficeIcon className="h-6 w-6 text-blue-500 mr-3" />
                  <div>
                    <div className="text-lg font-semibold text-gray-900">
                      {holdings.holdings.length}
                    </div>
                    <div className="text-sm text-gray-500">Companies Held</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <ChartPieIcon className="h-6 w-6 text-purple-500 mr-3" />
                  <div>
                    <div className="text-lg font-semibold text-gray-900">
                      {formatCurrency(holdings.total_portfolio_value / holdings.holdings.length)}
                    </div>
                    <div className="text-sm text-gray-500">Avg Position Size</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-6 w-6 text-green-500 mr-3" />
                  <div>
                    <div className="text-lg font-semibold text-gray-900">
                      {Math.max(...holdings.holdings.map(h => h.current_value)) === Math.min(...holdings.holdings.map(h => h.current_value)) 
                        ? formatCurrency(holdings.holdings[0]?.current_value || 0)
                        : `${formatCurrency(Math.min(...holdings.holdings.map(h => h.current_value)))} - ${formatCurrency(Math.max(...holdings.holdings.map(h => h.current_value)))}`}
                    </div>
                    <div className="text-sm text-gray-500">Position Range</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Holdings Table */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Individual Holdings</h3>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Shares Held
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Cost Basis
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current Price
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current Value
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Unrealized P&L
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Transaction
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total Transactions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {holdings.holdings.map((holding) => {
                      const unrealizedPL = (holding.latest_price - holding.avg_cost_basis) * holding.net_shares;
                      const unrealizedPercent = holding.avg_cost_basis > 0 ? ((holding.latest_price - holding.avg_cost_basis) / holding.avg_cost_basis) * 100 : 0;
                      
                      return (
                        <tr key={holding.company_ticker} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {holding.company_ticker}
                              </div>
                              <div className="text-sm text-gray-500">
                                {holding.company_name}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {holding.net_shares.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(holding.avg_cost_basis)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(holding.latest_price)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatCurrency(holding.current_value)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className={`text-sm font-medium ${getReturnColor(unrealizedPercent)}`}>
                              {formatCurrency(unrealizedPL)}
                            </div>
                            <div className={`text-xs ${getReturnColor(unrealizedPercent)}`}>
                              ({formatPercentage(unrealizedPercent)})
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center text-sm text-gray-500">
                              <CalendarIcon className="h-4 w-4 mr-1" />
                              {holding.last_transaction_date ? formatDate(holding.last_transaction_date) : 'N/A'}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {holding.total_transactions}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              
              {holdings.holdings.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-gray-500">No current holdings found.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent Trades */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Trades</h2>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
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
                    Value
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Price
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    30d Return
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    90d Return
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {trader.recent_trades?.map((trade) => (
                  <tr key={trade.trade_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(trade.transaction_date)}
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(trade.total_value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {trade.current_price ? `$${trade.current_price.toFixed(2)}` : 'N/A'}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trade.return_30d)}`}>
                      {formatPercentage(trade.return_30d)}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getReturnColor(trade.return_90d)}`}>
                      {formatPercentage(trade.return_90d)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {(!trader.recent_trades || trader.recent_trades.length === 0) && (
            <div className="text-center py-8">
              <p className="text-gray-500">No recent trades available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TraderProfile;
