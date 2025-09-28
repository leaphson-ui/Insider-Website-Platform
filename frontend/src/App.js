import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/globals.css';

// Pages
import Homepage from './pages/Homepage';
import Dashboard from './pages/Dashboard';
import EnhancedDashboard from './pages/EnhancedDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/dashboard" element={<EnhancedDashboard />} />
        <Route path="/dashboard-old" element={<Dashboard />} />
        <Route path="*" element={<Homepage />} />
      </Routes>
    </Router>
  );
}

export default App;