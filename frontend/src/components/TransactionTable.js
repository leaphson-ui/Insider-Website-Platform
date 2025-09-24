import React from 'react';

const TransactionTable = ({ transactions, loading }) => {
  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getTransactionTypeColor = (code) => {
    const buyCodes = ['P', 'A', 'D'];
    const sellCodes = ['S', 'F'];
    
    if (buyCodes.includes(code)) return 'text-green-600 bg-green-50';
    if (sellCodes.includes(code)) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getTransactionTypeLabel = (code) => {
    const typeMap = {
      'P': 'Purchase',
      'S': 'Sale',
      'A': 'Award',
      'D': 'Disposition',
      'F': 'Sale (Form 4)',
      'G': 'Grant',
      'H': 'Hold',
      'I': 'Incentive',
      'J': 'Other',
      'K': 'Equity Swap',
      'L': 'Small Acquisition',
      'M': 'Exercise',
      'N': 'Non-Open Market',
      'O': 'Option Exercise',
      'Q': 'Transfer',
      'R': 'Return',
      'T': 'Tax',
      'U': 'Underwriter',
      'V': 'Conversion',
      'W': 'Warrant',
      'X': 'Other',
      'Y': 'Trust',
      'Z': 'Deposit'
    };
    return typeMap[code] || code;
  };

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Transactions</h3>
        </div>
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">
          Recent Transactions ({transactions.length})
        </h3>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Insider
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
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {transactions.map((transaction) => (
              <tr key={transaction.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(transaction.transaction_date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {transaction.companies?.name || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500">
                    {transaction.companies?.ticker || 'N/A'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {transaction.insiders?.name || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500">
                    {transaction.insiders?.is_director && 'Director'}
                    {transaction.insiders?.is_officer && 'Officer'}
                    {transaction.insiders?.is_ten_percent_owner && '10% Owner'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTransactionTypeColor(transaction.transaction_code)}`}>
                    {getTransactionTypeLabel(transaction.transaction_code)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {transaction.transaction_shares ? 
                    new Intl.NumberFormat('en-US').format(transaction.transaction_shares) : 
                    'N/A'
                  }
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatCurrency(transaction.transaction_price_per_share)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {formatCurrency(transaction.calculated_transaction_value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {transactions.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-gray-500">No transactions found</div>
        </div>
      )}
    </div>
  );
};

export default TransactionTable;
