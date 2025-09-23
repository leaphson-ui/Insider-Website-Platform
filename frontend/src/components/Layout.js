import React from 'react';
import Navigation from './Navigation';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-primary">
      <Navigation />
      <main className="container py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;