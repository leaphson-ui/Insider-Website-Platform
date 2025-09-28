#!/usr/bin/env python3
"""
Process Only Post-2023 Quarters
Only processes quarters from 2023q1 onwards (when SEC format changed)
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from processor_post_2023 import Post2023Processor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_post_2023_quarters() -> List[str]:
    """Get list of post-2023 quarters only"""
    quarters = []
    
    # Generate quarters from 2023q1 to 2025q2 (when SEC format changed)
    for year in range(2023, 2026):
        for quarter in range(1, 5):
            if year == 2025 and quarter > 2:  # Only Q1 and Q2 for 2025
                break
            quarters.append(f"{year}q{quarter}_form345")
    
    return quarters

def process_post_2023_quarters():
    """Process only post-2023 quarters"""
    logger.info("🚀 PROCESSING POST-2023 QUARTERS ONLY")
    logger.info("=" * 60)
    
    # Initialize processor
    data_dir = Path('/Users/ronniederman/insider-alpha-platform/data-processing/sec_insider_data')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Missing Supabase credentials")
        return
    
    processor = Post2023Processor(data_dir, supabase_url, supabase_key)
    
    # Get post-2023 quarters only
    quarters = get_post_2023_quarters()
    logger.info(f"📅 Processing {len(quarters)} post-2023 quarters:")
    for quarter in quarters:
        logger.info(f"  - {quarter}")
    
    # Process each quarter
    completed = []
    failed = []
    start_time = datetime.now()
    
    for i, quarter in enumerate(quarters):
        logger.info(f"\n--- Progress: {i+1}/{len(quarters)} ({((i+1)/len(quarters)*100):.1f}%) ---")
        logger.info(f"🔄 Processing {quarter}...")
        
        try:
            # Check if already processed
            existing = processor.supabase.table('insider_transactions').select('id', count='exact').eq('quarter', quarter).execute()
            if existing.count > 0:
                logger.info(f"✅ {quarter} already processed ({existing.count:,} records), skipping")
                completed.append(quarter)
                continue
            
            # Process the quarter
            result = processor.process_quarter(quarter)
            completed.append(quarter)
            logger.info(f"✅ Successfully processed {quarter}: {result.get('inserted', 0):,} records")
            
        except Exception as e:
            failed.append(quarter)
            logger.error(f"❌ Failed to process {quarter}: {e}")
    
    # Final summary
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 FINAL RESULTS")
    logger.info("=" * 60)
    logger.info(f"✅ Completed: {len(completed)}/{len(quarters)} quarters")
    logger.info(f"❌ Failed: {len(failed)} quarters")
    logger.info(f"📊 Success rate: {(len(completed)/len(quarters)*100):.1f}%")
    logger.info(f"⏱️  Total duration: {total_duration}")
    
    if completed:
        logger.info(f"\n✅ Completed quarters:")
        for quarter in completed:
            logger.info(f"  - {quarter}")
    
    if failed:
        logger.info(f"\n❌ Failed quarters:")
        for quarter in failed:
            logger.info(f"  - {quarter}")

if __name__ == '__main__':
    process_post_2023_quarters()

