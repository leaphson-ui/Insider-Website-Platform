import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import Card from '../components/ui/Card';
import StatsCard from '../components/ui/StatsCard';
import DataTable from '../components/ui/DataTable';
import Button from '../components/ui/Button';
import { getTrader, getTraderHoldings, getTraderTrades, getTraderTradesCount } from '../utils/api';
import { formatCurrency, formatPercentage, formatDate, formatNumber, getReturnColor, getPerformanceScoreColor } from '../utils/formatters';

const TraderProfile = () => {
  const { traderId } = useParams();
  const [trader, setTrader] = useState(null);
  const [holdings, setHoldings] = useState(null);
  const [trades, setTrades] = useState([]);
  const [totalTrades, setTotalTrades] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [tradesPerPage, setTradesPerPage] = useState(50);
  const [loading, setLoading] = useState(true);
  const [tradesLoading, setTradesLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [traderData, holdingsData, tradesCountData] = await Promise.all([
          getTrader(traderId),
          getTraderHoldings(traderId),
          getTraderTradesCount(traderId)
        ]);
        
        setTrader(traderData);
        setHoldings(holdingsData);
        setTotalTrades(tradesCountData.total_trades);
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

  useEffect(() => {
    const fetchTrades = async () => {
      if (!traderId) return;
      
      try {
        setTradesLoading(true);
        const tradesData = await getTraderTrades(traderId, currentPage, tradesPerPage);
        setTrades(tradesData);
      } catch (err) {
        console.error('Error fetching trades:', err);
      } finally {
        setTradesLoading(false);
      }
    };

    fetchTrades();
  }, [traderId, currentPage, tradesPerPage]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin text-blue">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-red">{error}</p>
        </div>
      </Card>
    );
  }

  if (!trader) {
    return (
      <Card>
        <div className="text-center py-8">
          <p className="text-secondary">Trader not found</p>
        </div>
      </Card>
    );
  }

  // Holdings table columns
  const holdingsColumns = [
    { 
      key: 'company_ticker', 
      header: 'Company',
      render: (value, row) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-sm text-secondary">{row.company_name}</div>
        </div>
      )
    },
    { 
      key: 'net_shares', 
      header: 'Shares Held',
      render: (value) => formatNumber(value)
    },
    { 
      key: 'avg_cost_basis', 
      header: 'Avg Cost',
      render: (value) => formatCurrency(value)
    },
    { 
      key: 'latest_price', 
      header: 'Current Price',
      render: (value) => formatCurrency(value)
    },
    { 
      key: 'current_value', 
      header: 'Current Value',
      render: (value) => formatCurrency(value)
    },
    { 
      key: 'last_transaction_date', 
      header: 'Last Trade',
      render: (value) => formatDate(value)
    },
  ];

  // Trades table columns
  const tradesColumns = [
    { 
      key: 'transaction_date', 
      header: 'Date',
      render: (value) => formatDate(value)
    },
    { 
      key: 'transaction_type', 
      header: 'Type',
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value?.toUpperCase().includes('BUY') || value === 'P' || value === 'A'
            ? 'bg-green text-white' 
            : 'bg-red text-white'
        }`}>
          {value}
        </span>
      )
    },
    { 
      key: 'shares_traded', 
      header: 'Shares',
      render: (value) => formatNumber(value)
    },
    { 
      key: 'price_per_share', 
      header: 'Price',
      render: (value) => formatCurrency(value)
    },
    { 
      key: 'total_value', 
      header: 'Value',
      render: (value) => formatCurrency(value)
    },
    { 
      key: 'return_30d', 
      header: '30d Return',
      render: (value) => (
        <span className={`font-medium ${getReturnColor(value)}`}>
          {formatPercentage(value)}
        </span>
      )
    },
    { 
      key: 'return_90d', 
      header: '90d Return',
      render: (value) => (
        <span className={`font-medium ${getReturnColor(value)}`}>
          {formatPercentage(value)}
        </span>
      )
    },
  ];

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-secondary">
        <Link to="/dashboard" className="hover:text-primary">Dashboard</Link>
        <span>→</span>
        <Link to="/leaderboard" className="hover:text-primary">Leaderboard</Link>
        <span>→</span>
        <span className="text-primary">{trader?.name}</span>
      </div>

      {/* Header */}
      <Card>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-primary">{trader.name}</h1>
            <p className="text-lg text-secondary mt-1">{trader.title}</p>
            <p className="text-sm text-muted mt-1">
              {trader.relationship_to_company} at {trader.company_name} ({trader.company_ticker})
            </p>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getPerformanceScoreColor(trader.performance_score)}`}>
              {trader.performance_score?.toFixed(1) || 'N/A'}
            </div>
            <div className="text-sm text-secondary">Performance Score</div>
          </div>
        </div>
      </Card>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Trades"
          value={formatNumber(trader.total_trades)}
          subtitle="All time"
        />
        <StatsCard
          title="Win Rate"
          value={formatPercentage(trader.win_rate)}
          subtitle="Success rate"
        />
        <StatsCard
          title="90d Avg Return"
          value={formatPercentage(trader.avg_return_90d)}
          subtitle="Recent performance"
          trend={trader.avg_return_90d > 0 ? 'up' : 'down'}
          trendValue={formatPercentage(Math.abs(trader.avg_return_90d))}
        />
        <StatsCard
          title="Total P&L"
          value={formatCurrency(trader.total_profit_loss)}
          subtitle="All time"
          trend={trader.total_profit_loss > 0 ? 'up' : 'down'}
          trendValue={formatCurrency(Math.abs(trader.total_profit_loss))}
        />
      </div>

      {/* Return Breakdown */}
      <Card title="Return Breakdown">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className={`text-2xl font-bold ${getReturnColor(trader.avg_return_30d)}`}>
              {formatPercentage(trader.avg_return_30d)}
            </div>
            <div className="text-sm text-secondary">30-Day Average</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${getReturnColor(trader.avg_return_90d)}`}>
              {formatPercentage(trader.avg_return_90d)}
            </div>
            <div className="text-sm text-secondary">90-Day Average</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${getReturnColor(trader.avg_return_1y)}`}>
              {formatPercentage(trader.avg_return_1y)}
            </div>
            <div className="text-sm text-secondary">1-Year Average</div>
          </div>
        </div>
      </Card>

      {/* Current Holdings */}
      {holdings && holdings.holdings && holdings.holdings.length > 0 && (
        <div className="space-y-6">
          <Card title="Current Holdings Portfolio">
            <div className="flex items-center justify-between mb-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {formatCurrency(holdings.total_portfolio_value)}
                  </div>
                  <div className="text-sm text-secondary">Total Portfolio Value</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {holdings.holdings.length}
                  </div>
                  <div className="text-sm text-secondary">Companies Held</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {formatCurrency(holdings.total_portfolio_value / holdings.holdings.length)}
                  </div>
                  <div className="text-sm text-secondary">Avg Position Size</div>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Individual Holdings">
            <DataTable
              data={holdings.holdings}
              columns={holdingsColumns}
              loading={false}
            />
          </Card>
        </div>
      )}

      {/* All Trades */}
      <Card title={`All Trades (${formatNumber(totalTrades)})`}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <label className="text-sm text-secondary">Per page:</label>
            <select 
              value={tradesPerPage} 
              onChange={(e) => {
                setTradesPerPage(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="input w-20"
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        <DataTable
          data={trades}
          columns={tradesColumns}
          loading={tradesLoading}
        />

        {/* Pagination */}
        {totalTrades > 0 && (
          <div className="flex items-center justify-between mt-6 pt-6 border-t border">
            <div className="text-sm text-secondary">
              Showing {((currentPage - 1) * tradesPerPage) + 1} to {Math.min(currentPage * tradesPerPage, totalTrades)} of {formatNumber(totalTrades)} trades
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                ← Previous
              </Button>
              <span className="px-3 py-1 text-sm text-secondary">
                Page {currentPage} of {Math.ceil(totalTrades / tradesPerPage)}
              </span>
              <Button
                variant="secondary"
                onClick={() => setCurrentPage(Math.min(Math.ceil(totalTrades / tradesPerPage), currentPage + 1))}
                disabled={currentPage >= Math.ceil(totalTrades / tradesPerPage)}
              >
                Next →
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default TraderProfile;