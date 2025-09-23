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

        {/* Navigation Links - Removed */}

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