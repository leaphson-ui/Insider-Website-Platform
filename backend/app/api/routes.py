"""
FastAPI routes for Insider Alpha Platform
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Trader, Trade
from .schemas import TraderResponse, TradeResponse, LeaderboardResponse

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
        traders = db.query(Trader).filter(
            Trader.total_trades >= min_trades,
            Trader.performance_score.isnot(None)
        ).order_by(
            Trader.performance_score.desc()
        ).limit(limit).all()
        
        return [
            LeaderboardResponse(
                trader_id=trader.trader_id,
                name=trader.name,
                title=trader.title,
                company_ticker=trader.company_ticker,
                company_name=trader.company_name,
                total_trades=trader.total_trades,
                win_rate=float(trader.win_rate) if trader.win_rate else 0.0,
                avg_return_30d=float(trader.avg_return_30d) if trader.avg_return_30d else 0.0,
                avg_return_90d=float(trader.avg_return_90d) if trader.avg_return_90d else 0.0,
                avg_return_1y=float(trader.avg_return_1y) if trader.avg_return_1y else 0.0,
                performance_score=float(trader.performance_score) if trader.performance_score else 0.0,
                total_profit_loss=float(trader.total_profit_loss) if trader.total_profit_loss else 0.0
            )
            for trader in traders
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
        
        # Get recent trades for this trader
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

@router.get("/trades/recent", response_model=List[TradeResponse])
async def get_recent_trades(
    limit: int = Query(100, ge=1, le=500, description="Number of trades to return"),
    ticker: Optional[str] = Query(None, description="Filter by stock ticker"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """
    Get recent insider trades
    """
    try:
        query = db.query(Trade).join(Trader)
        
        # Filter by date
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
        
        # Get most active companies
        from sqlalchemy import func
        top_companies = db.query(
            Trade.company_ticker,
            func.count(Trade.trade_id).label('trade_count')
        ).group_by(Trade.company_ticker).order_by(
            func.count(Trade.trade_id).desc()
        ).limit(10).all()
        
        # Get latest trade date
        latest_trade = db.query(Trade).order_by(Trade.transaction_date.desc()).first()
        
        return {
            "total_traders": total_traders,
            "total_trades": total_trades,
            "active_traders": active_traders,
            "latest_trade_date": latest_trade.transaction_date.isoformat() if latest_trade else None,
            "top_companies": [
                {"ticker": company[0], "trade_count": company[1]}
                for company in top_companies
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching platform stats: {str(e)}")

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
