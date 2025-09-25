#!/usr/bin/env python3
"""
Retry Failed Quarters - Individual processing with better error handling
Processes the 17 failed quarters individually with improved resilience
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List
import time
from supabase import create_client, Client
from adaptive_sec_processor import AdaptiveSECProcessor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('retry_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FailedQuarterRetryProcessor:
    def __init__(self, data_dir: str = "sec_insider_data"):
        """Initialize retry processor for failed quarters"""
        self.data_dir = Path(data_dir)
        
        # Supabase connection
        self.url = 'https://sifpyksougtsklegphxf.supabase.co'
        self.key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZnB5a3NvdWd0c2tsZWdwaHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NzI5OTUsImV4cCI6MjA3NDI0ODk5NX0.NDc6nd1w9SFhgYYJkRrAqD_3pO584tUrGcNrDErCq9Y'
        self.supabase: Client = create_client(self.url, self.key)
        
        # Initialize processor
        self.processor = AdaptiveSECProcessor(str(self.data_dir))
        
        # Use existing table structure
        self.transactions_table = 'transactions_2025q2'
        
        # Results tracking
        self.results = {}
        self.retry_stats = {
            'total_attempted': 0,
            'successful': 0,
            'failed': 0,
            'total_transactions': 0
        }
    
    def safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def load_quarter_to_supabase(self, quarter: str, result: Dict) -> bool:
        """Load a single quarter's data to Supabase with improved error handling"""
        logger.info(f"📤 Loading {quarter} to Supabase...")
        
        transactions_df = result['transactions']
        batch_size = 25  # Smaller batches for better reliability
        total_imported = 0
        total_errors = 0
        
        try:
            for i in range(0, len(transactions_df), batch_size):
                batch_df = transactions_df.iloc[i:i + batch_size]
                
                # Prepare batch data
                batch_data = []
                for _, row in batch_df.iterrows():
                    try:
                        transaction = {
                            'accession_number': str(row['ACCESSION_NUMBER']),
                            'company_cik': str(row['ISSUERCIK']).zfill(10),
                            'insider_cik': str(row['RPTOWNERCIK']).zfill(10),
                            'transaction_date': str(row['TRANS_DATE']),
                            'transaction_code': str(row['TRANS_ACQUIRED_DISP_CD']),
                            'transaction_shares': self.safe_float(row['TRANS_SHARES']),
                            'transaction_price_per_share': self.safe_float(row['TRANS_PRICEPERSHARE']),
                            'calculated_transaction_value': self.safe_float(row['VALU_OWND_FOLWNG_TRANS']),
                            'shares_owned_following_transaction': self.safe_float(row['SHRS_OWND_FOLWNG_TRANS']),
                            'security_title': str(row['SECURITY_TITLE']),
                            'file_type': '4',
                            'quarter': quarter,
                            'data_source': f'{quarter}_form345',
                            'year': int(quarter.split('q')[0])
                        }
                        batch_data.append(transaction)
                    except Exception as e:
                        logger.warning(f"⚠️  Skipping problematic record: {e}")
                        total_errors += 1
                        continue
                
                if batch_data:
                    # Insert with retry logic
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            result_insert = self.supabase.table(self.transactions_table).insert(batch_data).execute()
                            if result_insert.data:
                                total_imported += len(result_insert.data)
                                break
                            else:
                                logger.warning(f"⚠️  Empty response on attempt {attempt + 1}")
                        except Exception as e:
                            logger.warning(f"⚠️  Insert attempt {attempt + 1} failed: {e}")
                            if attempt < max_retries - 1:
                                time.sleep(2 ** attempt)  # Exponential backoff
                            else:
                                logger.error(f"❌ Failed to insert batch after {max_retries} attempts")
                                total_errors += len(batch_data)
                
                # Progress update
                if i % (batch_size * 10) == 0:
                    logger.info(f"  📊 Imported {total_imported:,}/{len(transactions_df):,} transactions...")
            
            logger.info(f"✅ Successfully loaded {quarter}: {total_imported:,} transactions")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load {quarter}: {e}")
            return False
    
    def process_failed_quarter(self, quarter: str) -> Dict:
        """Process a single failed quarter with retry logic"""
        zip_file = f"{quarter}_form345.zip"
        
        logger.info(f"\n🔄 Processing failed quarter: {quarter}")
        logger.info("-" * 60)
        
        self.retry_stats['total_attempted'] += 1
        
        try:
            # Process the quarter
            result = self.processor.process_quarter(zip_file)
            
            if 'error' in result:
                logger.error(f"❌ Failed to process {quarter}: {result['error']}")
                self.retry_stats['failed'] += 1
                return {'status': 'processing_failed', 'error': result['error']}
            
            # Load to Supabase with retry
            if self.load_quarter_to_supabase(quarter, result):
                self.retry_stats['successful'] += 1
                self.retry_stats['total_transactions'] += result['stats']['total_transactions']
                
                logger.info(f"✅ Successfully processed {quarter}")
                return {'status': 'success', 'quarter': quarter, 'stats': result['stats']}
            else:
                self.retry_stats['failed'] += 1
                return {'status': 'supabase_load_failed', 'quarter': quarter}
                
        except Exception as e:
            logger.error(f"❌ Unexpected error processing {quarter}: {e}")
            self.retry_stats['failed'] += 1
            return {'status': 'unexpected_error', 'error': str(e)}
    
    def retry_all_failed_quarters(self):
        """Retry all failed quarters individually"""
        # Load failed quarters from progress file
        progress_file = Path("consolidated_processing_progress.json")
        if not progress_file.exists():
            logger.error("❌ Progress file not found!")
            return
        
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        
        failed_quarters = progress['failed']
        
        logger.info(f"🚀 Starting retry processing of {len(failed_quarters)} failed quarters")
        logger.info(f"📊 Failed quarters: {failed_quarters}")
        
        # Process each failed quarter
        for i, quarter in enumerate(failed_quarters, 1):
            logger.info(f"\n[{i}/{len(failed_quarters)}] 🔄 Retrying {quarter}")
            
            result = self.process_failed_quarter(quarter)
            self.results[quarter] = result
            
            # Small delay between quarters to avoid overwhelming the system
            if i < len(failed_quarters):
                time.sleep(5)
        
        # Print final summary
        print("\n" + "="*80)
        print("🎯 RETRY PROCESSING COMPLETE!")
        print("="*80)
        print(f"Total attempted: {self.retry_stats['total_attempted']}")
        print(f"Successful: {self.retry_stats['successful']}")
        print(f"Failed: {self.retry_stats['failed']}")
        print(f"Total transactions: {self.retry_stats['total_transactions']:,}")
        print("="*80)

def main():
    """Run retry processing for failed quarters"""
    processor = FailedQuarterRetryProcessor()
    processor.retry_all_failed_quarters()

if __name__ == "__main__":
    main()

