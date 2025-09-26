#!/usr/bin/env python3
"""
Post-2023 SEC Data Processor
Handles quarters 2023q1 through 2025q2 with 14-column SUBMISSION.tsv (includes AFF10B5ONE)
"""

import pandas as pd
import os
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Post2023Processor:
    def __init__(self, data_dir: str, supabase_url: str, supabase_key: str):
        """Initialize processor for post-2023 SEC data"""
        self.data_dir = Path(data_dir)
        self.supabase = create_client(supabase_url, supabase_key)
        self.processed_data = {}
        
    def process_quarter(self, quarter: str) -> Dict:
        """Process a single quarter with post-2023 format"""
        logger.info(f"🔄 Processing {quarter} with post-2023 format...")
        
        # Check if already processed
        if self.is_quarter_processed(quarter):
            logger.info(f"✅ {quarter} already processed, skipping")
            return {'status': 'already_processed', 'quarter': quarter}
        
        try:
            # Step 1: Extract ZIP file
            zip_path = self.data_dir / f"{quarter}.zip"
            if not zip_path.exists():
                raise FileNotFoundError(f"ZIP file not found: {zip_path}")
            
            extract_dir = self.data_dir / f"temp_{quarter}"
            self.extract_zip(zip_path, extract_dir)
            
            # Step 2: Load and process all 8 TSV files
            submission_df = self.load_submission_file(extract_dir)
            reporting_owner_df = self.load_reporting_owner_file(extract_dir)
            nonderiv_trans_df = self.load_nonderiv_trans_file(extract_dir)
            deriv_trans_df = self.load_deriv_trans_file(extract_dir)
            nonderiv_holding_df = self.load_nonderiv_holding_file(extract_dir)
            deriv_holding_df = self.load_deriv_holding_file(extract_dir)
            footnotes_df = self.load_footnotes_file(extract_dir)
            owner_signature_df = self.load_owner_signature_file(extract_dir)
            
            logger.info(f"📊 Loaded all 8 files for {quarter}:")
            logger.info(f"  - SUBMISSION: {len(submission_df)} records")
            logger.info(f"  - REPORTINGOWNER: {len(reporting_owner_df)} records")
            logger.info(f"  - NONDERIV_TRANS: {len(nonderiv_trans_df)} records")
            logger.info(f"  - DERIV_TRANS: {len(deriv_trans_df)} records")
            logger.info(f"  - NONDERIV_HOLDING: {len(nonderiv_holding_df)} records")
            logger.info(f"  - DERIV_HOLDING: {len(deriv_holding_df)} records")
            logger.info(f"  - FOOTNOTES: {len(footnotes_df)} records")
            logger.info(f"  - OWNER_SIGNATURE: {len(owner_signature_df)} records")
            
            # Step 3: Join all transaction data from all 8 files
            all_transactions = self.join_all_data(
                submission_df, reporting_owner_df, nonderiv_trans_df, deriv_trans_df,
                nonderiv_holding_df, deriv_holding_df, footnotes_df, owner_signature_df, quarter
            )
            
            logger.info(f"📈 Total transactions to process: {len(all_transactions)}")
            
            # Step 4: Insert to database with duplicate prevention
            result = self.insert_to_database(all_transactions, quarter)
            
            # Step 5: Validate no duplicates created
            self.validate_no_duplicates(quarter)
            
            # Step 6: Clean up temp files
            self.cleanup_temp_files(extract_dir)
            
            logger.info(f"✅ Successfully processed {quarter}")
            return {
                'status': 'success',
                'quarter': quarter,
                'transactions_processed': len(all_transactions),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing {quarter}: {e}")
            # Clean up temp files on error
            if 'extract_dir' in locals():
                self.cleanup_temp_files(extract_dir)
            raise
    
    def is_quarter_processed(self, quarter: str) -> bool:
        """Check if quarter is already processed"""
        try:
            result = self.supabase.table('insider_transactions').select('id').eq('quarter', quarter).limit(1).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.warning(f"Could not check if {quarter} is processed: {e}")
            return False
    
    def extract_zip(self, zip_path: Path, extract_dir: Path):
        """Extract ZIP file to temporary directory"""
        logger.info(f"📦 Extracting {zip_path.name}...")
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    
    def load_submission_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load SUBMISSION.tsv file (14 columns with AFF10B5ONE)"""
        file_path = extract_dir / 'SUBMISSION.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean company data
        df['ISSUERCIK'] = df['ISSUERCIK'].astype(str).str.strip().str.zfill(10)
        df['ISSUERNAME'] = df['ISSUERNAME'].astype(str).str.strip()
        df['ISSUERTRADINGSYMBOL'] = df['ISSUERTRADINGSYMBOL'].astype(str).str.strip()
        
        # Handle AFF10B5ONE column (post-2023 only)
        if 'AFF10B5ONE' in df.columns:
            df['AFF10B5ONE'] = df['AFF10B5ONE'].astype(str).str.strip()
        else:
            df['AFF10B5ONE'] = None
        
        logger.info(f"  ✅ Loaded {len(df)} submission records")
        return df
    
    def load_reporting_owner_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load REPORTINGOWNER.tsv file"""
        file_path = extract_dir / 'REPORTINGOWNER.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean insider data
        df['RPTOWNERCIK'] = df['RPTOWNERCIK'].astype(str).str.strip().str.zfill(10)
        df['RPTOWNERNAME'] = df['RPTOWNERNAME'].astype(str).str.strip()
        df['RPTOWNER_RELATIONSHIP'] = df['RPTOWNER_RELATIONSHIP'].astype(str).str.strip()
        
        logger.info(f"  ✅ Loaded {len(df)} reporting owner records")
        return df
    
    def load_nonderiv_trans_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load NONDERIV_TRANS.tsv file"""
        file_path = extract_dir / 'NONDERIV_TRANS.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean transaction data
        df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'], errors='coerce')
        df['TRANS_CODE'] = df['TRANS_CODE'].astype(str).str.strip().str.upper()
        
        # Clean numeric fields
        numeric_cols = ['TRANS_SHARES', 'TRANS_PRICEPERSHARE', 'SHRS_OWND_FOLWNG_TRANS']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate transaction value
        df['CALCULATED_TRANSACTION_VALUE'] = df['TRANS_SHARES'] * df['TRANS_PRICEPERSHARE']
        
        logger.info(f"  ✅ Loaded {len(df)} non-derivative transaction records")
        return df
    
    def load_deriv_trans_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load DERIV_TRANS.tsv file"""
        file_path = extract_dir / 'DERIV_TRANS.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean transaction data
        df['TRANS_DATE'] = pd.to_datetime(df['TRANS_DATE'], errors='coerce')
        df['TRANS_CODE'] = df['TRANS_CODE'].astype(str).str.strip().str.upper()
        
        # Clean numeric fields
        numeric_cols = ['TRANS_SHARES', 'TRANS_PRICEPERSHARE', 'SHRS_OWND_FOLWNG_TRANS']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate transaction value
        df['CALCULATED_TRANSACTION_VALUE'] = df['TRANS_SHARES'] * df['TRANS_PRICEPERSHARE']
        
        logger.info(f"  ✅ Loaded {len(df)} derivative transaction records")
        return df
    
    def load_nonderiv_holding_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load NONDERIV_HOLDING.tsv file"""
        file_path = extract_dir / 'NONDERIV_HOLDING.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean numeric fields
        numeric_cols = ['SHRS_OWND_FOLWNG_TRANS', 'VALU_OWND_FOLWNG_TRANS']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"  ✅ Loaded {len(df)} non-derivative holding records")
        return df
    
    def load_deriv_holding_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load DERIV_HOLDING.tsv file"""
        file_path = extract_dir / 'DERIV_HOLDING.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean numeric fields
        numeric_cols = ['SHRS_OWND_FOLWNG_TRANS', 'VALU_OWND_FOLWNG_TRANS']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"  ✅ Loaded {len(df)} derivative holding records")
        return df
    
    def load_footnotes_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load FOOTNOTES.tsv file"""
        file_path = extract_dir / 'FOOTNOTES.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean text fields
        if 'FOOTNOTE_TXT' in df.columns:
            df['FOOTNOTE_TXT'] = df['FOOTNOTE_TXT'].astype(str).str.strip()
        
        logger.info(f"  ✅ Loaded {len(df)} footnote records")
        return df
    
    def load_owner_signature_file(self, extract_dir: Path) -> pd.DataFrame:
        """Load OWNER_SIGNATURE.tsv file"""
        file_path = extract_dir / 'OWNER_SIGNATURE.tsv'
        logger.info(f"📄 Loading {file_path.name}")
        
        df = pd.read_csv(file_path, sep='\t', low_memory=False)
        
        # Clean date fields
        if 'OWNERSIGNATUREDATE' in df.columns:
            df['OWNERSIGNATUREDATE'] = pd.to_datetime(df['OWNERSIGNATUREDATE'], errors='coerce')
        
        # Clean text fields
        if 'OWNERSIGNATURENAME' in df.columns:
            df['OWNERSIGNATURENAME'] = df['OWNERSIGNATURENAME'].astype(str).str.strip()
        
        logger.info(f"  ✅ Loaded {len(df)} owner signature records")
        return df
    
    def join_all_data(self, submission_df: pd.DataFrame, reporting_owner_df: pd.DataFrame, 
                     nonderiv_trans_df: pd.DataFrame, deriv_trans_df: pd.DataFrame,
                     nonderiv_holding_df: pd.DataFrame, deriv_holding_df: pd.DataFrame,
                     footnotes_df: pd.DataFrame, owner_signature_df: pd.DataFrame, 
                     quarter: str) -> pd.DataFrame:
        """Join all transaction data from all 8 TSV files using vectorized operations"""
        logger.info("🔗 Joining all data from 8 TSV files using vectorized approach...")
        
        # Combine all transactions
        all_transactions = []
        
        # Process non-derivative transactions with vectorized operations
        if not nonderiv_trans_df.empty:
            logger.info(f"  📊 Processing {len(nonderiv_trans_df)} non-derivative transactions...")
            
            # Vectorized approach: Use pandas merge operations instead of iterrows()
            logger.info(f"  🔄 Creating filing-level cartesian product using vectorized operations...")
            
            # Step 1: Merge transactions with submission data (company info)
            nonderiv_with_company = nonderiv_trans_df.merge(
                submission_df, 
                on='ACCESSION_NUMBER', 
                how='left',
                suffixes=('', '_sub')
            )
            
            # Step 2: Merge with reporting owners (insider info) - this creates the cartesian product
            nonderiv_with_insiders = nonderiv_with_company.merge(
                reporting_owner_df,
                on='ACCESSION_NUMBER',
                how='inner',  # Only include transactions with insiders
                suffixes=('', '_owner')
            )
            
            # Step 3: Add holdings data if available
            if not nonderiv_holding_df.empty:
                # Get first holding record per filing (most filings have only one)
                nonderiv_holding_first = nonderiv_holding_df.groupby('ACCESSION_NUMBER').first().reset_index()
                # Only merge if the columns don't already exist to avoid conflicts
                holding_cols = ['ACCESSION_NUMBER']
                if 'SHRS_OWND_FOLWNG_TRANS' not in nonderiv_with_insiders.columns:
                    holding_cols.append('SHRS_OWND_FOLWNG_TRANS')
                if 'VALU_OWND_FOLWNG_TRANS' not in nonderiv_with_insiders.columns:
                    holding_cols.append('VALU_OWND_FOLWNG_TRANS')
                
                if len(holding_cols) > 1:  # More than just ACCESSION_NUMBER
                    nonderiv_with_insiders = nonderiv_with_insiders.merge(
                        nonderiv_holding_first[holding_cols],
                        on='ACCESSION_NUMBER',
                        how='left'
                    )
            
            # Step 4: Add footnotes if available
            if not footnotes_df.empty:
                # Get first footnote per filing
                footnotes_first = footnotes_df.groupby('ACCESSION_NUMBER').first().reset_index()
                nonderiv_with_insiders = nonderiv_with_insiders.merge(
                    footnotes_first[['ACCESSION_NUMBER', 'FOOTNOTE_ID', 'FOOTNOTE_TXT']],
                    on='ACCESSION_NUMBER',
                    how='left'
                )
            
            # Step 5: Add signature data if available
            if not owner_signature_df.empty:
                # Get first signature per filing
                signature_first = owner_signature_df.groupby('ACCESSION_NUMBER').first().reset_index()
                nonderiv_with_insiders = nonderiv_with_insiders.merge(
                    signature_first[['ACCESSION_NUMBER', 'OWNERSIGNATURENAME', 'OWNERSIGNATUREDATE']],
                    on='ACCESSION_NUMBER',
                    how='left'
                )
            
            # Add transaction type
            nonderiv_with_insiders['TRANSACTION_TYPE'] = 'Non-Derivative'
            
            all_transactions.append(nonderiv_with_insiders)
            logger.info(f"  ✅ Created {len(nonderiv_with_insiders)} non-derivative transaction-insider records")
        
        # Process derivative transactions with vectorized operations
        if not deriv_trans_df.empty:
            logger.info(f"  📊 Processing {len(deriv_trans_df)} derivative transactions...")
            
            # Vectorized approach: Use pandas merge operations instead of iterrows()
            logger.info(f"  🔄 Creating filing-level cartesian product using vectorized operations...")
            
            # Step 1: Merge transactions with submission data (company info)
            deriv_with_company = deriv_trans_df.merge(
                submission_df, 
                on='ACCESSION_NUMBER', 
                how='left',
                suffixes=('', '_sub')
            )
            
            # Step 2: Merge with reporting owners (insider info) - this creates the cartesian product
            deriv_with_insiders = deriv_with_company.merge(
                reporting_owner_df,
                on='ACCESSION_NUMBER',
                how='inner',  # Only include transactions with insiders
                suffixes=('', '_owner')
            )
            
            # Step 3: Add holdings data if available
            if not deriv_holding_df.empty:
                # Get first holding record per filing
                deriv_holding_first = deriv_holding_df.groupby('ACCESSION_NUMBER').first().reset_index()
                # Only merge if the columns don't already exist to avoid conflicts
                holding_cols = ['ACCESSION_NUMBER']
                if 'SHRS_OWND_FOLWNG_TRANS' not in deriv_with_insiders.columns:
                    holding_cols.append('SHRS_OWND_FOLWNG_TRANS')
                if 'VALU_OWND_FOLWNG_TRANS' not in deriv_with_insiders.columns:
                    holding_cols.append('VALU_OWND_FOLWNG_TRANS')
                
                if len(holding_cols) > 1:  # More than just ACCESSION_NUMBER
                    deriv_with_insiders = deriv_with_insiders.merge(
                        deriv_holding_first[holding_cols],
                        on='ACCESSION_NUMBER',
                        how='left'
                    )
            
            # Step 4: Add footnotes if available
            if not footnotes_df.empty:
                # Get first footnote per filing
                footnotes_first = footnotes_df.groupby('ACCESSION_NUMBER').first().reset_index()
                deriv_with_insiders = deriv_with_insiders.merge(
                    footnotes_first[['ACCESSION_NUMBER', 'FOOTNOTE_ID', 'FOOTNOTE_TXT']],
                    on='ACCESSION_NUMBER',
                    how='left'
                )
            
            # Step 5: Add signature data if available
            if not owner_signature_df.empty:
                # Get first signature per filing
                signature_first = owner_signature_df.groupby('ACCESSION_NUMBER').first().reset_index()
                deriv_with_insiders = deriv_with_insiders.merge(
                    signature_first[['ACCESSION_NUMBER', 'OWNERSIGNATURENAME', 'OWNERSIGNATUREDATE']],
                    on='ACCESSION_NUMBER',
                    how='left'
                )
            
            # Add transaction type
            deriv_with_insiders['TRANSACTION_TYPE'] = 'Derivative'
            
            all_transactions.append(deriv_with_insiders)
            logger.info(f"  ✅ Created {len(deriv_with_insiders)} derivative transaction-insider records")
        
        # Combine all transactions
        if all_transactions:
            combined_df = pd.concat(all_transactions, ignore_index=True)
        else:
            combined_df = pd.DataFrame()

        # Add metadata
        combined_df['QUARTER'] = quarter
        combined_df['YEAR'] = int(quarter[:4])
        combined_df['FILE_TYPE'] = '4'
        combined_df['DATA_SOURCE'] = 'SEC_EDGAR'
        
        # CRITICAL: Remove duplicates within the same batch to prevent constraint violations
        # This prevents the same (accession_number, transaction_date, insider_cik, transaction_code) 
        # combination from appearing multiple times in the same batch
        logger.info(f"  🔍 Checking for batch duplicates in {len(combined_df)} records...")
        initial_count = len(combined_df)
        
        # Create a unique key based on the database constraint
        # Use transaction surrogate key (NONDERIV_TRANS_SK or DERIV_TRANS_SK) for true uniqueness
        combined_df['_batch_unique_key'] = (
            combined_df['ACCESSION_NUMBER'].astype(str) + '_' +
            combined_df['TRANS_DATE'].astype(str) + '_' +
            combined_df['RPTOWNERCIK'].astype(str) + '_' +
            combined_df['TRANS_CODE'].astype(str) + '_' +
            combined_df.get('NONDERIV_TRANS_SK', combined_df.get('DERIV_TRANS_SK', '')).astype(str)
        )
        
        # Remove duplicates within the batch
        combined_df = combined_df.drop_duplicates(subset=['_batch_unique_key'], keep='first')
        combined_df = combined_df.drop('_batch_unique_key', axis=1)
        
        duplicates_removed = initial_count - len(combined_df)
        if duplicates_removed > 0:
            logger.warning(f"  ⚠️ Removed {duplicates_removed} batch duplicates")
        
        logger.info(f"  ✅ Combined {len(combined_df)} total transactions (after batch deduplication)")
        return combined_df
    
    def insert_to_database(self, transactions_df: pd.DataFrame, quarter: str) -> Dict:
        """Insert transactions to database with duplicate prevention"""
        logger.info(f"💾 Inserting {len(transactions_df)} transactions to database...")
        
        # Transform to database schema
        db_records = []
        for _, row in transactions_df.iterrows():
            # Convert Timestamp objects to strings for JSON serialization
            transaction_date = row['TRANS_DATE']
            if pd.notna(transaction_date) and hasattr(transaction_date, 'date'):
                transaction_date = transaction_date.date().isoformat()
            elif pd.notna(transaction_date):
                transaction_date = transaction_date.isoformat()
            else:
                transaction_date = None
            
            owner_signature_date = row.get('OWNERSIGNATUREDATE', None)
            if pd.notna(owner_signature_date) and hasattr(owner_signature_date, 'date'):
                owner_signature_date = owner_signature_date.date().isoformat()
            elif pd.notna(owner_signature_date):
                owner_signature_date = owner_signature_date.isoformat()
            else:
                owner_signature_date = None
            
            # Clean up NaN values and convert to JSON-serializable format
            def clean_value(value):
                if pd.isna(value):
                    return None
                if isinstance(value, float) and (value != value):  # Check for NaN
                    return None
                if isinstance(value, float) and (value == float('inf') or value == float('-inf')):
                    return None
                return value
            
            record = {
                       'accession_number': row['ACCESSION_NUMBER'],
                       'quarter': quarter,
                       'company_cik': row['ISSUERCIK'],
                       'company_name': clean_value(row['ISSUERNAME']),
                       'company_ticker': clean_value(row['ISSUERTRADINGSYMBOL']),
                       'company_sector': None,  # Will be populated later via external data source
                       'insider_cik': row['RPTOWNERCIK'],
                       'insider_name': clean_value(row['RPTOWNERNAME']),
                       'insider_relationship': clean_value(row['RPTOWNER_RELATIONSHIP']),
                       'insider_title': clean_value(row.get('RPTOWNER_TITLE', '')),
                       'transaction_date': transaction_date,
                       'transaction_code': clean_value(row['TRANS_CODE']),
                       'transaction_type': row['TRANSACTION_TYPE'],
                       'transaction_shares': clean_value(row['TRANS_SHARES']),
                       'transaction_price_per_share': clean_value(row['TRANS_PRICEPERSHARE']),
                       'calculated_transaction_value': clean_value(row['CALCULATED_TRANSACTION_VALUE']),
                       'shares_owned_following_transaction': clean_value(row['SHRS_OWND_FOLWNG_TRANS']),
                       'transaction_sk': clean_value(row.get('NONDERIV_TRANS_SK', row.get('DERIV_TRANS_SK', ''))),  # Transaction surrogate key
                       'security_title': clean_value(row.get('SECURITY_TITLE', '')),
                       'file_type': row['FILE_TYPE'],
                       'data_source': row['DATA_SOURCE'],
                       'year': row['YEAR'],
                       # Additional fields from all 8 TSV files
                       'footnote_id': clean_value(row.get('FOOTNOTE_ID', '')),
                       'footnote_txt': clean_value(row.get('FOOTNOTE_TXT', '')),
                       'owner_signature_name': clean_value(row.get('OWNERSIGNATURENAME', '')),
                       'owner_signature_date': owner_signature_date,
                       'aff10b5one': clean_value(row.get('AFF10B5ONE', None))  # Post-2023 specific field
                   }
            db_records.append(record)
        
        # Validate required fields before inserting
        self.validate_transaction_data(db_records)
        
        # Insert in batches to avoid timeouts
        batch_size = 25  # Reduced batch size to prevent Supabase timeouts
        total_inserted = 0
        
        for i in range(0, len(db_records), batch_size):
            batch = db_records[i:i + batch_size]
            try:
                result = self.supabase.table('insider_transactions').insert(batch).execute()
                total_inserted += len(batch)
                logger.info(f"  📊 Inserted batch {i//batch_size + 1}: {len(batch)} records")
            except Exception as e:
                logger.error(f"❌ Error inserting batch {i//batch_size + 1}: {e}")
                # Log the problematic batch for debugging
                logger.error(f"Problematic batch: {batch[:2]}...")  # Show first 2 records
                raise
        
        logger.info(f"✅ Successfully inserted {total_inserted} transactions")
        return {'inserted': total_inserted, 'quarter': quarter}
    
    def validate_transaction_data(self, db_records: List[Dict]):
        """Comprehensive data quality validation before insertion"""
        logger.info("🔍 Validating transaction data quality...")
        
        # Define valid values for validation
        valid_transaction_codes = ['P', 'S', 'A', 'D', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'U', 'V', 'W', 'X', 'Y', 'Z']
        valid_relationships = ['CEO', 'CFO', 'Director', 'Officer', '10% Owner', 'Other', 'President', 'Vice President', 'Secretary', 'Treasurer']
        
        required_fields = ['accession_number', 'quarter', 'company_cik', 'insider_cik']
        validation_errors = []
        validation_warnings = []
        
        for i, record in enumerate(db_records):
            # 1. Required field validation
            for field in required_fields:
                if not record.get(field):
                    validation_errors.append(f"Record {i}: Missing required field '{field}'")
            
            # 2. Transaction code validation
            if record.get('transaction_code'):
                if record['transaction_code'] not in valid_transaction_codes:
                    validation_warnings.append(f"Record {i}: Invalid transaction code '{record['transaction_code']}'")
            
            # 3. Date validation
            if record.get('transaction_date'):
                trans_date = record['transaction_date']
                # Convert to date object for comparison
                if hasattr(trans_date, 'date'):
                    trans_date = trans_date.date()
                elif isinstance(trans_date, str):
                    trans_date = datetime.strptime(trans_date, '%Y-%m-%d').date()
                
                if trans_date > datetime.now().date():
                    validation_warnings.append(f"Record {i}: Future transaction date {trans_date}")
                if trans_date < datetime(2006, 1, 1).date():
                    validation_warnings.append(f"Record {i}: Transaction date before 2006: {trans_date}")
            
            # 4. Amount validation
            if record.get('transaction_shares') is not None:
                if record['transaction_shares'] < 0:
                    validation_warnings.append(f"Record {i}: Negative shares {record['transaction_shares']}")
                if record['transaction_shares'] > 1000000000:  # 1 billion shares
                    validation_warnings.append(f"Record {i}: Suspiciously large share count {record['transaction_shares']}")
            
            if record.get('transaction_price_per_share') is not None:
                if record['transaction_price_per_share'] <= 0:
                    validation_warnings.append(f"Record {i}: Invalid price {record['transaction_price_per_share']}")
                if record['transaction_price_per_share'] > 10000:  # $10,000 per share
                    validation_warnings.append(f"Record {i}: Suspiciously high price {record['transaction_price_per_share']}")
            
            # 5. Relationship validation
            if record.get('insider_relationship'):
                if record['insider_relationship'] not in valid_relationships:
                    validation_warnings.append(f"Record {i}: Unusual relationship '{record['insider_relationship']}'")
            
            # 6. CIK validation (should be 10 digits)
            if record.get('company_cik'):
                if not str(record['company_cik']).isdigit() or len(str(record['company_cik'])) != 10:
                    validation_warnings.append(f"Record {i}: Invalid company CIK format {record['company_cik']}")
            
            if record.get('insider_cik'):
                if not str(record['insider_cik']).isdigit() or len(str(record['insider_cik'])) != 10:
                    validation_warnings.append(f"Record {i}: Invalid insider CIK format {record['insider_cik']}")
            
            # 7. Calculated value validation
            if record.get('calculated_transaction_value') is not None:
                if record['calculated_transaction_value'] < 0:
                    validation_warnings.append(f"Record {i}: Negative transaction value {record['calculated_transaction_value']}")
                if record['calculated_transaction_value'] > 1000000000:  # $1 billion
                    validation_warnings.append(f"Record {i}: Suspiciously large transaction value {record['calculated_transaction_value']}")
        
        # Report validation results
        if validation_errors:
            logger.error(f"❌ Found {len(validation_errors)} validation errors:")
            for error in validation_errors[:10]:  # Show first 10 errors
                logger.error(f"  - {error}")
            if len(validation_errors) > 10:
                logger.error(f"  ... and {len(validation_errors) - 10} more errors")
            raise ValueError(f"Data validation failed with {len(validation_errors)} errors")
        
        if validation_warnings:
            logger.warning(f"⚠️ Found {len(validation_warnings)} validation warnings:")
            for warning in validation_warnings[:10]:  # Show first 10 warnings
                logger.warning(f"  - {warning}")
            if len(validation_warnings) > 10:
                logger.warning(f"  ... and {len(validation_warnings) - 10} more warnings")
        
        logger.info(f"✅ Validated {len(db_records)} records - {len(validation_errors)} errors, {len(validation_warnings)} warnings")
    
    def validate_no_duplicates(self, quarter: str):
        """Validate no duplicates were created"""
        logger.info(f"🔍 Validating no duplicates in {quarter}...")
        
        try:
            # Check for duplicate records using the same unique constraint as the database
            result = self.supabase.table('insider_transactions').select('accession_number,transaction_date,insider_cik,transaction_code,transaction_sk').eq('quarter', quarter).execute()
            
            # Create unique keys for each record (same as our unique constraint)
            unique_keys = []
            for record in result.data:
                key = f"{record['accession_number']}_{record['transaction_date']}_{record['insider_cik']}_{record['transaction_code']}_{record['transaction_sk']}"
                unique_keys.append(key)
            
            duplicates = len(unique_keys) - len(set(unique_keys))
            
            if duplicates > 0:
                logger.error(f"❌ Found {duplicates} duplicate records in {quarter}")
                raise Exception(f"❌ Found {duplicates} duplicate records in {quarter}")
            
            logger.info(f"✅ No duplicates found in {quarter} ({len(result.data)} unique records)")
            
        except Exception as e:
            logger.error(f"❌ Duplicate validation failed: {e}")
            raise
    
    def cleanup_temp_files(self, extract_dir: Path):
        """Clean up temporary extraction directory"""
        logger.info(f"🧹 Cleaning up temporary files...")
        try:
            import shutil
            shutil.rmtree(extract_dir)
            logger.info(f"✅ Cleaned up {extract_dir}")
        except Exception as e:
            logger.warning(f"⚠️ Could not clean up {extract_dir}: {e}")

def main():
    """Test the post-2023 processor with 2025q2"""
    import os
    
    # Load environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials")
        return
    
    data_dir = "/Users/ronniederman/insider-alpha-platform/data-processing/sec_insider_data"
    
    try:
        processor = Post2023Processor(data_dir, SUPABASE_URL, SUPABASE_KEY)
        result = processor.process_quarter("2025q2_form345")
        
        print("\n" + "="*60)
        print("POST-2023 PROCESSOR TEST RESULTS")
        print("="*60)
        print(f"Status: {result['status']}")
        print(f"Quarter: {result['quarter']}")
        if 'transactions_processed' in result:
            print(f"Transactions processed: {result['transactions_processed']:,}")
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    main()
