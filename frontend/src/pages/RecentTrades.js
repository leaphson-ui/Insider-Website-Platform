import React, { useState, useEffect } from 'react';
import { Trade, TradesResponse, TradeFilters } from '../types/api';
import TradesTable from '../components/TradesTable';
import Filters from '../components/Filters';

const RecentTrades: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTrades, setTotalTrades] = useState(0);
  const [filters, setFilters] = useState<TradeFilters>({});
  const tradesPerPage = 100;

  useEffect(() => {
    fetchTrades();
  }, [currentPage, filters]);

  const fetchTrades = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: tradesPerPage.toString()
      });

      if (filters.ticker) params.append('ticker', filters.ticker);
      if (filters.action && filters.action !== 'all') params.append('type', filters.action);
      if (filters.dateFrom) params.append('dateFrom', filters.dateFrom);
      if (filters.dateTo) params.append('dateTo', filters.dateTo);

      const response = await fetch(`http://localhost:8000/api/trades/recent?${params}`);
      const data: TradesResponse = await response.json();
      
      setTrades(data.trades);
      setTotalPages(data.total_pages);
      setTotalTrades(data.total);
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFiltersChange = (newFilters: TradeFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handleApplyFilters = () => {
    fetchTrades();
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* SEO Meta Tags */}
        <title>Recent Insider Trades - Track Corporate Insider Activity | Insider Alpha</title>
        <meta name="description" content="View the latest insider trading activity. Track BUY/SELL transactions from corporate insiders with real-time data and performance metrics." />
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Recent Insider Trades</h1>
          <p className="text-gray-600">
            Track the latest insider trading activity from corporate executives and directors. 
            {totalTrades > 0 && ` Showing ${totalTrades.toLocaleString()} total transactions.`}
          </p>
        </div>

        <Filters 
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onApplyFilters={handleApplyFilters}
        />
        
        <TradesTable
          trades={trades}
          loading={loading}
          showTrader={true}
          showCompany={true}
          showPagination={true}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      </div>
    </div>
  );
};

export default RecentTrades;