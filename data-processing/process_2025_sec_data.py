#!/usr/bin/env python3
"""
2025-Specific SEC Data Processing Pipeline
Handles the modern SEC Form 4 data structure with proper ACCESSION_NUMBER linking
"""

import pandas as pd
import os
from pathlib import Path
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SEC2025Processor:
    def __init__(self, data_dir: str):
        """Initialize processor for 2025 SEC data"""
        self.data_dir = Path(data_dir)
        self.processed_data = {}
        
    def process_2025_data(self) -> Dict:
        """Process 2025 SEC data with proper ACCESSION_NUMBER linking"""
        logger.info("Processing 2025 SEC data with proper relationships...")
        
        # Step 1: Load all three core files
        submission_df = self.load_submission_file()
        reporting_owner_df = self.load_reporting_owner_file()
        transactions_df = self.load_transactions_file()
        
        logger.info(f"Loaded files:")
        logger.info(f"  - SUBMISSION: {len(submission_df)} records")
        logger.info(f"  - REPORTINGOWNER: {len(reporting_owner_df)} records")
        logger.info(f"  - NONDERIV_TRANS: {len(transactions_df)} records")
        
        # Step 2: Join transactions with submission data (company info)
        logger.info("Joining transactions with company data...")
        merged_df = transactions_df.merge(
            submission_df[['ACCESSION_NUMBER', 'ISSUERCIK', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL']],
            on='ACCESSION_NUMBER',
            how='left'
        )
        
        # Step 3: Join with reporting owner data (insider info)
        logger.info("Joining with insider data...")
        merged_df = merged_df.merge(
            reporting_owner_df[['ACCESSION_NUMBER', 'RPTOWNERCIK', 'RPTOWNERNAME', 'RPTOWNER_RELATIONSHIP']],
            on='ACCESSION_NUMBER',
            how='left'
        )
        
        logger.info(f"Final merged data: {len(merged_df)} records")
        
        # Step 4: Extract and clean the three datasets
        companies_df = self.extract_companies(merged_df)
        insiders_df = self.extract_insiders(merged_df)
        transactions_final_df = self.extract_transactions(merged_df)
        
        # Step 5: Create foreign key relationships
        companies_map = self.create_company_mapping(companies_df)
        insiders_map = self.create_insider_mapping(insiders_df)
        
        # Step 6: Add foreign keys to transactions
        transactions_final_df = self.add_foreign_keys(transactions_final_df, companies_map, insiders_map)
        
        self.processed_data = {
            'companies': companies_df,
            'insiders': insiders_df,
            'transactions': transactions_final_df,
            'companies_map': companies_map,
            'insiders_map': insiders_map
        }
        
        return self.processed_data
    
    def load_submission_file(self) -> pd.DataFrame:
        """Load SUBMISSION.tsv file"""
        file_path = self.data_dir / 'SUBMISSION.tsv'
        logger.info(f"Loading {file_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean company data
        df['ISSUERCIK'] = df['ISSUERCIK'].astype(str).str.strip().str.zfill(10)
        df['ISSUERNAME'] = df['ISSUERNAME'].astype(str).str.strip()
        df['ISSUERTRADINGSYMBOL'] = df['ISSUERTRADINGSYMBOL'].astype(str).str.strip()
        
        return df
    
    def load_reporting_owner_file(self) -> pd.DataFrame:
        """Load REPORTINGOWNER.tsv file"""
        file_path = self.data_dir / 'REPORTINGOWNER.tsv'
        logger.info(f"Loading {file_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean insider data
        df['RPTOWNERCIK'] = df['RPTOWNERCIK'].astype(str).str.strip().str.zfill(10)
        df['RPTOWNERNAME'] = df['RPTOWNERNAME'].astype(str).str.strip()
        
        return df
    
    def load_transactions_file(self) -> pd.DataFrame:
        """Load NONDERIV_TRANS.tsv file"""
        file_path = self.data_dir / 'NONDERIV_TRANS.tsv'
        logger.info(f"Loading {file_path}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean transaction data
        df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'], errors='coerce')
        df['TRANS_CODE'] = df['TRANS_CODE'].astype(str).str.strip().str.upper()
        
        # Clean numeric fields
        numeric_cols = ['TRANS_SHARES', 'TRANS_PRICEPERSHARE', 'SHRS_OWND_FOLWNG_TRANS']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate transaction value
        df['CALCULATED_TRANSACTION_VALUE'] = df['TRANS_SHARES'] * df['TRANS_PRICEPERSHARE']
        
        return df
    
    def extract_companies(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """Extract unique companies from merged data"""
        logger.info("Extracting companies...")
        
        companies_df = merged_df[['ISSUERCIK', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL']].drop_duplicates(subset=['ISSUERCIK'])
        companies_df = companies_df.rename(columns={
            'ISSUERCIK': 'cik',
            'ISSUERNAME': 'name',
            'ISSUERTRADINGSYMBOL': 'ticker'
        })
        
        logger.info(f"Extracted {len(companies_df)} unique companies")
        return companies_df
    
    def extract_insiders(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """Extract unique insiders from merged data"""
        logger.info("Extracting insiders...")
        
        insiders_df = merged_df[['RPTOWNERCIK', 'RPTOWNERNAME', 'RPTOWNER_RELATIONSHIP']].drop_duplicates(subset=['RPTOWNERCIK'])
        insiders_df = insiders_df.rename(columns={
            'RPTOWNERCIK': 'cik',
            'RPTOWNERNAME': 'name',
            'RPTOWNER_RELATIONSHIP': 'relationship'
        })
        
        # Add boolean fields based on relationship
        insiders_df['is_director'] = insiders_df['relationship'].str.contains('Director', case=False, na=False)
        insiders_df['is_officer'] = insiders_df['relationship'].str.contains('Officer', case=False, na=False)
        insiders_df['is_ten_percent_owner'] = insiders_df['relationship'].str.contains('TenPercentOwner', case=False, na=False)
        
        logger.info(f"Extracted {len(insiders_df)} unique insiders")
        return insiders_df
    
    def extract_transactions(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """Extract transactions from merged data"""
        logger.info("Extracting transactions...")
        
        transactions_df = merged_df.copy()
        
        # Rename columns to match our schema
        column_mapping = {
            'ACCESSION_NUMBER': 'accession_number',
            'TRANS_DATE': 'transaction_date',
            'TRANS_CODE': 'transaction_code',
            'TRANS_SHARES': 'transaction_shares',
            'TRANS_PRICEPERSHARE': 'transaction_price_per_share',
            'SHRS_OWND_FOLWNG_TRANS': 'shares_owned_following_transaction',
            'SECURITY_TITLE': 'security_title',
            'CALCULATED_TRANSACTION_VALUE': 'calculated_transaction_value'
        }
        
        transactions_df = transactions_df.rename(columns=column_mapping)
        
        # Add metadata
        transactions_df['file_type'] = '4'
        transactions_df['quarter'] = '2025q2_form345'
        
        logger.info(f"Extracted {len(transactions_df)} transactions")
        return transactions_df
    
    def create_company_mapping(self, companies_df: pd.DataFrame) -> Dict:
        """Create mapping from CIK to company ID"""
        companies_map = {}
        for idx, row in companies_df.iterrows():
            companies_map[row['cik']] = f"company_{idx}"  # Temporary ID
        return companies_map
    
    def create_insider_mapping(self, insiders_df: pd.DataFrame) -> Dict:
        """Create mapping from CIK to insider ID"""
        insiders_map = {}
        for idx, row in insiders_df.iterrows():
            insiders_map[row['cik']] = f"insider_{idx}"  # Temporary ID
        return insiders_map
    
    def add_foreign_keys(self, transactions_df: pd.DataFrame, companies_map: Dict, insiders_map: Dict) -> pd.DataFrame:
        """Add foreign key relationships to transactions"""
        logger.info("Adding foreign key relationships...")
        
        transactions_df['company_id'] = transactions_df['ISSUERCIK'].map(companies_map)
        transactions_df['insider_id'] = transactions_df['RPTOWNERCIK'].map(insiders_map)
        
        # Check success rate
        valid_company_keys = transactions_df['company_id'].notna().sum()
        valid_insider_keys = transactions_df['insider_id'].notna().sum()
        
        logger.info(f"Foreign key success rate:")
        logger.info(f"  - Company relationships: {valid_company_keys}/{len(transactions_df)} ({valid_company_keys/len(transactions_df)*100:.1f}%)")
        logger.info(f"  - Insider relationships: {valid_insider_keys}/{len(transactions_df)} ({valid_insider_keys/len(transactions_df)*100:.1f}%)")
        
        return transactions_df
    
    def save_processed_data(self, output_dir: str = "processed_2025_data"):
        """Save processed data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Saving processed data to {output_dir}")
        
        # Save companies
        companies_file = os.path.join(output_dir, "companies.csv")
        self.processed_data['companies'].to_csv(companies_file, index=False)
        logger.info(f"Saved {len(self.processed_data['companies'])} companies to {companies_file}")
        
        # Save insiders
        insiders_file = os.path.join(output_dir, "insiders.csv")
        self.processed_data['insiders'].to_csv(insiders_file, index=False)
        logger.info(f"Saved {len(self.processed_data['insiders'])} insiders to {insiders_file}")
        
        # Save transactions
        transactions_file = os.path.join(output_dir, "transactions.csv")
        self.processed_data['transactions'].to_csv(transactions_file, index=False)
        logger.info(f"Saved {len(self.processed_data['transactions'])} transactions to {transactions_file}")
        
        # Save summary
        summary = {
            'total_companies': len(self.processed_data['companies']),
            'total_insiders': len(self.processed_data['insiders']),
            'total_transactions': len(self.processed_data['transactions']),
            'transactions_with_company_keys': self.processed_data['transactions']['company_id'].notna().sum(),
            'transactions_with_insider_keys': self.processed_data['transactions']['insider_id'].notna().sum(),
            'processing_date': datetime.now().isoformat()
        }
        
        import json
        summary_file = os.path.join(output_dir, "processing_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Processing summary saved to {summary_file}")
        return summary

def main():
    """Main processing function for 2025 SEC data"""
    data_dir = "/Users/ronniederman/Downloads/2025q2_form345"
    
    if not os.path.exists(data_dir):
        print(f"ERROR: Data directory {data_dir} not found!")
        return
    
    try:
        processor = SEC2025Processor(data_dir)
        processed_data = processor.process_2025_data()
        summary = processor.save_processed_data()
        
        print("\n" + "="*60)
        print("2025 SEC DATA PROCESSING SUMMARY")
        print("="*60)
        print(f"Companies: {summary['total_companies']:,}")
        print(f"Insiders: {summary['total_insiders']:,}")
        print(f"Transactions: {summary['total_transactions']:,}")
        print(f"Transactions with company relationships: {summary['transactions_with_company_keys']:,}")
        print(f"Transactions with insider relationships: {summary['transactions_with_insider_keys']:,}")
        print(f"\nProcessed data saved to: processed_2025_data/")
        
    except Exception as e:
        print(f"ERROR: Processing failed: {str(e)}")
        logger.error(f"Processing failed: {str(e)}")

if __name__ == "__main__":
    main()
