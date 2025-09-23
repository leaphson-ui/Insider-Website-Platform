import React, { useState, useEffect } from 'react';
import { 
  BuildingOfficeIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  UsersIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

const CompanyPage = ({ companyTicker }) => {
  const [company, setCompany] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortField, setSortField] = useState('transaction_date');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    fetchCompanyData();
  }, [companyTicker]);

  const fetchCompanyData = async () => {
    try {
      setLoading(true);
      
      // Fetch company details
      const companyResponse = await fetch(`/api/companies/${companyTicker}`);
      if (!companyResponse.ok) throw new Error('Failed to fetch company data');
      const companyData = await companyResponse.json();
      setCompany(companyData);

      // Fetch recent transactions
      const transactionsResponse = await fetch(
        `/api/companies/${companyTicker}/transactions?limit=50&sort=${sortField}&direction=${sortDirection}`
      );
      if (!transactionsResponse.ok) throw new Error('Failed to fetch transactions');
      const transactionsData = await transactionsResponse.json();
      
      setTransactions(transactionsData.transactions || []);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
    fetchCompanyData();
  };

  const getSentimentSummary = () => {
    if (!transactions.length) return { sentiment: 'neutral', summary: 'No recent activity' };
    
    const recentTransactions = transactions.slice(0, 10);
    const buyCount = recentTransactions.filter(t => t.transaction_type === 'BUY').length;
    const sellCount = recentTransactions.filter(t => t.transaction_type === 'SELL').length;
    
    if (buyCount > sellCount) {
      return { 
        sentiment: 'positive', 
        summary: `Recent buying activity (${buyCount} buys vs ${sellCount} sells)`,
        icon: ArrowUpIcon,
        color: 'text-green-600'
      };
    } else if (sellCount > buyCount) {
      return { 
        sentiment: 'negative', 
        summary: `Recent selling activity (${sellCount} sells vs ${buyCount} buys)`,
        icon: ArrowDownIcon,
        color: 'text-red-600'
      };
    } else {
      return { 
        sentiment: 'neutral', 
        summary: `Balanced activity (${buyCount} buys, ${sellCount} sells)`,
        icon: ArrowTrendingUpIcon,
        color: 'text-gray-600'
      };
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading company data...</p>
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

  if (!company) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Company not found</p>
        </div>
      </div>
    );
  }

  const sentiment = getSentimentSummary();
  const SentimentIcon = sentiment.icon;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <BuildingOfficeIcon className="w-8 h-8 text-blue-600" />
              </div>
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {company.company_name}
              </h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span className="font-medium text-lg">{company.ticker}</span>
                {company.sector && (
                  <>
                    <span>•</span>
                    <span className="px-2 py-1 bg-gray-100 rounded-full text-xs">
                      {company.sector}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Sentiment Summary */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center space-x-3">
            <SentimentIcon className={`w-8 h-8 ${sentiment.color}`} />
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Recent Insider Sentiment</h2>
              <p className={`text-sm ${sentiment.color} font-medium`}>
                {sentiment.summary}
              </p>
            </div>
          </div>
        </div>

        {/* Company Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <UsersIcon className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Insiders</p>
                <p className="text-2xl font-bold text-gray-900">
                  {company.active_insiders || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <CalendarIcon className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Transactions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {company.total_transactions?.toLocaleString() || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <ArrowTrendingUpIcon className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg. Performance</p>
                <p className="text-2xl font-bold text-gray-900">
                  {company.avg_performance ? formatPercentage(company.avg_performance) : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Transactions Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Recent Insider Transactions</h2>
            <p className="text-sm text-gray-600 mt-1">
              Last 50 transactions for {company.ticker}
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('transaction_date')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Date</span>
                      {sortField === 'transaction_date' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('trader_name')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Insider</span>
                      {sortField === 'trader_name' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('transaction_type')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Type</span>
                      {sortField === 'transaction_type' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('shares_traded')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Shares</span>
                      {sortField === 'shares_traded' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('price_per_share')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Price</span>
                      {sortField === 'price_per_share' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('total_value')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Value</span>
                      {sortField === 'total_value' && (
                        sortDirection === 'asc' ? <ArrowUpIcon className="w-4 h-4" /> : <ArrowDownIcon className="w-4 h-4" />
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {transactions.map((transaction) => (
                  <tr key={transaction.trade_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(transaction.transaction_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {transaction.trader_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {transaction.trader_title}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        transaction.transaction_type === 'BUY' 
                          ? 'bg-green-100 text-green-800'
                          : transaction.transaction_type === 'SELL'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {transaction.transaction_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {transaction.shares_traded?.toLocaleString() || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${transaction.price_per_share?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(transaction.total_value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {transaction.return_30d ? (
                        <span className={`font-medium ${
                          transaction.return_30d > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatPercentage(transaction.return_30d)}%
                        </span>
                      ) : (
                        <span className="text-gray-400">N/A</span>
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

export default CompanyPage;
