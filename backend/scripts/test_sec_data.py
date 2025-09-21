"""
Test script to create realistic insider trading data based on recent SEC patterns
"""

import os
import sys
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict
import random

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECTestData:
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def create_realistic_sec_data(self):
        """
        Create realistic insider trading data based on actual SEC Form 4 patterns
        """
        logger.info("Creating realistic SEC-based insider trading data...")
        
        # Real companies and their recent insider activity patterns
        companies_data = [
            {
                'name': 'Apple Inc.',
                'ticker': 'AAPL',
                'current_price': 245.50,
                'insiders': [
                    {'name': 'Timothy D. Cook', 'title': 'Chief Executive Officer'},
                    {'name': 'Luca Maestri', 'title': 'Chief Financial Officer'},
                    {'name': 'Katherine L. Adams', 'title': 'General Counsel'},
                    {'name': 'Deirdre O\'Brien', 'title': 'Senior Vice President'}
                ]
            },
            {
                'name': 'Microsoft Corporation', 
                'ticker': 'MSFT',
                'current_price': 517.93,
                'insiders': [
                    {'name': 'Satya Nadella', 'title': 'Chief Executive Officer'},
                    {'name': 'Amy E. Hood', 'title': 'Chief Financial Officer'},
                    {'name': 'Bradford L. Smith', 'title': 'President'},
                    {'name': 'Christopher C. Capossela', 'title': 'Chief Marketing Officer'}
                ]
            },
            {
                'name': 'NVIDIA Corporation',
                'ticker': 'NVDA', 
                'current_price': 176.67,
                'insiders': [
                    {'name': 'Jensen Huang', 'title': 'Chief Executive Officer'},
                    {'name': 'Colette M. Kress', 'title': 'Chief Financial Officer'},
                    {'name': 'Ajay K. Puri', 'title': 'Executive Vice President'},
                    {'name': 'Debora Shoquist', 'title': 'Executive Vice President'}
                ]
            },
            {
                'name': 'Tesla, Inc.',
                'ticker': 'TSLA',
                'current_price': 385.00,
                'insiders': [
                    {'name': 'Elon Musk', 'title': 'Chief Executive Officer'},
                    {'name': 'Zachary Kirkhorn', 'title': 'Chief Financial Officer'},
                    {'name': 'Drew Baglino', 'title': 'Senior Vice President'},
                    {'name': 'Vaibhav Taneja', 'title': 'Chief Accounting Officer'}
                ]
            },
            {
                'name': 'Amazon.com, Inc.',
                'ticker': 'AMZN',
                'current_price': 231.48,
                'insiders': [
                    {'name': 'Andrew R. Jassy', 'title': 'Chief Executive Officer'},
                    {'name': 'Brian T. Olsavsky', 'title': 'Chief Financial Officer'},
                    {'name': 'David A. Zapolsky', 'title': 'General Counsel'},
                    {'name': 'Shelley Reynolds', 'title': 'Vice President'}
                ]
            }
        ]
        
        total_trades_created = 0
        
        for company in companies_data:
            logger.info(f"Creating trades for {company['name']} ({company['ticker']})")
            
            for insider in company['insiders']:
                # Create or get trader
                trader = self.db.query(Trader).filter(
                    Trader.name == insider['name'],
                    Trader.company_ticker == company['ticker']
                ).first()
                
                if not trader:
                    trader = Trader(
                        name=insider['name'],
                        title=insider['title'],
                        company_ticker=company['ticker'],
                        company_name=company['name'],
                        relationship_to_company=insider['title']
                    )
                    self.db.add(trader)
                    self.db.flush()
                
                # Create realistic trades over the past year
                num_trades = random.randint(2, 12)  # 2-12 trades per insider per year
                
                for i in range(num_trades):
                    # Random date in past year
                    days_back = random.randint(1, 365)
                    trade_date = datetime.now().date() - timedelta(days=days_back)
                    
                    # Realistic transaction patterns
                    # CEOs and high-level execs tend to have larger, less frequent trades
                    if 'Chief Executive' in insider['title'] or 'CEO' in insider['title']:
                        shares_range = (5000, 50000)
                        price_variance = 0.15  # ±15% from current price
                    elif 'Chief Financial' in insider['title'] or 'CFO' in insider['title']:
                        shares_range = (2000, 25000) 
                        price_variance = 0.12
                    else:
                        shares_range = (1000, 15000)
                        price_variance = 0.10
                    
                    shares = random.randint(*shares_range)
                    
                    # Price at time of trade (historical simulation)
                    current_price = company['current_price']
                    # Simulate price was different in the past
                    price_multiplier = random.uniform(1 - price_variance, 1 + price_variance)
                    trade_price = current_price * price_multiplier
                    
                    # Transaction type - mostly acquisitions (buys) for executives
                    transaction_types = ['BUY', 'BUY', 'BUY', 'SELL', 'OPTION_EXERCISE']
                    transaction_type = random.choice(transaction_types)
                    
                    # Adjust shares for sells (usually smaller)
                    if transaction_type == 'SELL':
                        shares = int(shares * random.uniform(0.3, 0.8))
                    
                    total_value = shares * trade_price
                    
                    # Check if similar trade exists
                    existing = self.db.query(Trade).filter(
                        Trade.trader_id == trader.trader_id,
                        Trade.transaction_date == trade_date
                    ).first()
                    
                    if not existing:
                        trade = Trade(
                            trader_id=trader.trader_id,
                            company_ticker=company['ticker'],
                            transaction_date=trade_date,
                            transaction_type=transaction_type,
                            shares_traded=Decimal(str(shares)),
                            price_per_share=Decimal(str(round(trade_price, 2))),
                            total_value=Decimal(str(round(total_value, 2))),
                            current_price=Decimal(str(current_price)),
                            form_type='Form 4',
                            filing_date=trade_date + timedelta(days=random.randint(1, 4))
                        )
                        
                        self.db.add(trade)
                        total_trades_created += 1
                
                # Update trader's trade count
                trader.total_trades = self.db.query(Trade).filter(
                    Trade.trader_id == trader.trader_id
                ).count()
        
        self.db.commit()
        logger.info(f"Created {total_trades_created} realistic insider trades")
        return total_trades_created

def main():
    """
    Main function to create test SEC data
    """
    try:
        test_data = SECTestData()
        trades_created = test_data.create_realistic_sec_data()
        
        print(f"\n🎉 Successfully created {trades_created} realistic insider trades!")
        print("This data simulates real SEC Form 4 filings with:")
        print("✅ Real company names and tickers")
        print("✅ Actual executive names and titles")
        print("✅ Realistic trade sizes and patterns")
        print("✅ Historical price variations")
        print("✅ Proper transaction types")
        print("\nRun performance calculations to see the results!")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
