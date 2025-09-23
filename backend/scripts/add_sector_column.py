#!/usr/bin/env python3
"""
Add sector column to traders table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_sector_column():
    """Add sector column to traders table"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'traders' AND column_name = 'sector'
            """))
            
            if result.fetchone():
                logger.info("Sector column already exists")
                return
            
            # Add the sector column
            logger.info("Adding sector column to traders table...")
            conn.execute(text("""
                ALTER TABLE traders 
                ADD COLUMN sector VARCHAR(50)
            """))
            
            # Create index on sector column
            logger.info("Creating index on sector column...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_traders_sector 
                ON traders(sector)
            """))
            
            conn.commit()
            logger.info("✅ Successfully added sector column to traders table")
            
    except Exception as e:
        logger.error(f"❌ Error adding sector column: {str(e)}")
        raise

if __name__ == "__main__":
    add_sector_column()


