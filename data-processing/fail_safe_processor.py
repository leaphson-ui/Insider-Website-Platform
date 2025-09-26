#!/usr/bin/env python3
"""
Fail-Safe SEC Data Processor
Main router that detects format and routes to correct processor
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
# Note: pre-2023 processor was deleted, so older quarters will need to be handled separately

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FailSafeProcessor:
    def __init__(self, data_dir: str, supabase_url: str, supabase_key: str):
        """Initialize fail-safe processor"""
        self.data_dir = Path(data_dir)
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.progress_file = self.data_dir / "processing_progress.json"
        self.progress = self.load_progress()
        
        # Test database connection
        self.test_database_connection()
    
    def test_database_connection(self):
        """Test database connection before processing"""
        logger.info("🔍 Testing database connection...")
        try:
            from supabase import create_client
            supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Test connection with a simple query
            result = supabase.table('insider_transactions').select('id').limit(1).execute()
            logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise ConnectionError(f"Cannot connect to Supabase: {e}")
    
    def load_progress(self) -> Dict:
        """Load processing progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")
        
        # Initialize progress
        return {
            "completed": [],
            "failed": [],
            "current_quarter": None,
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def save_progress(self):
        """Save processing progress to file"""
        self.progress["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress file: {e}")
    
    def detect_format(self, quarter: str) -> str:
        """Detect if quarter is pre-2023 or post-2023 format"""
        # Format changed at 2023q1 (13 columns -> 14 columns)
        year = int(quarter[:4])
        quarter_num = int(quarter[5:6])
        
        if year < 2023 or (year == 2023 and quarter_num < 1):
            return "pre_2023"
        else:
            return "post_2023"
    
    def get_all_quarters(self) -> List[str]:
        """Get list of all quarters to process"""
        quarters = []
        
        # Generate all quarters from 2006q1 to 2025q2
        for year in range(2006, 2026):
            for quarter in range(1, 5):
                if year == 2025 and quarter > 2:  # Only Q1 and Q2 for 2025
                    break
                quarters.append(f"{year}q{quarter}_form345")
        
        return quarters
    
    def validate_quarter_exists(self, quarter: str) -> bool:
        """Validate that quarter ZIP file exists"""
        zip_path = self.data_dir / f"{quarter}.zip"
        return zip_path.exists()
    
    def process_quarter(self, quarter: str) -> Dict:
        """Process a single quarter with format detection"""
        logger.info(f"🔄 Processing {quarter}...")
        
        # Validate quarter exists
        if not self.validate_quarter_exists(quarter):
            logger.error(f"❌ Quarter {quarter} not found in data directory")
            return {'status': 'quarter_not_found', 'quarter': quarter}
        
        # Check if already processed
        if quarter in self.progress["completed"]:
            logger.info(f"✅ {quarter} already completed, skipping")
            return {'status': 'already_completed', 'quarter': quarter}
        
        if quarter in self.progress["failed"]:
            logger.info(f"⚠️ {quarter} previously failed, retrying...")
        
        try:
            # Detect format
            format_type = self.detect_format(quarter)
            logger.info(f"📊 Detected format: {format_type}")
            
            # Route to correct processor
            if format_type == "pre_2023":
                logger.error(f"❌ Pre-2023 processor not available for {quarter}")
                return {'status': 'processor_not_available', 'quarter': quarter, 'format': format_type}
            else:
                processor = Post2023Processor(self.data_dir, self.supabase_url, self.supabase_key)
            
            # Process the quarter
            result = processor.process_quarter(quarter)
            
            # Update progress
            if result['status'] == 'success':
                self.progress["completed"].append(quarter)
                if quarter in self.progress["failed"]:
                    self.progress["failed"].remove(quarter)
                logger.info(f"✅ {quarter} completed successfully")
            else:
                logger.info(f"ℹ️ {quarter} status: {result['status']}")
            
            self.save_progress()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing {quarter}: {e}")
            
            # Update progress
            if quarter not in self.progress["failed"]:
                self.progress["failed"].append(quarter)
            self.save_progress()
            
            # Log detailed error for debugging
            logger.error(f"Error details for {quarter}: {type(e).__name__}: {str(e)}")
            
            return {'status': 'error', 'quarter': quarter, 'error': str(e)}
    
    def process_all_quarters(self) -> Dict:
        """Process all quarters systematically"""
        logger.info("🚀 Starting systematic processing of all quarters...")
        
        quarters = self.get_all_quarters()
        logger.info(f"📊 Total quarters to process: {len(quarters)}")
        
        start_time = datetime.now()
        results = {
            "completed": [],
            "failed": [],
            "errors": [],
            "start_time": start_time.isoformat(),
            "performance_metrics": {
                "quarters_per_minute": 0,
                "avg_processing_time": 0,
                "total_processing_time": 0
            }
        }
        
        for i, quarter in enumerate(quarters, 1):
            progress_pct = (i-1) / len(quarters) * 100
            logger.info(f"\n📈 Progress: {i}/{len(quarters)} ({progress_pct:.1f}%) - Processing {quarter}")
            
            try:
                result = self.process_quarter(quarter)
                
                if result['status'] == 'success':
                    results["completed"].append(quarter)
                    logger.info(f"✅ {quarter} completed ({i}/{len(quarters)})")
                elif result['status'] == 'already_completed':
                    results["completed"].append(quarter)
                    logger.info(f"ℹ️ {quarter} already completed ({i}/{len(quarters)})")
                else:
                    results["failed"].append(quarter)
                    results["errors"].append(f"{quarter}: {result.get('error', 'Unknown error')}")
                    logger.error(f"❌ {quarter} failed ({i}/{len(quarters)})")
                
            except Exception as e:
                results["failed"].append(quarter)
                results["errors"].append(f"{quarter}: {str(e)}")
                logger.error(f"❌ {quarter} failed with exception: {e}")
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        results["end_time"] = end_time.isoformat()
        results["total_quarters"] = len(quarters)
        results["success_rate"] = len(results["completed"]) / len(quarters) * 100
        
        # Calculate performance metrics
        results["performance_metrics"]["total_processing_time"] = total_time
        results["performance_metrics"]["quarters_per_minute"] = len(results["completed"]) / (total_time / 60) if total_time > 0 else 0
        results["performance_metrics"]["avg_processing_time"] = total_time / len(quarters) if len(quarters) > 0 else 0
        
        logger.info(f"\n🎯 Processing complete!")
        logger.info(f"✅ Completed: {len(results['completed'])}/{len(quarters)} quarters")
        logger.info(f"❌ Failed: {len(results['failed'])} quarters")
        logger.info(f"📊 Success rate: {results['success_rate']:.1f}%")
        
        return results
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        quarters = self.get_all_quarters()
        total_quarters = len(quarters)
        completed = len(self.progress["completed"])
        failed = len(self.progress["failed"])
        remaining = total_quarters - completed - failed
        
        return {
            "total_quarters": total_quarters,
            "completed": completed,
            "failed": failed,
            "remaining": remaining,
            "progress_percentage": (completed / total_quarters) * 100,
            "completed_quarters": self.progress["completed"],
            "failed_quarters": self.progress["failed"]
        }
    
    def retry_failed_quarters(self) -> Dict:
        """Retry processing failed quarters with smaller batch sizes"""
        logger.info("🔄 Retrying failed quarters...")
        
        failed_quarters = self.progress["failed"].copy()
        if not failed_quarters:
            logger.info("✅ No failed quarters to retry")
            return {'status': 'no_failures', 'retried': 0}
        
        logger.info(f"📊 Retrying {len(failed_quarters)} failed quarters")
        
        retry_results = {
            "retried": [],
            "still_failed": [],
            "errors": []
        }
        
        for quarter in failed_quarters:
            logger.info(f"🔄 Retrying {quarter}...")
            try:
                result = self.process_quarter(quarter)
                if result['status'] == 'success':
                    retry_results["retried"].append(quarter)
                    self.progress["failed"].remove(quarter)
                    self.progress["completed"].append(quarter)
                    logger.info(f"✅ {quarter} retry successful")
                else:
                    retry_results["still_failed"].append(quarter)
                    logger.warning(f"⚠️ {quarter} retry failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                retry_results["still_failed"].append(quarter)
                retry_results["errors"].append(f"{quarter}: {str(e)}")
                logger.error(f"❌ {quarter} retry failed with exception: {e}")
        
        self.save_progress()
        
        logger.info(f"🎯 Retry complete: {len(retry_results['retried'])} successful, {len(retry_results['still_failed'])} still failed")
        return retry_results

def main():
    """Main function for processing all quarters"""
    import os
    
    # Load environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials")
        print("Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        return
    
    data_dir = "/Users/ronniederman/insider-alpha-platform/data-processing/sec_insider_data"
    
    try:
        # Initialize processor
        processor = FailSafeProcessor(data_dir, SUPABASE_URL, SUPABASE_KEY)
        
        # Get current status
        status = processor.get_status()
        print(f"\n📊 Current Status:")
        print(f"  Total quarters: {status['total_quarters']}")
        print(f"  Completed: {status['completed']}")
        print(f"  Failed: {status['failed']}")
        print(f"  Remaining: {status['remaining']}")
        print(f"  Progress: {status['progress_percentage']:.1f}%")
        
        if status['remaining'] > 0:
            print(f"\n🚀 Starting processing of {status['remaining']} remaining quarters...")
            results = processor.process_all_quarters()
            
            print(f"\n🎯 Final Results:")
            print(f"  ✅ Completed: {len(results['completed'])} quarters")
            print(f"  ❌ Failed: {len(results['failed'])} quarters")
            print(f"  📊 Success rate: {results['success_rate']:.1f}%")
            
            if results['failed']:
                print(f"\n❌ Failed quarters:")
                for quarter in results['failed']:
                    print(f"  - {quarter}")
        else:
            print("✅ All quarters already processed!")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        logger.error(f"Processing failed: {e}")

if __name__ == "__main__":
    main()
