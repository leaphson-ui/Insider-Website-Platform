"""
Data ingestion script for fetching insider trading data from Polygon.io
"""

import os
import sys
import requests
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional

# Add the app directory to the path so we can import our models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import Trader, Trade, Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PolygonDataIngestion:
    def __init__(self):
        self.api_key = os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY environment variable is required")
        
        self.base_url = "https://api.polygon.io"
        self.session = requests.Session()
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def fetch_insider_trades(self, ticker: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Fetch insider trading data from Polygon.io
        
        Args:
            ticker: Optional stock ticker to filter by
            limit: Number of records to fetch (max 1000)
        
        Returns:
            List of insider trading records
        """
        try:
            # Polygon.io insider trading endpoint
            url = f"{self.base_url}/vX/reference/insider-transactions"
            
            params = {
                'apikey': self.api_key,
                'limit': min(limit, 1000)  # Polygon.io max limit
            }
            
            if ticker:
                params['ticker'] = ticker
            
            logger.info(f"Fetching insider trades from Polygon.io (ticker={ticker}, limit={limit})")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK' and 'results' in data:
                logger.info(f"Successfully fetched {len(data['results'])} insider trades")
                return data['results']
            else:
                logger.warning(f"No insider trades found or API error: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching insider trades: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in fetch_insider_trades: {e}")
            return []
    
    def process_insider_trade(self, trade_data: Dict) -> bool:
        """
        Process a single insider trade record and save to database
        
        Args:
            trade_data: Raw trade data from Polygon.io
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract trade information
            ticker = trade_data.get('ticker', '').upper()
            insider_name = trade_data.get('owner_name', 'Unknown')
            insider_title = trade_data.get('owner_title', '')
            company_name = trade_data.get('company_name', '')
            
            transaction_date = trade_data.get('transaction_date')
            if transaction_date:
                transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
            else:
                logger.warning(f"No transaction date for trade: {trade_data}")
                return False
            
            transaction_type = trade_data.get('transaction_code', 'Unknown')
            shares = Decimal(str(trade_data.get('transaction_shares', 0)))
            price = Decimal(str(trade_data.get('transaction_price_per_share', 0)))
            total_value = shares * price
            
            filing_date = trade_data.get('filing_date')
            if filing_date:
                filing_date = datetime.strptime(filing_date, '%Y-%m-%d').date()
            
            # Find or create trader
            trader = self.db.query(Trader).filter(
                Trader.name == insider_name,
                Trader.company_ticker == ticker
            ).first()
            
            if not trader:
                trader = Trader(
                    name=insider_name,
                    title=insider_title,
                    company_ticker=ticker,
                    company_name=company_name,
                    relationship_to_company=insider_title
                )
                self.db.add(trader)
                self.db.flush()  # Get the trader_id
                logger.info(f"Created new trader: {insider_name} ({ticker})")
            
            # Check if trade already exists
            existing_trade = self.db.query(Trade).filter(
                Trade.trader_id == trader.trader_id,
                Trade.transaction_date == transaction_date,
                Trade.shares_traded == shares,
                Trade.price_per_share == price
            ).first()
            
            if existing_trade:
                logger.debug(f"Trade already exists for {insider_name} on {transaction_date}")
                return True
            
            # Create new trade record
            trade = Trade(
                trader_id=trader.trader_id,
                company_ticker=ticker,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                shares_traded=shares,
                price_per_share=price,
                total_value=total_value,
                filing_date=filing_date
            )
            
            self.db.add(trade)
            
            # Update trader's total trades count
            trader.total_trades = self.db.query(Trade).filter(
                Trade.trader_id == trader.trader_id
            ).count() + 1
            
            self.db.commit()
            logger.info(f"Saved trade: {insider_name} {transaction_type} {shares} shares of {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing trade: {e}")
            self.db.rollback()
            return False
    
    def get_current_stock_price(self, ticker: str) -> Optional[Decimal]:
        """
        Get current stock price from Polygon.io
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Current stock price or None if not available
        """
        try:
            url = f"{self.base_url}/v2/aggs/ticker/{ticker}/prev"
            params = {'apikey': self.api_key}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK' and 'results' in data and data['results']:
                close_price = data['results'][0].get('c')  # closing price
                if close_price:
                    return Decimal(str(close_price))
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {e}")
            return None
    
    def run_ingestion(self, tickers: Optional[List[str]] = None, limit: int = 100):
        """
        Run the full data ingestion process
        
        Args:
            tickers: Optional list of tickers to focus on
            limit: Number of records to fetch per ticker
        """
        logger.info("Starting insider trading data ingestion...")
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        total_processed = 0
        total_successful = 0
        
        if tickers:
            # Fetch data for specific tickers
            for ticker in tickers:
                trades_data = self.fetch_insider_trades(ticker=ticker, limit=limit)
                for trade_data in trades_data:
                    total_processed += 1
                    if self.process_insider_trade(trade_data):
                        total_successful += 1
        else:
            # Fetch general insider trading data
            trades_data = self.fetch_insider_trades(limit=limit)
            for trade_data in trades_data:
                total_processed += 1
                if self.process_insider_trade(trade_data):
                    total_successful += 1
        
        logger.info(f"Ingestion complete: {total_successful}/{total_processed} trades processed successfully")

def main():
    """
    Main function to run the data ingestion
    """
    try:
        ingestion = PolygonDataIngestion()
        
        # For MVP, let's focus on some popular tickers
        popular_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
        
        ingestion.run_ingestion(tickers=popular_tickers, limit=50)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
