import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StatsCard from '../components/ui/StatsCard';
import DataTable from '../components/ui/DataTable';
import { getPlatformStats, getLeaderboard, getRecentTrades } from '../utils/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [recentTrades, setRecentTrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, leaderboardData, tradesData] = await Promise.all([
          getPlatformStats(),
          getLeaderboard(10, 5),
          getRecentTrades(10)
        ]);
        
        setStats(statsData);
        setLeaderboard(leaderboardData);
        setRecentTrades(tradesData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const leaderboardColumns = [
    { 
      key: 'name', 
      header: 'Trader',
      render: (value, row) => (
        <div 
          onClick={() => window.location.href = `/traders/${row.trader_id}`}
          className="cursor-pointer hover:text-blue transition-colors"
        >
          <div className="font-medium">{value}</div>
          <div className="text-sm text-secondary">{row.title}</div>
        </div>
      )
    },
    { key: 'company_ticker', header: 'Company' },
    { key: 'total_trades', header: 'Trades' },
    { key: 'avg_return_30d', header: '30d Return', render: (value) => `${value?.toFixed(2)}%` },
    { key: 'performance_score', header: 'Score', render: (value) => value?.toFixed(2) },
  ];

  const tradesColumns = [
    { key: 'trader_name', header: 'Trader' },
    { key: 'company_ticker', header: 'Company' },
    { key: 'transaction_type', header: 'Type' },
    { key: 'shares_traded', header: 'Shares', render: (value) => value?.toLocaleString() },
    { key: 'transaction_date', header: 'Date', render: (value) => new Date(value).toLocaleDateString() },
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-medium text-primary">Dashboard</h1>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="stats-card">
            <div className="text-secondary text-xs mb-1">Loading...</div>
            <div className="text-primary text-xl font-semibold">—</div>
          </div>
          <div className="stats-card">
            <div className="text-secondary text-xs mb-1">Loading...</div>
            <div className="text-primary text-xl font-semibold">—</div>
          </div>
          <div className="stats-card">
            <div className="text-secondary text-xs mb-1">Loading...</div>
            <div className="text-primary text-xl font-semibold">—</div>
          </div>
          <div className="stats-card">
            <div className="text-secondary text-xs mb-1">Loading...</div>
            <div className="text-primary text-xl font-semibold">—</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary">Dashboard</h1>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Traders"
            value={stats.total_traders?.toLocaleString()}
            subtitle="Active insiders"
          />
          <StatsCard
            title="Total Trades"
            value={stats.total_trades?.toLocaleString()}
            subtitle="All time"
          />
          <StatsCard
            title="Avg Return (30d)"
            value={`${stats.avg_return_30d?.toFixed(2)}%`}
            subtitle="Recent performance"
            trend={stats.avg_return_30d > 0 ? 'up' : 'down'}
            trendValue={`${Math.abs(stats.avg_return_30d).toFixed(2)}%`}
          />
          <StatsCard
            title="Companies Tracked"
            value={stats.total_companies?.toLocaleString()}
            subtitle="Unique tickers"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Performers */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-primary">Top Performers</h2>
            <Link to="/leaderboard" className="text-blue text-sm font-medium">
              View All →
            </Link>
          </div>
          <DataTable
            data={leaderboard}
            columns={leaderboardColumns}
            loading={loading}
          />
        </div>

        {/* Recent Activity */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-primary">Recent Trades</h2>
            <Link to="/trades" className="text-blue text-sm font-medium">
              View All →
            </Link>
          </div>
          <DataTable
            data={recentTrades}
            columns={tradesColumns}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
