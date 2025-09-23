#!/usr/bin/env python3
"""
Process ALL SEC Quarterly Data Correctly
Processes all 22 quarterly files with proper ticker mapping
"""

import os
import sys
import pandas as pd
import logging
import zipfile
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import numpy as np

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AllQuartersProcessor:
    def __init__(self):
        self.db = SessionLocal()
        self.transaction_code_map = {
            'A': 'BUY', 'D': 'SELL', 'P': 'BUY', 'S': 'SELL',
            'M': 'OPTION_EXERCISE', 'F': 'TAX_WITHHOLDING', 
            'G': 'GIFT', 'J': 'OTHER', 'K': 'OTHER', 'V': 'OTHER',
            'W': 'OTHER', 'C': 'CONVERSION', 'I': 'OTHER', 
            'L': 'OTHER', 'O': 'OTHER', 'X': 'OTHER', 'U': 'OTHER'
        }
        self.processed_count = 0
        self.trader_cache = {}
    
    def process_all_quarters(self, max_per_quarter: int = 50000):
        """Process all quarterly SEC data files"""
        logger.info("🚀 Starting to process ALL SEC quarterly data...")
        
        # Get all quarterly files
        quarterly_files = []
        data_dir = 'sec_quarterly_data'
        
        for filename in os.listdir(data_dir):
            if filename.endswith('_form345.zip'):
                quarterly_files.append(os.path.join(data_dir, filename))
        
        quarterly_files.sort()  # Process chronologically
        logger.info(f"Found {len(quarterly_files)} quarterly files to process")
        
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
        
        logger.info(f"\n🎉 ALL QUARTERS PROCESSED!")
        logger.info(f"Total transactions: {total_processed:,}")
        
        return total_processed
    
    def process_quarter_file(self, zip_file_path: str, limit: int) -> int:
        """Process a single quarterly file"""
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Load data from zip
            with zip_ref.open('SUBMISSION.tsv') as f:
                submissions_df = pd.read_csv(f, sep='\t')
            
            with zip_ref.open('REPORTINGOWNER.tsv') as f:
                owners_df = pd.read_csv(f, sep='\t')
            
            with zip_ref.open('NONDERIV_TRANS.tsv') as f:
                transactions_df = pd.read_csv(f, sep='\t')
        
        logger.info(f"  Loaded: {len(submissions_df):,} submissions, {len(owners_df):,} owners, {len(transactions_df):,} transactions")
        
        # Create company mapping with REAL tickers
        company_mapping = {}
        real_ticker_count = 0
        
        for _, row in submissions_df.iterrows():
            accession = row['ACCESSION_NUMBER']
            company_name = str(row.get('ISSUERNAME', '')).strip()
            ticker = str(row.get('ISSUERTRADINGSYMBOL', '')).strip()
            
            # Only use REAL tickers (not NA, NONE, empty)
            if ticker and ticker not in ['NA', 'NONE', 'N/A', '', 'nan'] and len(ticker) <= 6:
                company_mapping[accession] = {
                    'company_name': company_name,
                    'ticker': ticker.upper()
                }
                real_ticker_count += 1
        
        logger.info(f"  Found {real_ticker_count:,} companies with REAL tickers")
        
        # Process transactions with real ticker mapping
        valid_transactions = []
        
        for _, trans_row in transactions_df.iterrows():
            if len(valid_transactions) >= limit:
                break
                
            accession = trans_row['ACCESSION_NUMBER']
            
            # Skip if no real ticker mapping
            if accession not in company_mapping:
                continue
            
            # Get owner info
            owner_info = owners_df[owners_df['ACCESSION_NUMBER'] == accession]
            if owner_info.empty:
                continue
            
            owner_row = owner_info.iloc[0]
            company_info = company_mapping[accession]
            
            # Extract transaction
            transaction_data = self.extract_transaction(trans_row, owner_row, company_info)
            if transaction_data:
                valid_transactions.append(transaction_data)
        
        # Save to database
        saved_count = self.save_transactions(valid_transactions)
        return saved_count
    
    def extract_transaction(self, trans_row, owner_row, company_info) -> Optional[Dict]:
        """Extract transaction with REAL ticker"""
        try:
            # Company info (REAL ticker!)
            company_name = company_info['company_name']
            ticker = company_info['ticker']
            
            # Owner info
            owner_name = str(owner_row.get('RPTOWNERNAME', 'Unknown')).strip()
            owner_title = str(owner_row.get('RPTOWNER_TITLE', '')).strip()
            relationship = str(owner_row.get('RPTOWNER_RELATIONSHIP', '')).strip()
            
            # Transaction details
            trans_date = trans_row.get('TRANS_DATE')
            trans_code = str(trans_row.get('TRANS_CODE', '')).strip()
            shares = trans_row.get('TRANS_SHARES')
            price = trans_row.get('TRANS_PRICEPERSHARE')
            
            # Validate
            if pd.isna(trans_date) or not trans_code or pd.isna(shares) or pd.isna(price):
                return None
            
            try:
                shares = float(shares)
                price = float(price)
                if shares <= 0 or price <= 0:
                    return None
            except:
                return None
            
            # Parse date
            try:
                if isinstance(trans_date, str):
                    transaction_date = datetime.strptime(trans_date, '%d-%b-%Y').date()
                else:
                    transaction_date = trans_date
            except:
                return None
            
            transaction_type = self.transaction_code_map.get(trans_code, 'OTHER')
            
            return {
                'company_name': company_name,
                'ticker': ticker,  # REAL TICKER FROM SEC!
                'owner_name': owner_name,
                'owner_title': owner_title if owner_title != 'nan' else '',
                'relationship': relationship,
                'transaction_date': transaction_date,
                'transaction_type': transaction_type,
                'shares': shares,
                'price_per_share': price,
                'total_value': shares * price
            }
            
        except Exception as e:
            return None
    
    def save_transactions(self, transactions: List[Dict]) -> int:
        """Save transactions to database"""
        saved_count = 0
        
        try:
            for trans_data in transactions:
                # Find or create trader
                trader_key = f"{trans_data['owner_name']}_{trans_data['ticker']}"
                
                if trader_key not in self.trader_cache:
                    trader = self.db.query(Trader).filter(
                        Trader.name == trans_data['owner_name'],
                        Trader.company_ticker == trans_data['ticker']
                    ).first()
                    
                    if not trader:
                        trader = Trader(
                            name=trans_data['owner_name'],
                            title=trans_data['owner_title'],
                            company_ticker=trans_data['ticker'],  # REAL TICKER!
                            company_name=trans_data['company_name'],
                            relationship_to_company=trans_data['relationship']
                        )
                        self.db.add(trader)
                        self.db.flush()
                    
                    self.trader_cache[trader_key] = trader
                else:
                    trader = self.trader_cache[trader_key]
                
                # Create trade
                trade = Trade(
                    trader_id=trader.trader_id,
                    company_ticker=trans_data['ticker'],  # REAL TICKER!
                    transaction_date=trans_data['transaction_date'],
                    transaction_type=trans_data['transaction_type'],
                    shares_traded=Decimal(str(trans_data['shares'])),
                    price_per_share=Decimal(str(trans_data['price_per_share'])),
                    total_value=Decimal(str(trans_data['total_value'])),
                    form_type='Form 4'
                )
                
                self.db.add(trade)
                saved_count += 1
                
                # Commit in batches
                if saved_count % 1000 == 0:
                    self.db.commit()
            
            # Final commit
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving: {e}")
            raise
        
        return saved_count

def main():
    processor = AllQuartersProcessor()
    
    try:
        # Process all quarters with reasonable limits
        total = processor.process_all_quarters(max_per_quarter=20000)  # 20K per quarter = ~440K total
        logger.info(f"🎉 COMPLETE! Processed {total:,} transactions with REAL tickers!")
        
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        raise
    finally:
        if hasattr(processor, 'db'):
            processor.db.close()

if __name__ == "__main__":
    main()


