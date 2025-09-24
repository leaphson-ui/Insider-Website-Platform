#!/usr/bin/env python3
"""
SEC Insider Transactions Data Cleaning Pipeline Test
Tests data cleaning and normalization on sample datasets
"""

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECDataCleaner:
    def __init__(self):
        self.transaction_code_mapping = {
            'P': 'Purchase',
            'S': 'Sale', 
            'A': 'Grant/Award',
            'D': 'Sale to Issuer',
            'F': 'Payment with Respect to Shares',
            'G': 'Gift',
            'H': 'Expiration of Short Derivative Position',
            'I': 'Discretionary Transaction',
            'J': 'Other Acquisition',
            'K': 'Equity Swap',
            'L': 'Small Acquisition',
            'M': 'Exercise of Out-of-the-Money Derivative',
            'N': 'Acquisition (No Price)',
            'O': 'Acquisition of Derivative Security',
            'U': 'Acquisition Under 10b5-1 Plan',
            'V': 'Disposal Under 10b5-1 Plan',
            'W': 'Acquisition or Disposal by Will or Laws',
            'X': 'Exercise of In-the-Money or At-the-Money Derivative',
            'Y': 'Acquisition or Disposal by Gift',
            'Z': 'Deposit into or Withdrawal from Voting Trust'
        }
        
    def download_sample_data(self, quarters: List[str]) -> List[str]:
        """Download sample quarterly datasets for testing"""
        base_url = "https://www.sec.gov/files/data/insider-trading-data/"
        downloaded_files = []
        
        for quarter in quarters:
            filename = f"insider-trading-{quarter}.csv"
            url = f"{base_url}{filename}"
            
            logger.info(f"Downloading {filename}...")
            # Note: You'll need to implement actual download logic
            # For now, we'll assume files are manually downloaded
            
        return downloaded_files
    
    def load_csv_data(self, filepath: str) -> pd.DataFrame:
        """Load CSV data with proper encoding and error handling"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                    logger.info(f"Successfully loaded {len(df)} records from {filepath}")
                    return df
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f"Could not decode {filepath} with any standard encoding")
            
        except Exception as e:
            logger.error(f"Error loading {filepath}: {str(e)}")
            raise
    
    def clean_transaction_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize transaction dates"""
        logger.info("Cleaning transaction dates...")
        
        # Convert to datetime, handling multiple formats
        date_columns = ['transactionDate', 'transaction_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                
        return df
    
    def clean_transaction_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize transaction codes"""
        logger.info("Cleaning transaction codes...")
        
        code_columns = ['transactionCode', 'transaction_code']
        for col in code_columns:
            if col in df.columns:
                # Clean and standardize codes
                df[col] = df[col].astype(str).str.strip().str.upper()
                
                # Create readable descriptions
                desc_col = f"{col}_description"
                df[desc_col] = df[col].map(self.transaction_code_mapping)
                
        return df
    
    def clean_numeric_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean numeric fields (shares, prices, values)"""
        logger.info("Cleaning numeric fields...")
        
        numeric_columns = [
            'transactionShares', 'transaction_shares',
            'transactionPricePerShare', 'transaction_price_per_share',
            'sharesOwnedFollowingTransaction', 'shares_owned_following'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                # Remove commas, convert to numeric
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
    
    def calculate_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate missing transaction values"""
        logger.info("Calculating missing transaction values...")
        
        # Calculate transaction value if missing
        if 'transactionValue' not in df.columns:
            df['transactionValue'] = None
            
        # Fill missing values where we have shares and price
        shares_col = 'transactionShares' if 'transactionShares' in df.columns else 'transaction_shares'
        price_col = 'transactionPricePerShare' if 'transactionPricePerShare' in df.columns else 'transaction_price_per_share'
        
        if shares_col in df.columns and price_col in df.columns:
            mask = df['transactionValue'].isna() & df[shares_col].notna() & df[price_col].notna()
            df.loc[mask, 'transactionValue'] = df.loc[mask, shares_col] * df.loc[mask, price_col]
            
        return df
    
    def clean_company_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize company information"""
        logger.info("Cleaning company data...")
        
        # Standardize CIK (should be 10 digits, zero-padded)
        cik_columns = ['issuerCIK', 'issuer_cik']
        for col in cik_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                # Pad with zeros to make 10 digits
                df[col] = df[col].str.zfill(10)
                
        # Clean company names
        name_columns = ['issuerName', 'issuer_name']
        for col in name_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                
        return df
    
    def clean_insider_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize insider information"""
        logger.info("Cleaning insider data...")
        
        # Standardize insider CIK
        cik_columns = ['rptOwnerCIK', 'rpt_owner_cik']
        for col in cik_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.zfill(10)
                
        # Clean insider names
        name_columns = ['rptOwnerName', 'rpt_owner_name']
        for col in name_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate transactions"""
        logger.info("Removing duplicates...")
        
        initial_count = len(df)
        
        # Define columns to check for duplicates
        duplicate_columns = [
            'issuerCIK', 'issuer_cik',
            'rptOwnerCIK', 'rpt_owner_cik', 
            'transactionDate', 'transaction_date',
            'transactionCode', 'transaction_code',
            'transactionShares', 'transaction_shares'
        ]
        
        # Filter to existing columns
        existing_columns = [col for col in duplicate_columns if col in df.columns]
        
        if existing_columns:
            df = df.drop_duplicates(subset=existing_columns, keep='first')
            
        final_count = len(df)
        removed_count = initial_count - final_count
        
        logger.info(f"Removed {removed_count} duplicate records ({initial_count} -> {final_count})")
        
        return df
    
    def add_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add useful derived fields"""
        logger.info("Adding derived fields...")
        
        # Add quarter/year field for efficient querying
        date_col = 'transactionDate' if 'transactionDate' in df.columns else 'transaction_date'
        if date_col in df.columns:
            df['quarter_year'] = df[date_col].dt.to_period('Q').astype(str)
            df['year'] = df[date_col].dt.year
            df['month'] = df[date_col].dt.month
            
        # Add transaction direction (buy/sell)
        code_col = 'transactionCode' if 'transactionCode' in df.columns else 'transaction_code'
        if code_col in df.columns:
            buy_codes = ['P', 'A', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'U', 'W', 'X', 'Y', 'Z']
            df['is_buy'] = df[code_col].isin(buy_codes)
            df['is_sell'] = df[code_col].isin(['S', 'D', 'F', 'H', 'V'])
            
        return df
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict:
        """Validate data quality and return statistics"""
        logger.info("Validating data quality...")
        
        stats = {
            'total_records': len(df),
            'records_with_missing_dates': df['transactionDate'].isna().sum() if 'transactionDate' in df.columns else 0,
            'records_with_missing_codes': df['transactionCode'].isna().sum() if 'transactionCode' in df.columns else 0,
            'records_with_missing_shares': df['transactionShares'].isna().sum() if 'transactionShares' in df.columns else 0,
            'date_range': {
                'earliest': df['transactionDate'].min() if 'transactionDate' in df.columns else None,
                'latest': df['transactionDate'].max() if 'transactionDate' in df.columns else None
            },
            'unique_companies': df['issuerCIK'].nunique() if 'issuerCIK' in df.columns else 0,
            'unique_insiders': df['rptOwnerCIK'].nunique() if 'rptOwnerCIK' in df.columns else 0,
            'transaction_codes': df['transactionCode'].value_counts().to_dict() if 'transactionCode' in df.columns else {}
        }
        
        return stats
    
    def clean_dataset(self, filepath: str) -> pd.DataFrame:
        """Complete cleaning pipeline"""
        logger.info(f"Starting data cleaning pipeline for {filepath}")
        
        # Load data
        df = self.load_csv_data(filepath)
        
        # Apply cleaning steps
        df = self.clean_transaction_dates(df)
        df = self.clean_transaction_codes(df)
        df = self.clean_numeric_fields(df)
        df = self.calculate_missing_values(df)
        df = self.clean_company_data(df)
        df = self.clean_insider_data(df)
        df = self.remove_duplicates(df)
        df = self.add_derived_fields(df)
        
        # Validate
        stats = self.validate_data_quality(df)
        
        logger.info("Data cleaning completed!")
        logger.info(f"Final dataset: {stats['total_records']} records")
        
        return df, stats

def main():
    """Test the data cleaning pipeline"""
    cleaner = SECDataCleaner()
    
    # Test with sample file (you'll need to download this first)
    sample_file = "sample_insider_data.csv"
    
    if os.path.exists(sample_file):
        try:
            cleaned_df, stats = cleaner.clean_dataset(sample_file)
            
            # Save cleaned data
            output_file = "cleaned_sample_data.csv"
            cleaned_df.to_csv(output_file, index=False)
            
            print("\n" + "="*50)
            print("DATA CLEANING RESULTS")
            print("="*50)
            print(f"Total records processed: {stats['total_records']}")
            print(f"Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
            print(f"Unique companies: {stats['unique_companies']}")
            print(f"Unique insiders: {stats['unique_insiders']}")
            print(f"Records with missing dates: {stats['records_with_missing_dates']}")
            print(f"Records with missing transaction codes: {stats['records_with_missing_codes']}")
            print("\nTransaction code distribution:")
            for code, count in stats['transaction_codes'].items():
                print(f"  {code}: {count}")
            
            print(f"\nCleaned data saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Error in cleaning pipeline: {str(e)}")
    else:
        print(f"Sample file {sample_file} not found. Please download a sample dataset first.")

if __name__ == "__main__":
    main()
