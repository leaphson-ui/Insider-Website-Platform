#!/usr/bin/env python3
"""
Updated SEC data cleaning pipeline for multi-file TSV structure
Handles schema evolution from 2006 to present
"""

import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiFileSECCleaner:
    def __init__(self):
        self.schema_mappings = self.load_schema_mappings()
        self.processed_quarters = []
        
    def load_schema_mappings(self) -> Dict:
        """Load schema mappings for different file types and time periods"""
        return {
            'NONDERIV_TRANS': {
                'columns_2006_2010': [
                    'submission_id', 'issuer_cik', 'issuer_name', 'issuer_trading_symbol',
                    'rpt_owner_cik', 'rpt_owner_name', 'is_director', 'is_officer', 
                    'is_ten_percent_owner', 'officer_title', 'transaction_date',
                    'transaction_code', 'equity_swap_involved', 'transaction_shares',
                    'transaction_price_per_share', 'transaction_acquired_disposed_code',
                    'shares_owned_following_transaction', 'security_title'
                ],
                'columns_2011_present': [
                    'submission_id', 'issuer_cik', 'issuer_name', 'issuer_trading_symbol',
                    'rpt_owner_cik', 'rpt_owner_name', 'is_director', 'is_officer',
                    'is_ten_percent_owner', 'officer_title', 'transaction_date',
                    'transaction_code', 'equity_swap_involved', 'transaction_shares',
                    'transaction_price_per_share', 'transaction_acquired_disposed_code',
                    'shares_owned_following_transaction', 'security_title', 'underlying_security_title',
                    'underlying_security_shares', 'exercise_date', 'expiration_date',
                    'underlying_security_price', 'conversion_or_exercise_price'
                ]
            },
            'DERIV_TRANS': {
                'columns_2006_2010': [
                    'submission_id', 'issuer_cik', 'issuer_name', 'issuer_trading_symbol',
                    'rpt_owner_cik', 'rpt_owner_name', 'is_director', 'is_officer',
                    'is_ten_percent_owner', 'officer_title', 'transaction_date',
                    'transaction_code', 'equity_swap_involved', 'transaction_shares',
                    'transaction_price_per_share', 'transaction_acquired_disposed_code',
                    'shares_owned_following_transaction', 'security_title'
                ],
                'columns_2011_present': [
                    'submission_id', 'issuer_cik', 'issuer_name', 'issuer_trading_symbol',
                    'rpt_owner_cik', 'rpt_owner_name', 'is_director', 'is_officer',
                    'is_ten_percent_owner', 'officer_title', 'transaction_date',
                    'transaction_code', 'equity_swap_involved', 'transaction_shares',
                    'transaction_price_per_share', 'transaction_acquired_disposed_code',
                    'shares_owned_following_transaction', 'security_title', 'underlying_security_title',
                    'underlying_security_shares', 'exercise_date', 'expiration_date',
                    'underlying_security_price', 'conversion_or_exercise_price'
                ]
            }
        }
    
    def determine_year_period(self, quarter_path: str) -> str:
        """Determine which schema period to use based on quarter path"""
        # Extract year from directory name like "2006q1_form345" or "2024q3_form345"
        try:
            year = int(quarter_path.split('q')[0])
            if year <= 2010:
                return '2006_2010'
            else:
                return '2011_present'
        except:
            return '2011_present'  # Default to newer schema
    
    def process_quarter_directory(self, quarter_path: str) -> Dict:
        """Process all files in a quarter directory"""
        logger.info(f"Processing quarter: {quarter_path}")
        
        quarter_data = {
            'quarter': quarter_path,
            'submissions': None,
            'reporting_owners': None,
            'transactions': [],
            'holdings': [],
            'signatures': None,
            'footnotes': None
        }
        
        year_period = self.determine_year_period(quarter_path)
        logger.info(f"Using schema period: {year_period}")
        
        try:
            # Process files in order of dependency
            quarter_data['submissions'] = self.process_submissions_file(quarter_path)
            quarter_data['reporting_owners'] = self.process_reporting_owners_file(quarter_path)
            
            # Process transaction files
            quarter_data['transactions'].extend(
                self.process_transaction_file(quarter_path, 'NONDERIV_TRANS.tsv', year_period)
            )
            quarter_data['transactions'].extend(
                self.process_transaction_file(quarter_path, 'DERIV_TRANS.tsv', year_period)
            )
            
            # Process holdings
            quarter_data['holdings'].extend(
                self.process_holdings_file(quarter_path, 'NONDERIV_HOLDING.tsv')
            )
            quarter_data['holdings'].extend(
                self.process_holdings_file(quarter_path, 'DERIV_HOLDING.tsv')
            )
            
            # Process additional files
            quarter_data['signatures'] = self.process_signatures_file(quarter_path)
            quarter_data['footnotes'] = self.process_footnotes_file(quarter_path)
            
            logger.info(f"✓ Successfully processed {quarter_path}")
            
        except Exception as e:
            logger.error(f"Error processing {quarter_path}: {str(e)}")
            quarter_data['error'] = str(e)
        
        return quarter_data
    
    def process_submissions_file(self, quarter_path: str) -> pd.DataFrame:
        """Process SUBMISSION.tsv file"""
        file_path = os.path.join(quarter_path, 'SUBMISSION.tsv')
        
        if not os.path.exists(file_path):
            logger.warning(f"SUBMISSION.tsv not found in {quarter_path}")
            return pd.DataFrame()
        
        logger.info(f"Processing SUBMISSION.tsv from {quarter_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean submission data
        if 'submission_id' in df.columns:
            df['submission_id'] = df['submission_id'].astype(str).str.strip()
        
        # Parse submission date
        if 'submission_date' in df.columns:
            df['submission_date'] = pd.to_datetime(df['submission_date'], errors='coerce')
        
        return df
    
    def process_reporting_owners_file(self, quarter_path: str) -> pd.DataFrame:
        """Process REPORTINGOWNER.tsv file"""
        file_path = os.path.join(quarter_path, 'REPORTINGOWNER.tsv')
        
        if not os.path.exists(file_path):
            logger.warning(f"REPORTINGOWNER.tsv not found in {quarter_path}")
            return pd.DataFrame()
        
        logger.info(f"Processing REPORTINGOWNER.tsv from {quarter_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean owner data
        if 'rpt_owner_cik' in df.columns:
            df['rpt_owner_cik'] = df['rpt_owner_cik'].astype(str).str.strip().str.zfill(10)
        
        if 'rpt_owner_name' in df.columns:
            df['rpt_owner_name'] = df['rpt_owner_name'].astype(str).str.strip()
        
        # Convert boolean columns
        bool_cols = ['is_director', 'is_officer', 'is_ten_percent_owner']
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].fillna(False).astype(bool)
        
        return df
    
    def process_transaction_file(self, quarter_path: str, filename: str, year_period: str) -> List[pd.DataFrame]:
        """Process transaction files (NONDERIV_TRANS.tsv or DERIV_TRANS.tsv)"""
        file_path = os.path.join(quarter_path, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"{filename} not found in {quarter_path}")
            return []
        
        logger.info(f"Processing {filename} from {quarter_path}")
        
        try:
            df = pd.read_csv(file_path, sep='\t', low_memory=False)
            
            if df.empty:
                return []
            
            # Get expected columns for this file type and period
            file_type = filename.replace('.tsv', '').upper()
            expected_columns = self.schema_mappings.get(file_type, {}).get(f'columns_{year_period}', [])
            
            # Handle schema differences
            df = self.handle_schema_differences(df, expected_columns, file_type, year_period)
            
            # Clean transaction data
            df = self.clean_transaction_data(df)
            
            # Add file type identifier
            df['file_type'] = file_type
            df['quarter'] = quarter_path
            
            return [df]
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            return []
    
    def handle_schema_differences(self, df: pd.DataFrame, expected_columns: List[str], file_type: str, year_period: str) -> pd.DataFrame:
        """Handle differences in schema across time periods"""
        logger.info(f"Handling schema differences for {file_type} ({year_period})")
        
        # Add missing columns with default values
        for col in expected_columns:
            if col not in df.columns:
                logger.info(f"Adding missing column: {col}")
                if 'date' in col.lower():
                    df[col] = pd.NaT
                elif 'shares' in col.lower() or 'price' in col.lower():
                    df[col] = np.nan
                else:
                    df[col] = None
        
        # Remove extra columns not in expected schema
        extra_columns = [col for col in df.columns if col not in expected_columns]
        if extra_columns:
            logger.info(f"Removing extra columns: {extra_columns}")
            df = df.drop(columns=extra_columns)
        
        # Reorder columns to match expected schema
        df = df[expected_columns]
        
        return df
    
    def clean_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean transaction-specific data"""
        logger.info("Cleaning transaction data...")
        
        # Clean dates
        if 'transaction_date' in df.columns:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        # Clean transaction codes
        if 'transaction_code' in df.columns:
            df['transaction_code'] = df['transaction_code'].astype(str).str.strip().str.upper()
        
        # Clean numeric fields
        numeric_cols = ['transaction_shares', 'transaction_price_per_share', 'shares_owned_following_transaction']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate transaction value if missing
        if 'transaction_price_per_share' in df.columns and 'transaction_shares' in df.columns:
            df['calculated_transaction_value'] = df['transaction_shares'] * df['transaction_price_per_share']
        
        # Clean CIKs
        cik_cols = ['issuer_cik', 'rpt_owner_cik']
        for col in cik_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.zfill(10)
        
        # Clean company/owner names
        name_cols = ['issuer_name', 'rpt_owner_name']
        for col in name_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        return df
    
    def process_holdings_file(self, quarter_path: str, filename: str) -> List[pd.DataFrame]:
        """Process holdings files"""
        file_path = os.path.join(quarter_path, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"{filename} not found in {quarter_path}")
            return []
        
        logger.info(f"Processing {filename} from {quarter_path}")
        
        try:
            df = pd.read_csv(file_path, sep='\t', low_memory=False)
            
            if df.empty:
                return []
            
            # Clean holdings data
            df = self.clean_holdings_data(df)
            df['file_type'] = filename.replace('.tsv', '').upper()
            df['quarter'] = quarter_path
            
            return [df]
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            return []
    
    def clean_holdings_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean holdings-specific data"""
        logger.info("Cleaning holdings data...")
        
        # Clean numeric fields
        numeric_cols = ['shares_owned', 'value_owned']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def process_signatures_file(self, quarter_path: str) -> pd.DataFrame:
        """Process OWNER_SIGNATURE.tsv file"""
        file_path = os.path.join(quarter_path, 'OWNER_SIGNATURE.tsv')
        
        if not os.path.exists(file_path):
            logger.warning(f"OWNER_SIGNATURE.tsv not found in {quarter_path}")
            return pd.DataFrame()
        
        logger.info(f"Processing OWNER_SIGNATURE.tsv from {quarter_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        return df
    
    def process_footnotes_file(self, quarter_path: str) -> pd.DataFrame:
        """Process FOOTNOTES.tsv file"""
        file_path = os.path.join(quarter_path, 'FOOTNOTES.tsv')
        
        if not os.path.exists(file_path):
            logger.warning(f"FOOTNOTES.tsv not found in {quarter_path}")
            return pd.DataFrame()
        
        logger.info(f"Processing FOOTNOTES.tsv from {quarter_path}")
        
        # FOOTNOTES files can be very large, so process in chunks
        try:
            chunk_list = []
            chunk_size = 10000
            
            for chunk in pd.read_csv(file_path, sep='\t', chunksize=chunk_size, low_memory=False):
                chunk_list.append(chunk)
                if len(chunk_list) >= 10:  # Limit to prevent memory issues
                    break
            
            df = pd.concat(chunk_list, ignore_index=True) if chunk_list else pd.DataFrame()
            return df
            
        except Exception as e:
            logger.error(f"Error processing FOOTNOTES.tsv: {str(e)}")
            return pd.DataFrame()
    
    def consolidate_quarter_data(self, quarter_data: Dict) -> Dict:
        """Consolidate all data from a quarter into a unified format"""
        logger.info(f"Consolidating data for {quarter_data['quarter']}")
        
        consolidated = {
            'quarter': quarter_data['quarter'],
            'transactions': pd.DataFrame(),
            'companies': pd.DataFrame(),
            'insiders': pd.DataFrame(),
            'stats': {}
        }
        
        # Combine all transaction data
        if quarter_data['transactions']:
            all_transactions = pd.concat(quarter_data['transactions'], ignore_index=True)
            consolidated['transactions'] = all_transactions
            
            # Extract unique companies
            if 'issuer_cik' in all_transactions.columns and 'issuer_name' in all_transactions.columns:
                companies = all_transactions[['issuer_cik', 'issuer_name', 'issuer_trading_symbol']].drop_duplicates()
                consolidated['companies'] = companies
            
            # Extract unique insiders
            if 'rpt_owner_cik' in all_transactions.columns and 'rpt_owner_name' in all_transactions.columns:
                insiders = all_transactions[['rpt_owner_cik', 'rpt_owner_name', 'is_director', 'is_officer', 'is_ten_percent_owner']].drop_duplicates()
                consolidated['insiders'] = insiders
        
        # Generate statistics
        consolidated['stats'] = self.generate_quarter_stats(consolidated)
        
        return consolidated
    
    def generate_quarter_stats(self, consolidated_data: Dict) -> Dict:
        """Generate statistics for a quarter's data"""
        stats = {
            'total_transactions': len(consolidated_data['transactions']),
            'unique_companies': len(consolidated_data['companies']),
            'unique_insiders': len(consolidated_data['insiders']),
            'date_range': {},
            'transaction_types': {}
        }
        
        if not consolidated_data['transactions'].empty:
            if 'transaction_date' in consolidated_data['transactions'].columns:
                stats['date_range'] = {
                    'earliest': consolidated_data['transactions']['transaction_date'].min(),
                    'latest': consolidated_data['transactions']['transaction_date'].max()
                }
            
            if 'transaction_code' in consolidated_data['transactions'].columns:
                stats['transaction_types'] = consolidated_data['transactions']['transaction_code'].value_counts().to_dict()
        
        return stats
    
    def process_multiple_quarters(self, quarter_directories: List[str]) -> Dict:
        """Process multiple quarter directories"""
        logger.info(f"Processing {len(quarter_directories)} quarters")
        
        all_quarters_data = {}
        
        for quarter_dir in quarter_directories:
            if os.path.isdir(quarter_dir):
                quarter_data = self.process_quarter_directory(quarter_dir)
                consolidated = self.consolidate_quarter_data(quarter_data)
                all_quarters_data[quarter_dir] = consolidated
            else:
                logger.warning(f"Directory {quarter_dir} not found")
        
        return all_quarters_data
    
    def save_processed_data(self, all_quarters_data: Dict, output_dir: str = "processed_data"):
        """Save processed data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Saving processed data to {output_dir}")
        
        # Save each quarter's data
        for quarter, data in all_quarters_data.items():
            quarter_output_dir = os.path.join(output_dir, quarter)
            os.makedirs(quarter_output_dir, exist_ok=True)
            
            # Save transactions
            if not data['transactions'].empty:
                transactions_file = os.path.join(quarter_output_dir, "transactions.csv")
                data['transactions'].to_csv(transactions_file, index=False)
                logger.info(f"Saved {len(data['transactions'])} transactions to {transactions_file}")
            
            # Save companies
            if not data['companies'].empty:
                companies_file = os.path.join(quarter_output_dir, "companies.csv")
                data['companies'].to_csv(companies_file, index=False)
                logger.info(f"Saved {len(data['companies'])} companies to {companies_file}")
            
            # Save insiders
            if not data['insiders'].empty:
                insiders_file = os.path.join(quarter_output_dir, "insiders.csv")
                data['insiders'].to_csv(insiders_file, index=False)
                logger.info(f"Saved {len(data['insiders'])} insiders to {insiders_file}")
        
        # Save summary statistics
        summary_stats = {}
        for quarter, data in all_quarters_data.items():
            summary_stats[quarter] = data['stats']
        
        stats_file = os.path.join(output_dir, "processing_summary.json")
        with open(stats_file, 'w') as f:
            json.dump(summary_stats, f, indent=2, default=str)
        
        logger.info(f"Processing summary saved to {stats_file}")

def main():
    """Main processing function"""
    cleaner = MultiFileSECCleaner()
    
    # Look for quarter directories
    quarter_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and 'q' in d.lower()]
    
    if not quarter_dirs:
        print("No quarter directories found!")
        print("Expected directories like: 2006q1_form345, 2024q3_form345, etc.")
        return
    
    print(f"Found {len(quarter_dirs)} quarter directories: {quarter_dirs}")
    
    # Process all quarters
    all_quarters_data = cleaner.process_multiple_quarters(quarter_dirs)
    
    # Save processed data
    cleaner.save_processed_data(all_quarters_data)
    
    # Print summary
    print("\n" + "="*60)
    print("MULTI-FILE SEC DATA PROCESSING SUMMARY")
    print("="*60)
    
    total_transactions = 0
    total_companies = 0
    total_insiders = 0
    
    for quarter, data in all_quarters_data.items():
        stats = data['stats']
        print(f"\n{quarter}:")
        print(f"  Transactions: {stats['total_transactions']:,}")
        print(f"  Companies: {stats['unique_companies']:,}")
        print(f"  Insiders: {stats['unique_insiders']:,}")
        
        total_transactions += stats['total_transactions']
        total_companies += stats['unique_companies']
        total_insiders += stats['unique_insiders']
    
    print(f"\nTOTALS:")
    print(f"  Transactions: {total_transactions:,}")
    print(f"  Companies: {total_companies:,}")
    print(f"  Insiders: {total_insiders:,}")
    
    print(f"\nProcessed data saved to: processed_data/")

if __name__ == "__main__":
    main()
