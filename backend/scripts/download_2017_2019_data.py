#!/usr/bin/env python3
"""
Download SEC quarterly data for 2017-2019
"""

import os
import requests
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_historical_quarters():
    """Download quarterly data for 2017-2019"""
    
    # Create directory if it doesn't exist
    data_dir = 'sec_quarterly_data'
    os.makedirs(data_dir, exist_ok=True)
    
    # Quarters to download (2017-2019)
    quarters_to_download = [
        '2017q1', '2017q2', '2017q3', '2017q4',
        '2018q1', '2018q2', '2018q3', '2018q4', 
        '2019q1', '2019q2', '2019q3', '2019q4'
    ]
    
    base_url = "https://www.sec.gov/files/structureddata/data/form-345-xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    downloaded = 0
    
    for quarter in quarters_to_download:
        filename = f"{quarter}_form345.zip"
        filepath = os.path.join(data_dir, filename)
        
        # Skip if already exists
        if os.path.exists(filepath):
            logger.info(f"✅ {quarter}: Already exists, skipping")
            continue
        
        url = f"{base_url}/{filename}"
        logger.info(f"📥 Downloading {quarter}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=300)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            logger.info(f"✅ {quarter}: Downloaded {file_size_mb:.1f} MB")
            downloaded += 1
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to download {quarter}: {e}")
            continue
    
    logger.info(f"🎉 Downloaded {downloaded} new quarterly files!")
    
    # List all available quarters
    all_files = [f for f in os.listdir(data_dir) if f.endswith('_form345.zip')]
    all_files.sort()
    
    logger.info(f"\n📊 Total quarterly files available: {len(all_files)}")
    for f in all_files:
        logger.info(f"  - {f}")

if __name__ == "__main__":
    download_historical_quarters()


