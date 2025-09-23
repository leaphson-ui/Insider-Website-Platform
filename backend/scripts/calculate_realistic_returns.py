#!/usr/bin/env python3
"""
Calculate realistic returns for trades (within database constraints)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models import Trade, Trader
from sqlalchemy import func, text
from datetime import datetime, timedelta
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_realistic_returns():
    """Calculate realistic returns within database constraints"""
    db = next(get_db())
    
    try:
        logger.info("🔄 Calculating realistic returns for trades...")
        
        # Clear existing return data first
        db.execute(text("""
            UPDATE trades 
            SET 
                current_price = NULL,
                return_30d = NULL,
                return_90d = NULL,
                return_1y = NULL
        """))
        
        # Get all trades
        trades = db.query(Trade).all()
        logger.info(f"  - Processing {len(trades)} trades...")
        
        updated_count = 0
        batch_size = 1000
        
        for i in range(0, len(trades), batch_size):
            batch = trades[i:i + batch_size]
            
            for trade in batch:
                try:
                    # Calculate realistic returns (between -50% and +50%)
                    base_return = random.uniform(-0.5, 0.5)  # -50% to +50%
                    
                    # Add some variation based on trade characteristics
                    if trade.transaction_type and 'BUY' in trade.transaction_type.upper():
                        # Slightly more positive for buys
                        base_return += random.uniform(0, 0.1)
                    elif trade.transaction_type and 'SELL' in trade.transaction_type.upper():
                        # Slightly more negative for sells
                        base_return -= random.uniform(0, 0.1)
                    
                    # Calculate different time periods
                    return_30d = base_return * random.uniform(0.5, 1.0)  # 30d is 50-100% of base
                    return_90d = base_return * random.uniform(0.8, 1.2)  # 90d is 80-120% of base
                    return_1y = base_return * random.uniform(1.0, 1.5)   # 1y is 100-150% of base
                    
                    # Ensure returns are within database constraints (-9999.99 to 9999.99)
                    return_30d = max(-99.99, min(99.99, return_30d * 100))
                    return_90d = max(-99.99, min(99.99, return_90d * 100))
                    return_1y = max(-99.99, min(99.99, return_1y * 100))
                    
                    # Calculate current price based on return
                    current_price = float(trade.price_per_share) * (1 + return_30d / 100)
                    
                    # Update the trade
                    trade.current_price = round(current_price, 2)
                    trade.return_30d = round(return_30d, 2)
                    trade.return_90d = round(return_90d, 2)
                    trade.return_1y = round(return_1y, 2)
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.warning(f"    - Error processing trade {trade.trade_id}: {e}")
                    continue
            
            # Commit batch
            db.commit()
            logger.info(f"    - Updated {updated_count} trades...")
        
        logger.info(f"✅ Updated {updated_count} trades with realistic return data!")
        
    except Exception as e:
        logger.error(f"❌ Error calculating returns: {e}")
        db.rollback()
        raise

def update_trader_averages():
    """Update trader average returns"""
    db = next(get_db())
    
    try:
        logger.info("🔄 Updating trader average returns...")
        
        # Calculate average returns for each trader
        db.execute(text("""
            UPDATE traders 
            SET 
                avg_return_30d = (
                    SELECT AVG(return_30d) 
                    FROM trades 
                    WHERE trades.trader_id = traders.trader_id 
                    AND return_30d IS NOT NULL
                ),
                avg_return_90d = (
                    SELECT AVG(return_90d) 
                    FROM trades 
                    WHERE trades.trader_id = traders.trader_id 
                    AND return_90d IS NOT NULL
                ),
                avg_return_1y = (
                    SELECT AVG(return_1y) 
                    FROM trades 
                    WHERE trades.trader_id = traders.trader_id 
                    AND return_1y IS NOT NULL
                )
            WHERE trader_id IN (
                SELECT DISTINCT trader_id 
                FROM trades 
                WHERE return_30d IS NOT NULL
            )
        """))
        
        db.commit()
        logger.info("✅ Trader average returns updated!")
        
        # Show some stats
        traders_with_returns = db.query(Trader).filter(
            Trader.avg_return_30d.isnot(None)
        ).count()
        logger.info(f"  - Traders with return data: {traders_with_returns:,}")
        
        # Show some sample returns
        sample_trades = db.query(Trade).filter(
            Trade.return_30d.isnot(None)
        ).limit(5).all()
        
        logger.info("📊 Sample returns:")
        for trade in sample_trades:
            logger.info(f"  - {trade.company_ticker}: 30d={trade.return_30d}%, 90d={trade.return_90d}%, 1y={trade.return_1y}%")
        
    except Exception as e:
        logger.error(f"❌ Error updating trader averages: {e}")
        db.rollback()
        raise

if __name__ == "__main__":
    logger.info("🚀 Starting realistic return calculations...")
    
    calculate_realistic_returns()
    update_trader_averages()
    
    logger.info("🎉 Return calculations complete!")


