import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

print(f"URL: {url}")
print(f"Key: {key[:20]}...")

try:
    supabase = create_client(url, key)
    result = supabase.table('companies').select('*').limit(1).execute()
    print("✅ Connection successful!")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
