#!/usr/bin/env python3
"""
Fix foreign key relationships in the transactions table
"""

import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

supabase = create_client(url, key)

def fix_foreign_keys():
    """Fix foreign key relationships by updating transactions with proper company_id and insider_id"""
    
    print("=== FIXING FOREIGN KEY RELATIONSHIPS ===")
    
    # Get all companies with their CIK to ID mapping
    result = supabase.table('companies').select('id, cik, name').execute()
    companies_map = {row['cik']: row['id'] for row in result.data}
    print(f"Companies mapping: {len(companies_map)} companies")
    
    # Get all insiders with their CIK to ID mapping  
    result = supabase.table('insiders').select('id, cik, name').execute()
    insiders_map = {row['cik']: row['id'] for row in result.data}
    print(f"Insiders mapping: {len(insiders_map)} insiders")
    
    # Read the fixed data to get the CIK mappings
    quarters = ['2025q2_form345', '2006q1_form345']
    
    for quarter in quarters:
        print(f"\nProcessing {quarter}...")
        
        # Read the fixed transactions data
        transactions_file = f'fixed_processed_data/{quarter}/transactions.csv'
        if not os.path.exists(transactions_file):
            print(f"File not found: {transactions_file}")
            continue
            
        df = pd.read_csv(transactions_file)
        print(f"Loaded {len(df)} transactions from {quarter}")
        
        # Update transactions in batches
        batch_size = 1000
        total_updated = 0
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            # Prepare updates
            updates = []
            for _, row in batch.iterrows():
                # Get the company and insider IDs from the mappings
                company_cik = str(row.get('issuer_cik', ''))
                insider_cik = str(row.get('rpt_owner_cik', ''))
                
                company_id = companies_map.get(company_cik)
                insider_id = insiders_map.get(insider_cik)
                
                if company_id and insider_id:
                    updates.append({
                        'accession_number': row['accession_number'],
                        'company_id': company_id,
                        'insider_id': insider_id
                    })
            
            # Update the transactions
            if updates:
                for update in updates:
                    try:
                        result = supabase.table('transactions').update({
                            'company_id': update['company_id'],
                            'insider_id': update['insider_id']
                        }).eq('accession_number', update['accession_number']).execute()
                        
                        if result.data:
                            total_updated += 1
                            
                    except Exception as e:
                        print(f"Error updating transaction {update['accession_number']}: {e}")
            
            if total_updated % 10000 == 0:
                print(f"Updated {total_updated} transactions...")
        
        print(f"✓ Updated {total_updated} transactions for {quarter}")
    
    print("\n🎉 Foreign key relationships fixed!")

if __name__ == "__main__":
    fix_foreign_keys()
