#!/usr/bin/env python3
"""Script to inspect the structure of detection files."""

import pandas as pd
from pathlib import Path

def inspect_file_structure():
    # Check one detection file in detail
    file_path = Path('../data/raw/2021/detections/Master_Manual_9M_2h_2021.xlsx')
    
    if file_path.exists():
        print("=== DETAILED FILE INSPECTION ===")
        print(f"File: {file_path.name}")
        
        # Read the raw file to see structure
        df = pd.read_excel(file_path)
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        # Show first 10 rows to understand structure
        print("\n=== FIRST 10 ROWS ===")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(df.head(10))
        
        print("\n=== COLUMN NAMES ===")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
            
        # Look for actual data rows (skip headers/metadata)
        print("\n=== LOOKING FOR DATA ROWS ===")
        for i, row in df.iterrows():
            first_col = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            if first_col and not first_col.startswith(('Description', 'References', 'Filename')):
                print(f"Row {i}: {first_col[:50]}...")
                if i > 15:  # Stop after finding some data rows
                    break
    
    # Also check an environmental file
    env_file = Path('../data/raw/2021/environmental/Master_9M_Temp_2021.xlsx')
    if env_file.exists():
        print(f"\n\n=== ENVIRONMENTAL FILE INSPECTION ===")
        print(f"File: {env_file.name}")
        
        df_env = pd.read_excel(env_file)
        print(f"Total rows: {len(df_env)}")
        print(f"Columns: {list(df_env.columns)}")
        print("\n=== FIRST FEW ROWS ===")
        print(df_env.head())

if __name__ == "__main__":
    inspect_file_structure()