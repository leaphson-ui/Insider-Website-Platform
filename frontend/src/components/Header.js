import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Button from './ui/Button';

const Header = () => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/leaderboard', label: 'Leaderboard' },
    { path: '/trades', label: 'Recent Trades' },
    { path: '/networks', label: 'Networks' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-black sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo - Left */}
          <Link to="/" className="flex items-center no-underline">
            <div className="w-10 h-10 bg-yellow-400 flex items-center justify-center mr-4">
              <span className="text-black font-bold text-lg">IA</span>
            </div>
            <span className="text-xl font-bold text-white">Insider Alpha</span>
          </Link>
          
          {/* Nav Links - Center */}
          <nav className="flex items-center space-x-12">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="text-white text-sm font-medium flex items-center no-underline hover:no-underline"
              >
                {item.label}
                <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </Link>
            ))}
          </nav>
          
          {/* CTA Buttons - Right */}
          <div className="flex items-center space-x-3">
            <button className="bg-white text-black px-6 py-2 rounded-md text-sm font-medium">
              Start Trial
            </button>
            <button className="bg-gray-600 text-white px-6 py-2 rounded-md text-sm font-medium">
              Login
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;