"""
Alternative data sources for insider trading data
"""

import os
import sys
import requests
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Optional
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlternativeDataIngestion:
    def __init__(self):
        self.db = SessionLocal()
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def fetch_sec_edgar_data(self) -> List[Dict]:
        """
        Fetch insider trading data directly from SEC EDGAR
        This is free but requires more processing
        """
        logger.info("Fetching data from SEC EDGAR...")
        
        # SEC EDGAR RSS feed for recent filings
        try:
            # Recent Form 4 filings
            url = "https://www.sec.gov/cgi-bin/browse-edgar"
            params = {
                'action': 'getcurrent',
                'type': 'form4',
                'count': '40',
                'output': 'atom'
            }
            
            headers = {
                'User-Agent': 'Insider Alpha Platform contact@insideralpha.com'  # SEC requires User-Agent
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            logger.info("Successfully fetched SEC EDGAR data")
            # This would require XML parsing - for now return empty
            return []
            
        except Exception as e:
            logger.error(f"Error fetching SEC EDGAR data: {e}")
            return []
    
    def create_more_sample_data(self) -> bool:
        """
        Create more realistic sample data based on recent insider activity patterns
        """
        logger.info("Creating expanded sample dataset...")
        
        try:
            # More comprehensive sample data
            sample_insiders = [
                # Tech CEOs
                {'name': 'Tim Cook', 'title': 'CEO', 'ticker': 'AAPL', 'company': 'Apple Inc.'},
                {'name': 'Satya Nadella', 'title': 'CEO', 'ticker': 'MSFT', 'company': 'Microsoft Corporation'},
                {'name': 'Jensen Huang', 'title': 'CEO', 'ticker': 'NVDA', 'company': 'NVIDIA Corporation'},
                {'name': 'Sundar Pichai', 'title': 'CEO', 'ticker': 'GOOGL', 'company': 'Alphabet Inc.'},
                {'name': 'Andy Jassy', 'title': 'CEO', 'ticker': 'AMZN', 'company': 'Amazon.com Inc.'},
                
                # CFOs and other executives
                {'name': 'Luca Maestri', 'title': 'CFO', 'ticker': 'AAPL', 'company': 'Apple Inc.'},
                {'name': 'Amy Hood', 'title': 'CFO', 'ticker': 'MSFT', 'company': 'Microsoft Corporation'},
                {'name': 'Colette Kress', 'title': 'CFO', 'ticker': 'NVDA', 'company': 'NVIDIA Corporation'},
                {'name': 'Ruth Porat', 'title': 'CFO', 'ticker': 'GOOGL', 'company': 'Alphabet Inc.'},
                {'name': 'Brian Olsavsky', 'title': 'CFO', 'ticker': 'AMZN', 'company': 'Amazon.com Inc.'},
            ]
            
            # Sample stock prices (approximate current prices)
            current_prices = {
                'AAPL': 225.00,
                'MSFT': 420.00, 
                'NVDA': 875.00,
                'GOOGL': 140.00,
                'AMZN': 145.00
            }
            
            trader_id = 1
            
            for insider in sample_insiders:
                # Create or update trader
                trader = self.db.query(Trader).filter(
                    Trader.name == insider['name'],
                    Trader.company_ticker == insider['ticker']
                ).first()
                
                if not trader:
                    trader = Trader(
                        name=insider['name'],
                        title=insider['title'],
                        company_ticker=insider['ticker'],
                        company_name=insider['company'],
                        relationship_to_company=insider['title']
                    )
                    self.db.add(trader)
                    self.db.flush()
                
                # Create multiple trades for each insider (last 6 months)
                base_date = datetime.now().date() - timedelta(days=180)
                current_price = current_prices[insider['ticker']]
                
                # Generate 3-8 trades per insider
                import random
                num_trades = random.randint(3, 8)
                
                for i in range(num_trades):
                    # Random date in last 6 months
                    days_offset = random.randint(0, 180)
                    trade_date = base_date + timedelta(days=days_offset)
                    
                    # Random trade type (80% BUY, 20% SELL)
                    trade_type = 'BUY' if random.random() < 0.8 else 'SELL'
                    
                    # Random shares (1000-50000)
                    shares = random.randint(1000, 50000)
                    
                    # Price at time of trade (varies from current price)
                    price_variation = random.uniform(0.7, 1.3)  # ±30% from current
                    trade_price = current_price * price_variation
                    
                    # Total value
                    total_value = shares * trade_price
                    
                    # Check if trade already exists
                    existing = self.db.query(Trade).filter(
                        Trade.trader_id == trader.trader_id,
                        Trade.transaction_date == trade_date,
                        Trade.shares_traded == shares
                    ).first()
                    
                    if not existing:
                        trade = Trade(
                            trader_id=trader.trader_id,
                            company_ticker=insider['ticker'],
                            transaction_date=trade_date,
                            transaction_type=trade_type,
                            shares_traded=Decimal(str(shares)),
                            price_per_share=Decimal(str(round(trade_price, 2))),
                            total_value=Decimal(str(round(total_value, 2))),
                            current_price=Decimal(str(current_price)),
                            filing_date=trade_date + timedelta(days=random.randint(1, 4))
                        )
                        self.db.add(trade)
                
                trader_id += 1
            
            self.db.commit()
            logger.info(f"Created sample data for {len(sample_insiders)} insiders")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sample data: {e}")
            self.db.rollback()
            return False
    
    def get_real_stock_prices(self) -> Dict[str, float]:
        """
        Get current stock prices using Polygon.io (this should work with your API key)
        """
        logger.info("Fetching current stock prices...")
        
        tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN']
        prices = {}
        
        for ticker in tickers:
            try:
                url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
                params = {'apikey': self.polygon_api_key}
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get('status') == 'OK' and 'results' in data and data['results']:
                    close_price = data['results'][0].get('c')  # closing price
                    if close_price:
                        prices[ticker] = float(close_price)
                        logger.info(f"Got price for {ticker}: ${close_price}")
                
            except Exception as e:
                logger.error(f"Error fetching price for {ticker}: {e}")
        
        return prices
    
    def run_alternative_ingestion(self):
        """
        Run the alternative data ingestion process
        """
        logger.info("Starting alternative data ingestion...")
        
        # Method 1: Try to get real stock prices
        real_prices = self.get_real_stock_prices()
        if real_prices:
            logger.info(f"Successfully fetched {len(real_prices)} real stock prices")
        
        # Method 2: Create comprehensive sample data
        success = self.create_more_sample_data()
        
        if success:
            logger.info("Alternative data ingestion completed successfully")
        else:
            logger.error("Alternative data ingestion failed")

def main():
    """
    Main function to run alternative data ingestion
    """
    try:
        ingestion = AlternativeDataIngestion()
        ingestion.run_alternative_ingestion()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


