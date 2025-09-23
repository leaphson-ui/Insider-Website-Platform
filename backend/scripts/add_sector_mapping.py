#!/usr/bin/env python3
"""
Add sector mapping to companies in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models import Trade, Trader
from sqlalchemy import func, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sector mapping based on common ticker patterns and company names
SECTOR_MAPPING = {
    # Technology
    'AAPL': 'Information Technology',
    'MSFT': 'Information Technology', 
    'GOOG': 'Information Technology',
    'GOOGL': 'Information Technology',
    'AMZN': 'Consumer Discretionary',
    'META': 'Information Technology',
    'FB': 'Information Technology',
    'TSLA': 'Consumer Discretionary',
    'NVDA': 'Information Technology',
    'CRM': 'Information Technology',
    'ORCL': 'Information Technology',
    'ADBE': 'Information Technology',
    'INTC': 'Information Technology',
    'CSCO': 'Information Technology',
    'IBM': 'Information Technology',
    'NOW': 'Information Technology',
    'SNOW': 'Information Technology',
    'DDOG': 'Information Technology',
    'ZM': 'Information Technology',
    'ANET': 'Information Technology',
    'ZI': 'Information Technology',
    'CVNA': 'Consumer Discretionary',
    'MRNA': 'Health Care',
    'TPL': 'Energy',
    'HAYN': 'Materials',
    'PGNY': 'Health Care',
    'SAM': 'Consumer Staples',
    'MORN': 'Financials',
    'UMBF': 'Financials',
    'PSMT': 'Consumer Discretionary',
    'SSTK': 'Information Technology',
    'ZS': 'Information Technology',
    'DDOG': 'Information Technology',
    
    # Financials
    'JPM': 'Financials',
    'BAC': 'Financials',
    'WFC': 'Financials',
    'GS': 'Financials',
    'MS': 'Financials',
    'C': 'Financials',
    'AXP': 'Financials',
    'BLK': 'Financials',
    'SCHW': 'Financials',
    'COF': 'Financials',
    
    # Health Care
    'JNJ': 'Health Care',
    'PFE': 'Health Care',
    'UNH': 'Health Care',
    'ABBV': 'Health Care',
    'MRK': 'Health Care',
    'TMO': 'Health Care',
    'ABT': 'Health Care',
    'DHR': 'Health Care',
    'BMY': 'Health Care',
    'AMGN': 'Health Care',
    
    # Consumer Discretionary
    'HD': 'Consumer Discretionary',
    'MCD': 'Consumer Discretionary',
    'NKE': 'Consumer Discretionary',
    'SBUX': 'Consumer Discretionary',
    'LOW': 'Consumer Discretionary',
    'TJX': 'Consumer Discretionary',
    'BKNG': 'Consumer Discretionary',
    'CMG': 'Consumer Discretionary',
    'ORLY': 'Consumer Discretionary',
    'AZO': 'Consumer Discretionary',
    
    # Consumer Staples
    'PG': 'Consumer Staples',
    'KO': 'Consumer Staples',
    'PEP': 'Consumer Staples',
    'WMT': 'Consumer Staples',
    'COST': 'Consumer Staples',
    'CL': 'Consumer Staples',
    'KMB': 'Consumer Staples',
    'GIS': 'Consumer Staples',
    'K': 'Consumer Staples',
    'SYY': 'Consumer Staples',
    
    # Energy
    'XOM': 'Energy',
    'CVX': 'Energy',
    'COP': 'Energy',
    'EOG': 'Energy',
    'SLB': 'Energy',
    'PXD': 'Energy',
    'MPC': 'Energy',
    'VLO': 'Energy',
    'PSX': 'Energy',
    'KMI': 'Energy',
    
    # Materials
    'LIN': 'Materials',
    'APD': 'Materials',
    'SHW': 'Materials',
    'ECL': 'Materials',
    'DD': 'Materials',
    'DOW': 'Materials',
    'PPG': 'Materials',
    'NEM': 'Materials',
    'FCX': 'Materials',
    'NUE': 'Materials',
    
    # Industrials
    'BA': 'Industrials',
    'CAT': 'Industrials',
    'GE': 'Industrials',
    'HON': 'Industrials',
    'UPS': 'Industrials',
    'LMT': 'Industrials',
    'RTX': 'Industrials',
    'MMM': 'Industrials',
    'DE': 'Industrials',
    'EMR': 'Industrials',
    
    # Utilities
    'NEE': 'Utilities',
    'DUK': 'Utilities',
    'SO': 'Utilities',
    'D': 'Utilities',
    'AEP': 'Utilities',
    'EXC': 'Utilities',
    'XEL': 'Utilities',
    'WEC': 'Utilities',
    'ES': 'Utilities',
    'PEG': 'Utilities',
    
    # Real Estate
    'AMT': 'Real Estate',
    'PLD': 'Real Estate',
    'CCI': 'Real Estate',
    'EQIX': 'Real Estate',
    'PSA': 'Real Estate',
    'EXR': 'Real Estate',
    'AVB': 'Real Estate',
    'EQR': 'Real Estate',
    'MAA': 'Real Estate',
    'UDR': 'Real Estate',
    
    # Communication Services
    'VZ': 'Communication Services',
    'T': 'Communication Services',
    'CMCSA': 'Communication Services',
    'DIS': 'Communication Services',
    'NFLX': 'Communication Services',
    'CHTR': 'Communication Services',
    'TMUS': 'Communication Services',
    'DISH': 'Communication Services',
    'LUMN': 'Communication Services',
    'VZ': 'Communication Services',
}

def add_sector_column():
    """Add sector column to traders table if it doesn't exist"""
    db = next(get_db())
    
    try:
        logger.info("🔄 Adding sector column to traders table...")
        
        # Add sector column if it doesn't exist
        db.execute(text("""
            ALTER TABLE traders 
            ADD COLUMN IF NOT EXISTS sector VARCHAR(50)
        """))
        
        db.commit()
        logger.info("✅ Sector column added!")
        
    except Exception as e:
        logger.error(f"❌ Error adding sector column: {e}")
        db.rollback()
        raise

def map_company_sectors():
    """Map companies to their sectors"""
    db = next(get_db())
    
    try:
        logger.info("🔄 Mapping companies to sectors...")
        
        # Update sectors based on ticker mapping
        for ticker, sector in SECTOR_MAPPING.items():
            result = db.execute(text("""
                UPDATE traders 
                SET sector = :sector 
                WHERE company_ticker = :ticker
            """), {"sector": sector, "ticker": ticker})
            
            if result.rowcount > 0:
                logger.info(f"  - Mapped {ticker} to {sector} ({result.rowcount} traders)")
        
        # For unmapped companies, try to infer sector from company name
        logger.info("  - Inferring sectors from company names...")
        
        # Technology companies
        tech_keywords = ['TECH', 'SOFTWARE', 'SYSTEMS', 'DATA', 'CLOUD', 'DIGITAL', 'CYBER']
        for keyword in tech_keywords:
            db.execute(text("""
                UPDATE traders 
                SET sector = 'Information Technology'
                WHERE sector IS NULL 
                AND (UPPER(company_name) LIKE :pattern OR UPPER(company_ticker) LIKE :pattern)
            """), {"pattern": f"%{keyword}%"})
        
        # Financial companies
        fin_keywords = ['BANK', 'FINANCIAL', 'INVESTMENT', 'CAPITAL', 'CREDIT', 'INSURANCE']
        for keyword in fin_keywords:
            db.execute(text("""
                UPDATE traders 
                SET sector = 'Financials'
                WHERE sector IS NULL 
                AND (UPPER(company_name) LIKE :pattern OR UPPER(company_ticker) LIKE :pattern)
            """), {"pattern": f"%{keyword}%"})
        
        # Health Care companies
        health_keywords = ['HEALTH', 'MEDICAL', 'PHARMA', 'BIO', 'CARE', 'LIFE', 'THERAPEUTICS']
        for keyword in health_keywords:
            db.execute(text("""
                UPDATE traders 
                SET sector = 'Health Care'
                WHERE sector IS NULL 
                AND (UPPER(company_name) LIKE :pattern OR UPPER(company_ticker) LIKE :pattern)
            """), {"pattern": f"%{keyword}%"})
        
        # Set remaining companies to "Other"
        db.execute(text("""
            UPDATE traders 
            SET sector = 'Other'
            WHERE sector IS NULL
        """))
        
        db.commit()
        logger.info("✅ Sector mapping complete!")
        
        # Show sector distribution
        result = db.execute(text("""
            SELECT sector, COUNT(*) as count
            FROM traders 
            GROUP BY sector 
            ORDER BY count DESC
        """)).fetchall()
        
        logger.info("📊 Sector distribution:")
        for row in result:
            logger.info(f"  - {row[0]}: {row[1]:,} companies")
        
    except Exception as e:
        logger.error(f"❌ Error mapping sectors: {e}")
        db.rollback()
        raise

if __name__ == "__main__":
    logger.info("🚀 Starting sector mapping...")
    
    add_sector_column()
    map_company_sectors()
    
    logger.info("🎉 Sector mapping complete!")


