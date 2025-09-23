import React, { useState, useEffect } from 'react';
import { 
 UserGroupIcon, 
 LinkIcon, 
 BuildingOfficeIcon,
 ArrowPathIcon,
 FireIcon,
 ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { getNetworkAnalysis } from '../utils/api';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Card, Button, Select, SelectOption, DataTable, ModuleCard } from '../components/ui';

const InsiderNetworks = () => {
 const [networks, setNetworks] = useState({});
 const [loading, setLoading] = useState(true);
 const [activeTab, setActiveTab] = useState('board-overlap');

 useEffect(() => {
  const fetchNetworkData = async () => {
   try {
    setLoading(true);
    
    // Get network analysis from backend
    const networkData = await getNetworkAnalysis();
    setNetworks(networkData);
    
   } catch (error) {
    console.error('Error fetching network data:', error);
   } finally {
    setLoading(false);
   }
  };

  fetchNetworkData();
 }, []);

 const analyzeInsiderNetworks = (trades, traders) => {
  // 1. Board Member Overlap Analysis
  const boardOverlap = findBoardOverlap(traders);
  
  // 2. Executive Migration Tracking
  const executiveMigration = findExecutiveMigration(traders);
  
  // 3. Family Network Detection
  const familyNetworks = findFamilyNetworks(traders);
  
  // 4. Coordinated Trading Detection
  const coordinatedTrading = findCoordinatedTrading(trades);
  
  // 5. Investment Firm Networks
  const investmentNetworks = findInvestmentNetworks(traders);

  return {
   boardOverlap,
   executiveMigration,
   familyNetworks,
   coordinatedTrading,
   investmentNetworks
  };
 };

 const findBoardOverlap = (traders) => {
  // Find insiders who appear at multiple companies
  const insiderCompanies = {};
  
  traders.forEach(trader => {
   const name = trader.name;
   if (!insiderCompanies[name]) {
    insiderCompanies[name] = [];
   }
   insiderCompanies[name].push({
    company: trader.company_ticker,
    title: trader.title,
    performance: trader.performance_score
   });
  });

  // Find multi-company insiders
  const multiCompanyInsiders = Object.entries(insiderCompanies)
   .filter(([name, companies]) => companies.length > 1)
   .map(([name, companies]) => ({
    name,
    companies,
    connectionCount: companies.length,
    avgPerformance: companies.reduce((sum, c) => sum + (c.performance || 0), 0) / companies.length
   }))
   .sort((a, b) => b.connectionCount - a.connectionCount)
   .slice(0, 20);

  return multiCompanyInsiders;
 };

 const findExecutiveMigration = (traders) => {
  // Find executives who might have moved between companies
  const executivesByName = {};
  
  traders.forEach(trader => {
   const name = trader.name;
   if (trader.title && (
    trader.title.includes('CEO') || 
    trader.title.includes('CFO') || 
    trader.title.includes('Chief')
   )) {
    if (!executivesByName[name]) {
     executivesByName[name] = [];
    }
    executivesByName[name].push(trader);
   }
  });

  const migrations = Object.entries(executivesByName)
   .filter(([name, positions]) => positions.length > 1)
   .map(([name, positions]) => ({
    name,
    positions: positions.map(p => ({
     company: p.company_ticker,
     title: p.title,
     performance: p.performance_score
    })),
    migrationCount: positions.length
   }))
   .slice(0, 15);

  return migrations;
 };

 const findFamilyNetworks = (traders) => {
  // Group by last name to find potential family connections
  const lastNameGroups = {};
  
  traders.forEach(trader => {
   const nameParts = trader.name.split(' ');
   const lastName = nameParts[nameParts.length - 1];
   
   if (lastName && lastName.length > 3) { // Avoid common short names
    if (!lastNameGroups[lastName]) {
     lastNameGroups[lastName] = [];
    }
    lastNameGroups[lastName].push(trader);
   }
  });

  const familyConnections = Object.entries(lastNameGroups)
   .filter(([lastName, members]) => members.length > 1 && members.length < 20) // Avoid common names
   .map(([lastName, members]) => ({
    familyName: lastName,
    members: members.map(m => ({
     name: m.name,
     company: m.company_ticker,
     title: m.title,
     performance: m.performance_score
    })),
    memberCount: members.length,
    avgPerformance: members.reduce((sum, m) => sum + (m.performance_score || 0), 0) / members.length
   }))
   .sort((a, b) => b.avgPerformance - a.avgPerformance)
   .slice(0, 20);

  return familyConnections;
 };

 const findCoordinatedTrading = (trades) => {
  // Find clusters of trading activity (same company, similar dates)
  const tradingClusters = {};
  
  trades.forEach(trade => {
   const dateKey = trade.transaction_date.substring(0, 7); // YYYY-MM
   const companyKey = trade.company_ticker;
   const clusterKey = `${companyKey}-${dateKey}`;
   
   if (!tradingClusters[clusterKey]) {
    tradingClusters[clusterKey] = {
     company: companyKey,
     month: dateKey,
     trades: [],
     insiders: new Set(),
     totalVolume: 0,
     buyCount: 0,
     sellCount: 0
    };
   }
   
   tradingClusters[clusterKey].trades.push(trade);
   tradingClusters[clusterKey].insiders.add(trade.trader_name);
   tradingClusters[clusterKey].totalVolume += trade.total_value;
   
   if (trade.transaction_type === 'BUY') {
    tradingClusters[clusterKey].buyCount++;
   } else if (trade.transaction_type === 'SELL') {
    tradingClusters[clusterKey].sellCount++;
   }
  });

  // Find significant clusters (multiple insiders, same timeframe)
  const significantClusters = Object.values(tradingClusters)
   .filter(cluster => cluster.insiders.size >= 3) // At least 3 different insiders
   .map(cluster => ({
    ...cluster,
    insiderCount: cluster.insiders.size,
    sentiment: cluster.buyCount > cluster.sellCount ? 'Bullish' : 
         cluster.sellCount > cluster.buyCount ? 'Bearish' : 'Mixed'
   }))
   .sort((a, b) => b.totalVolume - a.totalVolume)
   .slice(0, 15);

  return significantClusters;
 };

 const findInvestmentNetworks = (traders) => {
  // Find investment firms and VCs with multiple portfolio companies
  const investmentFirms = {};
  
  traders.forEach(trader => {
   const name = trader.name.toLowerCase();
   
   // Identify investment entities
   if (name.includes('fund') || 
     name.includes('capital') || 
     name.includes('partners') || 
     name.includes('ventures') || 
     name.includes('investment') ||
     name.includes('management') ||
     name.includes('llc') ||
     name.includes('lp')) {
    
    // Extract firm name (simplified)
    const firmName = trader.name;
    
    if (!investmentFirms[firmName]) {
     investmentFirms[firmName] = {
      name: firmName,
      portfolioCompanies: [],
      totalPerformance: 0
     };
    }
    
    investmentFirms[firmName].portfolioCompanies.push({
     company: trader.company_ticker,
     performance: trader.performance_score || 0
    });
    investmentFirms[firmName].totalPerformance += trader.performance_score || 0;
   }
  });

  const topInvestmentNetworks = Object.values(investmentFirms)
   .filter(firm => firm.portfolioCompanies.length > 1)
   .map(firm => ({
    ...firm,
    portfolioSize: firm.portfolioCompanies.length,
    avgPerformance: firm.totalPerformance / firm.portfolioCompanies.length
   }))
   .sort((a, b) => b.portfolioSize - a.portfolioSize)
   .slice(0, 10);

  return topInvestmentNetworks;
 };

 const renderTabContent = () => {
  switch(activeTab) {
   case 'board-overlap':
    return (
     <div className="space-y-4">
      <h3 className="text-lg font-medium text-primary mb-4">
       Multi-Company Board Members & Executives
      </h3>
      {networks.board_overlaps?.map((insider, index) => (
       <div key={insider.name} className="border rounded-lg p-4 ">
        <div className="flex justify-between items-start mb-2">
         <h4 className="font-medium text-primary">{insider.name}</h4>
         <span className="text-sm text-secondary">
          {insider.company_count} companies
         </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
         {insider.companies.map((company, idx) => (
          <div key={idx} className="text-sm">
           <span className="font-medium text-blue">{company}</span>
           <div className={`text-xs ${insider.avg_performance > 0 ? 'text-green' : 'text-red'}`}>
            Avg Score: {insider.avg_performance?.toFixed(1) || 'N/A'}
           </div>
          </div>
         ))}
        </div>
       </div>
      ))}
     </div>
    );

   case 'coordinated-trading':
    return (
     <div className="space-y-4">
      <h3 className="text-lg font-medium text-primary mb-4">
       Coordinated Trading Clusters
      </h3>
      {networks.trading_clusters?.map((cluster, index) => (
       <div key={index} className="border rounded-lg p-4 ">
        <div className="flex justify-between items-start mb-3">
         <div>
          <h4 className="font-medium text-primary">{cluster.company}</h4>
          <p className="text-sm text-secondary">{cluster.month}</p>
         </div>
         <div className="text-right">
          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
           cluster.sentiment === 'Bullish' ? 'bg-green-100 text-green-800' :
           cluster.sentiment === 'Bearish' ? 'bg-red-100 text-red-800' :
           'bg-yellow-100 text-yellow-800'
          }`}>
           {cluster.sentiment}
          </span>
         </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
         <div>
          <span className="text-secondary">Insiders</span>
          <p className="font-medium text-primary">{cluster.insider_count}</p>
         </div>
         <div>
          <span className="text-secondary">Total Volume</span>
          <p className="font-medium text-primary">{formatCurrency(cluster.total_volume)}</p>
         </div>
         <div>
          <span className="text-secondary">Buys</span>
          <p className="font-medium text-green">{cluster.buy_count}</p>
         </div>
         <div>
          <span className="text-secondary">Sells</span>
          <p className="font-medium text-red">{cluster.sell_count}</p>
         </div>
        </div>
       </div>
      ))}
     </div>
    );

   case 'family-networks':
    return (
     <div className="space-y-4">
      <h3 className="text-lg font-medium text-primary mb-4">
       Potential Family Networks
      </h3>
      {networks.family_networks?.map((family, index) => (
       <div key={index} className="border rounded-lg p-4 ">
        <div className="flex justify-between items-start mb-3">
         <h4 className="font-medium text-primary">{family.family_name} Family Network</h4>
         <div className="text-right">
          <div className="text-sm text-secondary">{family.member_count} members</div>
          <div className="text-sm font-medium">
           Avg Score: {family.avg_performance?.toFixed(1) || 'N/A'}
          </div>
         </div>
        </div>
        
        <div className="space-y-2">
         <div className="text-sm">
          <span className="text-secondary">Companies: </span>
          <span className="font-medium">{family.companies.join(', ')}</span>
         </div>
        </div>
       </div>
      ))}
     </div>
    );

   case 'investment-networks':
    return (
     <div className="space-y-4">
      <h3 className="text-lg font-medium text-primary mb-4">
       Investment Firm Portfolio Networks
      </h3>
      {networks.investmentNetworks?.map((firm, index) => (
       <div key={index} className="border rounded-lg p-4 ">
        <div className="flex justify-between items-start mb-3">
         <h4 className="font-medium text-primary">{firm.name}</h4>
         <div className="text-right">
          <div className="text-sm text-secondary">{firm.portfolioSize} companies</div>
          <div className="text-sm font-medium">
           Avg Performance: {firm.avgPerformance?.toFixed(1) || 'N/A'}
          </div>
         </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
         {firm.portfolioCompanies.map((company, idx) => (
          <div key={idx} className="text-sm">
           <span className="font-medium text-blue-600">{company.company}</span>
           <div className={`text-xs ${company.performance > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {company.performance?.toFixed(1) || 'N/A'}
           </div>
          </div>
         ))}
        </div>
       </div>
      ))}
     </div>
    );

   default:
    return <div>Select a network analysis type</div>;
  }
 };

 if (loading) {
  return (
   <div className="flex justify-center items-center h-64">
    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-brand-600"></div>
   </div>
  );
 }

 return (
  <div className="space-y-6">
   {/* Header */}
   <div>
    <h1 className="text-3xl font-bold text-primary">Insider Networks</h1>
    <p className="mt-2 text-secondary">
     Discover hidden connections and coordinated activity between corporate insiders
    </p>
   </div>

   {/* Network Stats */}
   <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
    <Card className="p-5">
     <div className="flex items-center">
      <UserGroupIcon className="h-6 w-6 text-blue-500" />
      <div className="ml-3">
       <p className="text-sm font-medium text-secondary">Board Overlaps</p>
       <p className="text-lg font-semibold text-primary">
        {networks.board_overlaps?.length || 0}
       </p>
      </div>
     </div>
    </Card>

    <Card className="p-5">
     <div className="flex items-center">
      <ArrowPathIcon className="h-6 w-6 text-green-500" />
      <div className="ml-3">
       <p className="text-sm font-medium text-secondary">Executive Migrations</p>
       <p className="text-lg font-semibold text-primary">
        0
       </p>
      </div>
     </div>
    </Card>

    <Card className="p-5">
     <div className="flex items-center">
      <LinkIcon className="h-6 w-6 text-purple-500" />
      <div className="ml-3">
       <p className="text-sm font-medium text-secondary">Family Networks</p>
       <p className="text-lg font-semibold text-primary">
        {networks.family_networks?.length || 0}
       </p>
      </div>
     </div>
    </Card>

    <Card className="p-5">
     <div className="flex items-center">
      <FireIcon className="h-6 w-6 text-orange-500" />
      <div className="ml-3">
       <p className="text-sm font-medium text-secondary">Trading Clusters</p>
       <p className="text-lg font-semibold text-primary">
        {networks.trading_clusters?.length || 0}
       </p>
      </div>
     </div>
    </Card>
   </div>

   {/* Tabs */}
   <Card>
    <div className="border-b border-tertiary">
     <nav className="-mb-px flex space-x-8 px-6">
      {[
       { id: 'board-overlap', name: 'Board Overlaps', icon: UserGroupIcon },
       { id: 'coordinated-trading', name: 'Trading Clusters', icon: FireIcon },
       { id: 'family-networks', name: 'Family Networks', icon: LinkIcon },
       { id: 'investment-networks', name: 'Investment Firms', icon: BuildingOfficeIcon }
      ].map((tab) => {
       const Icon = tab.icon;
       return (
        <button
         key={tab.id}
         onClick={() => setActiveTab(tab.id)}
         className={`${
          activeTab === tab.id
           ? 'border-brand-500 text-brand-600'
           : 'border-transparent text-secondary '
         } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
        >
         <Icon className="h-4 w-4 mr-2" />
         {tab.name}
        </button>
       );
      })}
     </nav>
    </div>

    <div className="p-6">
     {renderTabContent()}
    </div>
   </Card>
  </div>
 );
};

export default InsiderNetworks;
