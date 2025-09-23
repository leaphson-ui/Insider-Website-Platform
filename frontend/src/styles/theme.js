// Simple theme configuration
export const theme = {
  colors: {
    background: {
      primary: '#0a0a0a',
      secondary: '#111111',
      card: '#0f0f0f',
      hover: '#1a1a1a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a3a3a3',
      muted: '#737373',
    },
    accent: {
      blue: '#3b82f6',
      green: '#10b981',
      red: '#ef4444',
      yellow: '#f59e0b',
      purple: '#8b5cf6',
    },
    border: {
      primary: '#262626',
      light: '#404040',
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
  },
};

export default theme;