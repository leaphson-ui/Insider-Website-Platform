import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import DataTable from '../components/ui/DataTable';
import StatsCard from '../components/ui/StatsCard';
import { getCompanyTrades } from '../utils/api';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const CompanyPage = () => {
  const { ticker } = useParams();
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [companyStats, setCompanyStats] = useState(null);

  useEffect(() => {
    const fetchCompanyData = async () => {
      try {
        setLoading(true);
        const data = await getCompanyTrades(ticker, 500);
        setTrades(data);
        
        // Calculate company stats
        const stats = calculateCompanyStats(data);
        setCompanyStats(stats);
      } catch (error) {
        console.error('Error fetching company data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanyData();
  }, [ticker]);

  const calculateCompanyStats = (trades) => {
    if (!trades.length) return null;

    const totalVolume = trades.reduce((sum, trade) => sum + trade.total_value, 0);
    const buyTrades = trades.filter(t => t.transaction_type === 'BUY');
    const sellTrades = trades.filter(t => t.transaction_type === 'SELL');
    const uniqueInsiders = new Set(trades.map(t => t.trader_name)).size;
    
    const avgReturn = trades.reduce((sum, t) => sum + (t.return_30d || 0), 0) / trades.length;

    return {
      totalVolume,
      totalTrades: trades.length,
      buyTrades: buyTrades.length,
      sellTrades: sellTrades.length,
      uniqueInsiders,
      avgReturn,
      netFlow: buyTrades.reduce((sum, t) => sum + t.total_value, 0) - 
               sellTrades.reduce((sum, t) => sum + t.total_value, 0)
    };
  };

  const columns = [
    { 
      key: 'trader_name', 
      header: 'Insider',
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
    { 
      key: 'transaction_type', 
      header: 'Type',
      render: (value) => (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          value === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {value}
        </span>
      )
    },
    { 
      key: 'shares_traded', 
      header: 'Shares',
      render: (value) => value?.toLocaleString()
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
      key: 'transaction_date', 
      header: 'Date',
      render: (value) => new Date(value).toLocaleDateString()
    },
    { 
      key: 'return_30d', 
      header: '30d Return',
      render: (value) => value ? `${value.toFixed(2)}%` : 'N/A'
    }
  ];

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-primary">Loading {ticker}...</h1>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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
        <h1 className="text-2xl font-bold text-primary">{ticker} Insider Activity</h1>
        <div className="text-sm text-secondary">
          {companyStats?.totalTrades} trades by {companyStats?.uniqueInsiders} insiders
        </div>
      </div>

      {/* Company Stats */}
      {companyStats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Volume"
            value={formatCurrency(companyStats.totalVolume)}
            subtitle="All trades"
          />
          <StatsCard
            title="Net Flow"
            value={formatCurrency(companyStats.netFlow)}
            subtitle={companyStats.netFlow >= 0 ? "Net buying" : "Net selling"}
            trend={companyStats.netFlow >= 0 ? 'up' : 'down'}
          />
          <StatsCard
            title="Buy/Sell Ratio"
            value={`${companyStats.buyTrades}/${companyStats.sellTrades}`}
            subtitle="Trades"
          />
          <StatsCard
            title="Avg Return"
            value={`${companyStats.avgReturn.toFixed(2)}%`}
            subtitle="30-day performance"
            trend={companyStats.avgReturn > 0 ? 'up' : 'down'}
          />
        </div>
      )}

      {/* Recent Trades */}
      <div>
        <h2 className="text-xl font-semibold text-primary mb-4">Recent Insider Trades</h2>
        <DataTable
          data={trades}
          columns={columns}
          loading={loading}
        />
      </div>
    </div>
  );
};

export default CompanyPage;
