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
      </div>
    </header>
  );
};

export default Navigation;