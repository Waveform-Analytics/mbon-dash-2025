#!/usr/bin/env python3
"""
Parquet File Analysis Script

This script analyzes all parquet files in the data/processed directory,
extracts their column names, shapes, and basic statistics, then generates
documentation for updating DATA-FILE-NAMING.md.
"""

import pandas as pd
from pathlib import Path
import sys
from collections import defaultdict

def analyze_parquet_file(file_path):
    """Analyze a single parquet file and return metadata."""
    try:
        df = pd.read_parquet(file_path)
        
        # Basic info
        info = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'missing_values': df.isnull().sum().to_dict(),
        }
        
        # Date range if datetime column exists
        datetime_cols = [col for col in df.columns if 'datetime' in col.lower() or 'date' in col.lower()]
        if datetime_cols:
            date_col = datetime_cols[0]
            if pd.api.types.is_datetime64_any_dtype(df[date_col]):
                info['date_range'] = {
                    'start': df[date_col].min(),
                    'end': df[date_col].max(),
                    'column': date_col
                }
        
        # Station info if station column exists
        station_cols = [col for col in df.columns if 'station' in col.lower()]
        if station_cols:
            station_col = station_cols[0]
            info['stations'] = sorted(df[station_col].unique().tolist())
        
        # Year info if year column exists
        year_cols = [col for col in df.columns if 'year' in col.lower()]
        if year_cols:
            year_col = year_cols[0]
            info['years'] = sorted(df[year_col].unique().tolist())
            
        return info
        
    except Exception as e:
        return {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'error': str(e)
        }

def categorize_columns(columns):
    """Categorize columns by type for better documentation."""
    categories = {
        'identifiers': [],
        'temporal': [],
        'environmental': [],
        'acoustic_indices': [],
        'detections': [],
        'statistics': [],
        'other': []
    }
    
    for col in columns:
        col_lower = col.lower()
        
        if col_lower in ['datetime', 'station', 'year', 'id', 'file']:
            categories['identifiers'].append(col)
        elif any(term in col_lower for term in ['hour', 'day', 'month', 'season', 'diel', 'time']):
            categories['temporal'].append(col)
        elif any(term in col_lower for term in ['temp', 'depth', 'pressure', 'spl', 'broadband', 'hz']):
            categories['environmental'].append(col)
        elif any(term in col_lower for term in ['sp', 'otbw', 'otg', 'bd', 'ss', 'rd', 'ac', 'vessel', 'dolphin', 'detection']):
            categories['detections'].append(col)
        elif any(term in col_lower for term in ['mean', 'std', 'count', 'min', 'max', 'correlation']):
            categories['statistics'].append(col)
        elif len(col) <= 10 and not any(char in col for char in [' ', '(', ')']):
            # Short names without spaces/parentheses are likely acoustic indices
            categories['acoustic_indices'].append(col)
        else:
            categories['other'].append(col)
    
    return categories

def format_columns_for_docs(columns, max_per_line=8):
    """Format column list for documentation."""
    if len(columns) <= max_per_line:
        return f"  - `{columns}`" if len(columns) > 1 else f"  - `'{columns[0]}'`"
    
    # Break into multiple lines
    lines = []
    for i in range(0, len(columns), max_per_line):
        chunk = columns[i:i+max_per_line]
        if i == 0:
            lines.append(f"  - `{chunk}`")
        else:
            lines.append(f"    `{chunk}`")
    return '\n'.join(lines)

def main():
    # Find all parquet files
    data_dir = Path("../data/processed")
    metadata_dir = data_dir / "metadata"
    
    if not data_dir.exists():
        print(f"Error: Data directory {data_dir} not found")
        sys.exit(1)
    
    # Find all parquet files
    parquet_files = []
    parquet_files.extend(data_dir.glob("*.parquet"))
    if metadata_dir.exists():
        parquet_files.extend(metadata_dir.glob("*.parquet"))
    
    if not parquet_files:
        print(f"No parquet files found in {data_dir}")
        sys.exit(1)
    
    print(f"Found {len(parquet_files)} parquet files")
    print("=" * 60)
    
    # Analyze each file
    file_info = {}
    for file_path in sorted(parquet_files):
        print(f"Analyzing: {file_path.name}")
        info = analyze_parquet_file(file_path)
        file_info[file_path.name] = info
        
        if 'error' in info:
            print(f"  ❌ Error: {info['error']}")
        else:
            print(f"  ✅ Shape: {info['shape']}, Columns: {len(info['columns'])}")
    
    print("\n" + "=" * 60)
    print("DETAILED ANALYSIS")
    print("=" * 60)
    
    # Generate documentation
    documentation = []
    
    documentation.append("# Data File Column Reference")
    documentation.append("")
    documentation.append("This document lists the actual column names found in each processed data file.")
    documentation.append("Updated automatically by analyzing all parquet files in data/processed/.")
    documentation.append("")
    
    # Group files by notebook number
    notebook_files = defaultdict(list)
    for filename, info in file_info.items():
        if 'error' not in info:
            # Extract notebook number from filename
            if filename.startswith('0') and '_' in filename:
                nb_num = filename.split('_')[0]
                notebook_files[nb_num].append((filename, info))
            else:
                notebook_files['other'].append((filename, info))
    
    # Document each notebook's files
    for nb_num in sorted(notebook_files.keys()):
        if nb_num == 'other':
            documentation.append("## Other Files")
        else:
            documentation.append(f"## Notebook {nb_num} Files")
        documentation.append("")
        
        for filename, info in sorted(notebook_files[nb_num]):
            documentation.append(f"### `{filename}`")
            documentation.append(f"- **Shape**: {info['shape'][0]:,} rows × {info['shape'][1]} columns")
            documentation.append(f"- **Size**: {info['memory_usage'] / 1024 / 1024:.1f} MB")
            
            if 'date_range' in info:
                documentation.append(f"- **Date Range**: {info['date_range']['start'].strftime('%Y-%m-%d')} to {info['date_range']['end'].strftime('%Y-%m-%d')}")
            
            if 'stations' in info:
                documentation.append(f"- **Stations**: {info['stations']}")
                
            if 'years' in info:
                documentation.append(f"- **Years**: {info['years']}")
            
            # Categorize columns
            categories = categorize_columns(info['columns'])
            
            documentation.append("")
            documentation.append("**Column Categories:**")
            
            for cat_name, cols in categories.items():
                if cols:
                    documentation.append(f"- **{cat_name.replace('_', ' ').title()}** ({len(cols)}): `{cols}`")
            
            # Show missing values if any
            missing = {k: v for k, v in info['missing_values'].items() if v > 0}
            if missing:
                documentation.append("")
                documentation.append("**Missing Values:**")
                for col, count in missing.items():
                    pct = (count / info['shape'][0]) * 100
                    documentation.append(f"- `{col}`: {count:,} ({pct:.1f}%)")
            
            documentation.append("")
    
    # Save documentation
    output_file = Path("../notes/DATA-FILE-COLUMNS.md")
    output_file.write_text('\n'.join(documentation))
    
    print(f"\n✅ Documentation saved to: {output_file}")
    print(f"📊 Analyzed {len(file_info)} files")
    
    # Print summary for updating DATA-FILE-NAMING.md
    print("\n" + "=" * 60)
    print("SUMMARY FOR DATA-FILE-NAMING.MD UPDATE")
    print("=" * 60)
    
    for nb_num in sorted(notebook_files.keys()):
        if nb_num != 'other':
            print(f"\n### Notebook {nb_num} Files:")
            for filename, info in sorted(notebook_files[nb_num]):
                print(f"- `{filename}`")
                print(f"  - Shape: {info['shape']}")
                print(f"  - Key columns: {info['columns'][:5]}{'...' if len(info['columns']) > 5 else ''}")

if __name__ == "__main__":
    main()