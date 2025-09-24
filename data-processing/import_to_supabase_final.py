#!/usr/bin/env python3
"""
Import cleaned SEC data to Supabase - Final Working Version
"""

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from typing import Dict, List
import json

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseDataImporter:
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
            
        self.supabase: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")
    
    def import_companies(self, companies_file: str) -> Dict[str, str]:
        """Import companies and return CIK to ID mapping"""
        logger.info(f"Importing companies from {companies_file}")
        
        df = pd.read_csv(companies_file)
        
        # Prepare companies data
        companies_data = []
        for _, row in df.iterrows():
            companies_data.append({
                'cik': str(row['issuer_cik']),
                'name': str(row['issuer_name']),
                'ticker': str(row['issuer_trading_symbol']) if pd.notna(row['issuer_trading_symbol']) and str(row['issuer_trading_symbol']).strip() else None
            })
        
        # Insert companies (upsert to handle duplicates)
        try:
            result = self.supabase.table('companies').upsert(
                companies_data, 
                on_conflict='cik'
            ).execute()
            
            # Create mapping from CIK to ID
            companies_map = {row['cik']: row['id'] for row in result.data}
            logger.info(f"✓ Imported {len(companies_map)} companies")
            return companies_map
            
        except Exception as e:
            logger.error(f"Error importing companies: {str(e)}")
            raise
    
    def import_insiders(self, insiders_file: str) -> Dict[str, str]:
        """Import insiders and return CIK to ID mapping"""
        logger.info(f"Importing insiders from {insiders_file}")
        
        df = pd.read_csv(insiders_file)
        
        # Prepare insiders data
        insiders_data = []
        for _, row in df.iterrows():
            insiders_data.append({
                'cik': str(row['rpt_owner_cik']),
                'name': str(row['rpt_owner_name']),
                'is_director': bool(row['is_director']),
                'is_officer': bool(row['is_officer']),
                'is_ten_percent_owner': bool(row['is_ten_percent_owner'])
            })
        
        # Insert insiders (upsert to handle duplicates)
        try:
            result = self.supabase.table('insiders').upsert(
                insiders_data,
                on_conflict='cik'
            ).execute()
            
            # Create mapping from CIK to ID
            insiders_map = {row['cik']: row['id'] for row in result.data}
            logger.info(f"✓ Imported {len(insiders_map)} insiders")
            return insiders_map
            
        except Exception as e:
            logger.error(f"Error importing insiders: {str(e)}")
            raise
    
    def import_transactions(self, transactions_file: str, companies_map: Dict[str, str], insiders_map: Dict[str, str]):
        """Import transactions - simplified version"""
        logger.info(f"Importing transactions from {transactions_file}")
        
        # Read transactions in chunks to handle large files
        chunk_size = 1000
        total_imported = 0
        
        try:
            for chunk in pd.read_csv(transactions_file, chunksize=chunk_size):
                # Prepare transactions data
                transactions_data = []
                
                for _, row in chunk.iterrows():
                    # Get company and insider IDs from the mapping
                    company_cik = str(row.get('issuer_cik', ''))
                    insider_cik = str(row.get('rpt_owner_cik', ''))
                    
                    company_id = companies_map.get(company_cik) if company_cik in companies_map else None
                    insider_id = insiders_map.get(insider_cik) if insider_cik in insiders_map else None
                    
                    transaction_data = {
                        'company_id': company_id,
                        'insider_id': insider_id,
                        'accession_number': str(row['accession_number']),
                        'transaction_date': row['transaction_date'] if pd.notna(row['transaction_date']) else None,
                        'deemed_execution_date': row['DEEMED_EXECUTION_DATE'] if pd.notna(row['DEEMED_EXECUTION_DATE']) else None,
                        'transaction_code': str(row['transaction_code']),
                        'transaction_shares': float(row['transaction_shares']) if pd.notna(row['transaction_shares']) else None,
                        'transaction_price_per_share': float(row['transaction_price_per_share']) if pd.notna(row['transaction_price_per_share']) else None,
                        'calculated_transaction_value': float(row['calculated_transaction_value']) if pd.notna(row['calculated_transaction_value']) else None,
                        'shares_owned_following_transaction': float(row['shares_owned_following_transaction']) if pd.notna(row['shares_owned_following_transaction']) else None,
                        'value_owned_following_transaction': float(row['VALU_OWND_FOLWNG_TRANS']) if pd.notna(row['VALU_OWND_FOLWNG_TRANS']) else None,
                        'security_title': str(row['security_title']) if pd.notna(row['security_title']) else None,
                        'transaction_form_type': str(row['TRANS_FORM_TYPE']) if pd.notna(row['TRANS_FORM_TYPE']) else None,
                        'file_type': str(row['file_type']),
                        'quarter': str(row['quarter'])
                    }
                    
                    transactions_data.append(transaction_data)
                
                # Insert chunk
                if transactions_data:
                    result = self.supabase.table('transactions').insert(transactions_data).execute()
                    total_imported += len(result.data)
                    
                    if total_imported % 10000 == 0:
                        logger.info(f"Imported {total_imported} transactions...")
            
            logger.info(f"✓ Imported {total_imported} transactions")
            
        except Exception as e:
            logger.error(f"Error importing transactions: {str(e)}")
            raise
    
    def import_quarter_data(self, quarter_dir: str):
        """Import all data for a quarter"""
        logger.info(f"Importing data for {quarter_dir}")
        
        # File paths
        companies_file = os.path.join(quarter_dir, "companies.csv")
        insiders_file = os.path.join(quarter_dir, "insiders.csv")
        transactions_file = os.path.join(quarter_dir, "transactions.csv")
        
        # Import companies and insiders first
        companies_map = self.import_companies(companies_file)
        insiders_map = self.import_insiders(insiders_file)
        
        # Import transactions
        self.import_transactions(transactions_file, companies_map, insiders_map)
        
        logger.info(f"✓ Completed import for {quarter_dir}")

def main():
    """Main import function"""
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("ERROR: .env file not found!")
        print("Create a .env file with your Supabase credentials:")
        print("SUPABASE_URL=https://your-project-id.supabase.co")
        print("SUPABASE_ANON_KEY=your-anon-key")
        return
    
    # Initialize importer
    try:
        importer = SupabaseDataImporter()
        
        # Test connection first
        print("Testing Supabase connection...")
        result = importer.supabase.table('companies').select('*').limit(1).execute()
        print("✓ Connection successful!")
        
        # Import data from both quarters using fixed data
        quarters = ['2025q2_form345', '2006q1_form345']
        
        for quarter in quarters:
            quarter_dir = os.path.join('fixed_processed_data', quarter)
            if os.path.exists(quarter_dir):
                importer.import_quarter_data(quarter_dir)
            else:
                logger.warning(f"Quarter directory {quarter_dir} not found")
        
        print("\n🎉 Data import completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        print("Check your Supabase credentials and database schema.")

if __name__ == "__main__":
    main()
