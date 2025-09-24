import pandas as pd
import os

quarter = '2006q1_form345'
print(f"Cleaning {quarter}")

companies_file = f'final_processed_data/{quarter}/companies.csv'
df = pd.read_csv(companies_file)
print(f"Original companies: {len(df)}")
df_clean = df.drop_duplicates(subset=['issuer_cik'], keep='first')
print(f"After removing duplicates: {len(df_clean)}")
df_clean.to_csv(companies_file, index=False)
print("✅ Companies cleaned")

insiders_file = f'final_processed_data/{quarter}/insiders.csv'
df = pd.read_csv(insiders_file)
print(f"Original insiders: {len(df)}")
df_clean = df.drop_duplicates(subset=['rpt_owner_cik'], keep='first')
print(f"After removing duplicates: {len(df_clean)}")
df_clean.to_csv(insiders_file, index=False)
print("✅ Insiders cleaned")
