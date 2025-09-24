import React from 'react';
import { Link } from 'react-router-dom';

const Navigation = () => {
  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <div className="navbar-logo">
          <Link to="/" className="logo-link">
            Insider Alpha
          </Link>
        </div>
        
        {/* Navigation Links */}
        <nav className="navbar-nav">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/dashboard" className="nav-link">Dashboard</Link>
        </nav>
      </div>
    </header>
  );
};

export default Navigation;