import React from 'react';
import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <div className="navbar-logo">
          <Link to="/" className="logo-link">
            <div className="logo-container">
              <svg className="logo-icon" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <rect x="3" y="16" width="3" height="5"/>
                <rect x="7" y="12" width="3" height="9"/>
                <rect x="11" y="8" width="3" height="13"/>
                <rect x="15" y="4" width="3" height="17"/>
              </svg>
              <span>Insider</span>
            </div>
          </Link>
        </div>
        
        {/* Navigation Links - Centered */}
        <nav className="navbar-nav navbar-nav-centered">
          <Link to="/dashboard" className="nav-link">Dashboard</Link>
        </nav>
        
        {/* Auth Buttons - Right */}
        <div className="navbar-auth">
          <button className="auth-btn auth-btn-login">
            Log In
          </button>
          <button className="auth-btn auth-btn-signup">
            Sign Up
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navigation;