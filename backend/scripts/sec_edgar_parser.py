"""
SEC EDGAR Form 4 Parser - Free insider trading data directly from SEC
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

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECEdgarParser:
    def __init__(self):
        self.db = SessionLocal()
        self.session = requests.Session()
        # SEC requires a User-Agent header with company specific information
        self.session.headers.update({
            'User-Agent': 'Insider Alpha Platform (admin@insideralpha.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
        self.base_url = "https://www.sec.gov"
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_recent_form4_filings(self, days_back: int = 7) -> List[Dict]:
        """
        Get recent Form 4 filings from SEC EDGAR RSS feed
        """
        logger.info(f"Fetching Form 4 filings from last {days_back} days...")
        
        try:
            # SEC EDGAR RSS feed for recent Form 4 filings
            rss_url = "https://www.sec.gov/cgi-bin/browse-edgar"
            params = {
                'action': 'getcurrent',
                'type': 'form4',
                'count': '100',  # Get last 100 Form 4s
                'output': 'atom'
            }
            
            response = self.session.get(rss_url, params=params)
            response.raise_for_status()
            
            # Parse the Atom feed
            filings = self.parse_atom_feed(response.content)
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_filings = [
                filing for filing in filings 
                if filing.get('date') and filing['date'] > cutoff_date
            ]
            
            logger.info(f"Found {len(recent_filings)} recent Form 4 filings")
            return recent_filings
            
        except Exception as e:
            logger.error(f"Error fetching Form 4 filings: {e}")
            return []
    
    def parse_atom_feed(self, atom_content: bytes) -> List[Dict]:
        """
        Parse SEC EDGAR Atom feed to extract filing information
        """
        filings = []
        
        try:
            # Parse the XML
            root = ET.fromstring(atom_content)
            
            # Define namespaces
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom'
            }
            
            # Extract entries
            entries = root.findall('.//atom:entry', namespaces)
            
            for entry in entries:
                try:
                    # Extract basic info
                    title_elem = entry.find('atom:title', namespaces)
                    link_elem = entry.find('atom:link', namespaces)
                    updated_elem = entry.find('atom:updated', namespaces)
                    
                    if title_elem is not None and link_elem is not None:
                        title = title_elem.text or ""
                        link = link_elem.get('href', '')
                        
                        # Parse date
                        filing_date = None
                        if updated_elem is not None:
                            try:
                                date_str = updated_elem.text
                                filing_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        # Extract company and person from title
                        # Title format is usually: "4 - [Company Name] (Ticker) - [Person Name]"
                        company_match = re.search(r'4\s*-\s*(.+?)\s*\(([A-Z]+)\)', title)
                        
                        if company_match:
                            company_name = company_match.group(1).strip()
                            ticker = company_match.group(2).strip()
                            
                            # Try to extract person name (after the ticker)
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
    
    def parse_form4_document(self, filing_url: str) -> List[Dict]:
        """
        Parse individual Form 4 document to extract transaction details
        """
        logger.debug(f"Parsing Form 4: {filing_url}")
        
        try:
            # SEC allows max 10 requests per second, so wait 0.2 seconds between requests
            time.sleep(0.2)
            
            response = self.session.get(filing_url)
            response.raise_for_status()
            
            # The URL might redirect to an HTML page, we need the actual XML
            # Look for links to the actual Form 4 XML file
            content = response.text
            
            # Find XML document link
            xml_match = re.search(r'href="([^"]*\.xml)"', content)
            if xml_match:
                xml_url = xml_match.group(1)
                if xml_url.startswith('/'):
                    xml_url = f"{self.base_url}{xml_url}"
                
                # Fetch the actual XML  
                time.sleep(0.2)  # SEC rate limit compliance
                xml_response = self.session.get(xml_url)
                xml_response.raise_for_status()
                
                return self.parse_form4_xml(xml_response.content)
            
            return []
            
        except Exception as e:
            logger.error(f"Error parsing Form 4 document {filing_url}: {e}")
            return []
    
    def parse_form4_xml(self, xml_content: bytes) -> List[Dict]:
        """
        Parse Form 4 XML content to extract transaction data
        """
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
            logger.error(f"Error parsing Form 4 XML: {e}")
            return []
    
    def extract_transaction_data(self, transaction_elem, company_name: str, 
                               ticker: str, owner_name: str, owner_title: str) -> Optional[Dict]:
        """
        Extract transaction data from XML element
        """
        try:
            # Transaction date
            date_elem = transaction_elem.find('.//transactionDate/value')
            if date_elem is None:
                return None
            
            transaction_date = datetime.strptime(date_elem.text, '%Y-%m-%d').date()
            
            # Transaction code (A=Acquisition, D=Disposition, etc.)
            code_elem = transaction_elem.find('.//transactionCode')
            transaction_code = code_elem.text if code_elem is not None else ""
            
            # Convert code to readable type
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
            
            # Total value
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
        """
        Convert SEC transaction codes to readable types
        """
        code_map = {
            'A': 'BUY',
            'D': 'SELL', 
            'P': 'BUY',
            'S': 'SELL',
            'M': 'OPTION_EXERCISE',
            'F': 'TAX_WITHHOLDING',
            'G': 'GIFT',
            'V': 'OTHER',
            'J': 'OTHER',
            'K': 'OTHER',
            'W': 'OTHER'
        }
        
        return code_map.get(code.upper(), 'OTHER')
    
    def save_transaction_to_db(self, transaction_data: Dict) -> bool:
        """
        Save parsed transaction to database
        """
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
                logger.info(f"Created new trader: {transaction_data['owner_name']} ({transaction_data['ticker']})")
            
            # Check if trade already exists
            existing_trade = self.db.query(Trade).filter(
                Trade.trader_id == trader.trader_id,
                Trade.transaction_date == transaction_data['transaction_date'],
                Trade.shares_traded == Decimal(str(transaction_data['shares'])),
                Trade.price_per_share == Decimal(str(transaction_data['price_per_share']))
            ).first()
            
            if existing_trade:
                logger.debug(f"Trade already exists for {transaction_data['owner_name']} on {transaction_data['transaction_date']}")
                return True
            
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
            
            # Update trader trade count
            trader.total_trades = self.db.query(Trade).filter(
                Trade.trader_id == trader.trader_id
            ).count() + 1
            
            self.db.commit()
            logger.info(f"Saved trade: {transaction_data['owner_name']} {transaction_data['transaction_type']} {transaction_data['shares']} shares of {transaction_data['ticker']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving transaction: {e}")
            self.db.rollback()
            return False
    
    def run_sec_ingestion(self, days_back: int = 7):
        """
        Run the full SEC EDGAR ingestion process
        """
        logger.info("Starting SEC EDGAR Form 4 ingestion...")
        
        total_processed = 0
        total_successful = 0
        
        try:
            # Get recent Form 4 filings
            filings = self.get_recent_form4_filings(days_back)
            
            for filing in filings[:20]:  # Limit to first 20 for testing
                logger.info(f"Processing: {filing['person_name']} at {filing['company_name']} ({filing['ticker']})")
                
                # Parse the Form 4 document
                transactions = self.parse_form4_document(filing['link'])
                
                for transaction in transactions:
                    total_processed += 1
                    if self.save_transaction_to_db(transaction):
                        total_successful += 1
                
                # Be respectful to SEC servers
                time.sleep(0.5)
            
            logger.info(f"SEC ingestion complete: {total_successful}/{total_processed} transactions processed successfully")
            
        except Exception as e:
            logger.error(f"Error in SEC ingestion: {e}")

def main():
    """
    Main function to run SEC EDGAR parsing
    """
    try:
        parser = SECEdgarParser()
        parser.run_sec_ingestion(days_back=7)  # Get last 7 days of Form 4s
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
