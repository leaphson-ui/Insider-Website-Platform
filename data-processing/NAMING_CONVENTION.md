# Database Naming Convention

## Schema Organization

### Historical Data (2006 and before)
- **Schema**: `schema_historical_2006_and_before`
- **Description**: Single consolidated database for historical SEC data
- **Tables**:
  - `companies_historical`
  - `insiders_historical`
  - `transactions_historical`

### Modern Data (2025 Q2)
- **Schema**: `schema_2025q2`
- **Description**: Quarterly database for 2025 Q2 SEC Form 4 filings
- **Tables**:
  - `companies_2025q2`
  - `insiders_2025q2`
  - `transactions_2025q2`

## Naming Convention Rules

### Schema Names
- Format: `schema_[period_description]`
- Examples:
  - `schema_historical_2006_and_before`
  - `schema_2025q2`
  - `schema_2025q3` (future)
  - `schema_2025q4` (future)

### Table Names
- Format: `[entity]_[period_description]`
- Examples:
  - `companies_historical`
  - `companies_2025q2`
  - `insiders_historical`
  - `insiders_2025q2`
  - `transactions_historical`
  - `transactions_2025q2`

### View Names
- Format: `v_[period_description]_[purpose]`
- Examples:
  - `v_historical_complete`
  - `v_2025q2_complete`
  - `v_historical_summary`
  - `v_2025q2_summary`
  - `v_all_data_summary`

## Data Access Patterns

### Querying Historical Data
```sql
-- Direct table access
SELECT * FROM schema_historical_2006_and_before.companies_historical;

-- Using views (recommended)
SELECT * FROM v_historical_complete;
```

### Querying 2025 Q2 Data
```sql
-- Direct table access
SELECT * FROM schema_2025q2.companies_2025q2;

-- Using views (recommended)
SELECT * FROM v_2025q2_complete;
```

### Querying All Data
```sql
-- Combined summary
SELECT * FROM v_all_data_summary;

-- Union queries for specific needs
SELECT * FROM v_historical_complete
UNION ALL
SELECT * FROM v_2025q2_complete;
```

## Future Expansion

### Adding New Quarters
When adding new quarterly data (e.g., 2025 Q3):

1. **Create new schema**: `schema_2025q3`
2. **Create tables**: `companies_2025q3`, `insiders_2025q3`, `transactions_2025q3`
3. **Create views**: `v_2025q3_complete`, `v_2025q3_summary`
4. **Update combined views** to include new data

### Adding New Years
When adding new years (e.g., 2026):

1. **Create quarterly schemas**: `schema_2026q1`, `schema_2026q2`, etc.
2. **Follow same naming pattern**
3. **Update combined views**

## Benefits of This Convention

### Clarity
- Immediately know what data is in each table
- Clear separation between time periods
- Self-documenting structure

### Organization
- Logical grouping by time period
- Easy to find specific data
- Scalable for future quarters/years

### Maintenance
- Easy to add new data
- Clear upgrade path
- Consistent patterns

### Performance
- Optimized queries per time period
- Efficient indexing
- Clear data boundaries

## Platform Integration

### Frontend Queries
```javascript
// Query specific time period
const recentData = await supabase
  .from('v_2025q2_complete')
  .select('*')
  .order('transaction_date', { ascending: false });

// Query historical data
const historicalData = await supabase
  .from('v_historical_complete')
  .select('*')
  .order('transaction_date', { ascending: false });

// Get summary statistics
const summary = await supabase
  .from('v_all_data_summary')
  .select('*');
```

### Backend Integration
```python
# Query specific schema
historical_companies = supabase.table('companies_historical', schema='schema_historical_2006_and_before').select('*').execute()

# Query using views (recommended)
recent_transactions = supabase.table('v_2025q2_complete').select('*').execute()
```

This naming convention ensures consistency, clarity, and scalability for your SEC data processing system.
