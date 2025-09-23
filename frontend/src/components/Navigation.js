import React from 'react';
import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <div className="navbar-logo">
          <Link to="/" className="logo-link">
            Insider
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="navbar-nav">
          <Link to="/dashboard" className="nav-link">
            Dashboard
          </Link>
          <Link to="/leaderboard" className="nav-link">
            Leaderboard
          </Link>
          <Link to="/trades" className="nav-link">
            Recent Trades
          </Link>
          <Link to="/analytics" className="nav-link">
            Analytics
          </Link>
          <Link to="/risk-profiles" className="nav-link">
            Risk Profiles
          </Link>
          <Link to="/timing" className="nav-link">
            Timing Intel
          </Link>
          <Link to="/networks" className="nav-link">
            Networks
          </Link>
        </nav>

        {/* Call-to-Action Buttons */}
        <div className="navbar-actions">
          <Link to="/trial" className="btn-start-trial">
            Start Trial
          </Link>
          <Link to="/login" className="btn-login">
            Login
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Navigation;