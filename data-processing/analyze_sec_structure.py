#!/usr/bin/env python3
"""
Analyze SEC dataset structure across different quarters to understand
file formats and schema evolution from 2006 to present
"""

import pandas as pd
import os
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECStructureAnalyzer:
    def __init__(self):
        self.quarter_structures = {}
        
    def analyze_quarter_directory(self, quarter_path: str):
        """Analyze the structure of a single quarter's data"""
        logger.info(f"Analyzing {quarter_path}")
        
        quarter_data = {
            'path': quarter_path,
            'files': {},
            'schema_changes': {}
        }
        
        # List all files in the quarter directory
        files = os.listdir(quarter_path)
        logger.info(f"Found {len(files)} files: {files}")
        
        # Analyze each TSV file
        for file in files:
            if file.endswith('.tsv'):
                file_path = os.path.join(quarter_path, file)
                file_info = self.analyze_tsv_file(file_path)
                quarter_data['files'][file] = file_info
                
        # Check for metadata files
        metadata_files = [f for f in files if f.endswith('.json') or f.endswith('.htm')]
        quarter_data['metadata_files'] = metadata_files
        
        return quarter_data
    
    def analyze_tsv_file(self, file_path: str):
        """Analyze structure of a single TSV file"""
        logger.info(f"Analyzing {file_path}")
        
        try:
            # Read first few rows to understand structure
            df_sample = pd.read_csv(file_path, sep='\t', nrows=5)
            
            file_info = {
                'columns': list(df_sample.columns),
                'column_count': len(df_sample.columns),
                'sample_data': df_sample.head(2).to_dict('records'),
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'estimated_rows': self.estimate_row_count(file_path)
            }
            
            # Check for common transaction-related columns
            file_info['has_transaction_data'] = any(col.lower() in ['transaction', 'trans'] for col in df_sample.columns)
            file_info['has_date_columns'] = any('date' in col.lower() for col in df_sample.columns)
            file_info['has_share_data'] = any('share' in col.lower() for col in df_sample.columns)
            file_info['has_price_data'] = any('price' in col.lower() for col in df_sample.columns)
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
            return {'error': str(e)}
    
    def estimate_row_count(self, file_path: str):
        """Estimate number of rows in a TSV file"""
        try:
            # Read file in chunks to estimate row count
            chunk_size = 1000
            total_rows = 0
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Skip header
                next(f)
                
                while True:
                    chunk = f.read(chunk_size * 50)  # Rough estimate
                    if not chunk:
                        break
                    total_rows += chunk.count('\n')
                    
            return total_rows
            
        except Exception as e:
            logger.error(f"Error estimating row count for {file_path}: {str(e)}")
            return None
    
    def compare_quarters(self, quarters_data):
        """Compare structure across different quarters to identify schema changes"""
        logger.info("Comparing structures across quarters...")
        
        comparison = {
            'file_consistency': {},
            'column_changes': {},
            'schema_evolution': {}
        }
        
        # Check which files are consistent across quarters
        all_files = set()
        for quarter_data in quarters_data.values():
            all_files.update(quarter_data['files'].keys())
        
        for file_name in all_files:
            comparison['file_consistency'][file_name] = []
            for quarter, data in quarters_data.items():
                comparison['file_consistency'][file_name].append(file_name in data['files'])
        
        # Check for column changes in key files
        key_files = ['NONDERIV_TRANS.tsv', 'DERIV_TRANS.tsv', 'REPORTINGOWNER.tsv']
        
        for file_name in key_files:
            if file_name in all_files:
                comparison['column_changes'][file_name] = {}
                
                for quarter, data in quarters_data.items():
                    if file_name in data['files']:
                        file_info = data['files'][file_name]
                        if 'columns' in file_info:
                            comparison['column_changes'][file_name][quarter] = file_info['columns']
        
        return comparison
    
    def generate_processing_strategy(self, quarters_data):
        """Generate a strategy for processing the multi-file datasets"""
        logger.info("Generating processing strategy...")
        
        strategy = {
            'primary_transaction_files': [],
            'reference_files': [],
            'processing_order': [],
            'schema_mapping': {}
        }
        
        # Identify primary transaction files
        transaction_files = ['NONDERIV_TRANS.tsv', 'DERIV_TRANS.tsv']
        reference_files = ['REPORTINGOWNER.tsv', 'SUBMISSION.tsv', 'OWNER_SIGNATURE.tsv']
        
        for file_name in transaction_files:
            if any(file_name in quarter['files'] for quarter in quarters_data.values()):
                strategy['primary_transaction_files'].append(file_name)
        
        for file_name in reference_files:
            if any(file_name in quarter['files'] for quarter in quarters_data.values()):
                strategy['reference_files'].append(file_name)
        
        # Define processing order
        strategy['processing_order'] = [
            'SUBMISSION.tsv',  # Filing metadata first
            'REPORTINGOWNER.tsv',  # Owner information
            'NONDERIV_TRANS.tsv',  # Main transactions
            'DERIV_TRANS.tsv',  # Derivative transactions
            'NONDERIV_HOLDING.tsv',  # Holdings
            'DERIV_HOLDING.tsv',  # Derivative holdings
            'FOOTNOTES.tsv',  # Additional notes
            'OWNER_SIGNATURE.tsv'  # Signatures
        ]
        
        return strategy
    
    def save_analysis_report(self, quarters_data, comparison, strategy, output_file='sec_structure_analysis.json'):
        """Save analysis results to JSON file"""
        report = {
            'quarters_analyzed': list(quarters_data.keys()),
            'quarter_structures': quarters_data,
            'comparison': comparison,
            'processing_strategy': strategy,
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Analysis report saved to {output_file}")

def main():
    """Main analysis function"""
    analyzer = SECStructureAnalyzer()
    
    # Look for quarter directories in current directory
    quarter_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and 'q' in d.lower()]
    
    if not quarter_dirs:
        print("No quarter directories found!")
        print("Expected directories like: 2006q1_form345, 2024q3_form345, etc.")
        return
    
    print(f"Found quarter directories: {quarter_dirs}")
    
    # Analyze each quarter
    quarters_data = {}
    for quarter_dir in quarter_dirs:
        try:
            quarter_data = analyzer.analyze_quarter_directory(quarter_dir)
            quarters_data[quarter_dir] = quarter_data
        except Exception as e:
            logger.error(f"Error analyzing {quarter_dir}: {str(e)}")
    
    # Compare structures
    comparison = analyzer.compare_quarters(quarters_data)
    
    # Generate processing strategy
    strategy = analyzer.generate_processing_strategy(quarters_data)
    
    # Save report
    analyzer.save_analysis_report(quarters_data, comparison, strategy)
    
    # Print summary
    print("\n" + "="*60)
    print("SEC DATASET STRUCTURE ANALYSIS SUMMARY")
    print("="*60)
    print(f"Quarters analyzed: {len(quarters_data)}")
    print(f"Primary transaction files: {strategy['primary_transaction_files']}")
    print(f"Reference files: {strategy['reference_files']}")
    
    print("\nFile consistency across quarters:")
    for file_name, presence in comparison['file_consistency'].items():
        present_count = sum(presence)
        print(f"  {file_name}: {present_count}/{len(quarters_data)} quarters")
    
    print(f"\nDetailed analysis saved to: sec_structure_analysis.json")

if __name__ == "__main__":
    main()
