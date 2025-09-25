#!/usr/bin/env python3
"""
Consolidated Batch Processor - Uses a single table for all quarters
Much simpler approach that avoids table creation issues
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
        logging.FileHandler('consolidated_batch_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConsolidatedBatchProcessor:
    def __init__(self, data_dir: str = "sec_insider_data"):
        """Initialize consolidated batch processor"""
        self.data_dir = Path(data_dir)
        
        # Supabase connection
        self.url = 'https://sifpyksougtsklegphxf.supabase.co'
        self.key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZnB5a3NvdWd0c2tsZWdwaHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NzI5OTUsImV4cCI6MjA3NDI0ODk5NX0.NDc6nd1w9SFhgYYJkRrAqD_3pO584tUrGcNrDErCq9Y'
        self.supabase: Client = create_client(self.url, self.key)
        
        # Initialize processor
        self.processor = AdaptiveSECProcessor(str(self.data_dir))
        
        # Use existing table structure
        self.transactions_table = 'transactions_2025q2'  # Use existing table
        self.companies_table = 'companies_2025q2'       # Use existing table  
        self.insiders_table = 'insiders_2025q2'         # Use existing table
        
        # Progress tracking
        self.progress_file = Path("consolidated_processing_progress.json")
        self.progress = self.load_progress()
        
        # Results tracking
        self.results = {}
        self.summary_stats = {
            'total_quarters': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'total_transactions': 0,
            'start_time': None,
            'end_time': None
        }
    
    def load_progress(self) -> Dict:
        """Load processing progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            'completed': [],
            'failed': [],
            'skipped': [],
            'start_time': None
        }
    
    def save_progress(self):
        """Save processing progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def get_quarter_name(self, zip_file: str) -> str:
        """Extract quarter name from zip file"""
        return zip_file.replace('_form345.zip', '')
    
    def safe_float(self, value, default=0):
        """Safely convert value to float"""
        if pd.isna(value) or np.isinf(value) or np.isnan(value):
            return default
        try:
            return float(value)
        except:
            return default
    
    def check_quarter_already_processed(self, quarter: str) -> bool:
        """Check if quarter data already exists in the consolidated table"""
        try:
            result = self.supabase.table(self.transactions_table).select('quarter', count='exact').eq('quarter', quarter).execute()
            return result.count > 0
        except Exception as e:
            logger.debug(f"Error checking quarter {quarter}: {e}")
            return False
    
    def load_quarter_to_supabase(self, quarter: str, result: Dict) -> bool:
        """Load a single quarter's data to the consolidated Supabase table"""
        logger.info(f"📤 Loading {quarter} to consolidated table...")
        
        # Prepare transaction data
        transactions_df = result['transactions']
        batch_size = 50  # Smaller batches for reliability
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
                    # Insert batch into consolidated table
                    result_insert = self.supabase.table(self.transactions_table).insert(batch_data).execute()
                    total_imported += len(result_insert.data)
                
                # Progress update
                if i % (batch_size * 10) == 0:
                    logger.info(f"  📊 Imported {total_imported:,}/{len(transactions_df):,} transactions...")
            
            logger.info(f"✅ Successfully loaded {quarter}: {total_imported:,} transactions")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load {quarter}: {e}")
            return False
    
    def process_single_quarter(self, zip_file: str) -> Dict:
        """Process a single quarter"""
        quarter = self.get_quarter_name(zip_file)
        
        logger.info(f"🔄 Processing {quarter}...")
        
        # Check if already processed
        if quarter in self.progress['completed']:
            logger.info(f"⏭️  {quarter} already processed")
            self.summary_stats['skipped'] += 1
            return {'status': 'already_processed', 'quarter': quarter}
        
        # Check if already in database
        if self.check_quarter_already_processed(quarter):
            logger.info(f"⏭️  {quarter} already exists in database")
            self.progress['completed'].append(quarter)
            self.summary_stats['skipped'] += 1
            return {'status': 'already_in_database', 'quarter': quarter}
        
        try:
            # Process the quarter
            result = self.processor.process_quarter(zip_file)
            
            if 'error' in result:
                logger.error(f"❌ Failed to process {quarter}: {result['error']}")
                self.progress['failed'].append(quarter)
                self.summary_stats['failed'] += 1
                return {'status': 'processing_failed', 'error': result['error']}
            
            # Load to Supabase
            if self.load_quarter_to_supabase(quarter, result):
                self.progress['completed'].append(quarter)
                self.summary_stats['successful'] += 1
                self.summary_stats['total_transactions'] += result['stats']['total_transactions']
                
                logger.info(f"✅ Successfully processed {quarter}")
                return {'status': 'success', 'quarter': quarter, 'stats': result['stats']}
            else:
                self.progress['failed'].append(quarter)
                self.summary_stats['failed'] += 1
                return {'status': 'supabase_load_failed', 'quarter': quarter}
                
        except Exception as e:
            logger.error(f"❌ Unexpected error processing {quarter}: {e}")
            self.progress['failed'].append(quarter)
            self.summary_stats['failed'] += 1
            return {'status': 'unexpected_error', 'error': str(e)}
    
    def process_all_quarters(self):
        """Process all quarters"""
        all_quarters = [f.name for f in self.data_dir.glob("*_form345.zip")]
        all_quarters.sort()
        
        self.summary_stats['total_quarters'] = len(all_quarters)
        self.summary_stats['start_time'] = datetime.now().isoformat()
        
        logger.info(f"🚀 Starting consolidated batch processing of {len(all_quarters)} quarters")
        logger.info(f"📊 Using consolidated table: {self.transactions_table}")
        
        # Process each quarter
        for i, zip_file in enumerate(all_quarters, 1):
            quarter = self.get_quarter_name(zip_file)
            
            logger.info(f"\n[{i}/{len(all_quarters)}] 🔄 Processing {quarter}")
            logger.info("-" * 60)
            
            result = self.process_single_quarter(zip_file)
            self.results[quarter] = result
            
            # Save progress every 5 quarters
            if i % 5 == 0:
                self.save_progress()
                logger.info(f"💾 Progress saved ({i}/{len(all_quarters)} processed)")
        
        # Final processing
        self.summary_stats['end_time'] = datetime.now().isoformat()
        self.save_progress()
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 CONSOLIDATED BATCH PROCESSING COMPLETE!")
        print("="*80)
        print(f"Total quarters: {self.summary_stats['total_quarters']}")
        print(f"Successful: {self.summary_stats['successful']}")
        print(f"Skipped: {self.summary_stats['skipped']}")
        print(f"Failed: {self.summary_stats['failed']}")
        print(f"Total transactions: {self.summary_stats['total_transactions']:,}")
        print(f"Consolidated table: {self.transactions_table}")
        print("="*80)

def main():
    """Run consolidated batch processing"""
    processor = ConsolidatedBatchProcessor()
    processor.process_all_quarters()

if __name__ == "__main__":
    main()
