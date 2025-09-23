#!/usr/bin/env python3
"""
Quick test script to show what the Insider Alpha Platform will do
This runs without needing the full setup - just to demonstrate the concept
"""

import json
from datetime import datetime, date
from decimal import Decimal

# Simulate some insider trading data (this would normally come from Polygon.io)
SAMPLE_DATA = [
    {
        "trader_name": "Tim Cook",
        "title": "CEO",
        "company": "Apple Inc.",
        "ticker": "AAPL",
        "trades": [
            {"date": "2024-01-15", "type": "BUY", "shares": 10000, "price": 185.50, "current_price": 225.00},
            {"date": "2024-02-20", "type": "BUY", "shares": 5000, "price": 190.25, "current_price": 225.00},
            {"date": "2024-03-10", "type": "SELL", "shares": 3000, "price": 210.00, "current_price": 225.00}
        ]
    },
    {
        "trader_name": "Satya Nadella", 
        "title": "CEO",
        "company": "Microsoft Corporation",
        "ticker": "MSFT",
        "trades": [
            {"date": "2024-01-10", "type": "BUY", "shares": 8000, "price": 375.00, "current_price": 420.00},
            {"date": "2024-02-15", "type": "BUY", "shares": 12000, "price": 385.50, "current_price": 420.00}
        ]
    },
    {
        "trader_name": "Jensen Huang",
        "title": "CEO", 
        "company": "NVIDIA Corporation",
        "ticker": "NVDA",
        "trades": [
            {"date": "2024-01-05", "type": "BUY", "shares": 15000, "price": 520.00, "current_price": 875.00},
            {"date": "2024-01-25", "type": "SELL", "shares": 5000, "price": 650.00, "current_price": 875.00}
        ]
    }
]

def calculate_performance(trades):
    """Calculate performance metrics for a trader's buy trades"""
    buy_trades = [t for t in trades if t["type"] == "BUY"]
    if not buy_trades:
        return {"total_return": 0, "win_rate": 0, "total_profit": 0}
    
    total_profit = 0
    winning_trades = 0
    
    for trade in buy_trades:
        profit_per_share = trade["current_price"] - trade["price"]
        trade_profit = profit_per_share * trade["shares"]
        total_profit += trade_profit
        
        if profit_per_share > 0:
            winning_trades += 1
    
    win_rate = (winning_trades / len(buy_trades)) * 100
    avg_return = (sum((t["current_price"] - t["price"]) / t["price"] * 100 for t in buy_trades) / len(buy_trades))
    
    return {
        "avg_return": avg_return,
        "win_rate": win_rate, 
        "total_profit": total_profit,
        "total_trades": len(trades)
    }

def calculate_performance_score(metrics):
    """Calculate composite performance score"""
    return (metrics["avg_return"] * 0.4) + (metrics["win_rate"] * 0.3) + (min(metrics["total_trades"], 10) * 0.3)

def main():
    print("🚀 INSIDER ALPHA PLATFORM - DEMO")
    print("=" * 50)
    print()
    
    # Calculate performance for each trader
    trader_performance = []
    
    for trader_data in SAMPLE_DATA:
        metrics = calculate_performance(trader_data["trades"])
        score = calculate_performance_score(metrics)
        
        trader_performance.append({
            "name": trader_data["trader_name"],
            "title": trader_data["title"],
            "company": trader_data["company"],
            "ticker": trader_data["ticker"],
            "score": score,
            **metrics
        })
    
    # Sort by performance score
    trader_performance.sort(key=lambda x: x["score"], reverse=True)
    
    # Display leaderboard
    print("📊 TOP PERFORMING INSIDERS")
    print("-" * 50)
    print(f"{'Rank':<4} {'Name':<15} {'Company':<8} {'Avg Return':<12} {'Win Rate':<10} {'Profit':<15} {'Score':<8}")
    print("-" * 80)
    
    for i, trader in enumerate(trader_performance, 1):
        profit_str = f"${trader['total_profit']:,.0f}"
        print(f"{i:<4} {trader['name'][:14]:<15} {trader['ticker']:<8} "
              f"{trader['avg_return']:>8.1f}%    {trader['win_rate']:>6.1f}%    "
              f"{profit_str:>12}  {trader['score']:>6.1f}")
    
    print()
    print("🔍 DETAILED ANALYSIS")
    print("-" * 50)
    
    # Show detailed analysis for top performer
    top_trader = trader_performance[0]
    top_trader_data = next(t for t in SAMPLE_DATA if t["trader_name"] == top_trader["name"])
    
    print(f"\n👑 TOP PERFORMER: {top_trader['name']}")
    print(f"   Title: {top_trader['title']}")
    print(f"   Company: {top_trader['company']} ({top_trader['ticker']})")
    print(f"   Performance Score: {top_trader['score']:.1f}")
    print(f"   Average Return: {top_trader['avg_return']:.1f}%")
    print(f"   Win Rate: {top_trader['win_rate']:.1f}%")
    print(f"   Total Profit: ${top_trader['total_profit']:,.0f}")
    
    print(f"\n📈 RECENT TRADES:")
    for trade in top_trader_data["trades"]:
        profit_loss = (trade["current_price"] - trade["price"]) * trade["shares"] if trade["type"] == "BUY" else 0
        status = "📈" if profit_loss > 0 else "📉" if profit_loss < 0 else "➡️"
        
        print(f"   {trade['date']} | {trade['type']:<4} | {trade['shares']:>6,} shares @ ${trade['price']:<7.2f} | "
              f"Current: ${trade['current_price']:.2f} | P&L: ${profit_loss:>8,.0f} {status}")
    
    print()
    print("🎯 WHAT THE FULL PLATFORM WILL DO:")
    print("-" * 50)
    print("✅ Track 1000+ corporate insiders in real-time")
    print("✅ Calculate performance scores automatically") 
    print("✅ Show interactive charts and graphs")
    print("✅ Filter by company, time period, trade size")
    print("✅ Get alerts when top performers make new trades")
    print("✅ Access via beautiful web dashboard")
    print("✅ Mobile-friendly responsive design")
    print()
    print("💡 This demo shows the core concept with sample data.")
    print("   The real platform will use live data from Polygon.io API!")
    print()
    print("🚀 Ready to see the real platform? Follow the setup instructions!")

if __name__ == "__main__":
    main()


