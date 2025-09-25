#!/usr/bin/env python3
"""
Monitor Batch Processing Progress
Shows real-time progress of the SEC data batch processing
"""

import json
import time
from pathlib import Path
from datetime import datetime

def monitor_progress():
    """Monitor the batch processing progress"""
    progress_file = Path("supabase_processing_progress.json")
    log_file = Path("supabase_batch_processing.log")
    
    print("📊 SEC Data Batch Processing Monitor")
    print("=" * 60)
    
    while True:
        try:
            # Check if progress file exists
            if progress_file.exists():
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                
                completed = len(progress.get('completed', []))
                failed = len(progress.get('failed', []))
                supabase_loaded = len(progress.get('supabase_loaded', []))
                total_quarters = 78  # Total quarters from 2006-2025
                
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
                print(f"📈 Progress: {completed}/{total_quarters} quarters processed ({completed/total_quarters*100:.1f}%)")
                print(f"✅ Successful: {completed}")
                print(f"❌ Failed: {failed}")
                print(f"📤 Supabase loaded: {supabase_loaded}")
                
                if completed > 0:
                    remaining = total_quarters - completed
                    print(f"⏳ Remaining: {remaining} quarters")
                
                # Show recent completions
                if progress.get('completed'):
                    recent = progress['completed'][-3:]
                    print(f"🔄 Recent completions: {', '.join(recent)}")
                
                # Show failures if any
                if progress.get('failed'):
                    print(f"❌ Failed quarters: {', '.join(progress['failed'])}")
                
                # Check if processing is complete
                if completed >= total_quarters:
                    print("\n🎉 BATCH PROCESSING COMPLETE!")
                    print("=" * 60)
                    break
                    
            else:
                print(f"⏳ Waiting for progress file... ({datetime.now().strftime('%H:%M:%S')})")
            
            # Check log file for recent activity
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if last_line:
                            print(f"📝 Latest log: {last_line}")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_progress()

