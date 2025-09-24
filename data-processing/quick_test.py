#!/usr/bin/env python3
"""
Quick test to understand the actual SEC data structure
"""

import pandas as pd
import os

def test_quarter_structure(quarter_path):
    print(f"\n=== Testing {quarter_path} ===")
    
    files = ['SUBMISSION.tsv', 'REPORTINGOWNER.tsv', 'NONDERIV_TRANS.tsv', 'DERIV_TRANS.tsv']
    
    for file in files:
        file_path = os.path.join(quarter_path, file)
        if os.path.exists(file_path):
            print(f"\n{file}:")
            try:
                df = pd.read_csv(file_path, sep='\t', nrows=5)
                print(f"  Columns: {list(df.columns)}")
                print(f"  Shape: {df.shape}")
                if not df.empty:
                    print(f"  Sample data:")
                    for col in df.columns[:3]:  # Show first 3 columns
                        print(f"    {col}: {df[col].iloc[0] if len(df) > 0 else 'N/A'}")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"\n{file}: NOT FOUND")

if __name__ == "__main__":
    # Test both quarters
    test_quarter_structure("2025q2_form345")
    test_quarter_structure("2006q1_form345")
