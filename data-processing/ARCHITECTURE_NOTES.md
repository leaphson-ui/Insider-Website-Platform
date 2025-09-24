# SEC Data Processing Architecture Notes

## Project Overview: Complete SEC Form 4 Data Processing System

This document outlines the architectural plan for processing and managing SEC Form 4 data (insider trading reports), which is complicated by the data's format and structural changes over time. The core challenge is integrating two fundamentally different data sets: Historical Data (2002 and before) and Modern Data (2003 onwards).

## Data Structure Evolution & Unknowns

### Known Structure Differences
- **2002 and before**: Single consolidated database with legacy format
- **2006**: Different structure (discovered during implementation)
- **2025 Q2**: Modern quarterly structure (discovered during implementation)

### Unknown Structure Variations
**Critical Challenge**: We know the data structure changes, but not when or how many times. The SEC's EDGAR system has evolved significantly, with major structural changes likely occurring at key regulatory milestones:

- **2003 (Post-Enron/Sarbanes-Oxley)**: Mandatory electronic filing transition
- **2009-2010 (XBRL/XML Adoption)**: Structured data requirements
- **2013-2015 (EDGAR Modernization)**: System updates and schema changes
- **2020-2023 (Recent Updates)**: Minor schema updates and field additions
- **2025+ (Current)**: Ongoing evolution (as seen in 2025 Q2 differences)

### Data Structure Risk & Investigation Plan
**Hypothesis**: Major structural changes occurred at regulatory milestones, with minor variations in between.

**Investigation Strategy**: 
1. **Schema Discovery**: Execute discovery scripts for each quarter 2003-2024
2. **Change Point Identification**: Document when and how structures evolved
3. **Transformation Mapping**: Create `transformer_<year>q<qtr>.py` for each unique structure
4. **Pattern Recognition**: Identify common transformation patterns across quarters

## Key Architectural Challenges

### 1. Data Structure Differences
- **2002 and before**: Custom format, single database
- **2003 onwards**: Quarterly databases with evolving SEC structure
- **CIK ranges**: Different time periods have different company/insider CIK ranges
- **Schema evolution**: SEC data structure changes over time

### 2. Foreign Key Relationships
- **Historical data**: Pre-established relationships
- **Quarterly data**: Each quarter silos its own CIK-based relationships
- **Overlap issues**: Companies/insiders may exist across multiple quarters
- **CIK format changes**: Different padding and formatting across time periods
- **Solution**: Entity Resolution to create permanent Master IDs for companies and insiders that persist across all time periods, regardless of CIK or name changes

### 3. Data Consolidation Strategy
- **Option 1**: Separate databases per quarter (current approach)
- **Option 2**: Massive consolidated database with complex deduplication
- **Option 3**: Hybrid approach with quarterly databases + consolidated view

## Project Phasing & Milestones

### Phase 1: Quarterly Processing (Current Focus)
**Goal**: Process and store each quarter's data in its own separate database to ensure raw, historical accuracy.

**Scope**: Process all quarters from 2003-2024, one quarter at a time, to isolate all structural variants.

**Deliverables**:
1. **Schema Discovery**: Document unique structure for each quarter
2. **Transformation Scripts**: Create `transformer_<year>q<qtr>.py` for each unique structure
3. **Quarterly Databases**: `transactions_<year>q<qtr>`, `companies_<year>q<qtr>`, `insiders_<year>q<qtr>`
4. **Optimized Views**: `v_<year>q<qtr>_complete` for frontend querying

**Dependencies**: Each quarter must be processed before consolidation can begin.

### Phase 2: Master Consolidation Project (Long-Term)
**Goal**: Create unified Master Tables to consolidate all quarterly and historical data.

**Master Tables Required**:
1. **Master Company Database**: Handle company lifecycle (mergers, acquisitions, name changes, delistings)
2. **Master Insider Database**: Handle insider changes (name variations, role changes, CIK reassignments)
3. **Master Transactions Database**: Link all transactions to consolidated master entities

**Entity Resolution Strategy**:
- **Master Company ID**: Never changes, regardless of CIK or ticker changes
- **Master Insider ID**: Never changes, regardless of name variations or role changes
- **Fuzzy Matching**: Required for insider name variations and company name changes

### Phase 3: Platform Integration
**Goal**: Make unified data available to the final platform/dashboard.

**Deliverables**:
1. **Unified Query Layer**: Seamlessly pull data from Master Tables and quarterly databases
2. **Performance Optimization**: Efficient querying across large datasets
3. **User Experience**: Consistent interface regardless of data source

## Implementation Notes

### Current Status (Updated September 2024)
- ✅ **2006 data**: Successfully processed and imported (685,544 transactions)
- ✅ **2025 Q2 data**: Successfully processed and imported (92,240 transactions)
- ✅ **Database views**: Fixed and working (`v_2025q2_complete`, `v_historical_complete`)
- ✅ **Data integrity**: 99.87% success rate for 2025 Q2 import
- ❌ **Data consolidation**: Not yet implemented (keeping quarterly approach)
- ❌ **Unified query layer**: Not yet implemented

### Phase 1 Roadmap: Complete Quarterly Processing (2024-2025)
**Immediate Next Steps**:
1. **✅ 2025 Q2 Complete** - 92,240 transactions processed
2. **Frontend Integration** - Update dashboard to query `v_2025q2_complete`
3. **Process 2025 Q3, Q4** - Apply quarterly-specific scripts
4. **Process 2024 Full Year** - Q1, Q2, Q3, Q4 with schema discovery
5. **Process 2023 Full Year** - Q1, Q2, Q3, Q4 with schema discovery
6. **Continue Backwards** - Process 2022, 2021, 2020... back to 2003

**Schema Discovery Process** (For Each Quarter):
1. **Download raw SEC data** for the quarter
2. **Execute schema discovery script** to identify unique structure
3. **Create transformation script** `transformer_<year>q<qtr>.py`
4. **Process and import data** with error handling
5. **Create optimized view** `v_<year>q<qtr>_complete`
6. **Document structure differences** for future reference

### Phase 2 Preparation: Master Consolidation Planning
**Long-term Preparation**:
1. **Entity Resolution Research** - Study company/insider lifecycle patterns
2. **Deduplication Algorithm Design** - Plan fuzzy matching strategies
3. **CIK Normalization Strategy** - Handle format changes across time
4. **Performance Planning** - Design for massive datasets (millions of records)

## Technical Considerations

### Database Design (Current Implementation)
- **✅ Quarterly databases**: `transactions_2025q2`, `companies_2025q2`, `insiders_2025q2`
- **✅ Database views**: `v_2025q2_complete` (92,240 records), `v_historical_complete` (685,544 records)
- **✅ Schema organization**: All data in `public` schema with descriptive naming
- **❌ Master database**: Not yet implemented (keeping quarterly approach)
- **❌ Data versioning**: Not yet implemented
- **✅ Performance**: Views optimized for large-scale queries

### Processing Pipeline (Current Implementation)
- **✅ Quarterly processors**: `process_2025_sec_data.py` handles 2025 Q2 structure
- **✅ Error handling**: `robust_import.py` with 99.87% success rate
- **✅ CIK normalization**: 10-digit padding implemented
- **✅ Data validation**: Float value handling, NaN/infinite value protection
- **❌ Deduplication logic**: Not needed for quarterly approach
- **❌ Cross-quarter mapping**: Not implemented (by design)

### Platform Integration (Current Status)
- **✅ Database views**: Working views for frontend integration
- **❌ Unified API**: Not implemented (using separate views)
- **✅ Data aggregation**: Views provide aggregated data
- **✅ Performance**: Views handle large datasets efficiently
- **✅ User experience**: Clean data with proper company/insider names

## Key Learnings from 2025 Q2 Implementation

### Data Import Challenges Discovered
- **Initial import failure**: Only 4,000 out of 76,330 transactions imported due to data quality issues
- **Float value problems**: Some records had infinite/NaN values causing JSON compliance errors
- **CIK format mismatches**: Different padding requirements between time periods
- **View relationship issues**: Views using wrong column names (`company_id` vs `company_cik`)

### Solutions Implemented
- **Robust import script**: `robust_import.py` with error handling for problematic records
- **Data validation**: Safe float conversion with NaN/infinite value protection
- **View fixes**: Updated `v_2025q2_complete` to use correct column mappings
- **Batch processing**: 100-record batches with error recovery

### Architecture Decisions Made
- **Quarterly approach confirmed**: Keep separate databases per quarter
- **Schema renaming abandoned**: All data stays in `public` schema for simplicity
- **View-based integration**: Use database views instead of master tables
- **Error tolerance**: 99.87% success rate acceptable for production

### Performance Insights
- **Large datasets**: 92,240 transactions processed efficiently
- **View performance**: `v_2025q2_complete` handles large datasets well
- **Memory management**: Batch processing prevents memory issues
- **Error recovery**: Graceful handling of problematic records

## Master Table Consolidation Strategy

### The Challenge
Creating a master table that consolidates all quarterly data requires handling:
- **Different SEC data structures** across quarters/years
- **CIK format evolution** (padding, ranges, formats)
- **Company/insider lifecycle** (delistings, name changes, ticker changes)
- **Schema evolution** (column names, data types, relationships)
- **Data quality issues** (missing values, format inconsistencies)

### Master Table Architecture
```python
# Pseudo-code for master consolidation
def create_master_table():
    master_transactions = []
    
    # Process each quarter with its unique structure
    for quarter in all_quarters:
        quarter_data = load_quarter_data(quarter)
        transformed_data = transform_quarter_format(quarter_data, quarter)
        master_transactions.extend(transformed_data)
    
    # Handle complex deduplication
    master_companies = deduplicate_companies(master_transactions)
    master_insiders = deduplicate_insiders(master_transactions)
    
    # Map foreign keys across time periods
    master_transactions = map_foreign_keys(master_transactions, master_companies, master_insiders)
    
    return master_transactions, master_companies, master_insiders
```

### Entity Resolution and Master ID Assignment
The master table consolidation will require sophisticated entity resolution:

**Company Entity Resolution**:
- **Master Company ID**: Permanent identifier that never changes
- **CIK Mapping**: Handle CIK changes, reassignments, and format variations
- **Name Variations**: Handle company name changes, mergers, acquisitions
- **Ticker Mapping**: Track ticker changes and delistings
- **Lifecycle Management**: Handle company delistings and re-listings

**Insider Entity Resolution**:
- **Master Insider ID**: Permanent identifier that never changes
- **Name Variations**: Handle minor name differences (middle initials, nicknames)
- **Role Changes**: Track position changes within same company
- **CIK Reassignments**: Handle insider CIK changes
- **Fuzzy Matching**: Required for name variations and typos

**Transaction Mapping**:
- **Foreign Key Resolution**: Link all transactions to master entities
- **Historical Accuracy**: Maintain original transaction data integrity
- **Cross-Quarter Tracking**: Enable tracking entities across time periods

### Implementation Options

#### Option A: Keep Separate (Recommended for now)
- **Pros**: Simpler, more maintainable, preserves data integrity
- **Cons**: More complex frontend queries, no unified view
- **Use case**: Current approach, good for development

#### Option B: Create Master Table
- **Pros**: Unified view, simpler frontend, better performance
- **Cons**: Extremely complex implementation, data loss risk
- **Use case**: Production system with mature data processing

#### Option C: Hybrid Approach
- **Pros**: Best of both worlds, gradual migration
- **Cons**: More complex architecture
- **Use case**: Long-term solution

### Master Table Implementation Phases

#### Phase 1: Data Structure Documentation
- Document each quarter's unique structure
- Create transformation mappings
- Identify common patterns and differences

#### Phase 2: Deduplication Logic
- Implement company deduplication (name changes, ticker changes)
- Implement insider deduplication (role changes, name variations)
- Handle CIK format differences

#### Phase 3: Master Table Creation
- Build complex consolidation script
- Handle all edge cases and data quality issues
- Implement data validation and consistency checks

#### Phase 4: Platform Integration
- Create unified query interface
- Implement performance optimizations
- Handle real-time updates for new quarters

### Technical Requirements
- **Complex Python scripts** for data transformation
- **Advanced SQL** for deduplication and mapping
- **Data validation** pipelines
- **Performance optimization** for large datasets
- **Error handling** for data quality issues

## Project Flow Summary

The complete project follows a clear, sequential flow:

**Schema Discovery → Data Transformation → Entity Resolution → Unified Query Layer**

### Phase 1: Schema Discovery & Data Transformation
1. **Process each quarter** (2003-2024) to discover unique structures
2. **Create transformation scripts** for each structural variant
3. **Build quarterly databases** with optimized views
4. **Document all structural differences** for future reference

### Phase 2: Entity Resolution & Master Consolidation
1. **Create Master Company IDs** that never change across time
2. **Create Master Insider IDs** that never change across time
3. **Build deduplication logic** for name variations and changes
4. **Link all transactions** to consolidated master entities

### Phase 3: Unified Query Layer & Platform Integration
1. **Build unified query interface** across all data sources
2. **Implement performance optimizations** for large datasets
3. **Create seamless user experience** regardless of data source

## Conclusion

This architecture successfully addresses the core challenge of SEC data evolution by:
1. **Acknowledging unknowns** - We know structures change, but not when/how
2. **Providing investigation strategy** - Systematic schema discovery approach
3. **Offering robust solution** - Master ID-based entity resolution
4. **Ensuring scalability** - Handles future quarters and regulatory changes

The master table consolidation with Entity Resolution is the most challenging but necessary component, requiring sophisticated data processing and deduplication logic to create a truly unified platform.
