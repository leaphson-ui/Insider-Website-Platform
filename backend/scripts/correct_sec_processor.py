#!/usr/bin/env python3
"""
CORRECT SEC Data Processor
Properly processes SEC Form 4 data using actual company tickers from ISSUERTRADINGSYMBOL
"""

import os
import sys
import pandas as pd
import logging
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

class CorrectSECProcessor:
    def __init__(self):
        self.db = SessionLocal()
        self.transaction_code_map = {
            'A': 'BUY',           # Acquisition
            'D': 'SELL',          # Disposition 
            'P': 'BUY',           # Purchase
            'S': 'SELL',          # Sale
            'M': 'OPTION_EXERCISE', # Option Exercise
            'F': 'TAX_WITHHOLDING', # Tax Withholding
            'G': 'GIFT',          # Gift
            'J': 'OTHER',         # Other
            'K': 'OTHER',         # Other
            'V': 'OTHER',         # Other  
            'W': 'OTHER',         # Other
            'C': 'CONVERSION',    # Conversion
            'I': 'OTHER',         # Discretionary Transaction
            'L': 'OTHER',         # Small Acquisition
            'O': 'OTHER',         # Exercise/Conversion
            'X': 'OTHER',         # Exercise of in-the-money option
            'U': 'OTHER'          # Disposition pursuant to tender offer
        }
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def load_sec_files(self) -> Dict[str, pd.DataFrame]:
        """Load SEC data files correctly"""
        logger.info("Loading SEC data files...")
        
        try:
            # Load the three key files
            submissions_df = pd.read_csv('SUBMISSION.tsv', sep='\t')
            owners_df = pd.read_csv('REPORTINGOWNER.tsv', sep='\t') 
            transactions_df = pd.read_csv('NONDERIV_TRANS.tsv', sep='\t')
            
            logger.info(f"Loaded:")
            logger.info(f"  Submissions: {len(submissions_df):,} records")
            logger.info(f"  Owners: {len(owners_df):,} records")
            logger.info(f"  Transactions: {len(transactions_df):,} records")
            
            return {
                'submissions': submissions_df,
                'owners': owners_df, 
                'transactions': transactions_df
            }
            
        except Exception as e:
            logger.error(f"Error loading SEC files: {e}")
            raise
    
    def process_sec_data_correctly(self, limit: int = 10000):
        """Process SEC data correctly using proper ticker symbols"""
        logger.info(f"Processing SEC data correctly (limit: {limit:,})...")
        
        # Load data files
        dataframes = self.load_sec_files()
        submissions_df = dataframes['submissions']
        owners_df = dataframes['owners']
        transactions_df = dataframes['transactions']
        
        # Step 1: Create company ticker mapping from submissions
        logger.info("Creating company ticker mapping...")
        company_mapping = {}
        
        for _, row in submissions_df.iterrows():
            accession = row['ACCESSION_NUMBER']
            company_name = str(row.get('ISSUERNAME', '')).strip()
            ticker = str(row.get('ISSUERTRADINGSYMBOL', '')).strip()
            
            # Only map if we have a real ticker (not NA, NONE, empty)
            if ticker and ticker not in ['NA', 'NONE', 'N/A', ''] and len(ticker) <= 6:
                company_mapping[accession] = {
                    'company_name': company_name,
                    'ticker': ticker.upper()
                }
        
        logger.info(f"Created mapping for {len(company_mapping):,} companies with real tickers")
        
        # Step 2: Merge all data properly
        logger.info("Merging transaction, owner, and company data...")
        
        # Start with transactions that have real tickers
        valid_transactions = []
        processed_count = 0
        
        for _, trans_row in transactions_df.iterrows():
            if processed_count >= limit:
                break
                
            accession = trans_row['ACCESSION_NUMBER']
            
            # Skip if no company mapping for this accession
            if accession not in company_mapping:
                continue
            
            # Get company info
            company_info = company_mapping[accession]
            
            # Get owner info for this accession
            owner_info = owners_df[owners_df['ACCESSION_NUMBER'] == accession]
            if owner_info.empty:
                continue
            
            owner_row = owner_info.iloc[0]  # Take first owner for this filing
            
            # Extract transaction details
            try:
                transaction_data = self.extract_correct_transaction(trans_row, owner_row, company_info)
                if transaction_data:
                    valid_transactions.append(transaction_data)
                    processed_count += 1
                    
                    if processed_count % 1000 == 0:
                        logger.info(f"Processed {processed_count:,} valid transactions...")
                        
            except Exception as e:
                logger.debug(f"Error processing transaction: {e}")
                continue
        
        logger.info(f"Extracted {len(valid_transactions):,} valid transactions")
        
        # Step 3: Save to database
        self.save_transactions_to_database(valid_transactions)
        
        return len(valid_transactions)
    
    def extract_correct_transaction(self, trans_row, owner_row, company_info) -> Optional[Dict]:
        """Extract transaction with correct company ticker"""
        try:
            # Company information (CORRECT!)
            company_name = company_info['company_name']
            ticker = company_info['ticker']
            
            # Owner information
            owner_name = str(owner_row.get('RPTOWNERNAME', 'Unknown')).strip()
            owner_title = str(owner_row.get('RPTOWNER_TITLE', '')).strip()
            relationship = str(owner_row.get('RPTOWNER_RELATIONSHIP', '')).strip()
            
            # Transaction details
            trans_date = trans_row.get('TRANS_DATE')
            trans_code = str(trans_row.get('TRANS_CODE', '')).strip()
            shares = trans_row.get('TRANS_SHARES')
            price = trans_row.get('TRANS_PRICEPERSHARE')
            
            # Validate required fields
            if pd.isna(trans_date) or not trans_code or pd.isna(shares) or pd.isna(price):
                return None
            
            # Convert and validate numeric fields
            try:
                shares = float(shares)
                price = float(price) 
                
                if shares <= 0 or price <= 0:
                    return None
                    
            except (ValueError, TypeError):
                return None
            
            # Parse date
            try:
                if isinstance(trans_date, str):
                    transaction_date = datetime.strptime(trans_date, '%d-%b-%Y').date()
                else:
                    transaction_date = trans_date
            except:
                return None
            
            # Map transaction code
            transaction_type = self.transaction_code_map.get(trans_code, 'OTHER')
            
            return {
                'company_name': company_name,
                'ticker': ticker,  # REAL TICKER!
                'owner_name': owner_name,
                'owner_title': owner_title if owner_title != 'nan' else '',
                'relationship': relationship,
                'transaction_date': transaction_date,
                'transaction_type': transaction_type,
                'transaction_code': trans_code,
                'shares': shares,
                'price_per_share': price,
                'total_value': shares * price,
                'accession_number': trans_row.get('ACCESSION_NUMBER', '')
            }
            
        except Exception as e:
            logger.debug(f"Error extracting transaction: {e}")
            return None
    
    def save_transactions_to_database(self, transactions: List[Dict]):
        """Save correctly processed transactions to database"""
        logger.info(f"Saving {len(transactions):,} transactions to database...")
        
        saved_count = 0
        trader_cache = {}  # Cache traders to avoid duplicate queries
        
        try:
            for i, trans_data in enumerate(transactions):
                # Create trader key for caching
                trader_key = f"{trans_data['owner_name']}_{trans_data['ticker']}"
                
                # Find or create trader
                if trader_key not in trader_cache:
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
                        self.db.flush()  # Get the ID
                    
                    trader_cache[trader_key] = trader
                else:
                    trader = trader_cache[trader_key]
                
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
                    logger.info(f"Saved {saved_count:,} transactions...")
            
            # Final commit
            self.db.commit()
            logger.info(f"✅ Successfully saved {saved_count:,} transactions!")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving transactions: {e}")
            raise

def main():
    """Main processing function"""
    processor = CorrectSECProcessor()
    
    try:
        # Process a reasonable amount of data first (10K transactions)
        transactions_processed = processor.process_sec_data_correctly(limit=10000)
        logger.info(f"✅ Processing complete! {transactions_processed:,} transactions processed correctly")
        
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        raise
    finally:
        if hasattr(processor, 'db'):
            processor.db.close()

if __name__ == "__main__":
    main()


