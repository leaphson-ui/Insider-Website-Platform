"""
API Routes for Insider Alpha Platform
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
from ..database import get_db
from ..models import Trader, Trade
from .schemas import (
    TraderResponse, 
    TradeResponse, 
    LeaderboardResponse,
    CompanyResponse,
    SectorResponse,
    PaginatedResponse
)

router = APIRouter()

@router.get("/traders/{trader_id}", response_model=TraderResponse)
async def get_trader(
    trader_id: int = Path(..., description="Trader ID"),
    db: Session = Depends(get_db)
):
    """Get trader details by ID"""
    trader = db.query(Trader).filter(Trader.trader_id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    return trader

@router.get("/traders/{trader_id}/transactions", response_model=List[TradeResponse])
async def get_trader_transactions(
    trader_id: int = Path(..., description="Trader ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get paginated transactions for a trader"""
    offset = (page - 1) * limit
    
    # Get total count
    total = db.query(Trade).filter(Trade.trader_id == trader_id).count()
    
    # Get transactions
    transactions = db.query(Trade)\
        .filter(Trade.trader_id == trader_id)\
        .order_by(desc(Trade.transaction_date))\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return {
        "transactions": transactions,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/companies/{ticker}", response_model=CompanyResponse)
async def get_company(
    ticker: str = Path(..., description="Company ticker"),
    db: Session = Depends(get_db)
):
    """Get company details and statistics"""
    # Get company info from traders
    company_traders = db.query(Trader).filter(Trader.company_ticker == ticker.upper()).all()
    
    if not company_traders:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Calculate company stats
    total_transactions = db.query(Trade).filter(Trade.company_ticker == ticker.upper()).count()
    active_insiders = len(company_traders)
    
    # Get average performance
    avg_performance = db.query(func.avg(Trader.avg_return_30d))\
        .filter(Trader.company_ticker == ticker.upper())\
        .scalar() or 0
    
    return {
        "ticker": ticker.upper(),
        "company_name": company_traders[0].company_name,
        "sector": company_traders[0].sector,
        "active_insiders": active_insiders,
        "total_transactions": total_transactions,
        "avg_performance": avg_performance
    }

@router.get("/companies/{ticker}/transactions", response_model=List[TradeResponse])
async def get_company_transactions(
    ticker: str = Path(..., description="Company ticker"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sort: str = Query("transaction_date", description="Sort field"),
    direction: str = Query("desc", description="Sort direction"),
    db: Session = Depends(get_db)
):
    """Get recent transactions for a company"""
    order_func = desc if direction.lower() == "desc" else asc
    
    # Map sort field to actual column
    sort_mapping = {
        "transaction_date": Trade.transaction_date,
        "trader_name": Trade.trader.has(Trader.name),
        "transaction_type": Trade.transaction_type,
        "shares_traded": Trade.shares_traded,
        "price_per_share": Trade.price_per_share,
        "total_value": Trade.total_value
    }
    
    sort_column = sort_mapping.get(sort, Trade.transaction_date)
    
    transactions = db.query(Trade)\
        .join(Trader, Trade.trader_id == Trader.trader_id)\
        .filter(Trade.company_ticker == ticker.upper())\
        .order_by(order_func(sort_column))\
        .limit(limit)\
        .all()
    
    return transactions

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    sort: str = Query("performance_score", description="Sort field"),
    direction: str = Query("desc", description="Sort direction"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    min_trades: int = Query(0, ge=0, description="Minimum number of trades"),
    db: Session = Depends(get_db)
):
    """Get leaderboard of top performing traders"""
    order_func = desc if direction.lower() == "desc" else asc
    
    # Build query
    query = db.query(Trader)
    
    # Apply filters
    if sector and sector != "all":
        query = query.filter(Trader.sector == sector)
    
    if min_trades > 0:
        query = query.filter(Trader.total_trades >= min_trades)
    
    # Map sort field to actual column
    sort_mapping = {
        "performance_score": Trader.performance_score,
        "win_rate": Trader.win_rate,
        "total_profit_loss": Trader.total_profit_loss,
        "total_trades": Trader.total_trades,
        "avg_return_30d": Trader.avg_return_30d,
        "avg_return_90d": Trader.avg_return_90d,
        "avg_return_1y": Trader.avg_return_1y,
        "name": Trader.name,
        "company_ticker": Trader.company_ticker
    }
    
    sort_column = sort_mapping.get(sort, Trader.performance_score)
    
    # Get results
    traders = query.order_by(order_func(sort_column)).limit(limit).all()
    
    return {
        "leaderboard": traders,
        "total": len(traders),
        "sort": sort,
        "direction": direction
    }

@router.get("/sectors", response_model=SectorResponse)
async def get_sectors(db: Session = Depends(get_db)):
    """Get list of all sectors"""
    sectors = db.query(Trader.sector)\
        .filter(Trader.sector.isnot(None))\
        .distinct()\
        .all()
    
    return {
        "sectors": [sector[0] for sector in sectors if sector[0]]
    }

@router.get("/trades/recent")
async def get_recent_trades(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Number of trades per page"),
    sort: str = Query("transaction_date", description="Sort field"),
    direction: str = Query("desc", description="Sort direction"),
    ticker: Optional[str] = Query(None, description="Filter by company ticker"),
    trader: Optional[str] = Query(None, description="Filter by trader name"),
    type: Optional[str] = Query(None, description="Filter by transaction type"),
    db: Session = Depends(get_db)
):
    """Get recent trades with pagination and filtering"""
    offset = (page - 1) * limit
    order_func = desc if direction.lower() == "desc" else asc
    
    # Build query
    query = db.query(Trade).join(Trader, Trade.trader_id == Trader.trader_id)
    
    # Apply filters
    if ticker:
        query = query.filter(Trade.company_ticker == ticker.upper())
    if trader:
        query = query.filter(Trader.name.ilike(f"%{trader}%"))
    if type and type != "all":
        query = query.filter(Trade.transaction_type == type.upper())
    
    # Map sort field to actual column
    sort_mapping = {
        "transaction_date": Trade.transaction_date,
        "trader_name": Trader.name,
        "company_ticker": Trade.company_ticker,
        "transaction_type": Trade.transaction_type,
        "shares_traded": Trade.shares_traded,
        "price_per_share": Trade.price_per_share,
        "total_value": Trade.total_value,
        "return_30d": Trade.return_30d
    }
    
    sort_column = sort_mapping.get(sort, Trade.transaction_date)
    
    # Get total count
    total = query.count()
    
    # Get trades with trader information
    trades = query.order_by(order_func(sort_column)).offset(offset).limit(limit).all()
    
    # Convert to list of dictionaries with trader names
    trades_data = []
    for trade in trades:
        trade_dict = {
            "trade_id": trade.trade_id,
            "trader_id": trade.trader_id,
            "trader_name": trade.trader.name if trade.trader else "Unknown",
            "trader_title": trade.trader.title if trade.trader else "",
            "company_ticker": trade.company_ticker,
            "company_name": trade.trader.company_name if trade.trader else "",
            "sector": trade.trader.sector if trade.trader else "",
            "transaction_date": trade.transaction_date,
            "transaction_type": trade.transaction_type,
            "shares_traded": trade.shares_traded,
            "price_per_share": trade.price_per_share,
            "total_value": trade.total_value,
            "current_price": trade.current_price,
            "return_30d": trade.return_30d,
            "return_90d": trade.return_90d,
            "return_1y": trade.return_1y,
            "form_type": trade.form_type,
            "filing_date": trade.filing_date,
            "created_at": trade.created_at,
            "updated_at": trade.updated_at
        }
        trades_data.append(trade_dict)
    
    return {
        "trades": trades_data,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}