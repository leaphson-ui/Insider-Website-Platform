#!/usr/bin/env python3
"""
Test the search functionality to debug why searches aren't working
"""

import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

print('=== TESTING SEARCH QUERY ===')

# Test the exact query our search uses
print('\n1. Testing MSFT search query...')
try:
    query = supabase.table('transactions').select('*, companies!inner(id, name, ticker), insiders!inner(id, name, is_director, is_officer)')
    or_condition = "companies.name.ilike.%msft%,companies.ticker.ilike.%msft%,insiders.name.ilike.%msft%"
    query = query.or(or_condition)
    result = query.limit(5).execute()
    
    print(f'MSFT search results: {len(result.data)}')
    if result.data:
        print(f'First result: {result.data[0]}')
    else:
        print('No results found')
        
except Exception as e:
    print(f'Error with search query: {e}')

# Test a simpler query to see if joins work
print('\n2. Testing simple join...')
try:
    simple_result = supabase.table('transactions').select('*, companies(name, ticker), insiders(name)').limit(3).execute()
    
    print(f'Simple join results: {len(simple_result.data)}')
    if simple_result.data:
        print(f'First result: {simple_result.data[0]}')
        
except Exception as e:
    print(f'Error with simple join: {e}')

# Test if we can find MSFT transactions at all
print('\n3. Testing MSFT transactions directly...')
try:
    msft_transactions = supabase.table('transactions').select('*, companies(name, ticker), insiders(name)').eq('companies.ticker', 'MSFT').limit(3).execute()
    
    print(f'MSFT transactions: {len(msft_transactions.data)}')
    if msft_transactions.data:
        print(f'First MSFT transaction: {msft_transactions.data[0]}')
        
except Exception as e:
    print(f'Error with MSFT transactions: {e}')

# Test the foreign key relationships
print('\n4. Testing foreign key relationships...')
try:
    # Get MSFT company ID
    msft_company = supabase.table('companies').select('id').eq('ticker', 'MSFT').execute()
    if msft_company.data:
        msft_id = msft_company.data[0]['id']
        print(f'MSFT company ID: {msft_id}')
        
        # Find transactions with this company_id
        msft_txns = supabase.table('transactions').select('*').eq('company_id', msft_id).limit(3).execute()
        print(f'Transactions with MSFT company_id: {len(msft_txns.data)}')
        if msft_txns.data:
            print(f'First MSFT transaction: {msft_txns.data[0]}')
        
except Exception as e:
    print(f'Error with foreign key test: {e}')