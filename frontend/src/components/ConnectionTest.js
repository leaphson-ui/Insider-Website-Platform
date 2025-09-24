import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const ConnectionTest = () => {
  const [connectionStatus, setConnectionStatus] = useState('Testing...');
  const [dataCounts, setDataCounts] = useState({});

  useEffect(() => {
    testConnection();
  }, []);

  const testConnection = async () => {
    try {
      // Test basic connection
      const { data: companies, error: companiesError } = await supabase
        .from('companies')
        .select('*', { count: 'exact', head: true });

      const { data: insiders, error: insidersError } = await supabase
        .from('insiders')
        .select('*', { count: 'exact', head: true });

      const { data: transactions, error: transactionsError } = await supabase
        .from('transactions')
        .select('*', { count: 'exact', head: true });

      if (companiesError || insidersError || transactionsError) {
        setConnectionStatus('❌ Connection failed');
        console.error('Connection errors:', { companiesError, insidersError, transactionsError });
      } else {
        setConnectionStatus('✅ Connected successfully!');
        setDataCounts({
          companies: companies?.length || 0,
          insiders: insiders?.length || 0,
          transactions: transactions?.length || 0
        });
      }
    } catch (error) {
      setConnectionStatus('❌ Connection failed');
      console.error('Connection test error:', error);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Database Connection Test</h3>
      <div className="space-y-2">
        <p className="text-sm text-gray-600">Status: {connectionStatus}</p>
        {Object.keys(dataCounts).length > 0 && (
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{dataCounts.companies}</div>
              <div className="text-sm text-gray-500">Companies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{dataCounts.insiders}</div>
              <div className="text-sm text-gray-500">Insiders</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{dataCounts.transactions}</div>
              <div className="text-sm text-gray-500">Transactions</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConnectionTest;
