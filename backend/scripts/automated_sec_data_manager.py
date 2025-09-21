"""
Automated SEC Data Manager
Handles downloading, processing, and updating SEC quarterly insider transaction data
"""

import os
import sys
import requests
import pandas as pd
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional
import zipfile
import json
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedSECDataManager:
    def __init__(self):
        self.db = SessionLocal()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Insider Alpha Platform (admin@insideralpha.com)'
        })
        self.data_dir = Path("sec_quarterly_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Enhanced company ticker mapping
        self.company_ticker_map = self.load_comprehensive_ticker_mapping()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def load_comprehensive_ticker_mapping(self) -> Dict[str, str]:
        """Load comprehensive company name to ticker mapping"""
        return {
            # Technology
            'APPLE': 'AAPL', 'APPLE INC': 'AAPL',
            'MICROSOFT': 'MSFT', 'MICROSOFT CORP': 'MSFT', 'MICROSOFT CORPORATION': 'MSFT',
            'ALPHABET': 'GOOGL', 'GOOGLE': 'GOOGL', 'ALPHABET INC': 'GOOGL',
            'NVIDIA': 'NVDA', 'NVIDIA CORP': 'NVDA', 'NVIDIA CORPORATION': 'NVDA',
            'META': 'META', 'META PLATFORMS': 'META', 'FACEBOOK': 'META',
            'TESLA': 'TSLA', 'TESLA INC': 'TSLA', 'TESLA MOTORS': 'TSLA',
            'AMAZON': 'AMZN', 'AMAZON COM': 'AMZN', 'AMAZON.COM': 'AMZN',
            'NETFLIX': 'NFLX', 'NETFLIX INC': 'NFLX',
            'ADOBE': 'ADBE', 'ADOBE INC': 'ADBE', 'ADOBE SYSTEMS': 'ADBE',
            'SALESFORCE': 'CRM', 'SALESFORCE COM': 'CRM',
            'ORACLE': 'ORCL', 'ORACLE CORP': 'ORCL', 'ORACLE CORPORATION': 'ORCL',
            
            # Financial
            'JPMORGAN': 'JPM', 'JP MORGAN': 'JPM', 'JPMORGAN CHASE': 'JPM',
            'BANK OF AMERICA': 'BAC', 'BANKAMERICA': 'BAC',
            'WELLS FARGO': 'WFC', 'WELLS FARGO & COMPANY': 'WFC',
            'GOLDMAN SACHS': 'GS', 'GOLDMAN SACHS GROUP': 'GS',
            'MORGAN STANLEY': 'MS',
            'AMERICAN EXPRESS': 'AXP', 'AMEX': 'AXP',
            
            # Healthcare
            'JOHNSON & JOHNSON': 'JNJ', 'JOHNSON AND JOHNSON': 'JNJ',
            'PFIZER': 'PFE', 'PFIZER INC': 'PFE',
            'MERCK': 'MRK', 'MERCK & CO': 'MRK',
            'ABBVIE': 'ABBV', 'ABBVIE INC': 'ABBV',
            'BRISTOL MYERS': 'BMY', 'BRISTOL-MYERS SQUIBB': 'BMY',
            
            # Consumer
            'COCA COLA': 'KO', 'COCA-COLA': 'KO', 'THE COCA-COLA COMPANY': 'KO',
            'PROCTER & GAMBLE': 'PG', 'PROCTER AND GAMBLE': 'PG',
            'WALMART': 'WMT', 'WAL-MART': 'WMT', 'WALMART INC': 'WMT',
            'HOME DEPOT': 'HD', 'THE HOME DEPOT': 'HD',
            'NIKE': 'NKE', 'NIKE INC': 'NKE',
            'MCDONALDS': 'MCD', "MCDONALD'S": 'MCD', "MCDONALD'S CORP": 'MCD',
            
            # Energy
            'EXXON': 'XOM', 'EXXON MOBIL': 'XOM', 'EXXONMOBIL': 'XOM',
            'CHEVRON': 'CVX', 'CHEVRON CORP': 'CVX',
            
            # Industrial
            'BOEING': 'BA', 'THE BOEING COMPANY': 'BA',
            'CATERPILLAR': 'CAT', 'CATERPILLAR INC': 'CAT',
            'GENERAL ELECTRIC': 'GE', 'GE': 'GE',
            
            # Biotech/Pharma (common in insider data)
            'MODERNA': 'MRNA', 'MODERNA INC': 'MRNA',
            'BIOGEN': 'BIIB', 'BIOGEN INC': 'BIIB',
            'GILEAD': 'GILD', 'GILEAD SCIENCES': 'GILD',
            'REGENERON': 'REGN', 'REGENERON PHARMACEUTICALS': 'REGN'
        }
    
    def get_latest_quarters(self, num_quarters: int = 8) -> List[str]:
        """Get list of latest quarters to download"""
        current_year = datetime.now().year
        current_quarter = (datetime.now().month - 1) // 3 + 1
        
        quarters = []
        year = current_year
        quarter = current_quarter
        
        for _ in range(num_quarters):
            quarters.append(f"{year}q{quarter}")
            quarter -= 1
            if quarter == 0:
                quarter = 4
                year -= 1
        
        return quarters
    
    def download_quarter_data(self, quarter: str) -> Optional[str]:
        """Download SEC quarterly data"""
        logger.info(f"Downloading SEC data for {quarter}...")
        
        try:
            url = f"https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{quarter}_form345.zip"
            zip_path = self.data_dir / f"{quarter}_form345.zip"
            
            # Skip if already downloaded
            if zip_path.exists():
                logger.info(f"Data for {quarter} already exists, skipping download")
                return str(zip_path)
            
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded {quarter} data ({len(response.content):,} bytes)")
            return str(zip_path)
            
        except Exception as e:
            logger.error(f"Error downloading {quarter}: {e}")
            return None
    
    def process_quarter_data(self, zip_path: str, max_transactions: int = 5000) -> int:
        """Process quarterly data and save to database"""
        quarter = Path(zip_path).stem.replace('_form345', '')
        logger.info(f"Processing {quarter} data...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract to temporary directory
                extract_dir = self.data_dir / f"{quarter}_extracted"
                zip_ref.extractall(extract_dir)
                
                # Load the main files
                trans_file = extract_dir / "NONDERIV_TRANS.tsv"
                owners_file = extract_dir / "REPORTINGOWNER.tsv"
                
                if not (trans_file.exists() and owners_file.exists()):
                    logger.error(f"Required files not found in {quarter} data")
                    return 0
                
                # Load dataframes
                logger.info("Loading transaction and owner data...")
                trans_df = pd.read_csv(trans_file, sep='\t', low_memory=False)
                owners_df = pd.read_csv(owners_file, sep='\t', low_memory=False)
                
                # Merge data
                merged_df = pd.merge(trans_df, owners_df, on='ACCESSION_NUMBER', how='inner')
                
                # Filter for quality data
                quality_df = merged_df[
                    (merged_df['TRANS_SHARES'].notna()) &
                    (merged_df['TRANS_PRICEPERSHARE'].notna()) &
                    (merged_df['TRANS_DATE'].notna()) &
                    (merged_df['RPTOWNERNAME'].notna()) &
                    (merged_df['TRANS_SHARES'] > 0) &
                    (merged_df['TRANS_PRICEPERSHARE'] > 0)
                ].copy()
                
                logger.info(f"Quality dataset: {len(quality_df):,} records")
                
                # Sample if too large
                if len(quality_df) > max_transactions:
                    quality_df = quality_df.sample(n=max_transactions, random_state=42)
                    logger.info(f"Sampled {max_transactions:,} records")
                
                # Process and save
                saved_count = self.save_processed_data(quality_df, quarter)
                
                # Clean up extracted files
                import shutil
                shutil.rmtree(extract_dir, ignore_errors=True)
                
                return saved_count
                
        except Exception as e:
            logger.error(f"Error processing {quarter} data: {e}")
            return 0
    
    def save_processed_data(self, df: pd.DataFrame, quarter: str) -> int:
        """Save processed SEC data to database"""
        logger.info(f"Saving {len(df):,} transactions from {quarter}...")
        
        saved_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extract company info
                company_name = str(row.get('RPTOWNERNAME', 'Unknown')).strip().upper()
                
                # Try to find ticker
                ticker = None
                for company_key, company_ticker in self.company_ticker_map.items():
                    if company_key in company_name:
                        ticker = company_ticker
                        break
                
                # If no major company match, create a ticker from company name
                if not ticker:
                    # Take first few letters of company name as ticker
                    ticker = ''.join(company_name.split()[:2])[:6].replace(' ', '')
                    if len(ticker) < 2:
                        continue
                
                # Extract transaction details
                trans_date = row.get('TRANS_DATE')
                if pd.isna(trans_date):
                    continue
                
                transaction_date = pd.to_datetime(trans_date).date()
                
                # Owner info
                owner_name = str(row.get('RPTOWNERNAME', 'Unknown')).title()
                owner_title = str(row.get('RPTOWNER_TITLE', '')).title()
                relationship = str(row.get('RPTOWNER_RELATIONSHIP', '')).title()
                
                # Transaction details
                trans_code = str(row.get('TRANS_CODE', '')).upper()
                transaction_type = self.convert_transaction_code(trans_code)
                
                shares = float(row.get('TRANS_SHARES', 0))
                price = float(row.get('TRANS_PRICEPERSHARE', 0))
                
                if shares <= 0 or price <= 0:
                    continue
                
                total_value = shares * price
                
                # Find or create trader
                trader = self.db.query(Trader).filter(
                    Trader.name == owner_name,
                    Trader.company_ticker == ticker
                ).first()
                
                if not trader:
                    trader = Trader(
                        name=owner_name,
                        title=owner_title,
                        company_ticker=ticker,
                        company_name=company_name.title(),
                        relationship_to_company=relationship
                    )
                    self.db.add(trader)
                    self.db.flush()
                
                # Check if trade exists
                existing = self.db.query(Trade).filter(
                    Trade.trader_id == trader.trader_id,
                    Trade.transaction_date == transaction_date,
                    Trade.shares_traded == Decimal(str(shares)),
                    Trade.price_per_share == Decimal(str(price))
                ).first()
                
                if not existing:
                    trade = Trade(
                        trader_id=trader.trader_id,
                        company_ticker=ticker,
                        transaction_date=transaction_date,
                        transaction_type=transaction_type,
                        shares_traded=Decimal(str(shares)),
                        price_per_share=Decimal(str(price)),
                        total_value=Decimal(str(total_value)),
                        form_type='Form 4'
                    )
                    
                    self.db.add(trade)
                    saved_count += 1
                
                if saved_count % 100 == 0 and saved_count > 0:
                    self.db.commit()
                    logger.info(f"Saved {saved_count} transactions...")
                    
            except Exception as e:
                logger.debug(f"Error processing row {index}: {e}")
                continue
        
        # Final commit
        self.db.commit()
        
        # Update trader counts
        traders = self.db.query(Trader).all()
        for trader in traders:
            trader.total_trades = self.db.query(Trade).filter(
                Trade.trader_id == trader.trader_id
            ).count()
        self.db.commit()
        
        return saved_count
    
    def convert_transaction_code(self, code: str) -> str:
        """Convert SEC transaction codes"""
        code_map = {
            'A': 'BUY', 'D': 'SELL', 'P': 'BUY', 'S': 'SELL',
            'M': 'OPTION_EXERCISE', 'F': 'TAX_WITHHOLDING',
            'G': 'GIFT', 'C': 'CONVERSION', 'J': 'OTHER'
        }
        return code_map.get(code, 'OTHER')
    
    def update_all_data(self, num_quarters: int = 4, max_per_quarter: int = 10000):
        """Download and process the latest quarters of SEC data"""
        logger.info(f"Updating SEC data for last {num_quarters} quarters...")
        
        quarters = self.get_latest_quarters(num_quarters)
        total_saved = 0
        
        for quarter in quarters:
            try:
                # Download quarter data
                zip_path = self.download_quarter_data(quarter)
                
                if zip_path:
                    # Process quarter data
                    saved = self.process_quarter_data(zip_path, max_per_quarter)
                    total_saved += saved
                    logger.info(f"Quarter {quarter}: {saved:,} transactions saved")
                
            except Exception as e:
                logger.error(f"Error processing quarter {quarter}: {e}")
                continue
        
        logger.info(f"SEC data update complete: {total_saved:,} total transactions saved")
        return total_saved
    
    def get_data_summary(self) -> Dict:
        """Get summary of current data in database"""
        try:
            total_traders = self.db.query(Trader).count()
            total_trades = self.db.query(Trade).count()
            
            # Get latest trade date
            latest_trade = self.db.query(Trade).order_by(Trade.transaction_date.desc()).first()
            latest_date = latest_trade.transaction_date if latest_trade else None
            
            # Get top companies by trade count
            from sqlalchemy import func
            top_companies = self.db.query(
                Trade.company_ticker,
                func.count(Trade.trade_id).label('trade_count')
            ).group_by(Trade.company_ticker).order_by(
                func.count(Trade.trade_id).desc()
            ).limit(10).all()
            
            return {
                'total_traders': total_traders,
                'total_trades': total_trades,
                'latest_trade_date': latest_date.isoformat() if latest_date else None,
                'top_companies': [
                    {'ticker': company[0], 'trade_count': company[1]}
                    for company in top_companies
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}

def main():
    """Main function for automated SEC data management"""
    try:
        manager = AutomatedSECDataManager()
        
        print("🚀 Automated SEC Data Manager")
        print("=" * 50)
        
        # Get current data summary
        current_summary = manager.get_data_summary()
        print(f"Current database:")
        print(f"  - Traders: {current_summary.get('total_traders', 0):,}")
        print(f"  - Trades: {current_summary.get('total_trades', 0):,}")
        print(f"  - Latest trade: {current_summary.get('latest_trade_date', 'None')}")
        print()
        
        # Update with latest SEC data
        print("Downloading and processing latest SEC quarterly data...")
        saved_count = manager.update_all_data(num_quarters=4, max_per_quarter=10000)
        
        # Get updated summary
        updated_summary = manager.get_data_summary()
        print(f"\nUpdated database:")
        print(f"  - Traders: {updated_summary.get('total_traders', 0):,}")
        print(f"  - Trades: {updated_summary.get('total_trades', 0):,}")
        print(f"  - New trades added: {saved_count:,}")
        
        print(f"\n✅ SEC data update complete!")
        print(f"Your platform now has real SEC insider trading data!")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
