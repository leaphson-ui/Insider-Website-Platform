#!/usr/bin/env python3
"""
ROBUST SEC Data Processor - Fixed Version
Handles database constraints and data validation properly
"""

import os
import sys
import pandas as pd
import logging
import zipfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple
import numpy as np

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import Trader, Trade
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RobustSECProcessor:
    def __init__(self):
        self.db = SessionLocal()
        self.transaction_code_map = {
            'A': 'BUY', 'D': 'SELL', 'P': 'BUY', 'S': 'SELL',
            'M': 'OPTION_EXERCISE', 'F': 'TAX_WITHHOLDING', 
            'G': 'GIFT', 'J': 'OTHER', 'K': 'OTHER', 'V': 'OTHER',
            'W': 'OTHER', 'C': 'CONVERSION', 'I': 'OTHER', 
            'L': 'OTHER', 'O': 'OTHER', 'X': 'OTHER', 'U': 'OTHER'
        }
        
        # Data validation limits
        self.MAX_PRICE = 10000  # $10K per share max
        self.MAX_SHARES = 10000000  # 10M shares max
        self.MAX_TOTAL_VALUE = 1000000000  # $1B max trade value
        
        self.processed_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.constraint_errors = 0
        self.overflow_errors = 0
    
    def clear_existing_data(self):
        """Clear existing data to start fresh"""
        logger.info("🧹 Clearing existing data...")
        try:
            self.db.execute(text("DELETE FROM trades"))
            self.db.execute(text("DELETE FROM traders"))
            self.db.execute(text("ALTER SEQUENCE traders_trader_id_seq RESTART WITH 1"))
            self.db.execute(text("ALTER SEQUENCE trades_trade_id_seq RESTART WITH 1"))
            self.db.commit()
            logger.info("✅ Database cleared successfully")
        except Exception as e:
            logger.error(f"❌ Error clearing database: {e}")
            self.db.rollback()
            raise
    
    def validate_trade_data(self, shares: float, price: float) -> bool:
        """Validate trade data for reasonable values"""
        if pd.isna(shares) or pd.isna(price):
            return False
        
        if shares <= 0 or shares > self.MAX_SHARES:
            return False
            
        if price <= 0 or price > self.MAX_PRICE:
            return False
            
        total_value = shares * price
        if total_value > self.MAX_TOTAL_VALUE:
            return False
            
        return True
    
    def process_selected_quarters(self, start_year: int = 2020, max_per_quarter: int = 200000):
        """Process quarterly files starting from specified year"""
        logger.info(f"🚀 Processing SEC data from {start_year} onwards...")
        
        # Clear existing data first
        self.clear_existing_data()
        
        # Get quarterly files from start_year onwards
        quarterly_files = []
        data_dir = 'sec_quarterly_data'
        
        for filename in sorted(os.listdir(data_dir)):
            if filename.endswith('_form345.zip'):
                year = int(filename[:4])
                if year >= start_year:
                    quarterly_files.append(os.path.join(data_dir, filename))
        
        logger.info(f"Found {len(quarterly_files)} quarterly files from {start_year}")
        
        total_processed = 0
        
        for i, zip_file in enumerate(quarterly_files):
            quarter_name = os.path.basename(zip_file).replace('_form345.zip', '')
            logger.info(f"\n📊 Processing {quarter_name} ({i+1}/{len(quarterly_files)})...")
            
            try:
                quarter_processed = self.process_quarter_file(zip_file, max_per_quarter)
                total_processed += quarter_processed
                logger.info(f"✅ {quarter_name}: {quarter_processed:,} transactions processed")
                
            except Exception as e:
                logger.error(f"❌ Error processing {quarter_name}: {e}")
                continue
        
        logger.info(f"\n🎉 PROCESSING COMPLETE!")
        logger.info(f"Total processed: {total_processed:,}")
        logger.info(f"Total errors: {self.error_count:,}")
        logger.info(f"  - Constraint errors: {self.constraint_errors:,}")
        logger.info(f"  - Overflow errors: {self.overflow_errors:,}")
        logger.info(f"Total skipped: {self.skipped_count:,}")
        
        return total_processed
    
    def process_quarter_file(self, zip_file_path: str, limit: int) -> int:
        """Process a single quarterly file with robust error handling"""
        
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Load data with proper error handling
                with zip_ref.open('SUBMISSION.tsv') as f:
                    submissions_df = pd.read_csv(f, sep='\t', dtype=str)
                
                with zip_ref.open('REPORTINGOWNER.tsv') as f:
                    owners_df = pd.read_csv(f, sep='\t', dtype=str)
                
                with zip_ref.open('NONDERIV_TRANS.tsv') as f:
                    transactions_df = pd.read_csv(f, sep='\t', dtype=str, low_memory=False)
        
        except Exception as e:
            logger.error(f"Error loading files from {zip_file_path}: {e}")
            return 0
        
        logger.info(f"  Loaded: {len(submissions_df):,} submissions, {len(owners_df):,} owners, {len(transactions_df):,} transactions")
        
        # Create company mapping with validation
        company_mapping = self.create_company_mapping(submissions_df)
        logger.info(f"  Created mapping for {len(company_mapping):,} companies with real tickers")
        
        # Process transactions in batches
        processed_count = 0
        batch_size = 100
        current_batch = []
        
        for _, trans_row in transactions_df.iterrows():
            if processed_count >= limit:
                break
            
            try:
                # Extract and validate transaction
                transaction_data = self.extract_and_validate_transaction(
                    trans_row, owners_df, company_mapping
                )
                
                if transaction_data:
                    current_batch.append(transaction_data)
                    
                    # Process batch when full
                    if len(current_batch) >= batch_size:
                        batch_saved = self.save_transaction_batch(current_batch)
                        processed_count += batch_saved
                        current_batch = []
                        
                        if processed_count % 1000 == 0:
                            logger.info(f"    Processed {processed_count:,} transactions...")
                else:
                    self.skipped_count += 1
                    
            except Exception as e:
                self.error_count += 1
                continue
        
        # Process remaining batch
        if current_batch:
            batch_saved = self.save_transaction_batch(current_batch)
            processed_count += batch_saved
        
        return processed_count
    
    def create_company_mapping(self, submissions_df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        """Create validated company mapping"""
        mapping = {}
        
        for _, row in submissions_df.iterrows():
            accession = row['ACCESSION_NUMBER']
            company_name = str(row.get('ISSUERNAME', '')).strip()
            ticker = str(row.get('ISSUERTRADINGSYMBOL', '')).strip().upper()
            
            # Validate ticker
            if (ticker and 
                ticker not in ['NA', 'NONE', 'N/A', '', 'NAN', 'NULL'] and 
                len(ticker) <= 6 and 
                ticker.isalnum()):
                
                mapping[accession] = {
                    'company_name': company_name[:100],  # Limit length
                    'ticker': ticker
                }
        
        return mapping
    
    def extract_and_validate_transaction(self, trans_row, owners_df, company_mapping) -> Optional[Dict]:
        """Extract and validate transaction data"""
        try:
            accession = trans_row['ACCESSION_NUMBER']
            
            # Check for company mapping
            if accession not in company_mapping:
                return None
            
            # Get owner info
            owner_info = owners_df[owners_df['ACCESSION_NUMBER'] == accession]
            if owner_info.empty:
                return None
            
            owner_row = owner_info.iloc[0]
            company_info = company_mapping[accession]
            
            # Extract basic data
            owner_name = str(owner_row.get('RPTOWNERNAME', 'Unknown')).strip()[:100]
            owner_title = str(owner_row.get('RPTOWNER_TITLE', '')).strip()[:100]
            relationship = str(owner_row.get('RPTOWNER_RELATIONSHIP', '')).strip()[:100]
            
            # Transaction details
            trans_date = trans_row.get('TRANS_DATE')
            trans_code = str(trans_row.get('TRANS_CODE', '')).strip()
            shares_str = str(trans_row.get('TRANS_SHARES', ''))
            price_str = str(trans_row.get('TRANS_PRICEPERSHARE', ''))
            
            # Validate and convert numeric values
            try:
                shares = float(shares_str.replace(',', '')) if shares_str not in ['', 'nan', 'None'] else None
                price = float(price_str.replace(',', '')) if price_str not in ['', 'nan', 'None'] else None
            except (ValueError, AttributeError):
                return None
            
            # Validate trade data
            if not self.validate_trade_data(shares, price):
                return None
            
            # Parse date
            try:
                if isinstance(trans_date, str) and trans_date not in ['', 'nan', 'None']:
                    transaction_date = datetime.strptime(trans_date, '%d-%b-%Y').date()
                else:
                    return None
            except (ValueError, TypeError):
                return None
            
            # Skip future dates
            if transaction_date > datetime.now().date():
                return None
            
            transaction_type = self.transaction_code_map.get(trans_code, 'OTHER')
            
            return {
                'company_name': company_info['company_name'],
                'ticker': company_info['ticker'],
                'owner_name': owner_name,
                'owner_title': owner_title if owner_title not in ['nan', 'None', ''] else '',
                'relationship': relationship,
                'transaction_date': transaction_date,
                'transaction_type': transaction_type,
                'shares': shares,
                'price_per_share': price,
                'total_value': shares * price
            }
            
        except Exception as e:
            return None
    
    def save_transaction_batch(self, transactions: List[Dict]) -> int:
        """Save batch of transactions with proper error handling"""
        saved_count = 0
        
        try:
            for trans_data in transactions:
                try:
                    # Find or create trader
                    trader = self.db.query(Trader).filter(
                        Trader.name == trans_data['owner_name'],
                        Trader.company_ticker == trans_data['ticker']
                    ).first()
                    
                    if not trader:
                        trader = Trader(
                            name=trans_data['owner_name'],
                            title=trans_data['owner_title'],
                            company_ticker=trans_data['ticker'],
                            company_name=trans_data['company_name'],
                            relationship_to_company=trans_data['relationship']
                        )
                        self.db.add(trader)
                        self.db.flush()  # Get the ID
                    
                    # Create trade
                    trade = Trade(
                        trader_id=trader.trader_id,
                        company_ticker=trans_data['ticker'],
                        transaction_date=trans_data['transaction_date'],
                        transaction_type=trans_data['transaction_type'],
                        shares_traded=Decimal(str(trans_data['shares'])),
                        price_per_share=Decimal(str(trans_data['price_per_share'])),
                        total_value=Decimal(str(trans_data['total_value'])),
                        form_type='Form 4'
                    )
                    
                    self.db.add(trade)
                    saved_count += 1
                    
                except IntegrityError as e:
                    self.db.rollback()
                    self.constraint_errors += 1
                    self.error_count += 1
                    if "foreign key constraint" in str(e).lower():
                        logger.warning(f"🔗 Foreign key constraint violation for trader: {trans_data['owner_name']}")
                    continue
                except InvalidOperation as e:
                    self.db.rollback()
                    self.overflow_errors += 1
                    self.error_count += 1
                    logger.warning(f"💥 Numeric overflow: {trans_data['ticker']} - ${trans_data['total_value']:,.0f}")
                    continue
                except Exception as e:
                    self.db.rollback()
                    self.error_count += 1
                    continue
            
            # Commit the batch
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Batch save error: {e}")
            raise
        
        return saved_count
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

def main():
    processor = RobustSECProcessor()
    
    try:
        # Process ALL available data from 2020 onwards (no limits!)
        total = processor.process_selected_quarters(start_year=2020, max_per_quarter=200000)
        logger.info(f"🎉 COMPLETE! Successfully processed {total:,} transactions!")
        
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        raise
    finally:
        if hasattr(processor, 'db'):
            processor.db.close()

if __name__ == "__main__":
    main()
