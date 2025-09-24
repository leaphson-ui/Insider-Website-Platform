#!/usr/bin/env python3
"""
Download sample SEC insider trading datasets for testing
"""

import requests
import os
from urllib.parse import urljoin
import time

def download_sec_data():
    """Download sample quarterly datasets"""
    
    # SEC insider trading data URLs (you'll need to find the exact URLs)
    base_url = "https://www.sec.gov/files/data/insider-trading-data/"
    
    # Sample quarters to download (start with recent ones)
    sample_quarters = [
        "2024-Q3",  # Most recent available
        "2024-Q2"   # Second most recent
    ]
    
    # Create data directory
    os.makedirs("sample_data", exist_ok=True)
    
    headers = {
        'User-Agent': 'Insider Alpha Platform Data Processing (your-email@domain.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    downloaded_files = []
    
    for quarter in sample_quarters:
        filename = f"insider-trading-{quarter}.csv"
        filepath = os.path.join("sample_data", filename)
        url = urljoin(base_url, filename)
        
        print(f"Downloading {filename}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            print(f"✓ Downloaded {filename} ({file_size:.1f} MB)")
            downloaded_files.append(filepath)
            
            # Be respectful to SEC servers
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to download {filename}: {str(e)}")
        except Exception as e:
            print(f"✗ Error saving {filename}: {str(e)}")
    
    return downloaded_files

def manual_download_instructions():
    """Print manual download instructions"""
    print("\n" + "="*60)
    print("MANUAL DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print("Since automated download might fail due to SEC server restrictions,")
    print("here are manual steps:")
    print()
    print("1. Go to: https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets")
    print("2. Download these files to your 'sample_data' folder:")
    print("   - insider-trading-2024-Q3.csv (or most recent quarter)")
    print("   - insider-trading-2024-Q2.csv")
    print("3. Make sure files are in the same directory as this script")
    print()
    print("Alternative: Use a smaller sample by taking the first 10,000 rows")
    print("from any quarterly file for initial testing.")
    print("="*60)

if __name__ == "__main__":
    print("SEC Insider Trading Data Downloader")
    print("="*40)
    
    # Try automated download first
    downloaded_files = download_sec_data()
    
    if downloaded_files:
        print(f"\n✓ Successfully downloaded {len(downloaded_files)} files")
        print("Files ready for data cleaning pipeline test!")
    else:
        print("\n✗ Automated download failed")
        manual_download_instructions()
