#!/usr/bin/env python3
"""
Simple progress monitor for SEC data processing
Run this in a separate terminal to watch progress
"""

import os
import time
from supabase import create_client
from dotenv import load_dotenv

def monitor_progress():
    """Monitor processing progress"""
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    supabase = create_client(supabase_url, supabase_key)
    
    print("📊 SEC DATA PROCESSING MONITOR")
    print("=" * 50)
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        while True:
            # Get current data
            result = supabase.table('insider_transactions').select('*').execute()
            
            # Count by quarter
            quarters = {}
            for record in result.data:
                quarter = record['quarter']
                quarters[quarter] = quarters.get(quarter, 0) + 1
            
            # Display progress
            print(f"\r⏰ {time.strftime('%H:%M:%S')} | Total: {len(result.data)} records", end="")
            
            if quarters:
                print(f" | Quarters: {', '.join([f'{q}: {c}' for q, c in quarters.items()])}")
            else:
                print(" | No data yet...")
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")

if __name__ == "__main__":
    monitor_progress()
