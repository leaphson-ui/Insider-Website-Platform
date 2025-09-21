"""
SEC Quarterly Insider Transaction Data Ingestion
Downloads and processes SEC's quarterly insider transaction datasets
"""

import os
import sys
import requests
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Optional
import pandas as pd
import zipfile
import io
import time
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECQuarterlyDataIngestion:
    def __init__(self):
        self.db = SessionLocal()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Insider Alpha Platform (admin@insideralpha.com)',
            'Accept-Encoding': 'gzip, deflate'
        })
        self.base_url = "https://www.sec.gov"
        self.data_dir = Path("sec_data")
        self.data_dir.mkdir(exist_ok=True)
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_available_quarters(self, years_back: int = 3) -> List[str]:
        """Generate list of quarters to download"""
        quarters = []
        current_date = datetime.now()
        
        for year in range(current_date.year - years_back, current_date.year + 1):
            for quarter in range(1, 5):
                # Don't try to get future quarters
                quarter_date = datetime(year, quarter * 3, 1)
                if quarter_date <= current_date:
                    quarters.append(f"{year}q{quarter}")
        
        return quarters
    
    def download_quarterly_data(self, quarter: str) -> Optional[str]:
        """Download quarterly insider transaction data from SEC"""
        logger.info(f"Downloading SEC data for {quarter}")
        
        try:
            # Try different URL patterns that SEC might use
            possible_urls = [
                f"https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{quarter}_insider.zip",
                f"https://www.sec.gov/files/insider-transactions-data-sets/{quarter}_insider.zip",
                f"https://www.sec.gov/data/insider-transactions/{quarter}.zip",
                f"https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets/{quarter}.zip"
            ]
            
            for url in possible_urls:
                try:
                    logger.info(f"Trying URL: {url}")
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        # Save the zip file
                        zip_path = self.data_dir / f"{quarter}_insider.zip"
                        with open(zip_path, 'wb') as f:
                            f.write(response.content)
                        
                        logger.info(f"Successfully downloaded {quarter} data ({len(response.content)} bytes)")
                        return str(zip_path)
                    
                except requests.exceptions.RequestException as e:
                    logger.debug(f"Failed to download from {url}: {e}")
                    continue
            
            logger.warning(f"Could not download data for {quarter} from any URL")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading {quarter} data: {e}")
            return None
    
    def extract_and_process_zip(self, zip_path: str) -> List[Dict]:
        """Extract and process the downloaded zip file"""
        logger.info(f"Processing zip file: {zip_path}")
        
        transactions = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # List contents
                file_list = zip_ref.namelist()
                logger.info(f"Zip contains files: {file_list}")
                
                # Look for CSV or TXT files
                data_files = [f for f in file_list if f.endswith(('.csv', '.txt', '.tsv'))]
                
                for data_file in data_files:
                    logger.info(f"Processing file: {data_file}")
                    
                    with zip_ref.open(data_file) as file:
                        # Try to read as CSV
                        try:
                            # Try different delimiters
                            content = file.read().decode('utf-8')
                            
                            # Detect delimiter
                            if '\t' in content:
                                delimiter = '\t'
                            elif '|' in content:
                                delimiter = '|'
                            else:
                                delimiter = ','
                            
                            # Read with pandas
                            df = pd.read_csv(io.StringIO(content), delimiter=delimiter, low_memory=False)
                            
                            logger.info(f"Loaded {len(df)} records from {data_file}")
                            logger.info(f"Columns: {list(df.columns)}")
                            
                            # Process the dataframe
                            file_transactions = self.process_dataframe(df)
                            transactions.extend(file_transactions)
                            
                        except Exception as e:
                            logger.error(f"Error processing {data_file}: {e}")
                            continue
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error extracting zip file {zip_path}: {e}")
            return []
    
    def process_dataframe(self, df: pd.DataFrame) -> List[Dict]:
        """Process pandas dataframe into transaction records"""
        transactions = []
        
        try:
            # Map common column names (SEC datasets may have different column names)
            column_mapping = {
                # Possible variations of column names
                'issuer_name': ['issuer_name', 'company_name', 'issuerName', 'CompanyName'],
                'issuer_ticker': ['issuer_ticker', 'ticker', 'issuerTradingSymbol', 'Ticker', 'Symbol'],
                'owner_name': ['owner_name', 'insider_name', 'ownerName', 'InsiderName', 'rptOwnerName'],
                'owner_title': ['owner_title', 'title', 'officerTitle', 'Title', 'Position'],
                'transaction_date': ['transaction_date', 'transactionDate', 'TransactionDate', 'Date'],
                'transaction_code': ['transaction_code', 'transactionCode', 'TransactionCode', 'Code'],
                'shares': ['shares', 'transaction_shares', 'transactionShares', 'Shares', 'SharesTraded'],
                'price': ['price', 'price_per_share', 'transactionPricePerShare', 'Price', 'PricePerShare'],
                'value': ['value', 'transaction_value', 'transactionValue', 'Value', 'TotalValue']
            }
            
            # Find actual column names
            actual_columns = {}
            for standard_name, possible_names in column_mapping.items():
                for possible_name in possible_names:
                    if possible_name in df.columns:
                        actual_columns[standard_name] = possible_name
                        break
            
            logger.info(f"Mapped columns: {actual_columns}")
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Extract data using mapped column names
                    company_name = str(row.get(actual_columns.get('issuer_name', ''), 'Unknown')).strip()
                    ticker = str(row.get(actual_columns.get('issuer_ticker', ''), '')).strip().upper()
                    owner_name = str(row.get(actual_columns.get('owner_name', ''), 'Unknown')).strip()
                    owner_title = str(row.get(actual_columns.get('owner_title', ''), '')).strip()
                    
                    # Skip if essential data is missing
                    if not ticker or ticker == 'NAN' or not company_name or company_name == 'Unknown':
                        continue
                    
                    # Transaction date
                    date_str = str(row.get(actual_columns.get('transaction_date', ''), ''))
                    try:
                        if date_str and date_str != 'nan':
                            transaction_date = pd.to_datetime(date_str).date()
                        else:
                            continue
                    except:
                        continue
                    
                    # Transaction details
                    transaction_code = str(row.get(actual_columns.get('transaction_code', ''), '')).strip().upper()
                    
                    # Shares and price
                    shares = row.get(actual_columns.get('shares', ''), 0)
                    price = row.get(actual_columns.get('price', ''), 0)
                    
                    try:
                        shares = float(shares) if pd.notna(shares) else 0
                        price = float(price) if pd.notna(price) else 0
                    except:
                        continue
                    
                    if shares <= 0 or price <= 0:
                        continue
                    
                    # Convert transaction code
                    transaction_type = self.convert_transaction_code(transaction_code)
                    
                    total_value = shares * price
                    
                    transaction = {
                        'company_name': company_name,
                        'ticker': ticker,
                        'owner_name': owner_name,
                        'owner_title': owner_title,
                        'transaction_date': transaction_date,
                        'transaction_type': transaction_type,
                        'transaction_code': transaction_code,
                        'shares': shares,
                        'price_per_share': price,
                        'total_value': total_value
                    }
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    logger.debug(f"Error processing row {index}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(transactions)} transactions from dataframe")
            return transactions
            
        except Exception as e:
            logger.error(f"Error processing dataframe: {e}")
            return []
    
    def convert_transaction_code(self, code: str) -> str:
        """Convert SEC transaction codes to readable types"""
        code_map = {
            'A': 'BUY', 'D': 'SELL', 'P': 'BUY', 'S': 'SELL',
            'M': 'OPTION_EXERCISE', 'F': 'TAX_WITHHOLDING',
            'G': 'GIFT', 'V': 'OTHER', 'J': 'OTHER', 'K': 'OTHER', 'W': 'OTHER'
        }
        return code_map.get(code.upper(), 'OTHER')
    
    def save_transactions_to_db(self, transactions: List[Dict]) -> int:
        """Save transactions to database"""
        logger.info(f"Saving {len(transactions)} transactions to database...")
        
        saved_count = 0
        batch_size = 1000
        
        try:
            for i in range(0, len(transactions), batch_size):
                batch = transactions[i:i + batch_size]
                
                for transaction_data in batch:
                    try:
                        # Find or create trader
                        trader = self.db.query(Trader).filter(
                            Trader.name == transaction_data['owner_name'],
                            Trader.company_ticker == transaction_data['ticker']
                        ).first()
                        
                        if not trader:
                            trader = Trader(
                                name=transaction_data['owner_name'],
                                title=transaction_data['owner_title'],
                                company_ticker=transaction_data['ticker'],
                                company_name=transaction_data['company_name'],
                                relationship_to_company=transaction_data['owner_title']
                            )
                            self.db.add(trader)
                            self.db.flush()
                        
                        # Check if trade already exists
                        existing_trade = self.db.query(Trade).filter(
                            Trade.trader_id == trader.trader_id,
                            Trade.transaction_date == transaction_data['transaction_date'],
                            Trade.shares_traded == Decimal(str(transaction_data['shares'])),
                            Trade.price_per_share == Decimal(str(transaction_data['price_per_share']))
                        ).first()
                        
                        if not existing_trade:
                            trade = Trade(
                                trader_id=trader.trader_id,
                                company_ticker=transaction_data['ticker'],
                                transaction_date=transaction_data['transaction_date'],
                                transaction_type=transaction_data['transaction_type'],
                                shares_traded=Decimal(str(transaction_data['shares'])),
                                price_per_share=Decimal(str(transaction_data['price_per_share'])),
                                total_value=Decimal(str(transaction_data['total_value'])),
                                form_type='Form 4',
                                filing_date=transaction_data['transaction_date']
                            )
                            
                            self.db.add(trade)
                            saved_count += 1
                    
                    except Exception as e:
                        logger.debug(f"Error saving transaction: {e}")
                        continue
                
                # Commit batch
                self.db.commit()
                
                if (i + batch_size) % 5000 == 0:
                    logger.info(f"Saved {i + batch_size}/{len(transactions)} transactions...")
            
            # Update trader trade counts
            logger.info("Updating trader trade counts...")
            traders = self.db.query(Trader).all()
            for trader in traders:
                trader.total_trades = self.db.query(Trade).filter(
                    Trade.trader_id == trader.trader_id
                ).count()
            
            self.db.commit()
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving transactions to database: {e}")
            self.db.rollback()
            return 0
    
    def run_quarterly_ingestion(self, years_back: int = 2):
        """Run quarterly data ingestion"""
        logger.info(f"Starting SEC quarterly data ingestion for {years_back} years...")
        
        total_transactions = 0
        total_saved = 0
        
        try:
            # Get list of quarters to download
            quarters = self.get_available_quarters(years_back)
            logger.info(f"Will attempt to download data for quarters: {quarters}")
            
            for quarter in quarters:
                logger.info(f"Processing quarter: {quarter}")
                
                # Download quarterly data
                zip_path = self.download_quarterly_data(quarter)
                
                if zip_path:
                    # Extract and process
                    transactions = self.extract_and_process_zip(zip_path)
                    total_transactions += len(transactions)
                    
                    if transactions:
                        # Save to database
                        saved = self.save_transactions_to_db(transactions)
                        total_saved += saved
                        
                        logger.info(f"Quarter {quarter}: {saved}/{len(transactions)} transactions saved")
                    
                    # Clean up zip file
                    try:
                        os.remove(zip_path)
                    except:
                        pass
                
                # Be respectful to SEC servers
                time.sleep(1)
            
            logger.info(f"Quarterly ingestion complete: {total_saved}/{total_transactions} transactions saved")
            
        except Exception as e:
            logger.error(f"Error in quarterly ingestion: {e}")

def main():
    """Main function to run SEC quarterly data ingestion"""
    try:
        ingestion = SECQuarterlyDataIngestion()
        
        # Try to download quarterly datasets for the past 2 years
        ingestion.run_quarterly_ingestion(years_back=2)
        
        print(f"\n🎉 SEC Quarterly Data Ingestion Complete!")
        print("If no data was found, the SEC might not have quarterly datasets available")
        print("or they might be in a different format/location.")
        print("\nAs a fallback, run the massive data generator:")
        print("python scripts/massive_data_generator.py")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
