import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const StatsOverview = () => {
  const [stats, setStats] = useState({
    totalTransactions: 0,
    totalCompanies: 0,
    totalInsiders: 0,
    totalValue: 0,
    recentTransactions: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);

      // Get total transactions
      const { count: transactionCount } = await supabase
        .from('transactions')
        .select('*', { count: 'exact', head: true });

      // Get total companies
      const { count: companyCount } = await supabase
        .from('companies')
        .select('*', { count: 'exact', head: true });

      // Get total insiders
      const { count: insiderCount } = await supabase
        .from('insiders')
        .select('*', { count: 'exact', head: true });

      // Get total transaction value
      const { data: valueData } = await supabase
        .from('transactions')
        .select('calculated_transaction_value')
        .not('calculated_transaction_value', 'is', null);

      const totalValue = valueData?.reduce((sum, item) => sum + (item.calculated_transaction_value || 0), 0) || 0;

      // Get recent transactions (last 7 days)
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      
      const { count: recentCount } = await supabase
        .from('transactions')
        .select('*', { count: 'exact', head: true })
        .gte('transaction_date', sevenDaysAgo.toISOString().split('T')[0]);

      setStats({
        totalTransactions: transactionCount || 0,
        totalCompanies: companyCount || 0,
        totalInsiders: insiderCount || 0,
        totalValue,
        recentTransactions: recentCount || 0
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Transactions',
      value: formatNumber(stats.totalTransactions),
      icon: '📊',
      color: 'bg-blue-50 text-blue-600'
    },
    {
      title: 'Companies',
      value: formatNumber(stats.totalCompanies),
      icon: '🏢',
      color: 'bg-green-50 text-green-600'
    },
    {
      title: 'Insiders',
      value: formatNumber(stats.totalInsiders),
      icon: '👥',
      color: 'bg-purple-50 text-purple-600'
    },
    {
      title: 'Total Value',
      value: formatCurrency(stats.totalValue),
      icon: '💰',
      color: 'bg-yellow-50 text-yellow-600'
    },
    {
      title: 'Recent (7 days)',
      value: formatNumber(stats.recentTransactions),
      icon: '🕒',
      color: 'bg-red-50 text-red-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
      {statCards.map((card, index) => (
        <div key={index} className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${card.color}`}>
              <span className="text-2xl">{card.icon}</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">{card.title}</p>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsOverview;
