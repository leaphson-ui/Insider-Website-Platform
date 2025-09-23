#!/usr/bin/env python3
"""
Comprehensive Data Quality Audit for SEC Form 4 Data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text
import pandas as pd
from datetime import datetime

def run_comprehensive_audit():
    """Run complete data quality audit"""
    db = SessionLocal()
    
    print("=" * 80)
    print("COMPREHENSIVE SEC FORM 4 DATA QUALITY AUDIT")
    print("=" * 80)
    
    # 1. Basic data statistics
    print("\n1. BASIC DATA INVENTORY:")
    print("-" * 40)
    
    stats = db.execute(text("""
        SELECT 
            (SELECT COUNT(*) FROM trades) as total_trades,
            (SELECT COUNT(*) FROM traders) as total_traders,
            (SELECT COUNT(DISTINCT trader_id) FROM trades) as active_traders,
            (SELECT MIN(transaction_date) FROM trades) as earliest_trade,
            (SELECT MAX(transaction_date) FROM trades) as latest_trade,
            (SELECT COUNT(DISTINCT company_ticker) FROM trades) as unique_tickers
    """)).fetchone()
    
    print(f"Total Trades: {stats[0]:,}")
    print(f"Total Traders: {stats[1]:,}")
    print(f"Active Traders: {stats[2]:,}")
    print(f"Date Range: {stats[3]} to {stats[4]}")
    print(f"Unique Tickers: {stats[5]:,}")
    
    # 2. Data quality issues
    print("\n2. DATA QUALITY ISSUES:")
    print("-" * 40)
    
    # Check for null values
    null_checks = db.execute(text("""
        SELECT 
            'trades' as table_name,
            SUM(CASE WHEN trader_id IS NULL THEN 1 ELSE 0 END) as null_trader_id,
            SUM(CASE WHEN company_ticker IS NULL THEN 1 ELSE 0 END) as null_ticker,
            SUM(CASE WHEN transaction_date IS NULL THEN 1 ELSE 0 END) as null_date,
            SUM(CASE WHEN transaction_type IS NULL THEN 1 ELSE 0 END) as null_type,
            SUM(CASE WHEN shares_traded IS NULL THEN 1 ELSE 0 END) as null_shares,
            SUM(CASE WHEN price_per_share IS NULL THEN 1 ELSE 0 END) as null_price,
            SUM(CASE WHEN total_value IS NULL THEN 1 ELSE 0 END) as null_value
        FROM trades
        UNION ALL
        SELECT 
            'traders' as table_name,
            SUM(CASE WHEN trader_id IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN company_ticker IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN name IS NULL THEN 1 ELSE 0 END),
            SUM(CASE WHEN title IS NULL OR title = 'nan' THEN 1 ELSE 0 END),
            0, 0, 0
        FROM traders
    """)).fetchall()
    
    for row in null_checks:
        print(f"{row[0]}: trader_id={row[1]}, ticker={row[2]}, date/name={row[3]}, type/title={row[4]}")
    
    # 3. Duplicate detection
    print("\n3. DUPLICATE ENTITY DETECTION:")
    print("-" * 40)
    
    duplicates = db.execute(text("""
        WITH name_similarities AS (
            SELECT 
                name,
                company_ticker,
                COUNT(*) as duplicate_count,
                ARRAY_AGG(trader_id) as trader_ids,
                ARRAY_AGG(title) as titles
            FROM traders
            WHERE name IS NOT NULL
            GROUP BY UPPER(TRIM(name)), company_ticker
            HAVING COUNT(*) > 1
        )
        SELECT * FROM name_similarities
        ORDER BY duplicate_count DESC
        LIMIT 10
    """)).fetchall()
    
    print(f"Found {len(duplicates)} potential duplicate groups:")
    for row in duplicates:
        print(f"  '{row[0][:30]}' ({row[1]}) - {row[2]} duplicates - IDs: {row[3][:5]}")
    
    # 4. Aggregation validation
    print("\n4. AGGREGATION VALIDATION:")
    print("-" * 40)
    
    # Check if trader totals match actual trade counts
    agg_check = db.execute(text("""
        SELECT 
            tr.trader_id,
            tr.name,
            tr.total_trades as reported_trades,
            COUNT(t.trade_id) as actual_trades,
            tr.total_profit_loss as reported_pnl
        FROM traders tr
        LEFT JOIN trades t ON tr.trader_id = t.trader_id
        WHERE tr.total_trades > 1000  -- Focus on high-volume traders
        GROUP BY tr.trader_id, tr.name, tr.total_trades, tr.total_profit_loss
        ORDER BY ABS(tr.total_trades - COUNT(t.trade_id)) DESC
        LIMIT 10
    """)).fetchall()
    
    print("Traders with aggregation mismatches:")
    for row in agg_check:
        mismatch = abs(row[2] - row[3])
        print(f"  {row[1][:25]:<25} | Reported: {row[2]:>8,} | Actual: {row[3]:>8,} | Diff: {mismatch:>8,}")
    
    # 5. Transaction type analysis
    print("\n5. TRANSACTION TYPE DISTRIBUTION:")
    print("-" * 40)
    
    trans_types = db.execute(text("""
        SELECT 
            transaction_type,
            COUNT(*) as count,
            COUNT(DISTINCT trader_id) as unique_traders,
            AVG(total_value) as avg_value,
            MIN(transaction_date) as earliest,
            MAX(transaction_date) as latest
        FROM trades 
        WHERE total_value > 0
        GROUP BY transaction_type
        ORDER BY count DESC
    """)).fetchall()
    
    for row in trans_types:
        print(f"  {row[0]:<15} | {row[1]:>8,} trades | {row[2]:>6,} traders | ${row[3]:>12,.0f} avg")
    
    # 6. Company ticker analysis
    print("\n6. COMPANY TICKER ISSUES:")
    print("-" * 40)
    
    ticker_issues = db.execute(text("""
        SELECT 
            company_ticker,
            COUNT(DISTINCT trader_id) as unique_traders,
            COUNT(*) as trade_count,
            MIN(LENGTH(company_ticker)) as min_len,
            MAX(LENGTH(company_ticker)) as max_len
        FROM trades
        WHERE company_ticker IS NOT NULL
        GROUP BY company_ticker
        HAVING LENGTH(company_ticker) > 6 OR LENGTH(company_ticker) < 2
        ORDER BY trade_count DESC
        LIMIT 10
    """)).fetchall()
    
    print("Suspicious tickers (too long/short):")
    for row in ticker_issues:
        print(f"  {row[0]:<15} | {row[1]:>4} traders | {row[2]:>6,} trades | Len: {row[3]}-{row[4]}")
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE - ISSUES IDENTIFIED")
    print("=" * 80)
    
    db.close()

if __name__ == "__main__":
    run_comprehensive_audit()


