#!/usr/bin/env python3
"""
Cute Progress Monitor - Simple progress display for retry processing
Shows progress without interrupting the main process
"""

import time
import json
import os
from datetime import datetime
from pathlib import Path

def get_emoji_progress(progress_pct):
    """Get cute emoji based on progress percentage"""
    if progress_pct < 10:
        return "🌱"
    elif progress_pct < 25:
        return "🌿"
    elif progress_pct < 50:
        return "🌳"
    elif progress_pct < 75:
        return "🌲"
    elif progress_pct < 90:
        return "🎄"
    else:
        return "🎉"

def get_spinner():
    """Get a cute spinner character"""
    spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    return spinners[int(time.time() * 10) % len(spinners)]

def get_loading_bar(progress_pct, width=20):
    """Create a cute loading bar"""
    filled = int(width * progress_pct / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress_pct:.1f}%"

def monitor_progress():
    """Monitor and display cute progress"""
    print("🎯 Cute Progress Monitor Started!")
    print("=" * 50)
    
    # Load initial failed quarters
    progress_file = Path("consolidated_processing_progress.json")
    if not progress_file.exists():
        print("❌ No progress file found!")
        return
    
    with open(progress_file, 'r') as f:
        initial_progress = json.load(f)
    
    initial_failed = set(initial_progress['failed'])
    total_failed = len(initial_failed)
    
    print(f"🎯 Monitoring retry of {total_failed} failed quarters...")
    print(f"📊 Initial failed quarters: {sorted(initial_failed)}")
    print()
    
    start_time = datetime.now()
    last_successful = 0
    
    try:
        while True:
            # Check if progress file exists and read it
            if progress_file.exists():
                with open(progress_file, 'r') as f:
                    current_progress = json.load(f)
                
                current_failed = set(current_progress['failed'])
                current_completed = set(current_progress['completed'])
                
                # Calculate progress
                newly_completed = initial_failed - current_failed
                progress_pct = (len(newly_completed) / total_failed) * 100
                
                # Get cute elements
                emoji = get_emoji_progress(progress_pct)
                spinner = get_spinner()
                bar = get_loading_bar(progress_pct)
                
                # Calculate time
                elapsed = datetime.now() - start_time
                elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
                
                # Clear screen and show progress
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🎯 Cute Progress Monitor")
                print("=" * 50)
                print(f"{emoji} Retry Progress: {bar}")
                print(f"{spinner} Elapsed: {elapsed_str}")
                print(f"📊 Completed: {len(newly_completed)}/{total_failed} quarters")
                print()
                
                if newly_completed:
                    print("✅ Recently completed:")
                    for quarter in sorted(newly_completed):
                        print(f"   🎉 {quarter}")
                    print()
                
                if current_failed:
                    print("⏳ Still processing:")
                    for quarter in sorted(current_failed):
                        print(f"   {spinner} {quarter}")
                
                # Check if we're done
                if len(current_failed) == 0:
                    print()
                    print("🎉 ALL QUARTERS COMPLETED! 🎉")
                    print("=" * 50)
                    print(f"🎯 Total time: {elapsed_str}")
                    print(f"📊 Success rate: 100%")
                    print("🎉 Your SEC database is now complete!")
                    break
                
                last_successful = len(newly_completed)
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Progress monitor stopped by user")
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")

if __name__ == "__main__":
    monitor_progress()

