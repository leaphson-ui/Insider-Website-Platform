"""
SQLAlchemy models for Insider Alpha Platform
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Trader(Base):
    __tablename__ = "traders"
    
    trader_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    company_ticker = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(50), index=True)
    relationship_to_company = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    total_profit_loss = Column(Numeric(15, 2), default=0.00)
    win_rate = Column(Numeric(5, 2), default=0.00)
    avg_return_30d = Column(Numeric(8, 4), default=0.0000)
    avg_return_90d = Column(Numeric(8, 4), default=0.0000)
    avg_return_1y = Column(Numeric(8, 4), default=0.0000)
    performance_score = Column(Numeric(8, 4), default=0.0000, index=True)
    last_calculated = Column(DateTime)
    
    # Relationship to trades
    trades = relationship("Trade", back_populates="trader")

class Trade(Base):
    __tablename__ = "trades"
    
    trade_id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, ForeignKey("traders.trader_id"), nullable=False, index=True)
    company_ticker = Column(String(10), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    shares_traded = Column(Numeric(15, 4), nullable=False)
    price_per_share = Column(Numeric(10, 4), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    
    # Performance tracking
    current_price = Column(Numeric(10, 4))
    return_30d = Column(Numeric(8, 4))
    return_90d = Column(Numeric(8, 4))
    return_1y = Column(Numeric(8, 4))
    
    # Metadata
    form_type = Column(String(20), default="Form 4")
    filing_date = Column(Date)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship to trader
    trader = relationship("Trader", back_populates="trades")
