#!/usr/bin/env python3
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

print('=== TESTING OR CONDITION ===')

# Test the OR condition that our frontend uses
print('\n1. Testing OR condition with MSFT...')
try:
    query = supabase.table('transactions').select('*, companies(name, ticker), insiders(name)')
    # Use the exact OR condition from our frontend
    or_condition = 'companies.name.ilike.%MSFT%,companies.ticker.ilike.%MSFT%,insiders.name.ilike.%MSFT%'
    result = query.or(or_condition).limit(5).execute()
    print(f'OR condition results: {len(result.data)}')
    if result.data:
        for i, item in enumerate(result.data):
            print(f'Result {i+1}: {item.get("companies", {}).get("name", "N/A")} - {item.get("companies", {}).get("ticker", "N/A")}')
except Exception as e:
    print(f'OR condition error: {e}')

# Test individual conditions
print('\n2. Testing individual conditions...')
try:
    # Test just the ticker condition
    query = supabase.table('transactions').select('*, companies(name, ticker), insiders(name)')
    result = query.ilike('companies.ticker', '%MSFT%').limit(3).execute()
    print(f'Ticker ilike results: {len(result.data)}')
    if result.data:
        print(f'First ticker result: {result.data[0].get("companies", {}).get("ticker", "N/A")}')
except Exception as e:
    print(f'Ticker ilike error: {e}')
