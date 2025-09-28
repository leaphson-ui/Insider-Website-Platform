#!/usr/bin/env python3
"""
Comprehensive analysis of SEC data structures across all quarters
Analyzes every ZIP file to identify unique data structure formats
"""

import os
import zipfile
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECStructureAnalyzer:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.structure_analysis = {}
        self.unique_formats = {}
        
    def analyze_all_quarters(self):
        """Analyze all quarters to identify unique data structures"""
        logger.info("🔍 Analyzing SEC data structures across all quarters...")
        
        # Get all ZIP files
        zip_files = list(self.data_dir.glob("*.zip"))
        logger.info(f"📊 Found {len(zip_files)} quarters to analyze")
        
        for zip_file in sorted(zip_files):
            quarter = zip_file.stem
            logger.info(f"\n📁 Analyzing {quarter}...")
            
            try:
                structure = self.analyze_quarter_structure(zip_file)
                self.structure_analysis[quarter] = structure
                
                # Categorize by structure
                structure_key = self.get_structure_key(structure)
                if structure_key not in self.unique_formats:
                    self.unique_formats[structure_key] = {
                        'format_name': f"Format_{len(self.unique_formats) + 1}",
                        'quarters': [],
                        'structure': structure
                    }
                self.unique_formats[structure_key]['quarters'].append(quarter)
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {quarter}: {e}")
                self.structure_analysis[quarter] = {'error': str(e)}
        
        # Generate summary
        self.generate_summary()
        
    def analyze_quarter_structure(self, zip_file: Path) -> dict:
        """Analyze the structure of a single quarter"""
        structure = {
            'quarter': zip_file.stem,
            'files': {},
            'total_files': 0,
            'has_submission': False,
            'has_reporting_owner': False,
            'has_nonderiv_trans': False,
            'has_deriv_trans': False,
            'has_deriv_holding': False,
            'has_nonderiv_holding': False,
            'has_footnotes': False,
            'has_owner_signature': False
        }
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            structure['total_files'] = len(file_list)
            structure['file_list'] = file_list
            
            # Analyze each file
            for file_name in file_list:
                if file_name.endswith('.tsv'):
                    try:
                        # Extract and analyze the file
                        with zip_ref.open(file_name) as f:
                            # Read first few lines to get structure
                            lines = []
                            for i, line in enumerate(f):
                                if i >= 5:  # Read first 5 lines
                                    break
                                lines.append(line.decode('utf-8', errors='ignore'))
                            
                            if lines:
                                # Get column headers (first line)
                                headers = lines[0].strip().split('\t')
                                file_analysis = {
                                    'file_name': file_name,
                                    'columns': headers,
                                    'column_count': len(headers),
                                    'sample_data': lines[1:3] if len(lines) > 1 else []
                                }
                                
                                structure['files'][file_name] = file_analysis
                                
                                # Check for key files
                                if 'SUBMISSION' in file_name.upper():
                                    structure['has_submission'] = True
                                    structure['submission_columns'] = headers
                                elif 'REPORTINGOWNER' in file_name.upper():
                                    structure['has_reporting_owner'] = True
                                    structure['reporting_owner_columns'] = headers
                                elif 'NONDERIV_TRANS' in file_name.upper():
                                    structure['has_nonderiv_trans'] = True
                                    structure['nonderiv_trans_columns'] = headers
                                elif 'DERIV_TRANS' in file_name.upper():
                                    structure['has_deriv_trans'] = True
                                    structure['deriv_trans_columns'] = headers
                                elif 'DERIV_HOLDING' in file_name.upper():
                                    structure['has_deriv_holding'] = True
                                elif 'NONDERIV_HOLDING' in file_name.upper():
                                    structure['has_nonderiv_holding'] = True
                                elif 'FOOTNOTES' in file_name.upper():
                                    structure['has_footnotes'] = True
                                elif 'OWNER_SIGNATURE' in file_name.upper():
                                    structure['has_owner_signature'] = True
                                    
                    except Exception as e:
                        logger.warning(f"⚠️ Could not analyze {file_name}: {e}")
                        structure['files'][file_name] = {'error': str(e)}
        
        return structure
    
    def get_structure_key(self, structure: dict) -> str:
        """Create a unique key for this structure format"""
        key_parts = []
        
        # File presence
        key_parts.append(f"submission:{structure.get('has_submission', False)}")
        key_parts.append(f"reporting_owner:{structure.get('has_reporting_owner', False)}")
        key_parts.append(f"nonderiv_trans:{structure.get('has_nonderiv_trans', False)}")
        key_parts.append(f"deriv_trans:{structure.get('has_deriv_trans', False)}")
        
        # Column counts for key files
        if structure.get('has_submission'):
            key_parts.append(f"submission_cols:{len(structure.get('submission_columns', []))}")
        if structure.get('has_reporting_owner'):
            key_parts.append(f"reporting_owner_cols:{len(structure.get('reporting_owner_columns', []))}")
        if structure.get('has_nonderiv_trans'):
            key_parts.append(f"nonderiv_trans_cols:{len(structure.get('nonderiv_trans_columns', []))}")
        
        return "|".join(key_parts)
    
    def generate_summary(self):
        """Generate summary of unique structures"""
        logger.info(f"\n📊 STRUCTURE ANALYSIS SUMMARY")
        logger.info(f"=" * 50)
        logger.info(f"Total quarters analyzed: {len(self.structure_analysis)}")
        logger.info(f"Unique structure formats: {len(self.unique_formats)}")
        
        for i, (structure_key, format_info) in enumerate(self.unique_formats.items(), 1):
            logger.info(f"\n🔍 Format {i}: {format_info['format_name']}")
            logger.info(f"   Quarters: {len(format_info['quarters'])}")
            logger.info(f"   Quarter list: {format_info['quarters'][:5]}{'...' if len(format_info['quarters']) > 5 else ''}")
            
            # Show key differences
            structure = format_info['structure']
            logger.info(f"   Files present:")
            logger.info(f"     - SUBMISSION: {structure.get('has_submission', False)}")
            logger.info(f"     - REPORTINGOWNER: {structure.get('has_reporting_owner', False)}")
            logger.info(f"     - NONDERIV_TRANS: {structure.get('has_nonderiv_trans', False)}")
            logger.info(f"     - DERIV_TRANS: {structure.get('has_deriv_trans', False)}")
            
            if structure.get('has_submission'):
                cols = structure.get('submission_columns', [])
                logger.info(f"     - SUBMISSION columns: {len(cols)} - {cols[:3]}...")
            if structure.get('has_nonderiv_trans'):
                cols = structure.get('nonderiv_trans_columns', [])
                logger.info(f"     - NONDERIV_TRANS columns: {len(cols)} - {cols[:3]}...")
        
        # Save detailed analysis
        self.save_analysis()
    
    def save_analysis(self):
        """Save detailed analysis to files"""
        # Save full analysis
        with open('sec_structure_analysis_detailed.json', 'w') as f:
            json.dump(self.structure_analysis, f, indent=2)
        
        # Save summary
        summary = {
            'total_quarters': len(self.structure_analysis),
            'unique_formats': len(self.unique_formats),
            'formats': self.unique_formats,
            'analysis_date': pd.Timestamp.now().isoformat()
        }
        
        with open('sec_structure_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\n💾 Analysis saved to:")
        logger.info(f"   - sec_structure_analysis_detailed.json")
        logger.info(f"   - sec_structure_summary.json")

def main():
    """Main analysis function"""
    data_dir = "/Users/ronniederman/insider-alpha-platform/data-processing/sec_insider_data"
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    analyzer = SECStructureAnalyzer(data_dir)
    analyzer.analyze_all_quarters()

if __name__ == "__main__":
    main()

