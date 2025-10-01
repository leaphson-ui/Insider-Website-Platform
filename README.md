# 📊 Insider Alpha Platform

A modern insider trading intelligence platform that provides real-time SEC Form 4 data, advanced analytics, and institutional-grade research tools.

## 🎯 Overview

Insider Alpha transforms complex SEC insider trading data into actionable intelligence. Track 10,000+ companies, 50,000+ insiders, and millions of transactions with powerful search, filtering, and analytics capabilities.

**Live Platform**: [https://insider-alpha-platform.vercel.app](https://insider-alpha-platform.vercel.app)

## ✨ Key Features

### 🔍 **Intelligent Search**
- Search by company name, ticker symbol, or insider name
- Real-time results from 1M+ transactions
- Smart autocomplete and search suggestions

### 📊 **Advanced Analytics**
- **Flow Sentiment** - Bullish/Bearish/Neutral market sentiment
- **Buy vs Sell Ratio** - Transaction volume breakdown
- **Buy/Sell Flow** - Dollar value of buy and sell transactions
- **Average Transaction Size** - Mean transaction value
- **Largest Transaction** - Biggest trades with context
- **Transaction Type Breakdown** - Purchase/Sale/Award distribution
- **Insider Role Distribution** - CEO/CFO/Director activity analysis

### 📈 **Comprehensive Dashboard**
- Compact, high-density table showing 30+ transactions at once
- Alternating row colors for easy scanning
- 10 data columns: Ticker, Transaction Value, Insider Name, Title, Company, Code, Shares, Price, Shares After, Date
- Color-coded transactions: Green (buy), Red (sell), Yellow (other)

### 🎛️ **Robust Filtering** (Flow Page)
- **Time Range**: 7d, 30d, 90d, YTD, or custom date range
- **Transaction Value**: Filter by dollar thresholds or custom min/max
- **Transaction Type**: Multi-select checkboxes for different transaction codes
- **Company**: Search by name or ticker symbol
- **Insider Role**: Filter by CEO, CFO, Director, Officer, President

### 📱 **Responsive Design**
- Mobile-optimized interface
- Performance-focused architecture
- Clean, professional UI following financial platform standards

## 🏗️ Tech Stack

### Frontend
- **Framework**: React.js (Create React App)
- **Styling**: Tailwind CSS + Custom CSS
- **Routing**: React Router v6
- **Icons**: Lucide React
- **Deployment**: Vercel

### Backend
- **Database**: Supabase (PostgreSQL)
- **Data Source**: SEC EDGAR (Form 4 filings)
- **Processing**: Python data pipeline
- **API**: Supabase REST API

### Data Processing
- **Language**: Python 3.x
- **Libraries**: Pandas, NumPy
- **Data Format**: TSV files from SEC EDGAR
- **Storage**: PostgreSQL with optimized indexes

## 📂 Project Structure

```
insider-alpha-platform/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── Navigation.js
│   │   │   ├── Pagination.js
│   │   │   └── ui/          # Base UI components
│   │   ├── pages/           # Page components
│   │   │   ├── Homepage.js
│   │   │   ├── UnifiedDashboard.js
│   │   │   └── FlowDashboard.js
│   │   ├── lib/             # Utilities
│   │   │   └── supabase.js  # Supabase client
│   │   └── styles/          # Global styles
│   │       └── globals.css
│   └── public/              # Static assets
├── data-processing/         # Python data pipeline
│   ├── processor_post_2023.py
│   ├── ARCHITECTURE_NOTES.md
│   └── README.md
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm
- Supabase account
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/leaphson-ui/Insider-Website-Platform.git
cd insider-alpha-platform
```

2. **Install frontend dependencies**
```bash
cd frontend
npm install
```

3. **Set up environment variables**

Create `frontend/.env` file:
```env
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

4. **Start development server**
```bash
npm start
```

Visit `http://localhost:3000` to see the platform.

### Production Build

```bash
cd frontend
npm run build
```

## 🗄️ Database Schema

### Main Table: `insider_transactions`

**Key Columns:**
- `company_name` - Company name
- `company_ticker` - Stock ticker symbol
- `insider_name` - Name of insider
- `insider_title` - Role (CEO, CFO, Director, etc.)
- `transaction_code` - SEC transaction code (P=Purchase, S=Sale, etc.)
- `transaction_shares` - Number of shares
- `transaction_price_per_share` - Price per share
- `calculated_transaction_value` - Total dollar value
- `shares_owned_following_transaction` - Shares owned after transaction
- `transaction_date` - Date of transaction
- `filing_date` - Date filed with SEC
- `quarter` - Quarter of data (e.g., "2024q4")

## 📊 SEC Transaction Codes

### Bullish/Buy Transactions
- **P** - Purchase (open market or private)
- **A** - Award (stock awards)
- **G** - Grant (stock grants)
- **M** - Exercise (option exercise)
- **I**, **Q**, **R**, **T**, **U**, **V**, **W**, **X**, **Y**, **Z** - Various acquisition types

### Bearish/Sell Transactions
- **S** - Sale (open market or private)
- **D** - Disposition (sale via derivative)
- **E** - Expiration (option expiration)

### Neutral/Other
- **C** - Conversion
- **F** - Payment of exercise price or tax
- **J**, **K**, **L**, **O**, **H** - Other types

## 🎨 Design System

### Color Palette
- **Background**: `#0A0A0A` (primary), `#111111` (secondary)
- **Card Background**: `#1C1C1C`
- **Accent Blue**: `#3B82F6`
- **Accent Green**: `#39FF14` (buys)
- **Accent Red**: `#EF4444` (sells)
- **Accent Yellow**: `#FFC233` (CTA, highlights)
- **Text Primary**: `#FFFFFF`
- **Text Secondary**: `#A3A3A3`

### Typography
- **Font Family**: Inter
- **Sizes**: 0.55rem (table headers) to 5xl (hero titles)

## 🔧 Development

### Available Scripts

**Frontend:**
- `npm start` - Start development server (port 3000)
- `npm run build` - Create production build
- `npm test` - Run tests

**Data Processing:**
- `python processor_post_2023.py` - Process SEC data files
- See `data-processing/README.md` for detailed instructions

### Key Components

**Navigation** (`Navigation.js`)
- Global navigation bar
- Links: Dashboard, Flow
- Auth buttons: Log In, Sign Up

**UnifiedDashboard** (`UnifiedDashboard.js`)
- Search hero section with popular searches
- Analytics cards
- Transaction table
- Conditional rendering based on search

**FlowDashboard** (`FlowDashboard.js`)
- Compact search bar with integrated filters
- 8 analytics cards in 2 rows
- Ultra-compact table (30+ rows visible)
- Alternating row colors
- Advanced filtering system

## 📈 Performance Optimizations

- **Client-side filtering** - Fast, responsive filtering without API calls
- **Pagination** - Efficient rendering of large datasets
- **Compact table design** - 40-50% more information density
- **Optimized CSS** - Minimal bundle size, no heavy animations
- **Search-first architecture** - Only loads data when needed
- **Supabase queries** - Optimized with `.limit()` and targeted filters

## 🚢 Deployment

### Vercel (Current)
Platform is deployed on Vercel with automatic builds on push to main branch.

**Configuration** (`vercel.json`):
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/build",
  "installCommand": "cd frontend && npm install",
  "framework": "create-react-app"
}
```

### Manual Deployment
```bash
cd frontend
npm run build
npx vercel --prod
```

## 🔐 Environment Variables

**Required:**
- `REACT_APP_SUPABASE_URL` - Supabase project URL
- `REACT_APP_SUPABASE_ANON_KEY` - Supabase anonymous key

**Optional:**
- `NODE_ENV` - Environment (development/production)

## 📊 Data Pipeline

### Current Data Coverage
- **Historical**: 2023-2024 data processed
- **Total Transactions**: 1M+ insider trades
- **Companies**: 10,000+ tracked
- **Insiders**: 50,000+ individuals

### Data Processing Flow
1. Download TSV files from SEC EDGAR
2. Process with Python pipeline (`processor_post_2023.py`)
3. Clean and transform data
4. Load into Supabase PostgreSQL
5. Frontend queries via Supabase client

## 🎯 Roadmap

### Completed ✅
- [x] Homepage with hero section and product showcase
- [x] Unified Dashboard with search and results
- [x] Flow Dashboard with compact table design
- [x] 8 analytics cards with real-time calculations
- [x] Search functionality with URL parameters
- [x] Pagination and records per page selector
- [x] Color-coded transaction types
- [x] Alternating row colors for readability
- [x] Filter system foundation (Time Range, Transaction Value)
- [x] Responsive navigation bar

### In Progress 🚧
- [ ] Complete filter system (Transaction Type, Company, Insider)
- [ ] Filter persistence and saved searches
- [ ] Active filter pills with remove buttons

### Planned 📋
- [ ] Real-time data updates
- [ ] Watchlist functionality
- [ ] Individual company/insider profile pages
- [ ] Time-series charts for trend visualization
- [ ] Alert system for unusual activity
- [ ] Export to CSV/PDF
- [ ] Mobile app (iOS/Android)
- [ ] API access for developers
- [ ] Authentication and user accounts

## 🤝 Contributing

This is a private project. For questions or collaboration inquiries, contact the project owner.

## 📄 License

All rights reserved. Proprietary and confidential.

## 🆘 Support

For technical issues:
1. Check the `data-processing/ARCHITECTURE_NOTES.md` for data pipeline details
2. Review `frontend/src/pages/` for component-specific documentation
3. Contact the development team

---

**Built with ❤️ for institutional-grade insider trading intelligence**

*Last updated: October 2025*