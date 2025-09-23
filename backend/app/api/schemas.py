"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class TradeResponse(BaseModel):
    trade_id: int
    trader_name: Optional[str] = None
    trader_title: Optional[str] = None
    company_ticker: str
    transaction_date: date
    transaction_type: str
    shares_traded: float
    price_per_share: float
    total_value: float
    current_price: Optional[float] = None
    return_30d: Optional[float] = None
    return_90d: Optional[float] = None
    return_1y: Optional[float] = None
    filing_date: Optional[date] = None

    class Config:
        from_attributes = True

class LeaderboardResponse(BaseModel):
    trader_id: int
    name: str
    title: Optional[str] = None
    company_ticker: str
    company_name: str
    total_trades: int
    win_rate: float
    avg_return_30d: float
    avg_return_90d: float
    avg_return_1y: float
    performance_score: float
    total_profit_loss: float

    class Config:
        from_attributes = True

class TraderResponse(BaseModel):
    trader_id: int
    name: str
    title: Optional[str] = None
    company_ticker: str
    company_name: str
    relationship_to_company: Optional[str] = None
    total_trades: int
    win_rate: float
    avg_return_30d: float
    avg_return_90d: float
    avg_return_1y: float
    performance_score: float
    total_profit_loss: float
    last_calculated: Optional[datetime] = None
    recent_trades: List[TradeResponse] = []

    class Config:
        from_attributes = True

class SearchSuggestionResponse(BaseModel):
    type: str  # "trader" or "company"
    id: Optional[int] = None
    name: str
    title: Optional[str] = None
    company: str
    ticker: str
    display_text: str

    class Config:
        from_attributes = True
