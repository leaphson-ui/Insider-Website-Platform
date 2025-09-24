#!/usr/bin/env python3
"""
Debug the exact frontend query construction
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

print('=== DEBUGGING FRONTEND QUERY CONSTRUCTION ===')

# Test the exact query construction from our frontend
print('\n1. Testing the exact frontend query with MSFT...')
try:
    # This is exactly what our frontend does
    searchTerm = 'msft'
    query = supabase.table('transactions').select('*, companies!inner(id, name, ticker), insiders!inner(id, name, is_director, is_officer)')
    query = query.order('transaction_date', ascending=False)
    
    # This is the exact OR condition from our frontend
    or_condition = f'companies.name.ilike.%{searchTerm}%,companies.ticker.ilike.%{searchTerm}%,insiders.name.ilike.%{searchTerm}%'
    print(f'OR condition: {or_condition}')
    
    result = query.or(or_condition).limit(5).execute()
    print(f'Frontend query results: {len(result.data)}')
    if result.data:
        for i, item in enumerate(result.data):
            company = item.get('companies', {})
            print(f'Result {i+1}: {company.get("name", "N/A")} - {company.get("ticker", "N/A")}')
except Exception as e:
    print(f'Frontend query error: {e}')

# Test if the issue is with the template literal construction
print('\n2. Testing manual OR condition...')
try:
    # Test with manually constructed OR condition
    query = supabase.table('transactions').select('*, companies!inner(id, name, ticker), insiders!inner(id, name, is_director, is_officer)')
    result = query.or('companies.name.ilike.%msft%,companies.ticker.ilike.%msft%,insiders.name.ilike.%msft%').limit(5).execute()
    print(f'Manual OR results: {len(result.data)}')
    if result.data:
        for i, item in enumerate(result.data):
            company = item.get('companies', {})
            print(f'Result {i+1}: {company.get("name", "N/A")} - {company.get("ticker", "N/A")}')
except Exception as e:
    print(f'Manual OR error: {e}')

# Test 3: Let's try a different approach - test individual conditions
print('\n3. Testing individual conditions...')
try:
    # Test just the ticker condition
    query = supabase.table('transactions').select('*, companies!inner(id, name, ticker), insiders!inner(id, name, is_director, is_officer)')
    result = query.ilike('companies.ticker', '%msft%').limit(3).execute()
    print(f'Ticker ilike results: {len(result.data)}')
    if result.data:
        for i, item in enumerate(result.data):
            company = item.get('companies', {})
            print(f'Result {i+1}: {company.get("name", "N/A")} - {company.get("ticker", "N/A")}')
except Exception as e:
    print(f'Ticker ilike error: {e}')

# Test 4: Test without inner joins
print('\n4. Testing without inner joins...')
try:
    query = supabase.table('transactions').select('*, companies(name, ticker), insiders(name)')
    result = query.ilike('companies.ticker', '%msft%').limit(3).execute()
    print(f'No inner join results: {len(result.data)}')
    if result.data:
        for i, item in enumerate(result.data):
            company = item.get('companies', {})
            print(f'Result {i+1}: {company.get("name", "N/A")} - {company.get("ticker", "N/A")}')
except Exception as e:
    print(f'No inner join error: {e}')
