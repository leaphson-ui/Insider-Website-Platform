#!/usr/bin/env python3
"""
Check Zuckerberg's trade data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models import Trader, Trade
from sqlalchemy import func

def check_zuckerberg():
    db = next(get_db())
    
    # Check Zuckerberg's actual trade count
    zuckerberg = db.query(Trader).filter(Trader.name.like('%Zuckerberg%')).first()
    if zuckerberg:
        print('🔍 Zuckerberg Trader Record:')
        print(f'  Trader ID: {zuckerberg.trader_id}')
        print(f'  Name: {zuckerberg.name}')
        print(f'  Company: {zuckerberg.company_ticker} ({zuckerberg.company_name})')
        print(f'  Total Trades (in record): {zuckerberg.total_trades}')
        
        # Count actual trades in database
        actual_trade_count = db.query(Trade).filter(Trade.trader_id == zuckerberg.trader_id).count()
        print(f'  Actual Trades in DB: {actual_trade_count}')
        
        # Get some sample trades
        sample_trades = db.query(Trade).filter(Trade.trader_id == zuckerberg.trader_id).order_by(Trade.transaction_date.desc()).limit(5).all()
        print('\n📊 Sample Recent Trades:')
        for trade in sample_trades:
            print(f'  {trade.transaction_date}: {trade.transaction_type} {trade.shares_traded} shares @ ${trade.price_per_share}')
    else:
        print('❌ Zuckerberg not found in database')
    
    db.close()

if __name__ == "__main__":
    check_zuckerberg()


