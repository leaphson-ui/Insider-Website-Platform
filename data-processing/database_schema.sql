-- SEC Insider Transactions Database Schema
-- Designed for fail-safe processing with duplicate prevention

-- Drop existing table if it exists (for clean start)
DROP TABLE IF EXISTS insider_transactions;

-- Create main transactions table
CREATE TABLE insider_transactions (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- Unique identifier (prevents duplicates)
    accession_number VARCHAR(50) NOT NULL,
    quarter VARCHAR(50) NOT NULL,
    
    -- Company information
    company_cik VARCHAR(20) NOT NULL,
    company_name VARCHAR(1000),
    company_ticker VARCHAR(20),
    company_sector VARCHAR(200), -- Will be populated later via external data source
    
    -- Insider information
    insider_cik VARCHAR(20) NOT NULL,
    insider_name VARCHAR(1000),
    insider_relationship VARCHAR(200),
    insider_title VARCHAR(500),
    
           -- Transaction details
           transaction_date DATE,
           transaction_code VARCHAR(10),
           transaction_type VARCHAR(50),
           transaction_shares DECIMAL(20,2),
           transaction_price_per_share DECIMAL(20,2),
           calculated_transaction_value DECIMAL(20,2),
           shares_owned_following_transaction DECIMAL(20,2),
           transaction_sk VARCHAR(50), -- Transaction surrogate key for true uniqueness
    
    -- Security information
    security_title VARCHAR(500),
    
    -- Metadata
    file_type VARCHAR(10),
    data_source VARCHAR(50),
    year INTEGER,
    
    -- Additional fields from all 8 TSV files
    footnote_id VARCHAR(50),
    footnote_txt TEXT,
    owner_signature_name VARCHAR(500),
    owner_signature_date DATE,
    aff10b5one VARCHAR(10), -- Post-2023 specific field
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create unique constraint to prevent duplicates
-- This is the key constraint that prevents duplicate processing
-- Uses transaction surrogate key for true uniqueness
CREATE UNIQUE INDEX idx_unique_transaction_insider_sk 
ON insider_transactions(accession_number, transaction_date, insider_cik, transaction_code, transaction_sk);

-- Create indexes for efficient querying
CREATE INDEX idx_company_cik ON insider_transactions(company_cik);
CREATE INDEX idx_insider_cik ON insider_transactions(insider_cik);
CREATE INDEX idx_transaction_date ON insider_transactions(transaction_date);
CREATE INDEX idx_quarter ON insider_transactions(quarter);
CREATE INDEX idx_company_ticker ON insider_transactions(company_ticker);
CREATE INDEX idx_insider_name ON insider_transactions(insider_name);

-- Create composite indexes for common queries
CREATE INDEX idx_company_date ON insider_transactions(company_cik, transaction_date);
CREATE INDEX idx_insider_date ON insider_transactions(insider_cik, transaction_date);
CREATE INDEX idx_quarter_date ON insider_transactions(quarter, transaction_date);

-- Add comments for documentation
COMMENT ON TABLE insider_transactions IS 'SEC Form 4 insider transactions with duplicate prevention';
COMMENT ON COLUMN insider_transactions.accession_number IS 'Unique SEC filing identifier';
COMMENT ON COLUMN insider_transactions.quarter IS 'Quarter identifier (e.g., 2025q2)';
COMMENT ON COLUMN insider_transactions.company_cik IS 'Company CIK identifier';
COMMENT ON COLUMN insider_transactions.insider_cik IS 'Insider CIK identifier';
COMMENT ON COLUMN insider_transactions.transaction_date IS 'Date of transaction';
COMMENT ON COLUMN insider_transactions.transaction_code IS 'SEC transaction code (P, S, A, D, etc.)';
COMMENT ON COLUMN insider_transactions.calculated_transaction_value IS 'Shares * Price per share';
COMMENT ON COLUMN insider_transactions.company_sector IS 'Company sector (populated later via external data source)';

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_transactions_updated_at 
    BEFORE UPDATE ON insider_transactions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
