import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import './styles/globals.css';

// Pages
import Homepage from './pages/Homepage';
import Dashboard from './pages/Dashboard';
import EnhancedDashboard from './pages/EnhancedDashboard';
import Leaderboard from './pages/Leaderboard';
import RecentTrades from './pages/RecentTrades';
import TraderProfile from './pages/TraderProfile';
import PortfolioLeaderboard from './pages/PortfolioLeaderboard';
import CompanyPage from './pages/CompanyPage';
import Analytics from './pages/Analytics';
import RiskProfiles from './pages/RiskProfiles';
import TimingIntelligence from './pages/TimingIntelligence';
import InsiderNetworks from './pages/InsiderNetworks';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/dashboard" element={
          <Layout>
            <EnhancedDashboard />
          </Layout>
        } />
        <Route path="/leaderboard" element={
          <Layout>
            <Leaderboard />
          </Layout>
        } />
        <Route path="/trades" element={
          <Layout>
            <RecentTrades />
          </Layout>
        } />
        <Route path="/analytics" element={
          <Layout>
            <Analytics />
          </Layout>
        } />
        <Route path="/risk-profiles" element={
          <Layout>
            <RiskProfiles />
          </Layout>
        } />
        <Route path="/networks" element={
          <Layout>
            <InsiderNetworks />
          </Layout>
        } />
        <Route path="/timing" element={
          <Layout>
            <TimingIntelligence />
          </Layout>
        } />
        <Route path="/portfolio" element={
          <Layout>
            <PortfolioLeaderboard />
          </Layout>
        } />
        <Route path="/traders/:traderId" element={
          <Layout>
            <TraderProfile />
          </Layout>
        } />
        <Route path="/companies/:ticker" element={
          <Layout>
            <CompanyPage />
          </Layout>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;