import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import './styles/globals.css';

// Pages
import Homepage from './pages/Homepage';
import EnhancedDashboard from './pages/EnhancedDashboard';
import PortfolioLeaderboard from './pages/PortfolioLeaderboard';
import CompanyPage from './pages/CompanyPage';
import InsiderProfile from './pages/InsiderProfile';
import LeaderboardPage from './components/pages/LeaderboardPage';
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
            <LeaderboardPage />
          </Layout>
        } />
        <Route path="/trades" element={
          <Layout>
            <div className="p-8">
              <h1 className="text-2xl font-bold">Recent Trades</h1>
              <p className="text-gray-600">This page is under construction.</p>
            </div>
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
        <Route path="/trader/:traderId" element={
          <Layout>
            <InsiderProfile />
          </Layout>
        } />
        <Route path="/company/:ticker" element={
          <Layout>
            <CompanyPage />
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