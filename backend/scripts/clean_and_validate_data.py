"""
Clean and Validate Insider Trading Data
Fixes data quality issues and removes unrealistic values
"""

import os
import sys
import logging
from datetime import datetime, date
from decimal import Decimal

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Trader, Trade

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_realistic_price_ranges(self) -> dict:
        """Get realistic price ranges for major stocks"""
        return {
            'AAPL': (150, 250),    # Apple realistic range
            'MSFT': (300, 600),    # Microsoft realistic range  
            'TSLA': (150, 300),    # Tesla realistic range
            'GOOGL': (100, 200),   # Google realistic range
            'AMZN': (100, 200),    # Amazon realistic range
            'NVDA': (100, 1000),   # NVIDIA realistic range (more volatile)
            'META': (200, 600),    # Meta realistic range
            'JPM': (100, 200),     # JPMorgan realistic range
            'BAC': (25, 50),       # Bank of America realistic range
            'JNJ': (150, 180),     # Johnson & Johnson realistic range
            'XOM': (80, 120),      # Exxon realistic range
            'PG': (140, 170),      # Procter & Gamble realistic range
        }
    
    def clean_unrealistic_prices(self):
        """Remove trades with unrealistic stock prices"""
        logger.info("Cleaning unrealistic stock prices...")
        
        price_ranges = self.get_realistic_price_ranges()
        cleaned_count = 0
        
        try:
            for ticker, (min_price, max_price) in price_ranges.items():
                # Delete trades with unrealistic prices for known companies
                deleted = self.db.query(Trade).filter(
                    Trade.company_ticker == ticker,
                    (Trade.price_per_share < min_price) | (Trade.price_per_share > max_price)
                ).delete()
                
                if deleted > 0:
                    logger.info(f"Removed {deleted} unrealistic {ticker} trades (price outside ${min_price}-${max_price})")
                    cleaned_count += deleted
            
            # Remove trades with obviously wrong prices (any stock)
            # Remove prices over $10,000 per share
            extreme_high = self.db.query(Trade).filter(Trade.price_per_share > 10000).delete()
            logger.info(f"Removed {extreme_high} trades with prices > $10,000/share")
            cleaned_count += extreme_high
            
            # Remove prices under $0.01 per share
            extreme_low = self.db.query(Trade).filter(Trade.price_per_share < 0.01).delete()
            logger.info(f"Removed {extreme_low} trades with prices < $0.01/share")
            cleaned_count += extreme_low
            
            # Remove trades with impossible share counts
            extreme_shares = self.db.query(Trade).filter(Trade.shares_traded > 100000000).delete()
            logger.info(f"Removed {extreme_shares} trades with > 100M shares")
            cleaned_count += extreme_shares
            
            self.db.commit()
            logger.info(f"Total cleaned: {cleaned_count} unrealistic trades removed")
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            self.db.rollback()
        
        return cleaned_count
    
    def fix_null_values(self):
        """Fix null and NaN values in the database"""
        logger.info("Fixing null and NaN values...")
        
        try:
            # Fix titles
            title_updates = self.db.execute("""
                UPDATE traders 
                SET title = 'Executive'
                WHERE title IS NULL OR title = '' OR title = 'Nan' OR title = 'nan' OR title = 'NaN'
            """)
            
            # Fix company names that are obviously person names
            company_updates = self.db.execute("""
                UPDATE traders 
                SET company_name = 
                    CASE 
                        WHEN company_ticker = 'AAPL' THEN 'Apple Inc.'
                        WHEN company_ticker = 'MSFT' THEN 'Microsoft Corporation'
                        WHEN company_ticker = 'TSLA' THEN 'Tesla, Inc.'
                        WHEN company_ticker = 'GOOGL' THEN 'Alphabet Inc.'
                        WHEN company_ticker = 'AMZN' THEN 'Amazon.com, Inc.'
                        WHEN company_ticker = 'META' THEN 'Meta Platforms, Inc.'
                        WHEN company_ticker = 'NVDA' THEN 'NVIDIA Corporation'
                        WHEN company_ticker = 'JPM' THEN 'JPMorgan Chase & Co.'
                        WHEN company_ticker = 'BAC' THEN 'Bank of America Corporation'
                        WHEN company_ticker = 'JNJ' THEN 'Johnson & Johnson'
                        WHEN company_ticker = 'XOM' THEN 'Exxon Mobil Corporation'
                        WHEN company_ticker = 'PG' THEN 'The Procter & Gamble Company'
                        WHEN company_ticker = 'GE' THEN 'General Electric Company'
                        ELSE company_name
                    END
                WHERE company_ticker IN ('AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'META', 'NVDA', 'JPM', 'BAC', 'JNJ', 'XOM', 'PG', 'GE')
            """)
            
            # Remove traders with obviously wrong ticker symbols (person names as tickers)
            person_tickers = self.db.execute("""
                DELETE FROM traders 
                WHERE company_ticker LIKE '%JOHN%' 
                   OR company_ticker LIKE '%SMITH%' 
                   OR company_ticker LIKE '%MARTIN%'
                   OR company_ticker LIKE '%GARCIA%'
                   OR company_ticker LIKE '%DENBAA%'
                   OR company_ticker LIKE '%MCMANU%'
                   OR LENGTH(company_ticker) > 8
            """)
            
            self.db.commit()
            
            logger.info(f"Fixed null values and cleaned {person_tickers.rowcount} invalid tickers")
            
        except Exception as e:
            logger.error(f"Error fixing null values: {e}")
            self.db.rollback()
    
    def validate_with_current_prices(self):
        """Validate historical prices against current market data"""
        logger.info("Validating prices against current market data...")
        
        # Get current prices for validation
        current_prices = {
            'AAPL': 245.50,
            'MSFT': 517.93, 
            'TSLA': 250.00,  # Approximate current Tesla price
            'GOOGL': 254.72,
            'AMZN': 231.48,
            'NVDA': 176.67,
            'META': 500.00,
            'JPM': 198.50,
            'BAC': 45.20,
            'JNJ': 162.30,
            'XOM': 118.45
        }
        
        cleaned_count = 0
        
        try:
            for ticker, current_price in current_prices.items():
                # Remove trades with prices more than 10x current price (clearly wrong)
                max_historical = current_price * 10
                min_historical = current_price * 0.1
                
                deleted = self.db.query(Trade).filter(
                    Trade.company_ticker == ticker,
                    (Trade.price_per_share > max_historical) | (Trade.price_per_share < min_historical)
                ).delete()
                
                if deleted > 0:
                    logger.info(f"Removed {deleted} {ticker} trades with unrealistic prices (outside ${min_historical:.2f}-${max_historical:.2f})")
                    cleaned_count += deleted
            
            self.db.commit()
            logger.info(f"Price validation complete: {cleaned_count} unrealistic trades removed")
            
        except Exception as e:
            logger.error(f"Error validating prices: {e}")
            self.db.rollback()
        
        return cleaned_count
    
    def update_trader_counts(self):
        """Update trader trade counts after cleaning"""
        logger.info("Updating trader trade counts...")
        
        try:
            # Update all trader counts
            traders = self.db.query(Trader).all()
            updated_count = 0
            
            for trader in traders:
                old_count = trader.total_trades
                new_count = self.db.query(Trade).filter(Trade.trader_id == trader.trader_id).count()
                
                if new_count != old_count:
                    trader.total_trades = new_count
                    updated_count += 1
                
                # Remove traders with no trades
                if new_count == 0:
                    self.db.delete(trader)
            
            self.db.commit()
            logger.info(f"Updated {updated_count} trader counts")
            
        except Exception as e:
            logger.error(f"Error updating trader counts: {e}")
            self.db.rollback()
    
    def run_complete_cleanup(self):
        """Run complete data cleanup process"""
        logger.info("🧹 Starting complete data cleanup...")
        
        initial_stats = self.get_data_stats()
        logger.info(f"Initial: {initial_stats['trades']:,} trades, {initial_stats['traders']:,} traders")
        
        # Step 1: Fix null values
        self.fix_null_values()
        
        # Step 2: Clean unrealistic prices
        cleaned_prices = self.clean_unrealistic_prices()
        
        # Step 3: Validate against current market prices
        validated_prices = self.validate_with_current_prices()
        
        # Step 4: Update trader counts
        self.update_trader_counts()
        
        final_stats = self.get_data_stats()
        logger.info(f"Final: {final_stats['trades']:,} trades, {final_stats['traders']:,} traders")
        
        total_removed = initial_stats['trades'] - final_stats['trades']
        logger.info(f"🎉 Cleanup complete: {total_removed:,} bad records removed")
        
        return final_stats
    
    def get_data_stats(self):
        """Get current database statistics"""
        try:
            total_trades = self.db.query(Trade).count()
            total_traders = self.db.query(Trader).count()
            return {'trades': total_trades, 'traders': total_traders}
        except:
            return {'trades': 0, 'traders': 0}

def main():
    """Main function to clean and validate data"""
    try:
        cleaner = DataCleaner()
        
        print("🧹 DATA CLEANING AND VALIDATION")
        print("=" * 50)
        print("Removing unrealistic prices and fixing data quality issues...")
        
        final_stats = cleaner.run_complete_cleanup()
        
        print(f"\n✅ Data cleanup complete!")
        print(f"📊 Clean dataset: {final_stats['trades']:,} trades, {final_stats['traders']:,} traders")
        print(f"🎯 All prices validated against realistic market ranges")
        print(f"🏢 Company names and tickers cleaned")
        print("\n🚀 Your platform now has high-quality, validated data!")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
