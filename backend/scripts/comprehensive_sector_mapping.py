#!/usr/bin/env python3
"""
Comprehensive sector mapping for all companies in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.models import Trader
from sqlalchemy import func, text
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive sector mapping based on company names and business descriptions
def get_sector_from_company_info(ticker, company_name):
    """Determine sector from company name and ticker"""
    name_lower = company_name.lower()
    ticker_lower = ticker.lower()
    
    # Health Care & Pharmaceuticals
    health_keywords = [
        'health', 'medical', 'pharma', 'biotech', 'drug', 'therapeutic', 'clinical', 'hospital',
        'care', 'wellness', 'diagnostic', 'surgical', 'device', 'vaccine', 'cancer', 'oncology',
        'cardio', 'neuro', 'ortho', 'dental', 'vision', 'mental', 'behavioral', 'rehab'
    ]
    if any(keyword in name_lower for keyword in health_keywords):
        return 'Health Care'
    
    # Financial Services
    financial_keywords = [
        'bank', 'financial', 'credit', 'loan', 'mortgage', 'insurance', 'investment', 'capital',
        'fund', 'trust', 'bancorp', 'bancshares', 'banc', 'savings', 'mutual', 'hedge',
        'asset', 'wealth', 'advisory', 'broker', 'trading', 'exchange', 'clearing', 'payment'
    ]
    if any(keyword in name_lower for keyword in financial_keywords):
        return 'Financials'
    
    # Technology
    tech_keywords = [
        'software', 'technology', 'tech', 'digital', 'data', 'cloud', 'cyber', 'security',
        'network', 'internet', 'platform', 'system', 'solution', 'service', 'computing',
        'artificial', 'intelligence', 'machine', 'learning', 'analytics', 'information',
        'communication', 'telecom', 'wireless', 'broadband', 'fiber', 'satellite'
    ]
    if any(keyword in name_lower for keyword in tech_keywords):
        return 'Information Technology'
    
    # Energy & Oil
    energy_keywords = [
        'energy', 'oil', 'gas', 'petroleum', 'fuel', 'power', 'electric', 'utility', 'renewable',
        'solar', 'wind', 'nuclear', 'coal', 'drilling', 'exploration', 'pipeline', 'refining',
        'chemical', 'plastics', 'materials', 'mining', 'metals', 'steel', 'aluminum'
    ]
    if any(keyword in name_lower for keyword in energy_keywords):
        return 'Energy'
    
    # Consumer Discretionary
    consumer_disc_keywords = [
        'retail', 'store', 'shop', 'mall', 'restaurant', 'hotel', 'travel', 'entertainment',
        'media', 'broadcast', 'publishing', 'gaming', 'sports', 'fitness', 'automotive',
        'auto', 'car', 'truck', 'vehicle', 'transportation', 'logistics', 'shipping',
        'airline', 'cruise', 'casino', 'gaming', 'leisure', 'recreation'
    ]
    if any(keyword in name_lower for keyword in consumer_disc_keywords):
        return 'Consumer Discretionary'
    
    # Consumer Staples
    staples_keywords = [
        'food', 'beverage', 'grocery', 'supermarket', 'consumer', 'household', 'personal',
        'care', 'beauty', 'cosmetic', 'tobacco', 'alcohol', 'wine', 'beer', 'spirits',
        'packaging', 'container', 'paper', 'tissue', 'cleaning', 'hygiene'
    ]
    if any(keyword in name_lower for keyword in staples_keywords):
        return 'Consumer Staples'
    
    # Industrials
    industrial_keywords = [
        'industrial', 'manufacturing', 'aerospace', 'defense', 'military', 'aviation',
        'construction', 'engineering', 'machinery', 'equipment', 'tool', 'automation',
        'logistics', 'supply', 'chain', 'distribution', 'warehouse', 'shipping',
        'railroad', 'trucking', 'freight', 'cargo', 'delivery', 'postal'
    ]
    if any(keyword in name_lower for keyword in industrial_keywords):
        return 'Industrials'
    
    # Materials
    materials_keywords = [
        'materials', 'chemical', 'plastic', 'polymer', 'resin', 'coating', 'paint',
        'adhesive', 'sealant', 'metal', 'steel', 'aluminum', 'copper', 'mining',
        'quarry', 'aggregate', 'cement', 'concrete', 'glass', 'ceramic', 'composite'
    ]
    if any(keyword in name_lower for keyword in materials_keywords):
        return 'Materials'
    
    # Real Estate
    real_estate_keywords = [
        'real estate', 'reit', 'property', 'properties', 'development', 'construction',
        'building', 'office', 'retail', 'residential', 'commercial', 'industrial',
        'warehouse', 'storage', 'apartment', 'condo', 'hotel', 'hospitality'
    ]
    if any(keyword in name_lower for keyword in real_estate_keywords):
        return 'Real Estate'
    
    # Utilities
    utility_keywords = [
        'utility', 'utilities', 'electric', 'power', 'gas', 'water', 'sewer',
        'waste', 'renewable', 'solar', 'wind', 'nuclear', 'hydro', 'thermal'
    ]
    if any(keyword in name_lower for keyword in utility_keywords):
        return 'Utilities'
    
    # Communication Services
    comm_keywords = [
        'communication', 'telecom', 'wireless', 'broadband', 'cable', 'satellite',
        'media', 'broadcast', 'publishing', 'entertainment', 'gaming', 'social',
        'advertising', 'marketing', 'content', 'streaming', 'digital'
    ]
    if any(keyword in name_lower for keyword in comm_keywords):
        return 'Communication Services'
    
    return 'Other'

def comprehensive_sector_mapping():
    """Apply comprehensive sector mapping to all traders"""
    try:
        db = next(get_db())
        
        logger.info("🚀 Starting comprehensive sector mapping...")
        
        # Get all unique companies
        companies = db.query(Trader.company_ticker, Trader.company_name).distinct().all()
        logger.info(f"📊 Found {len(companies)} unique companies to categorize")
        
        # Track mapping results
        sector_counts = {}
        mapped_count = 0
        
        for ticker, company_name in companies:
            # Get current sector
            current_trader = db.query(Trader).filter(Trader.company_ticker == ticker).first()
            if not current_trader:
                continue
                
            current_sector = current_trader.sector
            
            # Only update if currently "Other" or None
            if current_sector in [None, 'Other']:
                new_sector = get_sector_from_company_info(ticker, company_name)
                
                if new_sector != 'Other':
                    # Update all traders for this company
                    db.query(Trader).filter(Trader.company_ticker == ticker).update({
                        'sector': new_sector
                    })
                    
                    sector_counts[new_sector] = sector_counts.get(new_sector, 0) + 1
                    mapped_count += 1
                    
                    if mapped_count % 100 == 0:
                        logger.info(f"  - Mapped {mapped_count} companies...")
            else:
                # Count existing sectors
                sector_counts[current_sector] = sector_counts.get(current_sector, 0) + 1
        
        db.commit()
        
        logger.info(f"✅ Comprehensive sector mapping complete!")
        logger.info(f"📊 Mapped {mapped_count} additional companies")
        logger.info(f"📈 Final sector distribution:")
        
        # Get final counts from database
        final_counts = db.query(Trader.sector, func.count(Trader.trader_id)).group_by(Trader.sector).order_by(func.count(Trader.trader_id).desc()).all()
        
        for sector, count in final_counts:
            logger.info(f"  - {sector}: {count:,} traders")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Error in comprehensive sector mapping: {str(e)}")
        raise

if __name__ == "__main__":
    comprehensive_sector_mapping()


