import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import Header from './components/Header';
import Homepage from './pages/Homepage';
import Dashboard from './pages/Dashboard';
import EnhancedDashboard from './pages/EnhancedDashboard';
import Leaderboard from './pages/Leaderboard';
import TraderProfile from './pages/TraderProfile';
import RecentTrades from './pages/RecentTrades';
import InsiderNetworks from './pages/InsiderNetworks';
import TimingIntelligence from './pages/TimingIntelligence';
import PortfolioLeaderboard from './pages/PortfolioLeaderboard';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-primary transition-colors duration-300">
          <Header />
          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/dashboard" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <EnhancedDashboard />
              </main>
            } />
            <Route path="/simple-dashboard" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <Dashboard />
              </main>
            } />
            <Route path="/leaderboard" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <Leaderboard />
              </main>
            } />
            <Route path="/traders/:traderId" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <TraderProfile />
              </main>
            } />
            <Route path="/trades" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <RecentTrades />
              </main>
            } />
            <Route path="/networks" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <InsiderNetworks />
              </main>
            } />
            <Route path="/timing" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <TimingIntelligence />
              </main>
            } />
            <Route path="/portfolio" element={
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <PortfolioLeaderboard />
              </main>
            } />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
