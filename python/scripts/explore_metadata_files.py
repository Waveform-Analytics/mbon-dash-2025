#!/usr/bin/env python3
"""
Explore metadata files to understand their structure and suggest optimal storage format.
"""

import pandas as pd
from pathlib import Path
import json

def explore_excel_metadata(file_path):
    """Explore the Excel metadata file structure."""
    print(f"\n{'='*60}")
    print(f"EXPLORING: {file_path.name}")
    print(f"{'='*60}")
    
    # Read all sheets
    xlsx = pd.ExcelFile(file_path)
    print(f"\nNumber of sheets: {len(xlsx.sheet_names)}")
    print(f"Sheet names: {xlsx.sheet_names}")
    
    all_sheets_data = {}
    
    for sheet_name in xlsx.sheet_names:
        print(f"\n{'-'*40}")
        print(f"Sheet: '{sheet_name}'")
        print(f"{'-'*40}")
        
        # Read the sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        all_sheets_data[sheet_name] = df
        
        print(f"Shape: {df.shape} (rows: {len(df)}, columns: {len(df.columns)})")
        print(f"\nColumn names and types:")
        for col in df.columns:
            print(f"  - {col}: {df[col].dtype} (nulls: {df[col].isna().sum()})")
        
        print(f"\nFirst few rows:")
        print(df.head(3).to_string())
        
        # Check for unique identifiers
        print(f"\nPotential unique identifiers:")
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype == 'int64':
                unique_count = df[col].nunique()
                if unique_count == len(df):
                    print(f"  - {col}: All values unique ({unique_count} values)")
                elif unique_count > 1 and unique_count < len(df):
                    print(f"  - {col}: {unique_count} unique values out of {len(df)} rows")
        
        # Check date columns
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            print(f"\nDate/Time columns found: {date_cols}")
            for col in date_cols:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    print(f"  - {col}: Range from {df[col].min()} to {df[col].max()}")
    
    return all_sheets_data

def explore_csv_metadata(file_path):
    """Explore the CSV metadata file structure."""
    print(f"\n{'='*60}")
    print(f"EXPLORING: {file_path.name}")
    print(f"{'='*60}")
    
    # Read the CSV
    df = pd.read_csv(file_path)
    
    print(f"Shape: {df.shape} (rows: {len(df)}, columns: {len(df.columns)})")
    print(f"\nColumn names and types:")
    for col in df.columns:
        print(f"  - {col}: {df[col].dtype} (nulls: {df[col].isna().sum()})")
    
    print(f"\nFirst few rows:")
    print(df.head(5).to_string())
    
    # Check for unique identifiers
    print(f"\nUnique value counts per column:")
    for col in df.columns:
        unique_count = df[col].nunique()
        print(f"  - {col}: {unique_count} unique values")
        if unique_count <= 10:
            print(f"    Values: {df[col].unique().tolist()}")
    
    return df

def suggest_storage_format(excel_data, csv_data):
    """Suggest optimal storage format for the metadata."""
    print(f"\n{'='*60}")
    print("STORAGE RECOMMENDATIONS")
    print(f"{'='*60}")
    
    print("\n1. Excel Metadata (Deployments):")
    print("   - Since this has multiple sheets, consider:")
    print("     a) Store as multiple parquet files (one per sheet) in a 'deployments' folder")
    print("     b) Store as a single HDF5 file with multiple keys")
    print("     c) Combine related sheets and store as single parquet if they share keys")
    
    # Check if sheets can be joined
    if len(excel_data) > 1:
        print("\n   Checking for common columns across sheets:")
        sheet_names = list(excel_data.keys())
        for i in range(len(sheet_names)):
            for j in range(i+1, len(sheet_names)):
                sheet1, sheet2 = sheet_names[i], sheet_names[j]
                common_cols = set(excel_data[sheet1].columns) & set(excel_data[sheet2].columns)
                if common_cols:
                    print(f"     - '{sheet1}' and '{sheet2}' share: {common_cols}")
    
    print("\n2. CSV Metadata (Index Categories):")
    print("   - Single table, relatively small")
    print("   - Recommend: Store as parquet for consistency and better typing")
    
    print("\n3. Overall Recommendation:")
    print("   - Create a 'data/processed/metadata/' directory")
    print("   - Store deployment metadata as:")
    print("     * Individual parquet files per sheet if they're independent")
    print("     * OR combined parquet if sheets are related and share keys")
    print("   - Store index categories as: 'index_categories.parquet'")
    print("\n   Benefits of Parquet:")
    print("   - Preserves data types better than CSV")
    print("   - Efficient compression")
    print("   - Fast reading for analytics")
    print("   - Works well with pandas, polars, and other data tools")

def main():
    # Define paths
    base_path = Path("/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025")
    excel_path = base_path / "data/raw/metadata/1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
    csv_path = base_path / "data/raw/metadata/Updated_Index_Categories_v2.csv"
    
    # Explore Excel file
    excel_data = explore_excel_metadata(excel_path)
    
    # Explore CSV file
    csv_data = explore_csv_metadata(csv_path)
    
    # Suggest storage format
    suggest_storage_format(excel_data, csv_data)
    
    print(f"\n{'='*60}")
    print("EXPLORATION COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()