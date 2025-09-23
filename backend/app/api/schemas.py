"""
Pydantic schemas for API responses
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class TradeResponse(BaseModel):
    trade_id: int
    trader_id: int
    trader_name: str
    trader_title: str
    company_ticker: str
    transaction_date: date
    transaction_type: str
    shares_traded: Optional[Decimal]
    price_per_share: Optional[Decimal]
    total_value: Decimal
    current_price: Optional[Decimal]
    return_30d: Optional[Decimal]
    return_90d: Optional[Decimal]
    return_1y: Optional[Decimal]
    form_type: Optional[str]
    filing_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TraderResponse(BaseModel):
    trader_id: int
    name: str
    title: Optional[str]
    company_ticker: str
    company_name: str
    sector: Optional[str]
    relationship_to_company: Optional[str]
    total_trades: int
    total_profit_loss: Decimal
    win_rate: Decimal
    avg_return_30d: Decimal
    avg_return_90d: Decimal
    avg_return_1y: Decimal
    performance_score: Decimal
    last_calculated: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompanyResponse(BaseModel):
    ticker: str
    company_name: str
    sector: Optional[str]
    active_insiders: int
    total_transactions: int
    avg_performance: Decimal

class LeaderboardResponse(BaseModel):
    leaderboard: List[TraderResponse]
    total: int
    sort: str
    direction: str

class SectorResponse(BaseModel):
    sectors: List[str]

class PaginatedResponse(BaseModel):
    transactions: List[TradeResponse]
    total: int
    page: int
    limit: int
    total_pages: int