#!/usr/bin/env python3
"""
Set up full-text search for the transactions table
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

print('=== SETTING UP FULL-TEXT SEARCH ===')

# SQL commands to set up full-text search
sql_commands = [
    # Add search_vector column to transactions table
    """
    ALTER TABLE transactions 
    ADD COLUMN search_vector tsvector;
    """,
    
    # Create function to update search vector
    """
    CREATE OR REPLACE FUNCTION update_transactions_search_vector()
    RETURNS TRIGGER AS $$
    BEGIN
      NEW.search_vector := to_tsvector('english', 
        coalesce(NEW.accession_number, '') || ' ' ||
        coalesce(NEW.security_title, '') || ' ' ||
        coalesce(NEW.transaction_code, '')
      );
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """,
    
    # Create trigger to automatically update search vector
    """
    CREATE TRIGGER trigger_update_transactions_search_vector
    BEFORE INSERT OR UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_transactions_search_vector();
    """,
    
    # Create GIN index for performance
    """
    CREATE INDEX idx_transactions_search_vector 
    ON transactions USING gin(search_vector);
    """,
    
    # Update existing records with search vector
    """
    UPDATE transactions 
    SET search_vector = to_tsvector('english', 
      coalesce(accession_number, '') || ' ' ||
      coalesce(security_title, '') || ' ' ||
      coalesce(transaction_code, '')
    );
    """
]

print('\n1. Setting up full-text search infrastructure...')
for i, sql in enumerate(sql_commands, 1):
    try:
        print(f'\\nExecuting SQL command {i}...')
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print(f'✅ SQL command {i} executed successfully')
    except Exception as e:
        print(f'❌ SQL command {i} failed: {e}')

print('\\n2. Testing full-text search...')
try:
    # Test the full-text search
    result = supabase.table('transactions').select('*').filter('search_vector', 'fts', 'msft').limit(3).execute()
    print(f'Full-text search test results: {len(result.data)}')
    if result.data:
        print('✅ Full-text search is working!')
        for i, item in enumerate(result.data):
            print(f'Result {i+1}: {item.get("accession_number", "N/A")} - {item.get("security_title", "N/A")}')
    else:
        print('❌ No results found')
except Exception as e:
    print(f'❌ Full-text search test failed: {e}')
