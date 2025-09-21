import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChartBarIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../contexts/ThemeContext';

const Header = () => {
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useTheme();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'Leaderboard', href: '/leaderboard' },
    { name: 'Portfolio', href: '/portfolio' },
    { name: 'Recent Trades', href: '/trades' },
    { name: 'Networks', href: '/networks' },
    { name: 'Timing Intel', href: '/timing' },
  ];

  return (
    <header className="bg-secondary/80 backdrop-blur-md border-b border-default sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <Link to="/" className="flex items-center group">
              <ChartBarIcon className="h-8 w-8 text-brand-600 group-hover:text-brand-500 transition-colors" />
              <div className="ml-2">
                <div className="text-2xl font-bold text-primary">
                  Insider
                </div>
                <div className="text-xs text-secondary -mt-1">
                  Track. Analyze. Profit.
                </div>
              </div>
            </Link>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`${
                  location.pathname === item.href
                    ? 'border-brand-500 text-brand-600'
                    : 'border-transparent text-secondary hover:text-primary hover:border-default'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-all duration-200`}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          <div className="flex items-center space-x-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-tertiary border border-default hover:bg-secondary transition-all duration-200 group"
              aria-label="Toggle theme"
            >
              {isDarkMode ? (
                <SunIcon className="h-5 w-5 text-secondary group-hover:text-primary transition-colors" />
              ) : (
                <MoonIcon className="h-5 w-5 text-secondary group-hover:text-primary transition-colors" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
