#!/usr/bin/env python3
"""
Final comprehensive sector mapping for all remaining companies
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

# Comprehensive mapping for all major companies still in "Other"
MAJOR_COMPANY_MAPPINGS = {
    # Technology & Software
    'IOT': 'Information Technology',      # Samsara Inc. - IoT platform
    'AMPL': 'Information Technology',     # Amplitude, Inc. - analytics
    'ACN': 'Information Technology',      # Accenture plc - consulting/tech
    'SABR': 'Information Technology',     # Sabre Corp - travel technology
    'VRT': 'Information Technology',      # Vertiv Holdings - data center tech
    'LDOS': 'Information Technology',     # Leidos Holdings - defense tech
    'HRT': 'Information Technology',      # HireRight Holdings - HR tech
    
    # Financial Services
    'STT': 'Financials',                  # State Street Corp - banking
    'KEY': 'Financials',                  # KeyCorp - banking
    'CB': 'Financials',                   # Chubb Ltd - insurance
    
    # Healthcare & Biotech
    'CNC': 'Health Care',                 # Centene Corp - health insurance
    'XRAY': 'Health Care',                # Dentsply Sirona - dental
    'ILMN': 'Health Care',                # Illumina - genomics
    'JCI': 'Health Care',                 # Johnson Controls - building tech (healthcare focus)
    
    # Consumer Discretionary
    'DLTR': 'Consumer Discretionary',     # Dollar Tree - retail
    'FL': 'Consumer Discretionary',       # Foot Locker - retail
    'JWN': 'Consumer Discretionary',      # Nordstrom - retail
    'VAC': 'Consumer Discretionary',      # Marriott Vacations - hospitality
    'BLDR': 'Consumer Discretionary',     # Builders FirstSource - construction materials
    
    # Consumer Staples
    'STKL': 'Consumer Staples',           # SunOpta - organic foods
    'ACI': 'Consumer Staples',            # Albertsons - grocery
    'EL': 'Consumer Staples',             # Estee Lauder - cosmetics
    'MGPI': 'Consumer Staples',           # MGP Ingredients - food ingredients
    
    # Industrials
    'FDX': 'Industrials',                 # FedEx - transportation
    'SWK': 'Industrials',                 # Stanley Black & Decker - tools
    'XYL': 'Industrials',                 # Xylem - water technology
    
    # Utilities
    'NI': 'Utilities',                    # NiSource - utilities
    'ED': 'Utilities',                    # Consolidated Edison - utilities
    
    # Education
    'APEI': 'Consumer Discretionary',     # American Public Education - education services
    'ATGE': 'Consumer Discretionary',     # Adtalem Global Education - education
}

def enhanced_sector_detection(ticker, company_name):
    """Enhanced sector detection with better keyword matching"""
    name_lower = company_name.lower()
    ticker_lower = ticker.lower()
    
    # More comprehensive keyword patterns
    patterns = {
        'Health Care': [
            r'\b(health|medical|pharma|biotech|drug|therapeutic|clinical|hospital|care|wellness|diagnostic|surgical|device|vaccine|cancer|oncology|cardio|neuro|ortho|dental|vision|mental|behavioral|rehab|genomics|genetic|biomedical|pharmaceutical|therapeutic|clinical|medical|healthcare|health care)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(health|medical|pharma|biotech|drug|therapeutic|clinical|hospital|care|wellness|diagnostic|surgical|device|vaccine|cancer|oncology|cardio|neuro|ortho|dental|vision|mental|behavioral|rehab|genomics|genetic|biomedical|pharmaceutical|therapeutic|clinical|medical|healthcare|health care)\b'
        ],
        'Financials': [
            r'\b(bank|financial|credit|loan|mortgage|insurance|investment|capital|fund|trust|bancorp|bancshares|banc|savings|mutual|hedge|asset|wealth|advisory|broker|trading|exchange|clearing|payment|finance|financials|financial services|banking|insurance|investment|capital|fund|trust|bancorp|bancshares|banc|savings|mutual|hedge|asset|wealth|advisory|broker|trading|exchange|clearing|payment|finance)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(bank|financial|credit|loan|mortgage|insurance|investment|capital|fund|trust|bancorp|bancshares|banc|savings|mutual|hedge|asset|wealth|advisory|broker|trading|exchange|clearing|payment|finance|financials|financial services|banking|insurance|investment|capital|fund|trust|bancorp|bancshares|banc|savings|mutual|hedge|asset|wealth|advisory|broker|trading|exchange|clearing|payment|finance)\b'
        ],
        'Information Technology': [
            r'\b(software|technology|tech|digital|data|cloud|cyber|security|network|internet|platform|system|solution|service|computing|artificial|intelligence|machine|learning|analytics|information|communication|telecom|wireless|broadband|fiber|satellite|iot|sensors|automation|robotics|ai|ml|saas|paas|iaas|api|database|analytics|big data|machine learning|artificial intelligence|cybersecurity|information security|network security|cloud computing|software as a service|platform as a service|infrastructure as a service)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(software|technology|tech|digital|data|cloud|cyber|security|network|internet|platform|system|solution|service|computing|artificial|intelligence|machine|learning|analytics|information|communication|telecom|wireless|broadband|fiber|satellite|iot|sensors|automation|robotics|ai|ml|saas|paas|iaas|api|database|analytics|big data|machine learning|artificial intelligence|cybersecurity|information security|network security|cloud computing|software as a service|platform as a service|infrastructure as a service)\b'
        ],
        'Consumer Discretionary': [
            r'\b(retail|store|shop|mall|restaurant|hotel|travel|entertainment|media|broadcast|publishing|gaming|sports|fitness|automotive|auto|car|truck|vehicle|transportation|logistics|shipping|airline|cruise|casino|gaming|leisure|recreation|apparel|fashion|clothing|footwear|jewelry|luxury|entertainment|media|broadcasting|publishing|gaming|sports|fitness|automotive|auto|car|truck|vehicle|transportation|logistics|shipping|airline|cruise|casino|gaming|leisure|recreation|apparel|fashion|clothing|footwear|jewelry|luxury|entertainment|media|broadcasting|publishing|gaming|sports|fitness|automotive|auto|car|truck|vehicle|transportation|logistics|shipping|airline|cruise|casino|gaming|leisure|recreation|apparel|fashion|clothing|footwear|jewelry|luxury)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(retail|store|shop|mall|restaurant|hotel|travel|entertainment|media|broadcast|publishing|gaming|sports|fitness|automotive|auto|car|truck|vehicle|transportation|logistics|shipping|airline|cruise|casino|gaming|leisure|recreation|apparel|fashion|clothing|footwear|jewelry|luxury|entertainment|media|broadcasting|publishing|gaming|sports|fitness|automotive|auto|car|truck|vehicle|transportation|logistics|shipping|airline|cruise|casino|gaming|leisure|recreation|apparel|fashion|clothing|footwear|jewelry|luxury)\b'
        ],
        'Consumer Staples': [
            r'\b(food|beverage|grocery|supermarket|consumer|household|personal|care|beauty|cosmetic|tobacco|alcohol|wine|beer|spirits|packaging|container|paper|tissue|cleaning|hygiene|food|beverage|grocery|supermarket|consumer|household|personal|care|beauty|cosmetic|tobacco|alcohol|wine|beer|spirits|packaging|container|paper|tissue|cleaning|hygiene)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(food|beverage|grocery|supermarket|consumer|household|personal|care|beauty|cosmetic|tobacco|alcohol|wine|beer|spirits|packaging|container|paper|tissue|cleaning|hygiene|food|beverage|grocery|supermarket|consumer|household|personal|care|beauty|cosmetic|tobacco|alcohol|wine|beer|spirits|packaging|container|paper|tissue|cleaning|hygiene)\b'
        ],
        'Industrials': [
            r'\b(industrial|manufacturing|aerospace|defense|military|aviation|construction|engineering|machinery|equipment|tool|automation|logistics|supply|chain|distribution|warehouse|shipping|railroad|trucking|freight|cargo|delivery|postal|industrial|manufacturing|aerospace|defense|military|aviation|construction|engineering|machinery|equipment|tool|automation|logistics|supply|chain|distribution|warehouse|shipping|railroad|trucking|freight|cargo|delivery|postal)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(industrial|manufacturing|aerospace|defense|military|aviation|construction|engineering|machinery|equipment|tool|automation|logistics|supply|chain|distribution|warehouse|shipping|railroad|trucking|freight|cargo|delivery|postal|industrial|manufacturing|aerospace|defense|military|aviation|construction|engineering|machinery|equipment|tool|automation|logistics|supply|chain|distribution|warehouse|shipping|railroad|trucking|freight|cargo|delivery|postal)\b'
        ],
        'Energy': [
            r'\b(energy|oil|gas|petroleum|fuel|power|electric|utility|renewable|solar|wind|nuclear|coal|drilling|exploration|pipeline|refining|chemical|plastics|materials|mining|metals|steel|aluminum|energy|oil|gas|petroleum|fuel|power|electric|utility|renewable|solar|wind|nuclear|coal|drilling|exploration|pipeline|refining|chemical|plastics|materials|mining|metals|steel|aluminum)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(energy|oil|gas|petroleum|fuel|power|electric|utility|renewable|solar|wind|nuclear|coal|drilling|exploration|pipeline|refining|chemical|plastics|materials|mining|metals|steel|aluminum|energy|oil|gas|petroleum|fuel|power|electric|utility|renewable|solar|wind|nuclear|coal|drilling|exploration|pipeline|refining|chemical|plastics|materials|mining|metals|steel|aluminum)\b'
        ],
        'Materials': [
            r'\b(materials|chemical|plastic|polymer|resin|coating|paint|adhesive|sealant|metal|steel|aluminum|copper|mining|quarry|aggregate|cement|concrete|glass|ceramic|composite|materials|chemical|plastic|polymer|resin|coating|paint|adhesive|sealant|metal|steel|aluminum|copper|mining|quarry|aggregate|cement|concrete|glass|ceramic|composite)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(materials|chemical|plastic|polymer|resin|coating|paint|adhesive|sealant|metal|steel|aluminum|copper|mining|quarry|aggregate|cement|concrete|glass|ceramic|composite|materials|chemical|plastic|polymer|resin|coating|paint|adhesive|sealant|metal|steel|aluminum|copper|mining|quarry|aggregate|cement|concrete|glass|ceramic|composite)\b'
        ],
        'Real Estate': [
            r'\b(real estate|reit|property|properties|development|construction|building|office|retail|residential|commercial|industrial|warehouse|storage|apartment|condo|hotel|hospitality|real estate|reit|property|properties|development|construction|building|office|retail|residential|commercial|industrial|warehouse|storage|apartment|condo|hotel|hospitality)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(real estate|reit|property|properties|development|construction|building|office|retail|residential|commercial|industrial|warehouse|storage|apartment|condo|hotel|hospitality|real estate|reit|property|properties|development|construction|building|office|retail|residential|commercial|industrial|warehouse|storage|apartment|condo|hotel|hospitality)\b'
        ],
        'Utilities': [
            r'\b(utility|utilities|electric|power|gas|water|sewer|waste|renewable|solar|wind|nuclear|hydro|thermal|utility|utilities|electric|power|gas|water|sewer|waste|renewable|solar|wind|nuclear|hydro|thermal)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(utility|utilities|electric|power|gas|water|sewer|waste|renewable|solar|wind|nuclear|hydro|thermal|utility|utilities|electric|power|gas|water|sewer|waste|renewable|solar|wind|nuclear|hydro|thermal)\b'
        ],
        'Communication Services': [
            r'\b(communication|telecom|wireless|broadband|cable|satellite|media|broadcast|publishing|entertainment|gaming|social|advertising|marketing|content|streaming|digital|communication|telecom|wireless|broadband|cable|satellite|media|broadcast|publishing|entertainment|gaming|social|advertising|marketing|content|streaming|digital)\b',
            r'\b(inc|corp|ltd|llc|plc|co|company|holdings|technologies|systems|solutions|services|international|global|worldwide)\b.*\b(communication|telecom|wireless|broadband|cable|satellite|media|broadcast|publishing|entertainment|gaming|social|advertising|marketing|content|streaming|digital|communication|telecom|wireless|broadband|cable|satellite|media|broadcast|publishing|entertainment|gaming|social|advertising|marketing|content|streaming|digital)\b'
        ]
    }
    
    # Check specific mappings first
    if ticker in MAJOR_COMPANY_MAPPINGS:
        return MAJOR_COMPANY_MAPPINGS[ticker]
    
    # Check enhanced patterns
    for sector, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, name_lower, re.IGNORECASE):
                return sector
    
    return 'Other'

def final_sector_mapping():
    """Apply final comprehensive sector mapping"""
    try:
        db = next(get_db())
        
        logger.info("🚀 Starting final comprehensive sector mapping...")
        
        # Get all companies currently in "Other"
        other_companies = db.query(Trader.company_ticker, Trader.company_name).filter(Trader.sector == 'Other').distinct().all()
        logger.info(f"📊 Found {len(other_companies)} companies in 'Other' category")
        
        # Track mapping results
        sector_updates = {}
        mapped_count = 0
        
        for ticker, company_name in other_companies:
            new_sector = enhanced_sector_detection(ticker, company_name)
            
            if new_sector != 'Other':
                # Update all traders for this company
                result = db.query(Trader).filter(Trader.company_ticker == ticker).update({
                    'sector': new_sector
                })
                
                if result > 0:
                    sector_updates[new_sector] = sector_updates.get(new_sector, 0) + result
                    mapped_count += 1
                    
                    if mapped_count % 50 == 0:
                        logger.info(f"  - Mapped {mapped_count} companies...")
        
        db.commit()
        
        logger.info(f"✅ Final sector mapping complete!")
        logger.info(f"📊 Mapped {mapped_count} additional companies")
        logger.info(f"📈 Sector updates:")
        for sector, count in sector_updates.items():
            logger.info(f"  - {sector}: +{count:,} traders")
        
        # Get final counts from database
        final_counts = db.query(Trader.sector, func.count(Trader.trader_id)).group_by(Trader.sector).order_by(func.count(Trader.trader_id).desc()).all()
        
        logger.info(f"\\n📊 Final sector distribution:")
        total_traders = sum(count for _, count in final_counts)
        for sector, count in final_counts:
            percentage = (count / total_traders) * 100
            logger.info(f"  - {sector}: {count:,} traders ({percentage:.1f}%)")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Error in final sector mapping: {str(e)}")
        raise

if __name__ == "__main__":
    final_sector_mapping()


