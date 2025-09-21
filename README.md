# 📊 Insider Alpha Platform

A real-time platform that tracks, analyzes, and ranks corporate insiders based on their trading performance.

## 🚀 Quick Start for Non-Coders

### Step 1: Get Your API Key
1. Go to [Polygon.io](https://polygon.io/pricing)
2. Sign up for an account
3. Choose a plan (Basic $99/month or Starter $199/month recommended)
4. Copy your API key from the dashboard

### Step 2: Run the Setup
```bash
./setup.sh
```

### Step 3: Add Your API Key
1. Open the file `backend/.env` in a text editor
2. Replace `your_polygon_api_key_here` with your actual API key
3. Save the file

### Step 4: Start the Platform
```bash
./run_dev.sh
```

### Step 5: View Your Platform
- Open your web browser
- Go to: http://localhost:3000
- You should see the Insider Alpha dashboard!

### Step 6: Load Data

**Option A: Real SEC Data (Recommended)**
```bash
./configure_real_data.sh
```

**Option B: Sample Data**
```bash
cd backend
source venv/bin/activate
python scripts/massive_data_generator.py
python scripts/performance_calc.py
```

## 🎯 What You'll See

### Dashboard
- Overview of platform statistics
- Top performing insiders
- Recent trading activity

### Leaderboard
- Ranked list of all insiders by performance
- Filter by minimum trades, company, etc.
- Click on any trader to see their profile

### Trader Profiles
- Individual insider performance metrics
- Complete trading history
- Return calculations over different time periods

### Recent Trades
- Latest insider trading activity
- Filter by company, time period
- See real-time performance of trades

## 🆘 Need Help?

**If something doesn't work:**
1. Make sure PostgreSQL is installed and running
2. Check that your API key is correct in `backend/.env`
3. Try running the setup script again: `./setup.sh`

**Common Issues:**
- "Database connection error" → PostgreSQL isn't running
- "API key invalid" → Check your Polygon.io API key
- "Port already in use" → Close other applications using ports 3000 or 8000

## 💰 Costs

**Polygon.io API:**
- Basic: $99/month (good for testing)
- Starter: $199/month (recommended for live use)
- Free tier: Very limited, may not work well

**Other costs:**
- Everything else is free (PostgreSQL, React, etc.)

## 🔍 Testing the Platform

1. **Check the Dashboard** - Should show stats and recent activity
2. **Browse the Leaderboard** - See top performing insiders
3. **Click on a Trader** - View detailed performance metrics
4. **Filter Recent Trades** - Try different companies (AAPL, MSFT, etc.)
5. **Watch for Updates** - Data refreshes as new trades come in

The platform tracks real insider trading data and calculates performance scores automatically!