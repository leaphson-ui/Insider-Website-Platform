#!/usr/bin/env python3
"""
Comprehensive Data Quality Fix for SEC Form 4 Data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from sqlalchemy import text
import re
from datetime import datetime, date

def fix_data_quality():
    """Fix all identified data quality issues"""
    db = SessionLocal()
    
    print("=" * 80)
    print("FIXING SEC FORM 4 DATA QUALITY ISSUES")
    print("=" * 80)
    
    try:
        # 1. Fix corrupted tickers
        print("\n1. FIXING CORRUPTED TICKERS:")
        print("-" * 40)
        
        # Map known corrupted tickers to correct ones
        ticker_fixes = {
            'MUSKEL': 'TSLA',    # Elon Musk -> Tesla
            'BEZOJE': 'AMZN',    # Jeff Bezos -> Amazon  
            'BUFFWA': 'BRK.A',   # Warren Buffett -> Berkshire
            'COOKTI': 'AAPL',    # Tim Cook -> Apple
            'PICHAI': 'GOOGL',   # Sundar Pichai -> Google
            'NADELSA': 'MSFT',   # Satya Nadella -> Microsoft
        }
        
        for bad_ticker, good_ticker in ticker_fixes.items():
            # Fix in trades table
            result = db.execute(text("""
                UPDATE trades 
                SET company_ticker = :good_ticker 
                WHERE company_ticker = :bad_ticker
            """), {"good_ticker": good_ticker, "bad_ticker": bad_ticker})
            
            # Fix in traders table  
            result2 = db.execute(text("""
                UPDATE traders 
                SET company_ticker = :good_ticker 
                WHERE company_ticker = :bad_ticker
            """), {"good_ticker": good_ticker, "bad_ticker": bad_ticker})
            
            print(f"  Fixed {bad_ticker} -> {good_ticker}")
        
        # 2. Fix future dates (clearly corrupted)
        print("\n2. FIXING FUTURE DATES:")
        print("-" * 40)
        
        future_dates = db.execute(text("""
            SELECT COUNT(*) 
            FROM trades 
            WHERE transaction_date > CURRENT_DATE
        """)).fetchone()[0]
        
        print(f"Found {future_dates:,} trades with future dates")
        
        if future_dates > 0:
            # Cap dates at today
            db.execute(text("""
                UPDATE trades 
                SET transaction_date = CURRENT_DATE 
                WHERE transaction_date > CURRENT_DATE
            """))
            print("  Fixed future dates to current date")
        
        # 3. Fix NULL/nan titles
        print("\n3. FIXING NULL/NAN TITLES:")
        print("-" * 40)
        
        # Update based on common patterns
        title_fixes = [
            ("UPDATE traders SET title = 'Chief Executive Officer' WHERE name ILIKE '%elon musk%'", "Elon Musk CEO"),
            ("UPDATE traders SET title = 'Chairman & CEO' WHERE name ILIKE '%bezos%'", "Bezos titles"),
            ("UPDATE traders SET title = 'Chairman & CEO' WHERE name ILIKE '%buffett%'", "Buffett titles"),
            ("UPDATE traders SET title = 'Chief Executive Officer' WHERE name ILIKE '%cook%' AND company_ticker = 'AAPL'", "Tim Cook"),
            ("UPDATE traders SET title = 'Executive' WHERE title IS NULL OR title = 'nan'", "Generic executives"),
        ]
        
        for query, description in title_fixes:
            result = db.execute(text(query))
            print(f"  {description}: Fixed {result.rowcount} records")
        
        # 4. Recalculate trader aggregations
        print("\n4. RECALCULATING TRADER AGGREGATIONS:")
        print("-" * 40)
        
        db.execute(text("""
            UPDATE traders 
            SET 
                total_trades = subq.trade_count,
                total_profit_loss = subq.total_value
            FROM (
                SELECT 
                    trader_id,
                    COUNT(*) as trade_count,
                    SUM(total_value) as total_value
                FROM trades 
                WHERE total_value > 0
                GROUP BY trader_id
            ) subq
            WHERE traders.trader_id = subq.trader_id
        """))
        
        print("  Recalculated all trader aggregations")
        
        # 5. Remove obvious data errors
        print("\n5. REMOVING DATA ERRORS:")
        print("-" * 40)
        
        # Remove trades with impossible values
        removed = db.execute(text("""
            DELETE FROM trades 
            WHERE total_value <= 0 
               OR shares_traded <= 0 
               OR price_per_share <= 0
               OR price_per_share > 50000  -- No stock costs $50K per share
        """)).rowcount
        
        print(f"  Removed {removed:,} trades with impossible values")
        
        # 6. Commit all changes
        db.commit()
        print(f"\n✅ ALL DATA QUALITY FIXES COMMITTED")
        
        # 7. Final validation
        print("\n6. POST-FIX VALIDATION:")
        print("-" * 40)
        
        final_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_trades,
                COUNT(DISTINCT trader_id) as unique_traders,
                COUNT(DISTINCT company_ticker) as unique_tickers,
                MIN(transaction_date) as earliest,
                MAX(transaction_date) as latest,
                SUM(CASE WHEN title IS NULL OR title = 'nan' THEN 1 ELSE 0 END) as null_titles
            FROM trades t
            JOIN traders tr ON t.trader_id = tr.trader_id
        """)).fetchone()
        
        print(f"Final Stats:")
        print(f"  Total Trades: {final_stats[0]:,}")
        print(f"  Unique Traders: {final_stats[1]:,}")
        print(f"  Unique Tickers: {final_stats[2]:,}")
        print(f"  Date Range: {final_stats[3]} to {final_stats[4]}")
        print(f"  NULL Titles: {final_stats[5]:,}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ ERROR: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_data_quality()


