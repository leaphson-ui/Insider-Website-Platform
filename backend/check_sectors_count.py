#!/usr/bin/env python3
"""
Quick script to check total sectors count
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from sqlalchemy import func
from app.models import Trader

def check_sectors_count():
    db = next(get_db())
    
    try:
        # Count total unique sectors (excluding 'Other')
        total_sectors = db.query(func.count(func.distinct(Trader.sector))).filter(
            Trader.sector.isnot(None),
            Trader.sector != 'Other'
        ).scalar()
        
        # Count sectors with 'Other'
        other_sectors = db.query(func.count(func.distinct(Trader.sector))).filter(
            Trader.sector == 'Other'
        ).scalar()
        
        # Get all unique sectors
        all_sectors = db.query(Trader.sector).filter(
            Trader.sector.isnot(None)
        ).distinct().all()
        
        print(f"Total sectors (excluding 'Other'): {total_sectors}")
        print(f"Sectors with 'Other': {other_sectors}")
        print(f"Total unique sectors: {len(all_sectors)}")
        print("\nAll sectors:")
        for sector in sorted([s[0] for s in all_sectors]):
            print(f"  - {sector}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_sectors_count()


