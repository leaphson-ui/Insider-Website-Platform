#!/usr/bin/env python3
"""
Import cleaned SEC data to Supabase
"""

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from typing import Dict, List

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseImporter:
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
            
        self.supabase: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        logger.info("Creating database tables...")
        
        # This would typically be done via Supabase SQL editor
        # For now, we'll assume tables exist
        logger.info("Tables should be created via Supabase dashboard SQL editor")
    
    def prepare_companies_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare companies data for insertion"""
        logger.info("Preparing companies data...")
        
        # Get unique companies
        company_cols = ['issuerCIK', 'issuerName', 'issuerTradingSymbol']
        companies_df = df[company_cols].drop_duplicates()
        
        # Rename columns to match schema
        companies_df = companies_df.rename(columns={
            'issuerCIK': 'cik',
            'issuerName': 'name', 
            'issuerTradingSymbol': 'ticker'
        })
        
        # Clean data
        companies_df['cik'] = companies_df['cik'].astype(str).str.strip().str.zfill(10)
        companies_df['name'] = companies_df['name'].astype(str).str.strip()
        companies_df['ticker'] = companies_df['ticker'].astype(str).str.strip()
        
        return companies_df
    
    def prepare_insiders_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare insiders data for insertion"""
        logger.info("Preparing insiders data...")
        
        # Get unique insiders
        insider_cols = [
            'rptOwnerCIK', 'rptOwnerName', 'isDirector', 
            'isOfficer', 'isTenPercentOwner', 'officerTitle'
        ]
        insiders_df = df[insider_cols].drop_duplicates()
        
        # Rename columns to match schema
        insiders_df = insiders_df.rename(columns={
            'rptOwnerCIK': 'cik',
            'rptOwnerName': 'name',
            'isDirector': 'is_director',
            'isOfficer': 'is_officer', 
            'isTenPercentOwner': 'is_ten_percent_owner',
            'officerTitle': 'officer_title'
        })
        
        # Clean data
        insiders_df['cik'] = insiders_df['cik'].astype(str).str.strip().str.zfill(10)
        insiders_df['name'] = insiders_df['name'].astype(str).str.strip()
        
        # Convert boolean columns
        bool_cols = ['is_director', 'is_officer', 'is_ten_percent_owner']
        for col in bool_cols:
            insiders_df[col] = insiders_df[col].fillna(False).astype(bool)
        
        return insiders_df
    
    def prepare_transactions_data(self, df: pd.DataFrame, companies_map: Dict, insiders_map: Dict) -> pd.DataFrame:
        """Prepare transactions data for insertion"""
        logger.info("Preparing transactions data...")
        
        # Create mapping for company and insider IDs
        df['company_id'] = df['issuerCIK'].map(companies_map)
        df['insider_id'] = df['rptOwnerCIK'].map(insiders_map)
        
        # Select and rename columns
        transaction_cols = [
            'company_id', 'insider_id', 'transactionDate', 'transactionCode',
            'transactionShares', 'transactionPricePerShare', 'transactionValue',
            'acquiredDisposedCode', 'sharesOwnedFollowingTransaction', 
            'securityTitle', 'quarter_year', 'year', 'month', 'is_buy', 'is_sell'
        ]
        
        transactions_df = df[transaction_cols].copy()
        
        # Rename columns to match schema
        column_mapping = {
            'transactionDate': 'transaction_date',
            'transactionCode': 'transaction_code',
            'transactionShares': 'transaction_shares',
            'transactionPricePerShare': 'transaction_price_per_share',
            'transactionValue': 'transaction_value',
            'acquiredDisposedCode': 'acquired_disposed_code',
            'sharesOwnedFollowingTransaction': 'shares_owned_following',
            'securityTitle': 'security_title'
        }
        
        transactions_df = transactions_df.rename(columns=column_mapping)
        
        return transactions_df
    
    def insert_companies(self, companies_df: pd.DataFrame) -> Dict:
        """Insert companies and return ID mapping"""
        logger.info(f"Inserting {len(companies_df)} companies...")
        
        companies_list = companies_df.to_dict('records')
        
        try:
            result = self.supabase.table('companies').upsert(
                companies_list, 
                on_conflict='cik'
            ).execute()
            
            # Create mapping from CIK to ID
            companies_data = result.data
            cik_to_id = {row['cik']: row['id'] for row in companies_data}
            
            logger.info(f"✓ Inserted {len(companies_data)} companies")
            return cik_to_id
            
        except Exception as e:
            logger.error(f"Error inserting companies: {str(e)}")
            raise
    
    def insert_insiders(self, insiders_df: pd.DataFrame) -> Dict:
        """Insert insiders and return ID mapping"""
        logger.info(f"Inserting {len(insiders_df)} insiders...")
        
        insiders_list = insiders_df.to_dict('records')
        
        try:
            result = self.supabase.table('insiders').upsert(
                insiders_list,
                on_conflict='cik'
            ).execute()
            
            # Create mapping from CIK to ID
            insiders_data = result.data
            cik_to_id = {row['cik']: row['id'] for row in insiders_data}
            
            logger.info(f"✓ Inserted {len(insiders_data)} insiders")
            return cik_to_id
            
        except Exception as e:
            logger.error(f"Error inserting insiders: {str(e)}")
            raise
    
    def insert_transactions(self, transactions_df: pd.DataFrame, batch_size: int = 1000):
        """Insert transactions in batches"""
        logger.info(f"Inserting {len(transactions_df)} transactions...")
        
        transactions_list = transactions_df.to_dict('records')
        
        # Remove any None values that might cause issues
        for record in transactions_list:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        
        try:
            total_inserted = 0
            
            # Insert in batches
            for i in range(0, len(transactions_list), batch_size):
                batch = transactions_list[i:i + batch_size]
                
                result = self.supabase.table('transactions').insert(batch).execute()
                total_inserted += len(result.data)
                
                if i % (batch_size * 10) == 0:  # Log every 10 batches
                    logger.info(f"Inserted {total_inserted}/{len(transactions_list)} transactions...")
            
            logger.info(f"✓ Inserted {total_inserted} transactions")
            
        except Exception as e:
            logger.error(f"Error inserting transactions: {str(e)}")
            raise
    
    def import_cleaned_data(self, cleaned_csv_path: str):
        """Complete import process"""
        logger.info(f"Starting import of {cleaned_csv_path}")
        
        # Load cleaned data
        df = pd.read_csv(cleaned_csv_path)
        logger.info(f"Loaded {len(df)} records from cleaned data")
        
        # Prepare data
        companies_df = self.prepare_companies_data(df)
        insiders_df = self.prepare_insiders_data(df)
        
        # Insert companies and insiders first
        companies_map = self.insert_companies(companies_df)
        insiders_map = self.insert_insiders(insiders_df)
        
        # Prepare and insert transactions
        transactions_df = self.prepare_transactions_data(df, companies_map, insiders_map)
        self.insert_transactions(transactions_df)
        
        logger.info("✓ Import completed successfully!")

def main():
    """Main import function"""
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("ERROR: .env file not found!")
        print("Create a .env file with:")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_ANON_KEY=your_supabase_anon_key")
        return
    
    # Check if cleaned data exists
    cleaned_file = "cleaned_sample_data.csv"
    if not os.path.exists(cleaned_file):
        print(f"ERROR: {cleaned_file} not found!")
        print("Run test_data_cleaning.py first to generate cleaned data.")
        return
    
    try:
        importer = SupabaseImporter()
        importer.import_cleaned_data(cleaned_file)
        print("\n✓ Data import completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Import failed: {str(e)}")
        print("Check your Supabase credentials and database schema.")

if __name__ == "__main__":
    main()
