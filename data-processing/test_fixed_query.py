#!/usr/bin/env python3
"""
Test the fixed OR condition construction
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

print('=== TESTING FIXED OR CONDITION ===')

# Test the fixed OR condition construction
print('\n1. Testing fixed OR condition with MSFT...')
try:
    searchTerm = 'msft'
    searchPattern = f'%{searchTerm}%'
    or_condition = f'companies.name.ilike.{searchPattern},companies.ticker.ilike.{searchPattern},insiders.name.ilike.{searchPattern}'
    
    print(f'Search pattern: {searchPattern}')
    print(f'OR condition: {or_condition}')
    
    query = supabase.table('transactions').select('*, companies!inner(id, name, ticker), insiders!inner(id, name, is_director, is_officer)')
    query = query.order('transaction_date', ascending=False)
    result = query.or(or_condition).limit(5).execute()
    
    print(f'Fixed OR results: {len(result.data)}')
    if result.data:
        for i, item in enumerate(result.data):
            company = item.get('companies', {})
            print(f'Result {i+1}: {company.get("name", "N/A")} - {company.get("ticker", "N/A")}')
    else:
        print('No results found')
        
except Exception as e:
    print(f'Fixed OR error: {e}')

# Test with a different search term
print('\n2. Testing with Apple search...')
try:
    searchTerm = 'apple'
    searchPattern = f'%{searchTerm}%'
    or_condition = f'companies.name.ilike.{searchPattern},companies.ticker.ilike.{searchPattern},insiders.name.ilike.{searchPattern}'
    
    query = supabase.table('transactions').select('*, companies!inner(id, name, ticker), insiders!inner(id, name, is_director, is_officer)')
    query = query.order('transaction_date', ascending=False)
    result = query.or(or_condition).limit(3).execute()
    
    print(f'Apple search results: {len(result.data)}')
    if result.data:
        for i, item in enumerate(result.data):
            company = item.get('companies', {})
            print(f'Result {i+1}: {company.get("name", "N/A")} - {company.get("ticker", "N/A")}')
    else:
        print('No Apple results found')
        
except Exception as e:
    print(f'Apple search error: {e}')
