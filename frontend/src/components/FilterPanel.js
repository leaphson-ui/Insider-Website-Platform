import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const FilterPanel = ({ filters, onFilterChange, onClearFilters }) => {
  const [companies, setCompanies] = useState([]);
  const [insiders, setInsiders] = useState([]);
  const [transactionCodes, setTransactionCodes] = useState([]);

  useEffect(() => {
    fetchFilterOptions();
  }, []);

  const fetchFilterOptions = async () => {
    try {
      // Fetch unique companies
      const { data: companiesData } = await supabase
        .from('companies')
        .select('name, ticker')
        .order('name')
        .limit(100);

      // Fetch unique insiders
      const { data: insidersData } = await supabase
        .from('insiders')
        .select('name')
        .order('name')
        .limit(100);

      // Fetch unique transaction codes
      const { data: codesData } = await supabase
        .from('transactions')
        .select('transaction_code')
        .order('transaction_code');

      setCompanies(companiesData || []);
      setInsiders(insidersData || []);
      setTransactionCodes([...new Set((codesData || []).map(item => item.transaction_code))]);
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const handleInputChange = (field, value) => {
    onFilterChange({ [field]: value });
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Filters</h3>
      </div>
      
      <div className="p-6 space-y-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search
          </label>
          <input
            type="text"
            value={filters.search}
            onChange={(e) => handleInputChange('search', e.target.value)}
            placeholder="Search companies or insiders..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Company Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company
          </label>
          <select
            value={filters.company}
            onChange={(e) => handleInputChange('company', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Companies</option>
            {companies.map((company) => (
              <option key={company.name} value={company.name}>
                {company.name} ({company.ticker})
              </option>
            ))}
          </select>
        </div>

        {/* Insider Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Insider
          </label>
          <select
            value={filters.insider}
            onChange={(e) => handleInputChange('insider', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Insiders</option>
            {insiders.map((insider) => (
              <option key={insider.name} value={insider.name}>
                {insider.name}
              </option>
            ))}
          </select>
        </div>

        {/* Transaction Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Transaction Type
          </label>
          <select
            value={filters.transactionCode}
            onChange={(e) => handleInputChange('transactionCode', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            {transactionCodes.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
        </div>

        {/* Value Range */}
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Value
            </label>
            <input
              type="number"
              value={filters.minValue}
              onChange={(e) => handleInputChange('minValue', e.target.value)}
              placeholder="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Value
            </label>
            <input
              type="number"
              value={filters.maxValue}
              onChange={(e) => handleInputChange('maxValue', e.target.value)}
              placeholder="1000000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Clear Filters Button */}
        <button
          onClick={onClearFilters}
          className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          Clear All Filters
        </button>
      </div>
    </div>
  );
};

export default FilterPanel;
