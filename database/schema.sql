-- Insider Alpha Platform Database Schema

-- Create database (run separately)
-- CREATE DATABASE insider_alpha;

-- Traders table - stores insider profiles
CREATE TABLE IF NOT EXISTS traders (
    trader_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    company_ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    relationship_to_company VARCHAR(100), -- CEO, Director, Officer, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Performance metrics (calculated by performance engine)
    total_trades INTEGER DEFAULT 0,
    total_profit_loss DECIMAL(15,2) DEFAULT 0.00,
    win_rate DECIMAL(5,2) DEFAULT 0.00, -- percentage of profitable trades
    avg_return_30d DECIMAL(8,4) DEFAULT 0.0000, -- average 30-day return
    avg_return_90d DECIMAL(8,4) DEFAULT 0.0000, -- average 90-day return
    avg_return_1y DECIMAL(8,4) DEFAULT 0.0000,  -- average 1-year return
    performance_score DECIMAL(8,4) DEFAULT 0.0000, -- composite score for ranking
    last_calculated TIMESTAMP
);

-- Trades table - stores individual transactions
CREATE TABLE IF NOT EXISTS trades (
    trade_id SERIAL PRIMARY KEY,
    trader_id INTEGER REFERENCES traders(trader_id) ON DELETE CASCADE,
    company_ticker VARCHAR(10) NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- BUY, SELL, OPTION_EXERCISE, etc.
    shares_traded DECIMAL(15,4) NOT NULL,
    price_per_share DECIMAL(10,4) NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    
    -- Performance tracking
    current_price DECIMAL(10,4), -- updated by performance engine
    return_30d DECIMAL(8,4), -- 30-day return percentage
    return_90d DECIMAL(8,4), -- 90-day return percentage
    return_1y DECIMAL(8,4),  -- 1-year return percentage
    
    -- Metadata
    form_type VARCHAR(20) DEFAULT 'Form 4',
    filing_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_traders_performance_score ON traders(performance_score DESC);
CREATE INDEX IF NOT EXISTS idx_traders_company_ticker ON traders(company_ticker);
CREATE INDEX IF NOT EXISTS idx_trades_trader_id ON trades(trader_id);
CREATE INDEX IF NOT EXISTS idx_trades_company_ticker ON trades(company_ticker);
CREATE INDEX IF NOT EXISTS idx_trades_transaction_date ON trades(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_trades_transaction_type ON trades(transaction_type);

-- Create a view for the leaderboard
CREATE OR REPLACE VIEW leaderboard AS
SELECT 
    t.trader_id,
    t.name,
    t.title,
    t.company_ticker,
    t.company_name,
    t.total_trades,
    t.total_profit_loss,
    t.win_rate,
    t.avg_return_30d,
    t.avg_return_90d,
    t.avg_return_1y,
    t.performance_score,
    t.last_calculated
FROM traders t
WHERE t.total_trades > 0
ORDER BY t.performance_score DESC;

-- Sample data for testing (optional)
-- INSERT INTO traders (name, title, company_ticker, company_name, relationship_to_company) 
-- VALUES 
--     ('John Smith', 'CEO', 'AAPL', 'Apple Inc.', 'Chief Executive Officer'),
--     ('Jane Doe', 'CFO', 'MSFT', 'Microsoft Corporation', 'Chief Financial Officer');
