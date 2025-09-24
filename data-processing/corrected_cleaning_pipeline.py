#!/usr/bin/env python3
"""
Corrected SEC data cleaning pipeline with actual column mappings
Based on real SEC data structure analysis
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

class CorrectedSECCleaner:
    def __init__(self):
        # Actual column mappings based on real SEC data
        self.column_mappings = {
            'NONDERIV_TRANS': {
                'accession_number': 'ACCESSION_NUMBER',
                'security_title': 'SECURITY_TITLE',
                'transaction_date': 'TRANS_DATE',
                'deemed_execution_date': 'DEEMED_EXECUTION_DATE',
                'transaction_form_type': 'TRANS_FORM_TYPE',
                'transaction_code': 'TRANS_CODE',
                'equity_swap_involved': 'EQUITY_SWAP_INVOLVED',
                'transaction_timeliness': 'TRANS_TIMELINESS',
                'transaction_shares': 'TRANS_SHARES',
                'transaction_price_per_share': 'TRANS_PRICEPERSHARE',
                'transaction_acquired_disposed_code': 'TRANS_ACQUIRED_DISP_CD',
                'shares_owned_following_transaction': 'SHRS_OWND_FOLWNG_TRANS',
                'value_owned_following_transaction': 'VALU_OWND_FOLWNG_TRANS',
                'direct_indirect_ownership': 'DIRECT_INDIRECT_OWNERSHIP',
                'nature_of_ownership': 'NATURE_OF_OWNERSHIP'
            },
            'DERIV_TRANS': {
                'accession_number': 'ACCESSION_NUMBER',
                'security_title': 'SECURITY_TITLE',
                'conversion_exercise_price': 'CONV_EXERCISE_PRICE',
                'transaction_date': 'TRANS_DATE',
                'deemed_execution_date': 'DEEMED_EXECUTION_DATE',
                'transaction_form_type': 'TRANS_FORM_TYPE',
                'transaction_code': 'TRANS_CODE',
                'equity_swap_involved': 'EQUITY_SWAP_INVOLVED',
                'transaction_timeliness': 'TRANS_TIMELINESS',
                'transaction_shares': 'TRANS_SHARES',
                'transaction_total_value': 'TRANS_TOTAL_VALUE',
                'transaction_price_per_share': 'TRANS_PRICEPERSHARE',
                'transaction_acquired_disposed_code': 'TRANS_ACQUIRED_DISP_CD',
                'exercise_date': 'EXCERCISE_DATE',
                'expiration_date': 'EXPIRATION_DATE',
                'underlying_security_title': 'UNDLYNG_SEC_TITLE',
                'underlying_security_shares': 'UNDLYNG_SEC_SHARES',
                'underlying_security_value': 'UNDLYNG_SEC_VALUE',
                'shares_owned_following_transaction': 'SHRS_OWND_FOLWNG_TRANS',
                'value_owned_following_transaction': 'VALU_OWND_FOLWNG_TRANS',
                'direct_indirect_ownership': 'DIRECT_INDIRECT_OWNERSHIP',
                'nature_of_ownership': 'NATURE_OF_OWNERSHIP'
            },
            'REPORTINGOWNER': {
                'accession_number': 'ACCESSION_NUMBER',
                'rpt_owner_cik': 'RPTOWNERCIK',
                'rpt_owner_name': 'RPTOWNERNAME',
                'rpt_owner_relationship': 'RPTOWNER_RELATIONSHIP',
                'rpt_owner_title': 'RPTOWNER_TITLE',
                'rpt_owner_txt': 'RPTOWNER_TXT',
                'rpt_owner_street1': 'RPTOWNER_STREET1',
                'rpt_owner_street2': 'RPTOWNER_STREET2',
                'rpt_owner_city': 'RPTOWNER_CITY',
                'rpt_owner_state': 'RPTOWNER_STATE',
                'rpt_owner_zipcode': 'RPTOWNER_ZIPCODE',
                'rpt_owner_state_desc': 'RPTOWNER_STATE_DESC',
                'file_number': 'FILE_NUMBER'
            },
            'SUBMISSION': {
                'accession_number': 'ACCESSION_NUMBER',
                'form_type': 'FORM_TYPE',
                'issuer_cik': 'ISSUER_CIK',
                'issuer_name': 'ISSUER_NAME',
                'issuer_trading_symbol': 'ISSUER_TRADING_SYMBOL',
                'issuer_company_name': 'ISSUER_COMPANY_NAME',
                'issuer_state': 'ISSUER_STATE',
                'issuer_state_desc': 'ISSUER_STATE_DESC',
                'issuer_fiscal_year_end': 'ISSUER_FISCAL_YEAR_END',
                'issuer_sic': 'ISSUER_SIC',
                'issuer_sic_desc': 'ISSUER_SIC_DESC',
                'issuer_business_street1': 'ISSUER_BUSINESS_STREET1',
                'issuer_business_street2': 'ISSUER_BUSINESS_STREET2',
                'issuer_business_city': 'ISSUER_BUSINESS_CITY',
                'issuer_business_state': 'ISSUER_BUSINESS_STATE',
                'issuer_business_zipcode': 'ISSUER_BUSINESS_ZIPCODE',
                'issuer_business_phone': 'ISSUER_BUSINESS_PHONE',
                'issuer_mailing_street1': 'ISSUER_MAILING_STREET1',
                'issuer_mailing_street2': 'ISSUER_MAILING_STREET2',
                'issuer_mailing_city': 'ISSUER_MAILING_CITY',
                'issuer_mailing_state': 'ISSUER_MAILING_STATE',
                'issuer_mailing_zipcode': 'ISSUER_MAILING_ZIPCODE',
                'filing_date': 'FILING_DATE',
                'report_date': 'REPORT_DATE',
                'period_of_report': 'PERIOD_OF_REPORT',
                'file_number': 'FILE_NUMBER',
                'film_number': 'FILM_NUMBER',
                'edgar_link': 'EDGAR_LINK'
            }
        }
        
    def process_quarter_directory(self, quarter_path: str) -> Dict:
        """Process all files in a quarter directory with correct column mappings"""
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
        
        try:
            # Process files in order of dependency
            quarter_data['submissions'] = self.process_submissions_file(quarter_path)
            quarter_data['reporting_owners'] = self.process_reporting_owners_file(quarter_path)
            
            # Process transaction files
            quarter_data['transactions'].extend(
                self.process_transaction_file(quarter_path, 'NONDERIV_TRANS.tsv')
            )
            quarter_data['transactions'].extend(
                self.process_transaction_file(quarter_path, 'DERIV_TRANS.tsv')
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
        """Process SUBMISSION.tsv file with correct column mapping"""
        file_path = os.path.join(quarter_path, 'SUBMISSION.tsv')
        
        if not os.path.exists(file_path):
            logger.warning(f"SUBMISSION.tsv not found in {quarter_path}")
            return pd.DataFrame()
        
        logger.info(f"Processing SUBMISSION.tsv from {quarter_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Rename columns to standard names
        mapping = self.column_mappings['SUBMISSION']
        df = df.rename(columns={v: k for k, v in mapping.items() if v in df.columns})
        
        # Clean submission data
        if 'accession_number' in df.columns:
            df['accession_number'] = df['accession_number'].astype(str).str.strip()
        
        if 'issuer_cik' in df.columns:
            df['issuer_cik'] = df['issuer_cik'].astype(str).str.strip().str.zfill(10)
        
        # Parse dates
        date_cols = ['filing_date', 'report_date', 'period_of_report']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def process_reporting_owners_file(self, quarter_path: str) -> pd.DataFrame:
        """Process REPORTINGOWNER.tsv file with correct column mapping"""
        file_path = os.path.join(quarter_path, 'REPORTINGOWNER.tsv')
        
        if not os.path.exists(file_path):
            logger.warning(f"REPORTINGOWNER.tsv not found in {quarter_path}")
            return pd.DataFrame()
        
        logger.info(f"Processing REPORTINGOWNER.tsv from {quarter_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Rename columns to standard names
        mapping = self.column_mappings['REPORTINGOWNER']
        df = df.rename(columns={v: k for k, v in mapping.items() if v in df.columns})
        
        # Clean owner data
        if 'rpt_owner_cik' in df.columns:
            df['rpt_owner_cik'] = df['rpt_owner_cik'].astype(str).str.strip().str.zfill(10)
        
        if 'rpt_owner_name' in df.columns:
            df['rpt_owner_name'] = df['rpt_owner_name'].astype(str).str.strip()
        
        # Extract director/officer flags from relationship field
        if 'rpt_owner_relationship' in df.columns:
            df['is_director'] = df['rpt_owner_relationship'].str.contains('Director', case=False, na=False)
            df['is_officer'] = df['rpt_owner_relationship'].str.contains('Officer', case=False, na=False)
            df['is_ten_percent_owner'] = df['rpt_owner_relationship'].str.contains('10%', case=False, na=False)
        
        return df
    
    def process_transaction_file(self, quarter_path: str, filename: str) -> List[pd.DataFrame]:
        """Process transaction files with correct column mapping"""
        file_path = os.path.join(quarter_path, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"{filename} not found in {quarter_path}")
            return []
        
        logger.info(f"Processing {filename} from {quarter_path}")
        
        try:
            df = pd.read_csv(file_path, sep='\t', low_memory=False)
            
            if df.empty:
                return []
            
            # Get the correct column mapping for this file type
            file_type = filename.replace('.tsv', '').upper()
            mapping = self.column_mappings.get(file_type, {})
            
            # Rename columns to standard names
            df = df.rename(columns={v: k for k, v in mapping.items() if v in df.columns})
            
            # Clean transaction data
            df = self.clean_transaction_data(df)
            
            # Add file type identifier
            df['file_type'] = file_type
            df['quarter'] = quarter_path
            
            return [df]
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            return []
    
    def clean_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean transaction-specific data"""
        logger.info("Cleaning transaction data...")
        
        # Clean dates
        date_cols = ['transaction_date', 'deemed_execution_date', 'exercise_date', 'expiration_date']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean transaction codes
        if 'transaction_code' in df.columns:
            df['transaction_code'] = df['transaction_code'].astype(str).str.strip().str.upper()
        
        # Clean numeric fields
        numeric_cols = [
            'transaction_shares', 'transaction_price_per_share', 
            'shares_owned_following_transaction', 'value_owned_following_transaction',
            'transaction_total_value', 'conversion_exercise_price',
            'underlying_security_shares', 'underlying_security_value'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate transaction value if missing
        if 'transaction_price_per_share' in df.columns and 'transaction_shares' in df.columns:
            mask = df['transaction_shares'].notna() & df['transaction_price_per_share'].notna()
            df.loc[mask, 'calculated_transaction_value'] = (
                df.loc[mask, 'transaction_shares'] * df.loc[mask, 'transaction_price_per_share']
            )
        
        # Clean text fields
        text_cols = ['security_title', 'underlying_security_title', 'transaction_form_type']
        for col in text_cols:
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
            
            # Clean holdings data (basic cleaning for now)
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
        
        # Basic cleaning - we'll expand this as needed
        return df
    
    def process_signatures_file(self, quarter_path: str) -> pd.DataFrame:
        """Process OWNER_SIGNATURE.tsv file"""
        file_path = os.path.join(quarter_path, 'OWNER_SIGNATURE.tsv')
        
        if not os.path.exists(file_path):
            logger.warning(f"OWNER_SIGNATURE.tsv not found in {quarter_path}")
            return pd.DataFrame()
        
        logger.info(f"Processing OWNER_SIGNATURE.tsv from {quarter_path}")
        
        try:
            df = pd.read_csv(file_path, sep='\t', low_memory=False)
            return df
        except Exception as e:
            logger.error(f"Error processing OWNER_SIGNATURE.tsv: {str(e)}")
            return pd.DataFrame()
    
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
                if len(chunk_list) >= 5:  # Limit to prevent memory issues
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
            
            # Extract unique companies from submissions
            if not quarter_data['submissions'].empty:
                companies = quarter_data['submissions'][
                    ['issuer_cik', 'issuer_name', 'issuer_trading_symbol']
                ].drop_duplicates()
                consolidated['companies'] = companies
            
            # Extract unique insiders from reporting owners
            if not quarter_data['reporting_owners'].empty:
                insiders = quarter_data['reporting_owners'][
                    ['rpt_owner_cik', 'rpt_owner_name', 'is_director', 'is_officer', 'is_ten_percent_owner']
                ].drop_duplicates()
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
            'transaction_types': {},
            'file_types': {}
        }
        
        if not consolidated_data['transactions'].empty:
            # Date range
            if 'transaction_date' in consolidated_data['transactions'].columns:
                stats['date_range'] = {
                    'earliest': consolidated_data['transactions']['transaction_date'].min(),
                    'latest': consolidated_data['transactions']['transaction_date'].max()
                }
            
            # Transaction types
            if 'transaction_code' in consolidated_data['transactions'].columns:
                stats['transaction_types'] = consolidated_data['transactions']['transaction_code'].value_counts().to_dict()
            
            # File types
            if 'file_type' in consolidated_data['transactions'].columns:
                stats['file_types'] = consolidated_data['transactions']['file_type'].value_counts().to_dict()
        
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
    
    def save_processed_data(self, all_quarters_data: Dict, output_dir: str = "corrected_processed_data"):
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
    cleaner = CorrectedSECCleaner()
    
    # Look for quarter directories
    quarter_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and 'q' in d.lower()]
    
    if not quarter_dirs:
        print("No quarter directories found!")
        print("Expected directories like: 2006q1_form345, 2025q2_form345, etc.")
        return
    
    print(f"Found {len(quarter_dirs)} quarter directories: {quarter_dirs}")
    
    # Process all quarters
    all_quarters_data = cleaner.process_multiple_quarters(quarter_dirs)
    
    # Save processed data
    cleaner.save_processed_data(all_quarters_data)
    
    # Print summary
    print("\n" + "="*60)
    print("CORRECTED SEC DATA PROCESSING SUMMARY")
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
        
        if stats['date_range']:
            print(f"  Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
        if stats['transaction_types']:
            print(f"  Top transaction types:")
            for code, count in list(stats['transaction_types'].items())[:5]:
                print(f"    {code}: {count:,}")
        
        total_transactions += stats['total_transactions']
        total_companies += stats['unique_companies']
        total_insiders += stats['unique_insiders']
    
    print(f"\nTOTALS:")
    print(f"  Transactions: {total_transactions:,}")
    print(f"  Companies: {total_companies:,}")
    print(f"  Insiders: {total_insiders:,}")
    
    print(f"\nProcessed data saved to: corrected_processed_data/")

if __name__ == "__main__":
    main()
