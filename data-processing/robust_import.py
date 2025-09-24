#!/usr/bin/env python3
"""
Robust import that handles problematic records gracefully
"""

import os
import sys
import pandas as pd
import numpy as np
from supabase import create_client, Client

# Use hardcoded credentials from frontend
url = 'https://sifpyksougtsklegphxf.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZnB5a3NvdWd0c2tsZWdwaHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2NzI5OTUsImV4cCI6MjA3NDI0ODk5NX0.NDc6nd1w9SFhgYYJkRrAqD_3pO584tUrGcNrDErCq9Y'

supabase: Client = create_client(url, key)

def robust_import():
    print("🔧 Robust import of 2025 data...")
    
    # Load the processed data
    transactions_df = pd.read_csv('processed_2025_data/transactions.csv', low_memory=False)
    print(f"Total transactions in CSV: {len(transactions_df):,}")
    
    # Check current count in database
    result = supabase.table('transactions_2025q2').select('id', count='exact').execute()
    current_count = result.count
    print(f"Current transactions in DB: {current_count:,}")
    
    if current_count >= len(transactions_df):
        print("✅ All transactions already imported!")
        return
    
    # Import in small batches with error handling
    batch_size = 100
    total_imported = 0
    total_errors = 0
    
    def safe_float(value, default=0):
        if pd.isna(value) or np.isinf(value) or np.isnan(value):
            return default
        try:
            return float(value)
        except:
            return default
    
    for i in range(0, len(transactions_df), batch_size):
        batch_df = transactions_df.iloc[i:i + batch_size]
        
        try:
            # Prepare batch data
            batch_data = []
            for _, row in batch_df.iterrows():
                try:
                    transaction = {
                        'accession_number': str(row['accession_number']),
                        'company_cik': str(row['ISSUERCIK']).zfill(10),
                        'insider_cik': str(row['RPTOWNERCIK']).zfill(10),
                        'transaction_date': row['transaction_date'],
                        'transaction_code': str(row['transaction_code']),
                        'transaction_shares': safe_float(row['transaction_shares']),
                        'transaction_price_per_share': safe_float(row['transaction_price_per_share']),
                        'calculated_transaction_value': safe_float(row['calculated_transaction_value']),
                        'shares_owned_following_transaction': safe_float(row['shares_owned_following_transaction']),
                        'security_title': str(row['security_title']),
                        'file_type': '4',
                        'quarter': '2025q2_form345',
                        'data_source': '2025q2_form345',
                        'year': 2025
                    }
                    batch_data.append(transaction)
                except Exception as e:
                    print(f"  ⚠️  Skipping problematic record: {e}")
                    total_errors += 1
                    continue
            
            if batch_data:
                # Try to insert the batch
                result = supabase.table('transactions_2025q2').insert(batch_data).execute()
                total_imported += len(result.data)
            
            if i % (batch_size * 10) == 0:
                print(f"  Imported {total_imported:,}/{len(transactions_df):,} transactions... (Errors: {total_errors})")
                
        except Exception as e:
            print(f"  ❌ Batch error: {e}")
            total_errors += len(batch_df)
            continue
    
    print(f"\n✅ Import complete!")
    print(f"  Total imported: {total_imported:,}")
    print(f"  Total errors: {total_errors:,}")
    
    # Verify final count
    result = supabase.table('transactions_2025q2').select('id', count='exact').execute()
    print(f"Final transaction count: {result.count:,}")

if __name__ == "__main__":
    robust_import()
