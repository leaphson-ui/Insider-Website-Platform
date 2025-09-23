import React, { createContext, useContext } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const theme = {
    colors: {
      primary: '#0a0a0a',
      secondary: '#111111',
      card: '#0f0f0f',
      text: {
        primary: '#ffffff',
        secondary: '#a3a3a3',
        muted: '#737373',
      },
      accent: {
        blue: '#3b82f6',
        green: '#10b981',
        red: '#ef4444',
      },
    },
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;