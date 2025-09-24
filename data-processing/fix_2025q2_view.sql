-- Fix the v_2025q2_complete view to use the correct column names
-- The issue is that the view is trying to join using company_id/insider_id
-- but the actual table uses company_cik/insider_cik

-- Drop all dependent views first
DROP VIEW IF EXISTS v_all_data_summary CASCADE;
DROP VIEW IF EXISTS v_2025q2_complete CASCADE;
DROP VIEW IF EXISTS v_2025q2_summary CASCADE;

CREATE OR REPLACE VIEW v_2025q2_complete AS
SELECT 
    t.id as transaction_id,
    t.accession_number,
    t.transaction_date,
    t.transaction_code,
    t.transaction_shares,
    t.transaction_price_per_share,
    t.calculated_transaction_value,
    t.shares_owned_following_transaction,
    t.security_title,
    c.name as company_name,
    c.ticker as company_ticker,
    c.cik as company_cik,
    i.name as insider_name,
    i.cik as insider_cik,
    i.is_director,
    i.is_officer,
    i.is_ten_percent_owner,
    '2025 Q2' as data_period
FROM transactions_2025q2 t
LEFT JOIN companies_2025q2 c ON t.company_cik = c.cik
LEFT JOIN insiders_2025q2 i ON t.insider_cik = i.cik;

-- Recreate the summary view

CREATE OR REPLACE VIEW v_2025q2_summary AS
SELECT 
    '2025 Q2' as period,
    COUNT(DISTINCT c.id) as total_companies,
    COUNT(DISTINCT i.id) as total_insiders,
    COUNT(t.id) as total_transactions,
    SUM(t.calculated_transaction_value) as total_transaction_value,
    MIN(t.transaction_date) as earliest_transaction,
    MAX(t.transaction_date) as latest_transaction
FROM transactions_2025q2 t
LEFT JOIN companies_2025q2 c ON t.company_cik = c.cik
LEFT JOIN insiders_2025q2 i ON t.insider_cik = i.cik;

-- Recreate the combined summary view
CREATE OR REPLACE VIEW v_all_data_summary AS
SELECT * FROM v_2025q2_summary
UNION ALL
SELECT * FROM v_historical_summary;

-- Add comments
COMMENT ON VIEW v_2025q2_complete IS 'Complete view of 2025 Q2 transactions with company and insider details (FIXED)';
COMMENT ON VIEW v_2025q2_summary IS 'Summary statistics for 2025 Q2 data (FIXED)';
COMMENT ON VIEW v_all_data_summary IS 'Combined summary of all data periods (RECREATED)';
