#!/usr/bin/env python3
"""
Aggressive sector mapping - categorize EVERYTHING
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

def aggressive_sector_detection(ticker, company_name):
    """Aggressive sector detection that categorizes everything"""
    name_lower = company_name.lower()
    ticker_lower = ticker.lower()
    
    # Very aggressive patterns - if ANY keyword matches, categorize
    patterns = {
        'Health Care': [
            'health', 'medical', 'pharma', 'biotech', 'drug', 'therapeutic', 'clinical', 'hospital',
            'care', 'wellness', 'diagnostic', 'surgical', 'device', 'vaccine', 'cancer', 'oncology',
            'cardio', 'neuro', 'ortho', 'dental', 'vision', 'mental', 'behavioral', 'rehab',
            'genomics', 'genetic', 'biomedical', 'pharmaceutical', 'therapeutic', 'clinical',
            'medical', 'healthcare', 'health care', 'lilly', 'abbott', 'johnson', 'pfizer',
            'merck', 'bristol', 'myers', 'squibb', 'gilead', 'amgen', 'biogen', 'regeneron',
            'catalent', 'cvs', 'centene', 'unitedhealth', 'anthem', 'humana', 'cigna'
        ],
        'Financials': [
            'bank', 'financial', 'credit', 'loan', 'mortgage', 'insurance', 'investment', 'capital',
            'fund', 'trust', 'bancorp', 'bancshares', 'banc', 'savings', 'mutual', 'hedge',
            'asset', 'wealth', 'advisory', 'broker', 'trading', 'exchange', 'clearing', 'payment',
            'finance', 'financials', 'financial services', 'banking', 'insurance', 'investment',
            'capital', 'fund', 'trust', 'bancorp', 'bancshares', 'banc', 'savings', 'mutual',
            'hedge', 'asset', 'wealth', 'advisory', 'broker', 'trading', 'exchange', 'clearing',
            'payment', 'finance', 'jpmorgan', 'bank of america', 'wells fargo', 'goldman sachs',
            'morgan stanley', 'citigroup', 'american express', 'visa', 'mastercard', 'paypal',
            'blackrock', 'vanguard', 'fidelity', 'state street', 'northern trust', 'chubb',
            'berkshire', 'warren buffett', 'donegal', 'united fire', 'simmons', 'keycorp'
        ],
        'Information Technology': [
            'software', 'technology', 'tech', 'digital', 'data', 'cloud', 'cyber', 'security',
            'network', 'internet', 'platform', 'system', 'solution', 'service', 'computing',
            'artificial', 'intelligence', 'machine', 'learning', 'analytics', 'information',
            'communication', 'telecom', 'wireless', 'broadband', 'fiber', 'satellite', 'iot',
            'sensors', 'automation', 'robotics', 'ai', 'ml', 'saas', 'paas', 'iaas', 'api',
            'database', 'analytics', 'big data', 'machine learning', 'artificial intelligence',
            'cybersecurity', 'information security', 'network security', 'cloud computing',
            'software as a service', 'platform as a service', 'infrastructure as a service',
            'apple', 'microsoft', 'google', 'amazon', 'meta', 'facebook', 'tesla', 'nvidia',
            'salesforce', 'oracle', 'adobe', 'intel', 'cisco', 'ibm', 'service now', 'snowflake',
            'datadog', 'zoom', 'arista', 'zoom info', 'samsara', 'amplitude', 'accenture',
            'sabre', 'vertiv', 'leidos', 'hireright', 'diebold', 'hewlett packard', 'hpe'
        ],
        'Consumer Discretionary': [
            'retail', 'store', 'shop', 'mall', 'restaurant', 'hotel', 'travel', 'entertainment',
            'media', 'broadcast', 'publishing', 'gaming', 'sports', 'fitness', 'automotive',
            'auto', 'car', 'truck', 'vehicle', 'transportation', 'logistics', 'shipping',
            'airline', 'cruise', 'casino', 'gaming', 'leisure', 'recreation', 'apparel',
            'fashion', 'clothing', 'footwear', 'jewelry', 'luxury', 'entertainment', 'media',
            'broadcasting', 'publishing', 'gaming', 'sports', 'fitness', 'automotive', 'auto',
            'car', 'truck', 'vehicle', 'transportation', 'logistics', 'shipping', 'airline',
            'cruise', 'casino', 'gaming', 'leisure', 'recreation', 'apparel', 'fashion',
            'clothing', 'footwear', 'jewelry', 'luxury', 'dollar tree', 'foot locker',
            'nordstrom', 'marriott', 'builders firstsource', 'borgwarner', 'conn', 'vf corp',
            'toro', 'levi strauss', 'hamilton beach', 'bumble', 'dollar general', 'target',
            'walmart', 'home depot', 'lowes', 'mcdonalds', 'starbucks', 'nike', 'adidas'
        ],
        'Consumer Staples': [
            'food', 'beverage', 'grocery', 'supermarket', 'consumer', 'household', 'personal',
            'care', 'beauty', 'cosmetic', 'tobacco', 'alcohol', 'wine', 'beer', 'spirits',
            'packaging', 'container', 'paper', 'tissue', 'cleaning', 'hygiene', 'food',
            'beverage', 'grocery', 'supermarket', 'consumer', 'household', 'personal', 'care',
            'beauty', 'cosmetic', 'tobacco', 'alcohol', 'wine', 'beer', 'spirits', 'packaging',
            'container', 'paper', 'tissue', 'cleaning', 'hygiene', 'clorox', 'ingredion',
            'sunopta', 'albertsons', 'kraft heinz', 'mgp ingredients', 'estee lauder',
            'procter gamble', 'coca cola', 'pepsi', 'walmart', 'costco', 'kroger'
        ],
        'Industrials': [
            'industrial', 'manufacturing', 'aerospace', 'defense', 'military', 'aviation',
            'construction', 'engineering', 'machinery', 'equipment', 'tool', 'automation',
            'logistics', 'supply', 'chain', 'distribution', 'warehouse', 'shipping', 'railroad',
            'trucking', 'freight', 'cargo', 'delivery', 'postal', 'industrial', 'manufacturing',
            'aerospace', 'defense', 'military', 'aviation', 'construction', 'engineering',
            'machinery', 'equipment', 'tool', 'automation', 'logistics', 'supply', 'chain',
            'distribution', 'warehouse', 'shipping', 'railroad', 'trucking', 'freight', 'cargo',
            'delivery', 'postal', 'smith a.o.', 'eaton', 'gatx', 'oshkosh', 'nordson',
            'nacco', 'cummins', 'stanley black decker', '3m', 'general electric', 'honeywell',
            'caterpillar', 'boeing', 'lockheed martin', 'raytheon', 'northrop grumman',
            'huntington ingalls', 'fedex', 'ups', 'union pacific', 'norfolk southern'
        ],
        'Energy': [
            'energy', 'oil', 'gas', 'petroleum', 'fuel', 'power', 'electric', 'utility',
            'renewable', 'solar', 'wind', 'nuclear', 'coal', 'drilling', 'exploration',
            'pipeline', 'refining', 'chemical', 'plastics', 'materials', 'mining', 'metals',
            'steel', 'aluminum', 'energy', 'oil', 'gas', 'petroleum', 'fuel', 'power',
            'electric', 'utility', 'renewable', 'solar', 'wind', 'nuclear', 'coal', 'drilling',
            'exploration', 'pipeline', 'refining', 'chemical', 'plastics', 'materials', 'mining',
            'metals', 'steel', 'aluminum', 'exxon', 'chevron', 'conocophillips', 'schlumberger',
            'eog', 'pioneer', 'marathon', 'valero', 'phillips 66', 'kinder morgan', 'oneok',
            'green plains', 'california resources', 'talos', 'lyondellbasell'
        ],
        'Materials': [
            'materials', 'chemical', 'plastic', 'polymer', 'resin', 'coating', 'paint',
            'adhesive', 'sealant', 'metal', 'steel', 'aluminum', 'copper', 'mining', 'quarry',
            'aggregate', 'cement', 'concrete', 'glass', 'ceramic', 'composite', 'materials',
            'chemical', 'plastic', 'polymer', 'resin', 'coating', 'paint', 'adhesive',
            'sealant', 'metal', 'steel', 'aluminum', 'copper', 'mining', 'quarry', 'aggregate',
            'cement', 'concrete', 'glass', 'ceramic', 'composite', 'dow', 'dupont', '3m',
            'ppg', 'sherwin williams', 'lyondellbasell', 'eastman chemical', 'air products'
        ],
        'Real Estate': [
            'real estate', 'reit', 'property', 'properties', 'development', 'construction',
            'building', 'office', 'retail', 'residential', 'commercial', 'industrial',
            'warehouse', 'storage', 'apartment', 'condo', 'hotel', 'hospitality', 'real estate',
            'reit', 'property', 'properties', 'development', 'construction', 'building', 'office',
            'retail', 'residential', 'commercial', 'industrial', 'warehouse', 'storage',
            'apartment', 'condo', 'hotel', 'hospitality', 'american tower', 'prologis',
            'crown castle', 'equinix', 'public storage', 'extra space', 'avalonbay',
            'equity residential', 'mid america', 'udr', 'cbl', 'simon property'
        ],
        'Utilities': [
            'utility', 'utilities', 'electric', 'power', 'gas', 'water', 'sewer', 'waste',
            'renewable', 'solar', 'wind', 'nuclear', 'hydro', 'thermal', 'utility', 'utilities',
            'electric', 'power', 'gas', 'water', 'sewer', 'waste', 'renewable', 'solar', 'wind',
            'nuclear', 'hydro', 'thermal', 'next era', 'duke energy', 'southern', 'dominion',
            'exelon', 'consolidated edison', 'american electric', 'pacific gas', 'edison international',
            'xcel energy', 'niSource', 'firstenergy', 'entergy', 'pinnacle west'
        ],
        'Communication Services': [
            'communication', 'telecom', 'wireless', 'broadband', 'cable', 'satellite', 'media',
            'broadcast', 'publishing', 'entertainment', 'gaming', 'social', 'advertising',
            'marketing', 'content', 'streaming', 'digital', 'communication', 'telecom',
            'wireless', 'broadband', 'cable', 'satellite', 'media', 'broadcast', 'publishing',
            'entertainment', 'gaming', 'social', 'advertising', 'marketing', 'content',
            'streaming', 'digital', 'verizon', 'at&t', 't mobile', 'comcast', 'charter',
            'disney', 'netflix', 'meta', 'facebook', 'twitter', 'snapchat', 'tiktok',
            'e.w. scripps', 'frontier', 'dish network', 'lumen'
        ]
    }
    
    # Check each sector's keywords
    for sector, keywords in patterns.items():
        for keyword in keywords:
            if keyword in name_lower or keyword in ticker_lower:
                return sector
    
    # If no keywords match, try to infer from company name structure
    if any(word in name_lower for word in ['inc', 'corp', 'ltd', 'llc', 'plc', 'co', 'company', 'holdings']):
        # If it's a real company but no keywords match, default to Industrials
        return 'Industrials'
    
    return 'Other'

def aggressive_sector_mapping():
    """Apply aggressive sector mapping to categorize everything"""
    try:
        db = next(get_db())
        
        logger.info("🚀 Starting aggressive sector mapping...")
        
        # Get all companies currently in "Other"
        other_companies = db.query(Trader.company_ticker, Trader.company_name).filter(Trader.sector == 'Other').distinct().all()
        logger.info(f"📊 Found {len(other_companies)} companies in 'Other' category")
        
        # Track mapping results
        sector_updates = {}
        mapped_count = 0
        
        for ticker, company_name in other_companies:
            new_sector = aggressive_sector_detection(ticker, company_name)
            
            if new_sector != 'Other':
                # Update all traders for this company
                result = db.query(Trader).filter(Trader.company_ticker == ticker).update({
                    'sector': new_sector
                })
                
                if result > 0:
                    sector_updates[new_sector] = sector_updates.get(new_sector, 0) + result
                    mapped_count += 1
                    
                    if mapped_count % 100 == 0:
                        logger.info(f"  - Mapped {mapped_count} companies...")
        
        db.commit()
        
        logger.info(f"✅ Aggressive sector mapping complete!")
        logger.info(f"📊 Mapped {mapped_count} additional companies")
        logger.info(f"📈 Sector updates:")
        for sector, count in sector_updates.items():
            logger.info(f"  - {sector}: +{count:,} traders")
        
        # Get final counts from database
        final_counts = db.query(Trader.sector, func.count(Trader.trader_id)).group_by(Trader.sector).order_by(func.count(Trader.trader_id).desc()).all()
        
        logger.info(f"\\n📊 Final sector distribution:")
        total_traders = sum(count for _, count in final_counts)
        other_count = next((count for sector, count in final_counts if sector == 'Other'), 0)
        logger.info(f"  Other: {other_count:,} traders ({(other_count/total_traders)*100:.1f}%)")
        
        for sector, count in final_counts:
            if sector != 'Other':
                percentage = (count / total_traders) * 100
                logger.info(f"  {sector}: {count:,} traders ({percentage:.1f}%)")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Error in aggressive sector mapping: {str(e)}")
        raise

if __name__ == "__main__":
    aggressive_sector_mapping()


