"""
Download and Process Massive SEC Dataset
Downloads multiple years of SEC quarterly insider trading data
"""

import os
import sys
import requests
import logging
from pathlib import Path
import time
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MassiveSECDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Insider Alpha Platform (admin@insideralpha.com)'
        })
        self.data_dir = Path("sec_quarterly_data")
        self.data_dir.mkdir(exist_ok=True)
    
    def get_all_available_quarters(self) -> List[str]:
        """Get all available quarters from 2006-2025"""
        quarters = []
        
        # Generate all quarters from 2020-2025 (last 5 years for faster processing)
        for year in range(2020, 2026):
            for quarter in range(1, 5):
                if year == 2025 and quarter > 2:  # Don't go beyond current quarter
                    break
                quarters.append(f"{year}q{quarter}")
        
        return quarters
    
    def download_quarter(self, quarter: str) -> bool:
        """Download a single quarter's data"""
        try:
            url = f"https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{quarter}_form345.zip"
            zip_path = self.data_dir / f"{quarter}_form345.zip"
            
            if zip_path.exists():
                logger.info(f"✅ {quarter} already downloaded ({zip_path.stat().st_size:,} bytes)")
                return True
            
            logger.info(f"📥 Downloading {quarter}...")
            response = self.session.get(url, timeout=120)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Downloaded {quarter} ({len(response.content):,} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {quarter}: {e}")
            return False
    
    def download_massive_dataset(self, years_back: int = 5):
        """Download multiple years of SEC data"""
        logger.info(f"🚀 Downloading {years_back} years of SEC insider trading data...")
        
        quarters = self.get_all_available_quarters()
        total_size = 0
        successful_downloads = 0
        
        for i, quarter in enumerate(quarters, 1):
            logger.info(f"📊 Progress: {i}/{len(quarters)} quarters")
            
            if self.download_quarter(quarter):
                successful_downloads += 1
                
                # Check file size
                zip_path = self.data_dir / f"{quarter}_form345.zip"
                if zip_path.exists():
                    total_size += zip_path.stat().st_size
            
            # Be respectful to SEC servers
            time.sleep(0.5)
        
        logger.info(f"\n🎉 Download Summary:")
        logger.info(f"📊 Successfully downloaded: {successful_downloads}/{len(quarters)} quarters")
        logger.info(f"💾 Total data size: {total_size / (1024*1024):.1f} MB")
        logger.info(f"📅 Time period: {years_back} years (2020-2025)")
        logger.info(f"📈 Estimated transactions: {successful_downloads * 60000:,}")
        
        return successful_downloads

def main():
    """Main function to download massive SEC dataset"""
    try:
        downloader = MassiveSECDownloader()
        
        print("🚀 MASSIVE SEC DATASET DOWNLOADER")
        print("=" * 60)
        print("This will download 5+ years of SEC insider trading data")
        print("Each quarter contains 50,000-70,000 real transactions")
        print("Total estimated: 1+ million insider trades")
        print("=" * 60)
        
        # Download last 5 years of data
        successful = downloader.download_massive_dataset(years_back=5)
        
        print(f"\n✅ Download complete!")
        print(f"📊 {successful} quarters downloaded")
        print(f"💾 Data ready for processing")
        print(f"\n🎯 Next steps:")
        print("1. Run: python scripts/automated_sec_data_manager.py")
        print("2. Run: python scripts/performance_calc.py") 
        print("3. Refresh your browser to see massive dataset!")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
