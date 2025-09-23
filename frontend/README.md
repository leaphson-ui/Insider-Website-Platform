# Insider Alpha Frontend

A clean, simple React frontend for the Insider Alpha Platform.

## 🎨 Design System

### Colors
- **Primary**: Dark theme with consistent color palette
- **Background**: `#0a0a0a` (primary), `#111111` (secondary), `#0f0f0f` (cards)
- **Text**: `#ffffff` (primary), `#a3a3a3` (secondary), `#737373` (muted)
- **Accents**: Blue (`#3b82f6`), Green (`#10b981`), Red (`#ef4444`)

### Typography
- **Font**: Inter (Google Fonts)
- **Sizes**: xs (12px) to 3xl (30px)
- **Weights**: 400 (normal) to 700 (bold)

### Components
- **Card**: Consistent card styling with header/body
- **Button**: Primary and secondary variants
- **DataTable**: Responsive table with loading states
- **StatsCard**: Display key metrics with trends

## 🚀 Getting Started

```bash
npm install
npm start
```

Visit `http://localhost:3001` to view the application.

## 📁 Structure

```
src/
├── components/
│   ├── ui/           # Reusable UI components
│   ├── Header.js     # Navigation header
│   └── Layout.js     # Page layout wrapper
├── pages/            # Page components
├── styles/
│   ├── globals.css   # Global styles and design system
│   └── theme.js      # Theme configuration
├── utils/
│   ├── api.js        # API functions
│   └── formatters.js # Data formatting utilities
└── contexts/         # React contexts
```

## ✨ Features

- **Consistent Design**: Single source of truth for colors, fonts, spacing
- **Responsive**: Mobile-first responsive design
- **Performance**: Optimized components with loading states
- **Accessibility**: Proper semantic HTML and keyboard navigation
- **Clean Code**: Simple, maintainable component structure

## 🎯 Key Improvements

1. **Simplified CSS**: Removed complex Tailwind config, using pure CSS variables
2. **Consistent Components**: All components follow the same design patterns
3. **Better Organization**: Clear separation of concerns
4. **Performance**: Removed unnecessary dependencies and complex animations
5. **Maintainability**: Easy to understand and modify code structure


