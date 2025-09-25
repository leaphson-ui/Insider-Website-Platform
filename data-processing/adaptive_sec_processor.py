#!/usr/bin/env python3
"""
Adaptive SEC Data Processor
Safely handles both 2006-2022 and 2023-2025 data structures
Automatically detects and adapts to column differences
"""

import pandas as pd
import zipfile
import os
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdaptiveSECProcessor:
    def __init__(self, data_dir: str):
        """Initialize adaptive processor for SEC data"""
        self.data_dir = Path(data_dir)
        self.processed_data = {}
        
        # Define expected file structure
        self.expected_files = [
            'DERIV_HOLDING.tsv',
            'DERIV_TRANS.tsv',
            'FOOTNOTES.tsv',
            'NONDERIV_HOLDING.tsv',
            'NONDERIV_TRANS.tsv',
            'OWNER_SIGNATURE.tsv',
            'REPORTINGOWNER.tsv',
            'SUBMISSION.tsv'
        ]
        
        # Column evolution tracking
        self.column_evolution = {}
        
    def detect_quarter_from_filename(self, zip_file: str) -> str:
        """Extract quarter information from filename"""
        match = re.search(r'(\d{4})q(\d)', zip_file)
        if match:
            year = int(match.group(1))
            quarter = int(match.group(2))
            return f"{year}Q{quarter}"
        return "unknown"
    
    def is_pre_2023_quarter(self, quarter: str) -> bool:
        """Determine if quarter is before 2023 (13-column SUBMISSION.tsv)"""
        if quarter == "unknown":
            return True  # Default to older format for safety
        
        year = int(quarter.split('Q')[0])
        return year < 2023
    
    def safe_column_access(self, df: pd.DataFrame, column: str, default_value=None) -> pd.Series:
        """Safely access a column, returning default if column doesn't exist"""
        if column in df.columns:
            return df[column]
        else:
            logger.warning(f"Column '{column}' not found, using default value: {default_value}")
            return pd.Series([default_value] * len(df), index=df.index)
    
    def safe_column_selection(self, df: pd.DataFrame, columns: List[str], default_value=None) -> pd.DataFrame:
        """Safely select columns, adding missing ones with default values"""
        result_df = pd.DataFrame(index=df.index)
        
        for col in columns:
            if col in df.columns:
                result_df[col] = df[col]
            else:
                logger.warning(f"Column '{col}' not found, adding with default value: {default_value}")
                result_df[col] = default_value
        
        return result_df
    
    def load_tsv_from_zip(self, zip_path: str, tsv_file: str) -> Optional[pd.DataFrame]:
        """Load TSV file from ZIP archive with error handling"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                with zip_ref.open(tsv_file) as f:
                    df = pd.read_csv(f, sep='\t', dtype=str, na_filter=False)
                    logger.info(f"Loaded {tsv_file}: {len(df)} records")
                    return df
        except Exception as e:
            logger.error(f"Error loading {tsv_file} from {zip_path}: {e}")
            return None
    
    def analyze_submission_structure(self, df: pd.DataFrame) -> Dict:
        """Analyze SUBMISSION.tsv structure and detect column differences"""
        analysis = {
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'has_aff10b5one': 'AFF10B5ONE' in df.columns,
            'structure_type': 'unknown'
        }
        
        if analysis['has_aff10b5one']:
            analysis['structure_type'] = 'post_2023'
        else:
            analysis['structure_type'] = 'pre_2023'
        
        return analysis
    
    def process_submission_file(self, zip_path: str, quarter: str) -> Optional[pd.DataFrame]:
        """Process SUBMISSION.tsv with adaptive column handling"""
        logger.info(f"Processing SUBMISSION.tsv for {quarter}")
        
        df = self.load_tsv_from_zip(zip_path, 'SUBMISSION.tsv')
        if df is None:
            return None
        
        # Analyze structure
        structure = self.analyze_submission_structure(df)
        self.column_evolution[quarter] = structure
        logger.info(f"Structure detected: {structure['structure_type']} ({structure['column_count']} columns)")
        
        # Define columns we need (core columns that exist in both periods)
        core_columns = [
            'ACCESSION_NUMBER',
            'ISSUERCIK', 
            'ISSUERNAME',
            'ISSUERTRADINGSYMBOL',
            'FILING_DATE',
            'PERIOD_OF_REPORT'
        ]
        
        # Handle AFF10B5ONE column adaptively
        if structure['has_aff10b5one']:
            logger.info("Detected AFF10B5ONE column - using 2023+ structure")
            selected_columns = core_columns + ['AFF10B5ONE']
        else:
            logger.info("No AFF10B5ONE column - using pre-2023 structure")
            selected_columns = core_columns
        
        # Safely select columns
        result_df = self.safe_column_selection(df, selected_columns, default_value='')
        
        # Clean and normalize data
        result_df = self.clean_submission_data(result_df)
        
        return result_df
    
    def clean_submission_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize submission data"""
        # Normalize CIK to 10 digits
        if 'ISSUERCIK' in df.columns:
            df['ISSUERCIK'] = df['ISSUERCIK'].astype(str).str.zfill(10)
        
        # Clean company names
        if 'ISSUERNAME' in df.columns:
            df['ISSUERNAME'] = df['ISSUERNAME'].str.strip()
        
        # Clean ticker symbols
        if 'ISSUERTRADINGSYMBOL' in df.columns:
            df['ISSUERTRADINGSYMBOL'] = df['ISSUERTRADINGSYMBOL'].str.strip()
        
        return df
    
    def process_reporting_owner_file(self, zip_path: str, quarter: str) -> Optional[pd.DataFrame]:
        """Process REPORTINGOWNER.tsv (structure is consistent across all periods)"""
        logger.info(f"Processing REPORTINGOWNER.tsv for {quarter}")
        
        df = self.load_tsv_from_zip(zip_path, 'REPORTINGOWNER.tsv')
        if df is None:
            return None
        
        # Define columns we need (consistent across all periods)
        selected_columns = [
            'ACCESSION_NUMBER',
            'RPTOWNERCIK',
            'RPTOWNERNAME', 
            'RPTOWNER_RELATIONSHIP',
            'RPTOWNER_TITLE'
        ]
        
        # Select columns (should be safe since structure is consistent)
        result_df = df[selected_columns].copy()
        
        # Clean and normalize data
        if 'RPTOWNERCIK' in result_df.columns:
            result_df['RPTOWNERCIK'] = result_df['RPTOWNERCIK'].astype(str).str.zfill(10)
        
        if 'RPTOWNERNAME' in result_df.columns:
            result_df['RPTOWNERNAME'] = result_df['RPTOWNERNAME'].str.strip()
        
        return result_df
    
    def process_transactions_file(self, zip_path: str, quarter: str) -> Optional[pd.DataFrame]:
        """Process NONDERIV_TRANS.tsv (structure is consistent across all periods)"""
        logger.info(f"Processing NONDERIV_TRANS.tsv for {quarter}")
        
        df = self.load_tsv_from_zip(zip_path, 'NONDERIV_TRANS.tsv')
        if df is None:
            return None
        
        # Define columns we need (consistent across all periods)
        selected_columns = [
            'ACCESSION_NUMBER',
            'TRANS_DATE',
            'TRANS_SHARES',
            'TRANS_PRICEPERSHARE',
            'VALU_OWND_FOLWNG_TRANS',
            'TRANS_ACQUIRED_DISP_CD',
            'SECURITY_TITLE',
            'SHRS_OWND_FOLWNG_TRANS'
        ]
        
        # Select columns (should be safe since structure is consistent)
        result_df = df[selected_columns].copy()
        
        # Clean and normalize data
        result_df = self.clean_transaction_data(result_df)
        
        return result_df
    
    def clean_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize transaction data"""
        # Convert numeric columns safely
        numeric_columns = ['TRANS_SHARES', 'TRANS_PRICEPERSHARE', 'VALU_OWND_FOLWNG_TRANS', 'SHRS_OWND_FOLWNG_TRANS']
        
        for col in numeric_columns:
            if col in df.columns:
                # Replace problematic values
                df[col] = df[col].replace(['', 'N/A', 'nan', 'NaN'], '0')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Clean transaction codes
        if 'TRANS_ACQUIRED_DISP_CD' in df.columns:
            df['TRANS_ACQUIRED_DISP_CD'] = df['TRANS_ACQUIRED_DISP_CD'].str.strip()
        
        # Clean security titles
        if 'SECURITY_TITLE' in df.columns:
            df['SECURITY_TITLE'] = df['SECURITY_TITLE'].str.strip()
        
        return df
    
    def join_data_safely(self, transactions_df: pd.DataFrame, submission_df: pd.DataFrame, 
                        reporting_owner_df: pd.DataFrame) -> pd.DataFrame:
        """Safely join all data with proper error handling"""
        logger.info("Joining transaction, company, and insider data...")
        
        # Start with transactions
        result_df = transactions_df.copy()
        
        # Join with company data (from SUBMISSION)
        logger.info("Joining with company data...")
        company_cols = ['ACCESSION_NUMBER', 'ISSUERCIK', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL']
        company_df = submission_df[company_cols]
        
        result_df = result_df.merge(
            company_df,
            on='ACCESSION_NUMBER',
            how='left'
        )
        
        # Join with insider data (from REPORTINGOWNER)
        logger.info("Joining with insider data...")
        insider_cols = ['ACCESSION_NUMBER', 'RPTOWNERCIK', 'RPTOWNERNAME', 'RPTOWNER_RELATIONSHIP']
        insider_df = reporting_owner_df[insider_cols]
        
        result_df = result_df.merge(
            insider_df,
            on='ACCESSION_NUMBER',
            how='left'
        )
        
        # Add processing metadata
        result_df['quarter'] = self.current_quarter
        result_df['processed_at'] = datetime.now().isoformat()
        
        return result_df
    
    def extract_unique_entities(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Extract unique companies and insiders"""
        logger.info("Extracting unique companies and insiders...")
        
        # Unique companies
        companies_df = df[['ISSUERCIK', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL']].drop_duplicates()
        companies_df = companies_df[companies_df['ISSUERCIK'] != '']  # Remove empty CIKs
        companies_df['company_id'] = companies_df['ISSUERCIK']  # Use CIK as ID
        
        # Unique insiders
        insiders_df = df[['RPTOWNERCIK', 'RPTOWNERNAME', 'RPTOWNER_RELATIONSHIP']].drop_duplicates()
        insiders_df = insiders_df[insiders_df['RPTOWNERCIK'] != '']  # Remove empty CIKs
        insiders_df['insider_id'] = insiders_df['RPTOWNERCIK']  # Use CIK as ID
        
        return {
            'companies': companies_df,
            'insiders': insiders_df
        }
    
    def process_quarter(self, zip_file: str) -> Dict:
        """Process a single quarter's data with full error handling"""
        logger.info(f"🚀 Processing quarter: {zip_file}")
        logger.info("=" * 60)
        
        # Extract quarter info
        self.current_quarter = self.detect_quarter_from_filename(zip_file)
        zip_path = os.path.join(self.data_dir, zip_file)
        
        if not os.path.exists(zip_path):
            logger.error(f"ZIP file not found: {zip_path}")
            return {'error': f'File not found: {zip_file}'}
        
        try:
            # Process core files
            submission_df = self.process_submission_file(zip_path, self.current_quarter)
            reporting_owner_df = self.process_reporting_owner_file(zip_path, self.current_quarter)
            transactions_df = self.process_transactions_file(zip_path, self.current_quarter)
            
            if submission_df is None or reporting_owner_df is None or transactions_df is None:
                return {'error': 'Failed to load one or more required files'}
            
            # Join all data
            complete_df = self.join_data_safely(transactions_df, submission_df, reporting_owner_df)
            
            # Extract unique entities
            entities = self.extract_unique_entities(complete_df)
            
            # Prepare results
            result = {
                'quarter': self.current_quarter,
                'zip_file': zip_file,
                'transactions': complete_df,
                'companies': entities['companies'],
                'insiders': entities['insiders'],
                'stats': {
                    'total_transactions': len(complete_df),
                    'unique_companies': len(entities['companies']),
                    'unique_insiders': len(entities['insiders']),
                    'structure_type': self.column_evolution.get(self.current_quarter, {}).get('structure_type', 'unknown')
                }
            }
            
            logger.info(f"✅ Successfully processed {zip_file}")
            logger.info(f"   - Transactions: {result['stats']['total_transactions']:,}")
            logger.info(f"   - Companies: {result['stats']['unique_companies']:,}")
            logger.info(f"   - Insiders: {result['stats']['unique_insiders']:,}")
            logger.info(f"   - Structure: {result['stats']['structure_type']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing {zip_file}: {e}")
            return {'error': f'Processing failed: {str(e)}'}
    
    def process_multiple_quarters(self, zip_files: List[str]) -> Dict:
        """Process multiple quarters with progress tracking"""
        logger.info(f"🚀 Processing {len(zip_files)} quarters")
        logger.info("=" * 60)
        
        results = {}
        successful = 0
        failed = 0
        
        for i, zip_file in enumerate(zip_files, 1):
            logger.info(f"\n[{i}/{len(zip_files)}] Processing: {zip_file}")
            
            result = self.process_quarter(zip_file)
            
            if 'error' in result:
                logger.error(f"❌ Failed: {result['error']}")
                failed += 1
            else:
                results[zip_file] = result
                successful += 1
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 PROCESSING SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total quarters: {len(zip_files)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {successful/len(zip_files)*100:.1f}%")
        
        return {
            'results': results,
            'summary': {
                'total': len(zip_files),
                'successful': successful,
                'failed': failed,
                'success_rate': successful/len(zip_files)*100
            }
        }

def main():
    """Test the adaptive processor with sample quarters"""
    processor = AdaptiveSECProcessor("sec_insider_data")
    
    # Test with quarters from different periods
    test_quarters = [
        "2006q1_form345.zip",  # Pre-2023 structure
        "2020q1_form345.zip",  # Pre-2023 structure  
        "2023q1_form345.zip",  # Post-2023 structure
        "2025q2_form345.zip"   # Post-2023 structure
    ]
    
    results = processor.process_multiple_quarters(test_quarters)
    
    # Display results
    print("\n🎯 ADAPTIVE PROCESSOR TEST RESULTS")
    print("=" * 60)
    
    for zip_file, result in results['results'].items():
        if 'error' not in result:
            stats = result['stats']
            print(f"{zip_file}:")
            print(f"  - Structure: {stats['structure_type']}")
            print(f"  - Transactions: {stats['total_transactions']:,}")
            print(f"  - Companies: {stats['unique_companies']:,}")
            print(f"  - Insiders: {stats['unique_insiders']:,}")
            print()

if __name__ == "__main__":
    main()
