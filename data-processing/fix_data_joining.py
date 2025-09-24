#!/usr/bin/env python3
"""
Fix the data joining issue by properly linking SEC files
"""

import pandas as pd
import os
from pathlib import Path

def fix_quarter_data(quarter_dir):
    """Fix the data joining for a specific quarter"""
    print(f"Fixing data for {quarter_dir}")
    
    # Read the original SEC files
    submission_file = f"{quarter_dir}/SUBMISSION.tsv"
    reporting_owner_file = f"{quarter_dir}/REPORTINGOWNER.tsv"
    transactions_file = f"{quarter_dir}/NONDERIV_TRANS.tsv"
    
    if not all(os.path.exists(f) for f in [submission_file, reporting_owner_file, transactions_file]):
        print(f"Missing files for {quarter_dir}")
        return
    
    # Read the files
    print("Reading SEC files...")
    submission_df = pd.read_csv(submission_file, sep='\t')
    reporting_owner_df = pd.read_csv(reporting_owner_file, sep='\t')
    transactions_df = pd.read_csv(transactions_file, sep='\t')
    
    print(f"Submission: {len(submission_df)} rows")
    print(f"Reporting Owner: {len(reporting_owner_df)} rows")
    print(f"Transactions: {len(transactions_df)} rows")
    
    # Join transactions with submission data (for company info)
    print("Joining transactions with submission data...")
    merged_df = transactions_df.merge(
        submission_df[['ACCESSION_NUMBER', 'ISSUERCIK', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL']],
        on='ACCESSION_NUMBER',
        how='left'
    )
    
    # Join with reporting owner data (for insider info)
    print("Joining with reporting owner data...")
    merged_df = merged_df.merge(
        reporting_owner_df[['ACCESSION_NUMBER', 'RPTOWNERCIK', 'RPTOWNERNAME']],
        on='ACCESSION_NUMBER',
        how='left'
    )
    
    print(f"Merged data: {len(merged_df)} rows")
    
    # Create the final datasets
    print("Creating final datasets...")
    
    # Companies (unique by CIK)
    companies_df = merged_df[['ISSUERCIK', 'ISSUERNAME', 'ISSUERTRADINGSYMBOL']].drop_duplicates(subset=['ISSUERCIK'])
    companies_df = companies_df.rename(columns={
        'ISSUERCIK': 'issuer_cik',
        'ISSUERNAME': 'issuer_name', 
        'ISSUERTRADINGSYMBOL': 'issuer_trading_symbol'
    })
    
    # Insiders (unique by CIK)
    insiders_df = merged_df[['RPTOWNERCIK', 'RPTOWNERNAME']].drop_duplicates(subset=['RPTOWNERCIK'])
    insiders_df = insiders_df.rename(columns={
        'RPTOWNERCIK': 'rpt_owner_cik',
        'RPTOWNERNAME': 'rpt_owner_name'
    })
    # Add default values for boolean fields
    insiders_df['is_director'] = False
    insiders_df['is_officer'] = False
    insiders_df['is_ten_percent_owner'] = False
    
    # Transactions (with proper column names)
    transactions_final = merged_df.copy()
    transactions_final = transactions_final.rename(columns={
        'ACCESSION_NUMBER': 'accession_number',
        'TRANS_DATE': 'transaction_date',
        'TRANS_CODE': 'transaction_code',
        'TRANS_SHARES': 'transaction_shares',
        'TRANS_PRICEPERSHARE': 'transaction_price_per_share',
        'SHRS_OWND_FOLWNG_TRANS': 'shares_owned_following_transaction',
        'SECURITY_TITLE': 'security_title',
        'ISSUERCIK': 'issuer_cik',
        'ISSUERNAME': 'issuer_name',
        'ISSUERTRADINGSYMBOL': 'issuer_trading_symbol',
        'RPTOWNERCIK': 'rpt_owner_cik',
        'RPTOWNERNAME': 'rpt_owner_name'
    })
    
    # Calculate transaction value
    transactions_final['calculated_transaction_value'] = (
        transactions_final['transaction_shares'] * transactions_final['transaction_price_per_share']
    ).fillna(0)
    
    # Add quarter info
    transactions_final['quarter'] = quarter_dir
    transactions_final['file_type'] = '4'
    
    # Save the fixed data
    output_dir = f"fixed_processed_data/{quarter_dir}"
    os.makedirs(output_dir, exist_ok=True)
    
    companies_df.to_csv(f"{output_dir}/companies.csv", index=False)
    insiders_df.to_csv(f"{output_dir}/insiders.csv", index=False)
    transactions_final.to_csv(f"{output_dir}/transactions.csv", index=False)
    
    print(f"✓ Fixed data saved to {output_dir}")
    print(f"  Companies: {len(companies_df)}")
    print(f"  Insiders: {len(insiders_df)}")
    print(f"  Transactions: {len(transactions_final)}")
    
    return output_dir

def main():
    """Fix data for both quarters"""
    quarters = ['2025q2_form345', '2006q1_form345']
    
    for quarter in quarters:
        if os.path.exists(quarter):
            fix_quarter_data(quarter)
        else:
            print(f"Quarter directory {quarter} not found")

if __name__ == "__main__":
    main()
