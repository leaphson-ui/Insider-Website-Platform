"""
Performance calculation engine for analyzing insider trading returns
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine
from app.models import Trader, Trade
from data_ingestion import PolygonDataIngestion
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceCalculator:
    def __init__(self):
        self.db = SessionLocal()
        self.polygon_client = PolygonDataIngestion()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def calculate_trade_returns(self, trade: Trade) -> Dict[str, Optional[Decimal]]:
        """
        Calculate returns for a specific trade over different time periods
        
        Args:
            trade: Trade object to calculate returns for
        
        Returns:
            Dictionary with return percentages for different periods
        """
        try:
            current_price = self.polygon_client.get_current_stock_price(trade.company_ticker)
            if not current_price:
                logger.warning(f"Could not get current price for {trade.company_ticker}")
                return {'30d': None, '90d': None, '1y': None}
            
            # Update current price in trade record
            trade.current_price = current_price
            
            # Calculate days since transaction
            days_since_trade = (datetime.now().date() - trade.transaction_date).days
            
            # Only calculate returns for buy transactions
            if trade.transaction_type.upper() not in ['BUY', 'P', 'A']:  # P=Purchase, A=Acquisition
                return {'30d': None, '90d': None, '1y': None}
            
            # Calculate percentage return
            purchase_price = trade.price_per_share
            if purchase_price <= 0:
                return {'30d': None, '90d': None, '1y': None}
            
            return_pct = ((current_price - purchase_price) / purchase_price) * 100
            
            # Return based on time periods
            returns = {
                '30d': return_pct if days_since_trade >= 30 else None,
                '90d': return_pct if days_since_trade >= 90 else None,
                '1y': return_pct if days_since_trade >= 365 else None
            }
            
            return returns
            
        except Exception as e:
            logger.error(f"Error calculating returns for trade {trade.trade_id}: {e}")
            return {'30d': None, '90d': None, '1y': None}
    
    def update_trade_performance(self, trade: Trade):
        """
        Update performance metrics for a single trade
        """
        try:
            returns = self.calculate_trade_returns(trade)
            
            trade.return_30d = returns['30d']
            trade.return_90d = returns['90d']
            trade.return_1y = returns['1y']
            trade.updated_at = datetime.now()
            
            logger.debug(f"Updated returns for trade {trade.trade_id}: 30d={returns['30d']}, 90d={returns['90d']}, 1y={returns['1y']}")
            
        except Exception as e:
            logger.error(f"Error updating trade performance for {trade.trade_id}: {e}")
    
    def calculate_trader_performance(self, trader: Trader):
        """
        Calculate overall performance metrics for a trader
        """
        try:
            # Get all trades for this trader
            trades = self.db.query(Trade).filter(Trade.trader_id == trader.trader_id).all()
            
            if not trades:
                logger.warning(f"No trades found for trader {trader.name}")
                return
            
            # Calculate performance metrics
            buy_trades = [t for t in trades if t.transaction_type.upper() in ['BUY', 'P', 'A']]
            
            if not buy_trades:
                logger.warning(f"No buy trades found for trader {trader.name}")
                return
            
            # Calculate average returns
            returns_30d = [t.return_30d for t in buy_trades if t.return_30d is not None]
            returns_90d = [t.return_90d for t in buy_trades if t.return_90d is not None]
            returns_1y = [t.return_1y for t in buy_trades if t.return_1y is not None]
            
            trader.avg_return_30d = Decimal(str(sum(returns_30d) / len(returns_30d))) if returns_30d else Decimal('0')
            trader.avg_return_90d = Decimal(str(sum(returns_90d) / len(returns_90d))) if returns_90d else Decimal('0')
            trader.avg_return_1y = Decimal(str(sum(returns_1y) / len(returns_1y))) if returns_1y else Decimal('0')
            
            # Calculate win rate (percentage of profitable trades)
            profitable_trades = len([r for r in returns_30d if r > 0])
            trader.win_rate = Decimal(str((profitable_trades / len(returns_30d)) * 100)) if returns_30d else Decimal('0')
            
            # Calculate total profit/loss
            total_pl = Decimal('0')
            for trade in buy_trades:
                if trade.current_price and trade.price_per_share:
                    pl = (trade.current_price - trade.price_per_share) * trade.shares_traded
                    total_pl += pl
            
            trader.total_profit_loss = total_pl
            trader.total_trades = len(trades)
            
            # Calculate composite performance score
            # Score = (avg_return_90d * 0.4) + (win_rate * 0.3) + (total_trades_factor * 0.3)
            trades_factor = min(len(buy_trades) / 10, 1) * 10  # Max 10 points for having 10+ trades
            
            performance_score = (
                (trader.avg_return_90d * Decimal('0.4')) +
                (trader.win_rate * Decimal('0.3')) +
                (Decimal(str(trades_factor)) * Decimal('0.3'))
            )
            
            trader.performance_score = performance_score
            trader.last_calculated = datetime.now()
            trader.updated_at = datetime.now()
            
            logger.info(f"Updated performance for {trader.name}: Score={performance_score}, Win Rate={trader.win_rate}%, Avg 90d Return={trader.avg_return_90d}%")
            
        except Exception as e:
            logger.error(f"Error calculating trader performance for {trader.name}: {e}")
    
    def run_performance_calculation(self, trader_id: Optional[int] = None):
        """
        Run performance calculations for all traders or a specific trader
        
        Args:
            trader_id: Optional specific trader ID to calculate
        """
        logger.info("Starting performance calculation...")
        
        try:
            if trader_id:
                # Calculate for specific trader
                trader = self.db.query(Trader).filter(Trader.trader_id == trader_id).first()
                if not trader:
                    logger.error(f"Trader with ID {trader_id} not found")
                    return
                
                traders = [trader]
            else:
                # Calculate for all traders
                traders = self.db.query(Trader).all()
            
            total_traders = len(traders)
            logger.info(f"Calculating performance for {total_traders} traders...")
            
            for i, trader in enumerate(traders, 1):
                logger.info(f"Processing trader {i}/{total_traders}: {trader.name}")
                
                # Update all trades for this trader
                trades = self.db.query(Trade).filter(Trade.trader_id == trader.trader_id).all()
                for trade in trades:
                    self.update_trade_performance(trade)
                
                # Calculate overall trader performance
                self.calculate_trader_performance(trader)
                
                # Commit changes for this trader
                self.db.commit()
            
            logger.info("Performance calculation completed successfully")
            
        except Exception as e:
            logger.error(f"Error in performance calculation: {e}")
            self.db.rollback()

def main():
    """
    Main function to run performance calculations
    """
    try:
        calculator = PerformanceCalculator()
        calculator.run_performance_calculation()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
