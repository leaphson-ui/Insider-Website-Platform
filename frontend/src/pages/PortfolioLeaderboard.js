import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  CurrencyDollarIcon, 
  BuildingOfficeIcon,
  ChartBarIcon,
  FireIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';
import { getPortfolioLeaderboard } from '../utils/api';
import { formatCurrency, formatPercentage, getPerformanceScoreColor } from '../utils/formatters';

const PortfolioLeaderboard = () => {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [minValue, setMinValue] = useState(100000);
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    const fetchPortfolios = async () => {
      try {
        setLoading(true);
        const data = await getPortfolioLeaderboard(limit, minValue);
        setPortfolios(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching portfolio leaderboard:', err);
        setError('Failed to load portfolio data');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolios();
  }, [limit, minValue]);

  const handleMinValueChange = (value) => {
    setMinValue(value);
  };

  const handleLimitChange = (value) => {
    setLimit(value);
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portfolio Holdings Leaderboard</h1>
          <p className="mt-2 text-gray-600">
            Insiders ranked by current portfolio value based on their trading history
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={minValue}
            onChange={(e) => handleMinValueChange(parseInt(e.target.value))}
            className="rounded-lg border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
          >
            <option value={10000}>Min $10K</option>
            <option value={50000}>Min $50K</option>
            <option value={100000}>Min $100K</option>
            <option value={500000}>Min $500K</option>
            <option value={1000000}>Min $1M</option>
            <option value={5000000}>Min $5M</option>
          </select>
          <select
            value={limit}
            onChange={(e) => handleLimitChange(parseInt(e.target.value))}
            className="rounded-lg border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500"
          >
            <option value={25}>Top 25</option>
            <option value={50}>Top 50</option>
            <option value={100}>Top 100</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Portfolio Value</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(portfolios.reduce((sum, p) => sum + p.total_portfolio_value, 0))}
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
                <BuildingOfficeIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Holders</dt>
                  <dd className="text-lg font-medium text-gray-900">{portfolios.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Portfolio Size</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(portfolios.length > 0 ? portfolios.reduce((sum, p) => sum + p.total_portfolio_value, 0) / portfolios.length : 0)}
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
                <FireIcon className="h-6 w-6 text-orange-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Top Portfolio</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {portfolios.length > 0 ? formatCurrency(portfolios[0].total_portfolio_value) : '$0'}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Leaderboard Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Portfolio Holdings Leaderboard</h2>
            <span className="text-sm text-gray-500">{portfolios.length} holders found</span>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Insider</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Portfolio Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Companies Held</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Trades</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {portfolios.map((portfolio, index) => (
                  <tr key={portfolio.trader_id} className="hover:bg-gray-50">
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
                          to={`/traders/${portfolio.trader_id}`}
                          className="text-sm font-medium text-brand-600 hover:text-brand-500"
                        >
                          {portfolio.name}
                        </Link>
                        <div className="text-sm text-gray-500">{portfolio.title}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{portfolio.company_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-green-600">
                        {formatCurrency(portfolio.total_portfolio_value)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {portfolio.companies_held} companies
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {portfolio.total_trades}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`text-sm font-bold ${getPerformanceScoreColor(portfolio.performance_score)}`}>
                          {portfolio.performance_score?.toFixed(1) || 'N/A'}
                        </div>
                        <div className="ml-2">
                          {portfolio.performance_score > 30 ? (
                            <ArrowUpIcon className="h-4 w-4 text-green-500" />
                          ) : portfolio.performance_score > 0 ? (
                            <ArrowUpIcon className="h-4 w-4 text-yellow-500" />
                          ) : (
                            <ArrowDownIcon className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <Link
                        to={`/traders/${portfolio.trader_id}`}
                        className="text-brand-600 hover:text-brand-500"
                      >
                        View Profile
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {portfolios.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">No portfolios found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioLeaderboard;
