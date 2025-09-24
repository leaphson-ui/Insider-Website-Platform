# SEC Insider Trading Data Cleaning Pipeline

This directory contains scripts to test and implement the data cleaning pipeline for SEC Form 4 insider trading data with multi-file TSV structure.

## Quick Start

### 1. Set up environment
```bash
cd data-processing
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Download sample quarterly data
Download quarterly datasets from:
https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets

Each quarter contains multiple TSV files:
- `NONDERIV_TRANS.tsv` - Stock transactions
- `DERIV_TRANS.tsv` - Options/derivative transactions  
- `REPORTINGOWNER.tsv` - Insider information
- `SUBMISSION.tsv` - Filing metadata
- `NONDERIV_HOLDING.tsv` - Stock holdings
- `DERIV_HOLDING.tsv` - Derivative holdings
- `FOOTNOTES.tsv` - Additional notes
- `OWNER_SIGNATURE.tsv` - Signature details

### 3. Test multi-file pipeline
```bash
python test_multi_file_pipeline.py
```

## What the Pipeline Does

### Multi-File Processing:
1. **Analyze structure** - Understand file formats across different quarters
2. **Handle schema evolution** - Adapt to changes from 2006 to present
3. **Process transaction files** - NONDERIV_TRANS.tsv and DERIV_TRANS.tsv
4. **Process reference files** - REPORTINGOWNER.tsv, SUBMISSION.tsv, etc.
5. **Consolidate data** - Combine all files into unified format

### Data Cleaning Steps:
1. **Load TSV data** with proper encoding and schema handling
2. **Standardize dates** - convert various formats to ISO dates
3. **Clean transaction codes** - map to standard codes (P, S, A, etc.)
4. **Normalize numeric fields** - shares, prices, values
5. **Calculate missing values** - transaction value = shares × price
6. **Clean company/insider data** - standardize CIKs and names
7. **Handle schema differences** - adapt to changes over time
8. **Remove duplicates** - eliminate duplicate filings
9. **Add derived fields** - quarter/year, buy/sell flags

### Data Quality Validation:
- Total records processed
- Missing data statistics
- Date range coverage
- Unique companies/insiders
- Transaction code distribution

## Expected Output

After running the pipeline, you'll get:
- `cleaned_sample_data.csv` - processed data ready for Supabase
- Console output with data quality statistics
- Validation report showing data completeness

## Next Steps

Once data cleaning is validated:
1. Set up Supabase project
2. Create database schema
3. Import cleaned data
4. Build frontend dashboard

## Troubleshooting

### Common Issues:
- **Encoding errors**: The script tries multiple encodings automatically
- **Missing columns**: Adjust column names in the script if SEC format changes
- **Large files**: Use smaller sample files for initial testing
- **Memory issues**: Process files in chunks for very large datasets
