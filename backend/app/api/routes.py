"""
FastAPI routes for Insider Alpha Platform
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Trader, Trade
from .schemas import TraderResponse, TradeResponse, LeaderboardResponse, SearchSuggestionResponse

router = APIRouter()

@router.get("/leaderboard", response_model=List[LeaderboardResponse])
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100, description="Number of traders to return"),
    min_trades: int = Query(5, ge=1, description="Minimum number of trades required"),
    db: Session = Depends(get_db)
):
    """
    Get the top performing insiders ranked by performance score
    """
    try:
        # Calculate trade counts on the fly since total_trades isn't updated
        query = text("""
            SELECT 
                t.trader_id,
                t.name,
                t.title,
                t.company_ticker,
                t.company_name,
                COUNT(tr.trade_id) as total_trades,
                t.win_rate,
                t.avg_return_30d,
                t.avg_return_90d,
                t.avg_return_1y,
                t.performance_score,
                t.total_profit_loss
            FROM traders t
            LEFT JOIN trades tr ON t.trader_id = tr.trader_id
            GROUP BY t.trader_id, t.name, t.title, t.company_ticker, t.company_name, 
                     t.win_rate, t.avg_return_30d, t.avg_return_90d, t.avg_return_1y, 
                     t.performance_score, t.total_profit_loss
            HAVING COUNT(tr.trade_id) >= :min_trades
            ORDER BY COUNT(tr.trade_id) DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"min_trades": min_trades, "limit": limit}).fetchall()
        
        return [
            LeaderboardResponse(
                trader_id=row[0],
                name=row[1],
                title=row[2],
                company_ticker=row[3],
                company_name=row[4],
                total_trades=row[5],
                win_rate=float(row[6]) if row[6] else 0.0,
                avg_return_30d=float(row[7]) if row[7] else 0.0,
                avg_return_90d=float(row[8]) if row[8] else 0.0,
                avg_return_1y=float(row[9]) if row[9] else 0.0,
                performance_score=float(row[10]) if row[10] else 0.0,
                total_profit_loss=float(row[11]) if row[11] else 0.0
            )
            for row in result
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching leaderboard: {str(e)}")

@router.get("/traders/{trader_id}", response_model=TraderResponse)
async def get_trader(trader_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific trader
    """
    try:
        trader = db.query(Trader).filter(Trader.trader_id == trader_id).first()
        
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        # Get recent trades for this trader (limited for performance)
        recent_trades = db.query(Trade).filter(
            Trade.trader_id == trader_id
        ).order_by(
            Trade.transaction_date.desc()
        ).limit(20).all()
        
        return TraderResponse(
            trader_id=trader.trader_id,
            name=trader.name,
            title=trader.title,
            company_ticker=trader.company_ticker,
            company_name=trader.company_name,
            relationship_to_company=trader.relationship_to_company,
            total_trades=trader.total_trades,
            win_rate=float(trader.win_rate) if trader.win_rate else 0.0,
            avg_return_30d=float(trader.avg_return_30d) if trader.avg_return_30d else 0.0,
            avg_return_90d=float(trader.avg_return_90d) if trader.avg_return_90d else 0.0,
            avg_return_1y=float(trader.avg_return_1y) if trader.avg_return_1y else 0.0,
            performance_score=float(trader.performance_score) if trader.performance_score else 0.0,
            total_profit_loss=float(trader.total_profit_loss) if trader.total_profit_loss else 0.0,
            last_calculated=trader.last_calculated,
            recent_trades=[
                TradeResponse(
                    trade_id=trade.trade_id,
                    company_ticker=trade.company_ticker,
                    transaction_date=trade.transaction_date,
                    transaction_type=trade.transaction_type,
                    shares_traded=float(trade.shares_traded),
                    price_per_share=float(trade.price_per_share),
                    total_value=float(trade.total_value),
                    current_price=float(trade.current_price) if trade.current_price else None,
                    return_30d=float(trade.return_30d) if trade.return_30d else None,
                    return_90d=float(trade.return_90d) if trade.return_90d else None,
                    return_1y=float(trade.return_1y) if trade.return_1y else None,
                    filing_date=trade.filing_date
                )
                for trade in recent_trades
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trader: {str(e)}")

@router.get("/traders/{trader_id}/trades", response_model=List[TradeResponse])
async def get_trader_trades(
    trader_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Number of trades per page"),
    db: Session = Depends(get_db)
):
    """
    Get all trades for a specific trader with pagination
    """
    try:
        # Check if trader exists
        trader = db.query(Trader).filter(Trader.trader_id == trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get trades with pagination
        trades = db.query(Trade).filter(
            Trade.trader_id == trader_id
        ).order_by(
            Trade.transaction_date.desc()
        ).offset(offset).limit(limit).all()
        
        return [
            TradeResponse(
                trade_id=trade.trade_id,
                trader_name=trader.name,
                trader_title=trader.title,
                company_ticker=trade.company_ticker,
                transaction_date=trade.transaction_date,
                transaction_type=trade.transaction_type,
                shares_traded=float(trade.shares_traded),
                price_per_share=float(trade.price_per_share),
                total_value=float(trade.total_value),
                current_price=float(trade.current_price) if trade.current_price else None,
                return_30d=float(trade.return_30d) if trade.return_30d else None,
                return_90d=float(trade.return_90d) if trade.return_90d else None,
                return_1y=float(trade.return_1y) if trade.return_1y else None,
                filing_date=trade.filing_date
            )
            for trade in trades
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trader trades: {str(e)}")

@router.get("/traders/{trader_id}/trades/count")
async def get_trader_trades_count(trader_id: int, db: Session = Depends(get_db)):
    """
    Get total count of trades for a specific trader
    """
    try:
        # Check if trader exists
        trader = db.query(Trader).filter(Trader.trader_id == trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        # Get total count
        total_count = db.query(Trade).filter(Trade.trader_id == trader_id).count()
        
        return {"total_trades": total_count}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trader trades count: {str(e)}")

@router.get("/trades/recent", response_model=List[TradeResponse])
async def get_recent_trades(
    limit: int = Query(100, ge=1, le=500, description="Number of trades to return"),
    ticker: Optional[str] = Query(None, description="Filter by stock ticker"),
    days: int = Query(1095, ge=1, le=3650, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get recent insider trades
    """
    try:
        query = db.query(Trade).join(Trader)
        
        # Filter by date (default to 3 years since our data is historical)
        cutoff_date = datetime.now().date() - timedelta(days=days)
        query = query.filter(Trade.transaction_date >= cutoff_date)
        
        # Filter by ticker if provided
        if ticker:
            query = query.filter(Trade.company_ticker == ticker.upper())
        
        trades = query.order_by(Trade.transaction_date.desc()).limit(limit).all()
        
        return [
            TradeResponse(
                trade_id=trade.trade_id,
                trader_name=trade.trader.name,
                trader_title=trade.trader.title,
                company_ticker=trade.company_ticker,
                transaction_date=trade.transaction_date,
                transaction_type=trade.transaction_type,
                shares_traded=float(trade.shares_traded),
                price_per_share=float(trade.price_per_share),
                total_value=float(trade.total_value),
                current_price=float(trade.current_price) if trade.current_price else None,
                return_30d=float(trade.return_30d) if trade.return_30d else None,
                return_90d=float(trade.return_90d) if trade.return_90d else None,
                return_1y=float(trade.return_1y) if trade.return_1y else None,
                filing_date=trade.filing_date
            )
            for trade in trades
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent trades: {str(e)}")

@router.get("/companies/{ticker}/insider-trades", response_model=List[TradeResponse])
async def get_company_insider_trades(
    ticker: str,
    limit: int = Query(100, ge=1, le=500, description="Number of trades to return"),
    db: Session = Depends(get_db)
):
    """
    Get all insider trades for a specific company
    """
    try:
        trades = db.query(Trade).join(Trader).filter(
            Trade.company_ticker == ticker.upper()
        ).order_by(
            Trade.transaction_date.desc()
        ).limit(limit).all()
        
        if not trades:
            raise HTTPException(status_code=404, detail=f"No insider trades found for {ticker}")
        
        return [
            TradeResponse(
                trade_id=trade.trade_id,
                trader_name=trade.trader.name,
                trader_title=trade.trader.title,
                company_ticker=trade.company_ticker,
                transaction_date=trade.transaction_date,
                transaction_type=trade.transaction_type,
                shares_traded=float(trade.shares_traded),
                price_per_share=float(trade.price_per_share),
                total_value=float(trade.total_value),
                current_price=float(trade.current_price) if trade.current_price else None,
                return_30d=float(trade.return_30d) if trade.return_30d else None,
                return_90d=float(trade.return_90d) if trade.return_90d else None,
                return_1y=float(trade.return_1y) if trade.return_1y else None,
                filing_date=trade.filing_date
            )
            for trade in trades
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company trades: {str(e)}")

@router.get("/stats/summary")
async def get_platform_stats(db: Session = Depends(get_db)):
    """
    Get platform summary statistics
    """
    try:
        total_traders = db.query(Trader).count()
        total_trades = db.query(Trade).count()
        active_traders = db.query(Trader).filter(Trader.total_trades > 0).count()
        
        # Calculate buy/sell ratio
        buy_trades = db.query(Trade).filter(Trade.transaction_type.like('%BUY%')).count()
        sell_trades = db.query(Trade).filter(Trade.transaction_type.like('%SELL%')).count()
        buy_sell_ratio = buy_trades / sell_trades if sell_trades > 0 else 0
        
        # Calculate average trade size
        avg_trade_size = db.query(func.avg(Trade.total_value)).scalar()
        
        # Get most active companies
        top_companies = db.query(
            Trade.company_ticker,
            func.count(Trade.trade_id).label('trade_count')
        ).group_by(Trade.company_ticker).order_by(
            func.count(Trade.trade_id).desc()
        ).limit(10).all()
        
        # Get latest trade date
        latest_trade = db.query(Trade).order_by(Trade.transaction_date.desc()).first()
        
        # Calculate total unique companies
        total_companies = db.query(Trade.company_ticker.distinct()).count()
        
        # Calculate average return 30d across all trades
        avg_return_30d = db.query(func.avg(Trade.return_30d)).filter(
            Trade.return_30d.isnot(None)
        ).scalar()
        
        return {
            "total_traders": total_traders,
            "total_trades": total_trades,
            "active_traders": active_traders,
            "total_companies": total_companies,
            "avg_return_30d": round(float(avg_return_30d), 2) if avg_return_30d else 0,
            "buy_sell_ratio": round(buy_sell_ratio, 2),
            "avg_trade_size": round(float(avg_trade_size), 2) if avg_trade_size else 0,
            "latest_trade_date": latest_trade.transaction_date.isoformat() if latest_trade else None,
            "top_companies": [
                {"ticker": company[0], "trade_count": company[1]}
                for company in top_companies
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching platform stats: {str(e)}")

@router.get("/analytics/sectors")
async def get_sector_analytics(db: Session = Depends(get_db)):
    """
    Get sector-based analytics for dashboard
    """
    try:
        # Get all sectors by volume
        sector_volume = db.execute(text("""
            SELECT 
                COALESCE(t.sector, 'Other') as sector,
                COUNT(tr.trade_id) as trade_count,
                SUM(tr.total_value) as total_volume,
                COUNT(CASE WHEN tr.transaction_type LIKE '%BUY%' THEN 1 END) as buy_count,
                COUNT(CASE WHEN tr.transaction_type LIKE '%SELL%' THEN 1 END) as sell_count
            FROM traders t
            JOIN trades tr ON t.trader_id = tr.trader_id
            WHERE t.sector IS NOT NULL
            GROUP BY t.sector
            ORDER BY total_volume DESC
        """)).fetchall()
        
        # Get insider sentiment (buy vs sell ratio)
        sentiment_data = db.execute(text("""
            SELECT 
                COUNT(CASE WHEN transaction_type LIKE '%BUY%' THEN 1 END) as buy_trades,
                COUNT(CASE WHEN transaction_type LIKE '%SELL%' THEN 1 END) as sell_trades,
                COUNT(*) as total_trades
            FROM trades
        """)).fetchone()
        
        return {
            "top_sectors": [
                {
                    "sector": row[0],
                    "trade_count": row[1],
                    "total_volume": float(row[2]) if row[2] else 0,
                    "buy_count": row[3],
                    "sell_count": row[4],
                    "buy_sell_ratio": round(row[3] / row[4], 2) if row[4] > 0 else 0
                }
                for row in sector_volume
            ],
            "insider_sentiment": {
                "buy_trades": sentiment_data[0] if sentiment_data else 0,
                "sell_trades": sentiment_data[1] if sentiment_data else 0,
                "total_trades": sentiment_data[2] if sentiment_data else 0,
                "bullish_percentage": round((sentiment_data[0] / sentiment_data[2]) * 100, 1) if sentiment_data and sentiment_data[2] > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector analytics: {str(e)}")

@router.post("/admin/update-data")
async def update_sec_data():
    """
    Trigger SEC data update (admin endpoint)
    """
    try:
        import subprocess
        import os
        
        # Run the automated SEC data manager
        script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'automated_sec_data_manager.py')
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "SEC data update completed successfully",
                "output": result.stdout
            }
        else:
            return {
                "status": "error", 
                "message": "SEC data update failed",
                "error": result.stderr
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating SEC data: {str(e)}")

@router.get("/analytics/networks")
async def get_network_analysis(db: Session = Depends(get_db)):
    """
    Get insider network analysis data
    """
    try:
        from sqlalchemy import func, text
        
        # Simple board overlaps query
        board_overlaps_query = """
            SELECT name, COUNT(*) as company_count, AVG(performance_score) as avg_performance
            FROM traders 
            WHERE total_trades > 0
            GROUP BY name
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC, AVG(performance_score) DESC
            LIMIT 20
        """
        board_overlaps = db.execute(text(board_overlaps_query)).fetchall()
        
        # Trading clusters - simplified
        trading_clusters_query = """
            SELECT t.company_ticker,
                   COUNT(DISTINCT t.trader_id) as insider_count,
                   COUNT(*) as trade_count,
                   SUM(t.total_value) as total_volume,
                   SUM(CASE WHEN t.transaction_type = 'BUY' THEN 1 ELSE 0 END) as buy_count,
                   SUM(CASE WHEN t.transaction_type = 'SELL' THEN 1 ELSE 0 END) as sell_count
            FROM trades t
            WHERE t.transaction_date >= (CURRENT_DATE - INTERVAL '6 months')
            GROUP BY t.company_ticker
            HAVING COUNT(DISTINCT t.trader_id) >= 3
            ORDER BY SUM(t.total_value) DESC
            LIMIT 20
        """
        trading_clusters = db.execute(text(trading_clusters_query)).fetchall()
        
        # Family networks - simplified
        family_networks = []  # Simplified for now
        
        return {
            "board_overlaps": [
                {
                    "name": row[0],
                    "company_count": row[1], 
                    "companies": [f"Company_{i+1}" for i in range(row[1])],  # Simplified
                    "avg_performance": float(row[2]) if row[2] else 0
                }
                for row in board_overlaps
            ],
            "trading_clusters": [
                {
                    "company": row[0],
                    "month": "2024-2025",
                    "insider_count": row[1],
                    "trade_count": row[2],
                    "total_volume": float(row[3]) if row[3] else 0,
                    "buy_count": row[4],
                    "sell_count": row[5],
                    "sentiment": "Bullish" if row[4] > row[5] else "Bearish" if row[5] > row[4] else "Mixed"
                }
                for row in trading_clusters
            ],
            "family_networks": [
                {
                    "family_name": row[0],
                    "member_count": row[1],
                    "companies": row[2].split(', ') if row[2] else [],
                    "avg_performance": float(row[3]) if row[3] else 0
                }
                for row in family_networks
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching network analysis: {str(e)}")

@router.get("/analytics/timing")
async def get_timing_analysis(db: Session = Depends(get_db)):
    """
    Get insider timing pattern analysis
    """
    try:
        from sqlalchemy import func, text
        
        # Day of week patterns
        day_patterns = db.execute(text("""
            SELECT EXTRACT(DOW FROM transaction_date) as day_of_week,
                   TO_CHAR(transaction_date, 'Day') as day_name,
                   COUNT(*) as trade_count,
                   SUM(total_value) as total_volume,
                   AVG(total_value) as avg_trade_size,
                   SUM(CASE WHEN transaction_type = 'BUY' THEN 1 ELSE 0 END) as buy_count,
                   SUM(CASE WHEN transaction_type = 'SELL' THEN 1 ELSE 0 END) as sell_count
            FROM trades
            WHERE transaction_date >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY EXTRACT(DOW FROM transaction_date), TO_CHAR(transaction_date, 'Day')
            ORDER BY day_of_week
        """)).fetchall()
        
        # Month patterns
        month_patterns = db.execute(text("""
            SELECT EXTRACT(MONTH FROM transaction_date) as month_num,
                   TO_CHAR(transaction_date, 'Month') as month_name,
                   COUNT(*) as trade_count,
                   SUM(total_value) as total_volume,
                   AVG(total_value) as avg_trade_size
            FROM trades
            WHERE transaction_date >= CURRENT_DATE - INTERVAL '2 years'
            GROUP BY EXTRACT(MONTH FROM transaction_date), TO_CHAR(transaction_date, 'Month')
            ORDER BY month_num
        """)).fetchall()
        
        # Insider timing consistency
        timing_consistency = db.execute(text("""
            SELECT tr.name, tr.company_ticker,
                   COUNT(t.trade_id) as trade_count,
                   MODE() WITHIN GROUP (ORDER BY EXTRACT(DOW FROM t.transaction_date)) as preferred_day,
                   MODE() WITHIN GROUP (ORDER BY EXTRACT(MONTH FROM t.transaction_date)) as preferred_month,
                   AVG(t.total_value) as avg_trade_size,
                   tr.performance_score
            FROM traders tr
            JOIN trades t ON tr.trader_id = t.trader_id
            WHERE t.transaction_date >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY tr.trader_id, tr.name, tr.company_ticker, tr.performance_score
            HAVING COUNT(t.trade_id) >= 5
            ORDER BY tr.performance_score DESC
            LIMIT 30
        """)).fetchall()
        
        return {
            "day_patterns": [
                {
                    "day_of_week": int(row[0]),
                    "day_name": row[1].strip(),
                    "trade_count": row[2],
                    "total_volume": float(row[3]) if row[3] else 0,
                    "avg_trade_size": float(row[4]) if row[4] else 0,
                    "buy_count": row[5],
                    "sell_count": row[6]
                }
                for row in day_patterns
            ],
            "month_patterns": [
                {
                    "month_num": int(row[0]),
                    "month_name": row[1].strip(),
                    "trade_count": row[2],
                    "total_volume": float(row[3]) if row[3] else 0,
                    "avg_trade_size": float(row[4]) if row[4] else 0
                }
                for row in month_patterns
            ],
            "timing_consistency": [
                {
                    "name": row[0],
                    "company": row[1],
                    "trade_count": row[2],
                    "preferred_day": int(row[3]) if row[3] else 0,
                    "preferred_month": int(row[4]) if row[4] else 0,
                    "avg_trade_size": float(row[5]) if row[5] else 0,
                    "performance_score": float(row[6]) if row[6] else 0
                }
                for row in timing_consistency
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching timing analysis: {str(e)}")

@router.get("/portfolio/leaderboard")
async def get_portfolio_leaderboard(
    limit: int = Query(50, ge=1, le=100, description="Number of traders to return"),
    min_holdings_value: float = Query(100000, ge=0, description="Minimum portfolio value"),
    db: Session = Depends(get_db)
):
    """
    Get the top insiders by current portfolio holdings value
    """
    try:
        # Calculate current holdings by summing net shares for each trader/company combination
        # Then multiply by current/latest price to get current value
        portfolio_holdings = db.execute(text("""
            WITH net_positions AS (
                SELECT 
                    tr.trader_id,
                    tr.name,
                    tr.title,
                    t.company_ticker,
                    tr.company_name,
                    SUM(CASE 
                        WHEN t.transaction_type IN ('P', 'A', 'BUY') THEN t.shares_traded
                        WHEN t.transaction_type IN ('S', 'D', 'SELL') THEN -t.shares_traded
                        ELSE 0
                    END) as net_shares,
                    MAX(t.price_per_share) as latest_price,
                    COUNT(t.trade_id) as total_trades,
                    tr.performance_score
                FROM traders tr
                JOIN trades t ON tr.trader_id = t.trader_id
                WHERE t.shares_traded IS NOT NULL 
                  AND t.price_per_share IS NOT NULL
                  AND t.price_per_share > 0
                GROUP BY tr.trader_id, tr.name, tr.title, t.company_ticker, tr.company_name, tr.performance_score
                HAVING SUM(CASE 
                    WHEN t.transaction_type IN ('P', 'A', 'BUY') THEN t.shares_traded
                    WHEN t.transaction_type IN ('S', 'D', 'SELL') THEN -t.shares_traded
                    ELSE 0
                END) > 0
            ),
            portfolio_values AS (
                SELECT 
                    trader_id,
                    name,
                    title,
                    company_name,
                    SUM(net_shares * latest_price) as total_portfolio_value,
                    COUNT(DISTINCT company_ticker) as companies_held,
                    SUM(total_trades) as total_trades,
                    AVG(performance_score) as avg_performance_score
                FROM net_positions
                GROUP BY trader_id, name, title, company_name
            )
            SELECT 
                trader_id,
                name,
                title,
                company_name,
                total_portfolio_value,
                companies_held,
                total_trades,
                avg_performance_score
            FROM portfolio_values
            WHERE total_portfolio_value >= :min_value
            ORDER BY total_portfolio_value DESC
            LIMIT :limit
        """), {"min_value": min_holdings_value, "limit": limit}).fetchall()
        
        return [
            {
                "trader_id": row[0],
                "name": row[1],
                "title": row[2],
                "company_name": row[3],
                "total_portfolio_value": float(row[4]) if row[4] else 0,
                "companies_held": row[5],
                "total_trades": row[6],
                "performance_score": float(row[7]) if row[7] else 0
            }
            for row in portfolio_holdings
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio leaderboard: {str(e)}")

@router.get("/traders/{trader_id}/holdings")
async def get_trader_holdings(
    trader_id: int,
    db: Session = Depends(get_db)
):
    """
    Get current holdings for a specific trader
    """
    try:
        # Check if trader exists
        trader = db.query(Trader).filter(Trader.trader_id == trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        # Calculate current holdings by company
        holdings = db.execute(text("""
            SELECT 
                t.company_ticker,
                tr.company_name,
                SUM(CASE 
                    WHEN t.transaction_type IN ('P', 'A', 'BUY') THEN t.shares_traded
                    WHEN t.transaction_type IN ('S', 'D', 'SELL') THEN -t.shares_traded
                    ELSE 0
                END) as net_shares,
                AVG(t.price_per_share) as avg_cost_basis,
                MAX(t.price_per_share) as latest_price,
                MAX(t.transaction_date) as last_transaction_date,
                COUNT(t.trade_id) as total_transactions
            FROM trades t
            JOIN traders tr ON t.trader_id = tr.trader_id
            WHERE t.trader_id = :trader_id
              AND t.shares_traded IS NOT NULL 
              AND t.price_per_share IS NOT NULL
              AND t.price_per_share > 0
            GROUP BY t.company_ticker, tr.company_name
            HAVING SUM(CASE 
                WHEN t.transaction_type IN ('P', 'A', 'BUY') THEN t.shares_traded
                WHEN t.transaction_type IN ('S', 'D', 'SELL') THEN -t.shares_traded
                ELSE 0
            END) > 0
            ORDER BY SUM(CASE 
                WHEN t.transaction_type IN ('P', 'A', 'BUY') THEN t.shares_traded
                WHEN t.transaction_type IN ('S', 'D', 'SELL') THEN -t.shares_traded
                ELSE 0
            END) * MAX(t.price_per_share) DESC
        """), {"trader_id": trader_id}).fetchall()
        
        total_portfolio_value = sum(row[2] * row[4] for row in holdings if row[2] and row[4])
        
        return {
            "trader_info": {
                "trader_id": trader.trader_id,
                "name": trader.name,
                "title": trader.title,
                "company_ticker": trader.company_ticker,
                "company_name": trader.company_name,
                "performance_score": float(trader.performance_score) if trader.performance_score else 0
            },
            "total_portfolio_value": total_portfolio_value,
            "holdings": [
                {
                    "company_ticker": row[0],
                    "company_name": row[1],
                    "net_shares": row[2],
                    "avg_cost_basis": float(row[3]) if row[3] else 0,
                    "latest_price": float(row[4]) if row[4] else 0,
                    "current_value": row[2] * row[4] if row[2] and row[4] else 0,
                    "last_transaction_date": row[5].isoformat() if row[5] else None,
                    "total_transactions": row[6]
                }
                for row in holdings
            ]
        }
        
    except Exception as e:
        if "Trader not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching trader holdings: {str(e)}")

@router.get("/search", response_model=List[SearchSuggestionResponse])
async def search_suggestions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions to return"),
    db: Session = Depends(get_db)
):
    """
    Search for traders and companies by name or ticker
    """
    try:
        # Normalize search query - split into individual words
        search_words = [word.strip().lower() for word in q.split() if word.strip()]
        
        if not search_words:
            return []
        
        # Build dynamic query for traders - each word must be found in the name
        trader_query = db.query(Trader)
        for word in search_words:
            trader_query = trader_query.filter(
                func.lower(Trader.name).like(f"%{word}%")
            )
        
        trader_results = trader_query.limit(limit // 2).all()
        
        # Search for companies by ticker (from traders table)
        company_query = db.query(
            Trader.company_ticker.label('ticker'),
            Trader.company_name.label('name')
        )
        
        # Search by ticker (exact match for tickers)
        ticker_matches = company_query.filter(
            func.lower(Trader.company_ticker).like(f"%{q.lower()}%")
        ).distinct().limit(limit // 2).all()
        
        # Also search by company name (word-based like traders)
        company_name_query = db.query(
            Trader.company_ticker.label('ticker'),
            Trader.company_name.label('name')
        )
        for word in search_words:
            company_name_query = company_name_query.filter(
                func.lower(Trader.company_name).like(f"%{word}%")
            )
        
        company_name_matches = company_name_query.distinct().limit(limit // 2).all()
        
        # Combine and deduplicate results
        company_results = ticker_matches + company_name_matches
        seen_companies = set()
        unique_company_results = []
        for company in company_results:
            if company.ticker not in seen_companies:
                seen_companies.add(company.ticker)
                unique_company_results.append(company)
                if len(unique_company_results) >= limit // 2:
                    break
        
        suggestions = []
        
        # Add trader suggestions
        for trader in trader_results:
            suggestions.append({
                "type": "trader",
                "id": trader.trader_id,
                "name": trader.name,
                "title": trader.title,
                "company": trader.company_name,
                "ticker": trader.company_ticker,
                "display_text": f"{trader.name} ({trader.title}) - {trader.company_ticker}"
            })
        
        # Add company suggestions
        for company in unique_company_results:
            suggestions.append({
                "type": "company",
                "id": None,
                "name": company.name,
                "title": None,
                "company": company.name,
                "ticker": company.ticker,
                "display_text": f"{company.ticker} - {company.name}"
            })
        
        # Remove duplicates and limit results
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = (suggestion["type"], suggestion["ticker"], suggestion["name"])
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
                if len(unique_suggestions) >= limit:
                    break
        
        return unique_suggestions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

