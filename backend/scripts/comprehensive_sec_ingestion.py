"""
Comprehensive SEC EDGAR Form 4 Data Ingestion
This script pulls extensive historical and real-time insider trading data
"""

import os
import sys
import requests
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import re
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveSECIngestion:
    def __init__(self):
        self.db = SessionLocal()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Insider Alpha Platform (admin@insideralpha.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
        self.base_url = "https://www.sec.gov"
        self.rate_limiter = threading.Semaphore(10)  # Max 10 concurrent requests
        self.request_count = 0
        self.last_request_time = time.time()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def rate_limited_request(self, url, **kwargs):
        """Make rate-limited requests to SEC (max 10 per second)"""
        with self.rate_limiter:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < 0.1:  # Ensure at least 0.1 seconds between requests
                time.sleep(0.1 - time_since_last)
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            if self.request_count % 100 == 0:
                logger.info(f"Made {self.request_count} requests to SEC")
            
            return self.session.get(url, **kwargs)
    
    def get_company_cik_list(self) -> Dict[str, str]:
        """Get comprehensive list of company CIKs and tickers"""
        try:
            logger.info("Fetching comprehensive company list...")
            
            # Get company tickers JSON from SEC
            url = "https://www.sec.gov/files/company_tickers.json"
            response = self.rate_limited_request(url)
            response.raise_for_status()
            
            company_data = response.json()
            
            # Convert to ticker -> CIK mapping
            ticker_to_cik = {}
            for entry in company_data.values():
                ticker = entry.get('ticker', '').upper()
                cik = str(entry.get('cik_str', '')).zfill(10)  # Pad CIK to 10 digits
                
                if ticker and cik:
                    ticker_to_cik[ticker] = cik
            
            logger.info(f"Found {len(ticker_to_cik)} companies")
            return ticker_to_cik
            
        except Exception as e:
            logger.error(f"Error fetching company list: {e}")
            # Fallback to our known companies
            return {
                'AAPL': '0000320193',
                'MSFT': '0000789019', 
                'GOOGL': '0001652044',
                'NVDA': '0001045810',
                'TSLA': '0001318605',
                'AMZN': '0001018724',
                'META': '0001326801'
            }
    
    def get_historical_form4_filings(self, cik: str, ticker: str, years_back: int = 2) -> List[Dict]:
        """Get historical Form 4 filings for a specific company"""
        logger.info(f"Fetching historical Form 4 filings for {ticker} (CIK: {cik})")
        
        filings = []
        
        try:
            # SEC submissions API
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = self.rate_limited_request(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract Form 4 filings
            if 'filings' in data and 'recent' in data['filings']:
                forms = data['filings']['recent']['form']
                filing_dates = data['filings']['recent']['filingDate']
                accession_numbers = data['filings']['recent']['accessionNumber']
                
                cutoff_date = datetime.now().date() - timedelta(days=years_back * 365)
                
                for i, form in enumerate(forms):
                    if form == '4':  # Form 4 filing
                        filing_date = datetime.strptime(filing_dates[i], '%Y-%m-%d').date()
                        
                        if filing_date >= cutoff_date:
                            filings.append({
                                'ticker': ticker,
                                'cik': cik,
                                'accession_number': accession_numbers[i],
                                'filing_date': filing_date,
                                'url': f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession_numbers[i].replace('-', '')}/{accession_numbers[i]}.txt"
                            })
            
            logger.info(f"Found {len(filings)} Form 4 filings for {ticker}")
            return filings
            
        except Exception as e:
            logger.error(f"Error fetching historical filings for {ticker}: {e}")
            return []
    
    def get_recent_form4_filings_comprehensive(self, days_back: int = 30) -> List[Dict]:
        """Get comprehensive recent Form 4 filings from RSS feed"""
        logger.info(f"Fetching comprehensive Form 4 filings from last {days_back} days...")
        
        all_filings = []
        
        try:
            # Get multiple pages of recent filings
            for start in range(0, 1000, 100):  # Get up to 1000 recent filings
                params = {
                    'action': 'getcurrent',
                    'type': 'form4',
                    'count': '100',
                    'start': str(start),
                    'output': 'atom'
                }
                
                url = "https://www.sec.gov/cgi-bin/browse-edgar"
                response = self.rate_limited_request(url, params=params)
                response.raise_for_status()
                
                # Parse the Atom feed
                filings = self.parse_atom_feed(response.content)
                
                if not filings:  # No more filings
                    break
                
                # Filter by date
                cutoff_date = datetime.now() - timedelta(days=days_back)
                recent_filings = [
                    filing for filing in filings 
                    if filing.get('date') and filing['date'] > cutoff_date
                ]
                
                all_filings.extend(recent_filings)
                
                if len(recent_filings) < len(filings):  # We've gone past our date range
                    break
                
                # Small delay between pages
                time.sleep(0.2)
            
            logger.info(f"Found {len(all_filings)} comprehensive recent Form 4 filings")
            return all_filings
            
        except Exception as e:
            logger.error(f"Error fetching comprehensive recent filings: {e}")
            return []
    
    def parse_atom_feed(self, atom_content: bytes) -> List[Dict]:
        """Parse SEC EDGAR Atom feed to extract filing information"""
        filings = []
        
        try:
            root = ET.fromstring(atom_content)
            namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('.//atom:entry', namespaces)
            
            for entry in entries:
                try:
                    title_elem = entry.find('atom:title', namespaces)
                    link_elem = entry.find('atom:link', namespaces)
                    updated_elem = entry.find('atom:updated', namespaces)
                    
                    if title_elem is not None and link_elem is not None:
                        title = title_elem.text or ""
                        link = link_elem.get('href', '')
                        
                        filing_date = None
                        if updated_elem is not None:
                            try:
                                date_str = updated_elem.text
                                filing_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        # Enhanced parsing for company and person info
                        company_match = re.search(r'4\s*-\s*(.+?)\s*\(([A-Z]+)\)', title)
                        
                        if company_match:
                            company_name = company_match.group(1).strip()
                            ticker = company_match.group(2).strip()
                            
                            person_match = re.search(r'\([A-Z]+\)\s*-\s*(.+)', title)
                            person_name = person_match.group(1).strip() if person_match else "Unknown"
                            
                            filing = {
                                'title': title,
                                'company_name': company_name,
                                'ticker': ticker,
                                'person_name': person_name,
                                'link': f"{self.base_url}{link}" if link.startswith('/') else link,
                                'date': filing_date,
                                'raw_title': title
                            }
                            
                            filings.append(filing)
                            
                except Exception as e:
                    logger.debug(f"Error parsing entry: {e}")
                    continue
            
            return filings
            
        except Exception as e:
            logger.error(f"Error parsing Atom feed: {e}")
            return []
    
    def process_filing_batch(self, filings: List[Dict]) -> int:
        """Process a batch of filings in parallel"""
        successful_trades = 0
        
        with ThreadPoolExecutor(max_workers=5) as executor:  # Limit concurrent processing
            future_to_filing = {
                executor.submit(self.parse_and_save_form4, filing): filing 
                for filing in filings
            }
            
            for future in as_completed(future_to_filing):
                filing = future_to_filing[future]
                try:
                    trades_count = future.result()
                    successful_trades += trades_count
                except Exception as e:
                    logger.error(f"Error processing filing {filing.get('title', 'Unknown')}: {e}")
        
        return successful_trades
    
    def parse_and_save_form4(self, filing: Dict) -> int:
        """Parse individual Form 4 and save transactions"""
        try:
            transactions = self.parse_form4_document(filing['link'])
            trades_saved = 0
            
            for transaction in transactions:
                if self.save_transaction_to_db(transaction):
                    trades_saved += 1
            
            return trades_saved
            
        except Exception as e:
            logger.error(f"Error parsing Form 4 {filing.get('link', 'Unknown')}: {e}")
            return 0
    
    def parse_form4_document(self, filing_url: str) -> List[Dict]:
        """Parse individual Form 4 document to extract transaction details"""
        try:
            response = self.rate_limited_request(filing_url)
            response.raise_for_status()
            
            content = response.text
            
            # Find XML document link
            xml_match = re.search(r'href="([^"]*\.xml)"', content)
            if xml_match:
                xml_url = xml_match.group(1)
                if xml_url.startswith('/'):
                    xml_url = f"{self.base_url}{xml_url}"
                
                xml_response = self.rate_limited_request(xml_url)
                xml_response.raise_for_status()
                
                return self.parse_form4_xml(xml_response.content)
            
            return []
            
        except Exception as e:
            logger.debug(f"Error parsing Form 4 document {filing_url}: {e}")
            return []
    
    def parse_form4_xml(self, xml_content: bytes) -> List[Dict]:
        """Parse Form 4 XML content to extract transaction data"""
        transactions = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Extract issuer information
            issuer = root.find('.//issuer')
            company_name = ""
            ticker = ""
            
            if issuer is not None:
                name_elem = issuer.find('issuerName')
                ticker_elem = issuer.find('issuerTradingSymbol')
                
                if name_elem is not None:
                    company_name = name_elem.text or ""
                if ticker_elem is not None:
                    ticker = ticker_elem.text or ""
            
            # Extract reporting owner information
            owner = root.find('.//reportingOwner')
            owner_name = ""
            owner_title = ""
            
            if owner is not None:
                name_elem = owner.find('.//rptOwnerName')
                title_elem = owner.find('.//officerTitle')
                
                if name_elem is not None:
                    owner_name = name_elem.text or ""
                if title_elem is not None:
                    owner_title = title_elem.text or ""
            
            # Extract non-derivative transactions
            non_derivative_table = root.find('.//nonDerivativeTable')
            if non_derivative_table is not None:
                for transaction in non_derivative_table.findall('.//nonDerivativeTransaction'):
                    try:
                        trans_data = self.extract_transaction_data(
                            transaction, company_name, ticker, owner_name, owner_title
                        )
                        if trans_data:
                            transactions.append(trans_data)
                    except Exception as e:
                        logger.debug(f"Error extracting transaction: {e}")
                        continue
            
            return transactions
            
        except Exception as e:
            logger.debug(f"Error parsing Form 4 XML: {e}")
            return []
    
    def extract_transaction_data(self, transaction_elem, company_name: str, 
                               ticker: str, owner_name: str, owner_title: str) -> Optional[Dict]:
        """Extract transaction data from XML element"""
        try:
            # Transaction date
            date_elem = transaction_elem.find('.//transactionDate/value')
            if date_elem is None:
                return None
            
            transaction_date = datetime.strptime(date_elem.text, '%Y-%m-%d').date()
            
            # Transaction code
            code_elem = transaction_elem.find('.//transactionCode')
            transaction_code = code_elem.text if code_elem is not None else ""
            transaction_type = self.convert_transaction_code(transaction_code)
            
            # Shares/amount
            shares_elem = transaction_elem.find('.//transactionShares/value')
            if shares_elem is None:
                return None
            
            shares = float(shares_elem.text)
            
            # Price per share
            price_elem = transaction_elem.find('.//transactionPricePerShare/value')
            if price_elem is None:
                return None
            
            price_per_share = float(price_elem.text)
            total_value = shares * price_per_share
            
            return {
                'company_name': company_name,
                'ticker': ticker,
                'owner_name': owner_name,
                'owner_title': owner_title,
                'transaction_date': transaction_date,
                'transaction_type': transaction_type,
                'transaction_code': transaction_code,
                'shares': shares,
                'price_per_share': price_per_share,
                'total_value': total_value
            }
            
        except Exception as e:
            logger.debug(f"Error extracting transaction data: {e}")
            return None
    
    def convert_transaction_code(self, code: str) -> str:
        """Convert SEC transaction codes to readable types"""
        code_map = {
            'A': 'BUY', 'D': 'SELL', 'P': 'BUY', 'S': 'SELL',
            'M': 'OPTION_EXERCISE', 'F': 'TAX_WITHHOLDING',
            'G': 'GIFT', 'V': 'OTHER', 'J': 'OTHER', 'K': 'OTHER', 'W': 'OTHER'
        }
        return code_map.get(code.upper(), 'OTHER')
    
    def save_transaction_to_db(self, transaction_data: Dict) -> bool:
        """Save parsed transaction to database"""
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
            
            if existing_trade:
                return True  # Already exists
            
            # Create new trade
            trade = Trade(
                trader_id=trader.trader_id,
                company_ticker=transaction_data['ticker'],
                transaction_date=transaction_data['transaction_date'],
                transaction_type=transaction_data['transaction_type'],
                shares_traded=Decimal(str(transaction_data['shares'])),
                price_per_share=Decimal(str(transaction_data['price_per_share'])),
                total_value=Decimal(str(transaction_data['total_value'])),
                form_type='Form 4',
                filing_date=datetime.now().date()
            )
            
            self.db.add(trade)
            trader.total_trades = self.db.query(Trade).filter(
                Trade.trader_id == trader.trader_id
            ).count() + 1
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving transaction: {e}")
            self.db.rollback()
            return False
    
    def run_comprehensive_ingestion(self, historical_years: int = 2, recent_days: int = 90):
        """Run comprehensive SEC EDGAR ingestion"""
        logger.info("Starting comprehensive SEC EDGAR Form 4 ingestion...")
        logger.info(f"Historical data: {historical_years} years, Recent data: {recent_days} days")
        
        total_processed = 0
        total_successful = 0
        
        try:
            # 1. Get comprehensive company list
            company_list = self.get_company_cik_list()
            
            # 2. Focus on major companies first (top 100 by market cap)
            priority_tickers = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-A', 'UNH', 'JNJ',
                'XOM', 'JPM', 'V', 'PG', 'HD', 'CVX', 'MA', 'PFE', 'ABBV', 'BAC',
                'COST', 'DIS', 'KO', 'ADBE', 'WMT', 'CRM', 'MRK', 'TMO', 'NFLX', 'ACN',
                'LLY', 'NKE', 'MDT', 'UPS', 'NEE', 'ORCL', 'DHR', 'VZ', 'QCOM', 'TXN'
            ]
            
            # 3. Process historical data for priority companies
            logger.info("Processing historical data for priority companies...")
            for ticker in priority_tickers:
                if ticker in company_list:
                    cik = company_list[ticker]
                    historical_filings = self.get_historical_form4_filings(cik, ticker, historical_years)
                    
                    if historical_filings:
                        # Process in batches
                        batch_size = 50
                        for i in range(0, len(historical_filings), batch_size):
                            batch = historical_filings[i:i + batch_size]
                            successful = self.process_filing_batch(batch)
                            total_processed += len(batch)
                            total_successful += successful
                            
                            logger.info(f"Processed {i + len(batch)}/{len(historical_filings)} filings for {ticker}")
            
            # 4. Get comprehensive recent filings
            logger.info("Processing comprehensive recent filings...")
            recent_filings = self.get_recent_form4_filings_comprehensive(recent_days)
            
            if recent_filings:
                # Process in batches
                batch_size = 100
                for i in range(0, len(recent_filings), batch_size):
                    batch = recent_filings[i:i + batch_size]
                    successful = self.process_filing_batch(batch)
                    total_processed += len(batch)
                    total_successful += successful
                    
                    logger.info(f"Processed {i + len(batch)}/{len(recent_filings)} recent filings")
            
            logger.info(f"Comprehensive ingestion complete: {total_successful}/{total_processed} transactions processed successfully")
            logger.info(f"Total SEC requests made: {self.request_count}")
            
        except Exception as e:
            logger.error(f"Error in comprehensive ingestion: {e}")

def main():
    """Main function to run comprehensive SEC EDGAR ingestion"""
    try:
        ingestion = ComprehensiveSECIngestion()
        
        # Run comprehensive ingestion
        # Historical: 2 years, Recent: 90 days
        ingestion.run_comprehensive_ingestion(historical_years=2, recent_days=90)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
