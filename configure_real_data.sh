#!/bin/bash

# Configure Real SEC Data for Insider Alpha Platform

echo "🚀 Configuring Real SEC Insider Trading Data..."
echo "=" * 60

# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate

echo "📊 Step 1: Downloading and processing real SEC quarterly data..."
python scripts/automated_sec_data_manager.py

echo ""
echo "⚡ Step 2: Calculating performance scores with real stock prices..."
python scripts/performance_calc.py

echo ""
echo "✅ Configuration Complete!"
echo ""
echo "🎯 Your platform now has:"
echo "  - Real SEC insider trading data"
echo "  - Actual corporate insiders and their trades"
echo "  - Live stock price performance calculations"
echo "  - Professional-grade analytics"
echo ""
echo "🌐 View your platform at: http://localhost:3001"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "🔄 To update data regularly, run:"
echo "  python scripts/automated_sec_data_manager.py"
echo "  python scripts/performance_calc.py"
