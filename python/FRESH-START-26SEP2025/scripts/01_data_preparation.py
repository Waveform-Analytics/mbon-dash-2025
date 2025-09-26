#!/usr/bin/env python3
"""
Script 1: Data Preparation
=========================

Purpose: Load, align, and clean all data streams for acoustic indices vs environmental analysis
Key Question: What data do we have and is it analysis-ready?

This script implements the data preparation phase of our focused analysis pipeline.
It loads acoustic indices, manual detections, environmental data, and SPL measurements,
then performs quality assessment and temporal alignment to 2-hour intervals.

Key Outputs:
- data/processed/aligned_dataset_2021.parquet - Complete temporally aligned dataset
- data/processed/data_quality_report.json - Coverage and quality metrics
- figures/01_data_coverage_summary.png - Temporal coverage visualization  
- figures/01_missing_data_heatmap.png - Missing data patterns

Reference Sources:
- python/scripts/notebooks/01_data_prep.py - Data loading patterns
- python/scripts/notebooks/02_temporal_aggregation.py - Temporal alignment approach
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def find_project_root():
    """Find main project root (mbon-dash-2025) by looking for data/raw folder structure"""
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    # Go up from FRESH-START-26SEP2025/scripts to find main project root
    project_root = current_dir
    while not (project_root / "data" / "raw").exists() and project_root != project_root.parent:
        project_root = project_root.parent
    return project_root

# Set up paths: input and output both use main project data folder
PROJECT_ROOT = find_project_root()
DATA_ROOT = PROJECT_ROOT / "data"  # Main project data folder
DATA_DIR = DATA_ROOT / "raw"  # Main project raw data
OUTPUT_DIR = DATA_ROOT / "processed"  # Main project processed folder
FIGURE_DIR = DATA_ROOT / "processed" / "fresh_start_figures"  # Figures subfolder in processed

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Analysis parameters
YEAR = 2021
STATIONS = ['9M', '14M', '37M']

print("="*60)
print("SCRIPT 1: DATA PREPARATION")
print("="*60)
print(f"Project root: {PROJECT_ROOT}")
print(f"Data root: {DATA_ROOT}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Figure directory: {FIGURE_DIR}")
print(f"Analysis year: {YEAR}")
print(f"Stations: {', '.join(STATIONS)}")
print()

def load_acoustic_indices():
    """Load acoustic indices data for all stations"""
    print("1. LOADING ACOUSTIC INDICES")
    print("-" * 30)
    
    indices_data = {}
    indices_info = {}
    
    for station in STATIONS:
        file_path = DATA_DIR / "indices" / f"Acoustic_Indices_{station}_{YEAR}_FullBW_v2_Final.csv"
        
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                indices_data[station] = df
                indices_info[station] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'file_size_mb': file_path.stat().st_size / (1024*1024),
                    'date_range': (df.iloc[0]['Date'], df.iloc[-1]['Date']) if 'Date' in df.columns else None
                }
                print(f"✓ {station}: {len(df)} rows, {len(df.columns)} columns ({indices_info[station]['file_size_mb']:.1f} MB)")
                
            except Exception as e:
                print(f"✗ {station}: Error loading - {e}")
        else:
            print(f"✗ {station}: File not found - {file_path}")
    
    print(f"Acoustic indices loaded for {len(indices_data)}/{len(STATIONS)} stations")
    print()
    return indices_data, indices_info

def load_manual_detections():
    """Load manual detection data with species filtering"""
    print("2. LOADING MANUAL DETECTIONS")
    print("-" * 30)
    
    # First load the metadata to know which species to keep
    metadata_path = DATA_DIR / "metadata" / "det_column_names.csv"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Species metadata file not found: {metadata_path}")
    
    metadata_df = pd.read_csv(metadata_path)
    keep_columns = metadata_df[metadata_df['keep_species'] == 1]['long_name'].tolist()
    essential_columns = ['Date', 'Date ', 'Time', 'Deployment ID', 'File']
    
    print(f"Species to keep: {', '.join(keep_columns)}")
    print()
    
    detection_data = {}
    detection_info = {}
    
    for station in STATIONS:
        file_path = DATA_DIR / str(YEAR) / "detections" / f"Master_Manual_{station}_2h_{YEAR}.xlsx"
        
        if file_path.exists():
            try:
                # Load the "Data" sheet
                df = pd.read_excel(file_path, sheet_name="Data")
                
                # Filter columns based on metadata
                available_keep_cols = [col for col in keep_columns if col in df.columns]
                available_essential_cols = [col for col in essential_columns if col in df.columns]
                cols_to_keep = list(set(available_keep_cols + available_essential_cols))
                
                df_filtered = df[cols_to_keep]
                detection_data[station] = df_filtered
                
                detection_info[station] = {
                    'rows': len(df_filtered),
                    'columns': len(df_filtered.columns),
                    'original_columns': len(df.columns),
                    'file_size_mb': file_path.stat().st_size / (1024*1024),
                    'species_columns': available_keep_cols,
                    'date_range': (df_filtered.iloc[0]['Date'], df_filtered.iloc[-1]['Date']) if 'Date' in df_filtered.columns else None
                }
                
                print(f"✓ {station}: {len(df_filtered)} rows, {len(df_filtered.columns)} columns (filtered from {len(df.columns)})")
                print(f"  Species: {', '.join(available_keep_cols)}")
                
            except Exception as e:
                print(f"✗ {station}: Error loading - {e}")
        else:
            print(f"✗ {station}: File not found - {file_path}")
    
    print(f"Manual detection data loaded for {len(detection_data)}/{len(STATIONS)} stations")
    print()
    return detection_data, detection_info

def load_environmental_data():
    """Load temperature and depth/pressure data"""
    print("3. LOADING ENVIRONMENTAL DATA")
    print("-" * 30)
    
    temp_data = {}
    depth_data = {}
    env_info = {}
    
    # Load temperature data (20-minute intervals)
    for station in STATIONS:
        temp_file = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station}_Temp_{YEAR}.xlsx"
        
        if temp_file.exists():
            try:
                df_temp = pd.read_excel(temp_file)
                temp_data[station] = df_temp
                print(f"✓ {station} temperature: {len(df_temp)} rows")
            except Exception as e:
                print(f"✗ {station} temperature: Error loading - {e}")
        else:
            print(f"✗ {station} temperature: File not found")
    
    # Load depth/pressure data (hourly intervals)  
    for station in STATIONS:
        depth_file = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station}_Depth_{YEAR}.xlsx"
        
        if depth_file.exists():
            try:
                df_depth = pd.read_excel(depth_file)
                depth_data[station] = df_depth
                print(f"✓ {station} depth: {len(df_depth)} rows")
            except Exception as e:
                print(f"✗ {station} depth: Error loading - {e}")
        else:
            # Try alternative naming
            depth_file = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station}_Press_{YEAR}.xlsx"
            if depth_file.exists():
                try:
                    df_depth = pd.read_excel(depth_file)
                    depth_data[station] = df_depth
                    print(f"✓ {station} pressure: {len(df_depth)} rows")
                except Exception as e:
                    print(f"✗ {station} pressure: Error loading - {e}")
            else:
                print(f"✗ {station} depth/pressure: File not found")
    
    env_info = {
        'temperature_stations': list(temp_data.keys()),
        'depth_stations': list(depth_data.keys()),
        'temp_total_rows': sum(len(df) for df in temp_data.values()),
        'depth_total_rows': sum(len(df) for df in depth_data.values())
    }
    
    print(f"Environmental data - Temperature: {len(temp_data)} stations, Depth: {len(depth_data)} stations")
    print()
    return temp_data, depth_data, env_info

def load_spl_data():
    """Load SPL (Sound Pressure Level) data"""
    print("4. LOADING SPL DATA") 
    print("-" * 30)
    
    spl_data = {}
    spl_info = {}
    
    for station in STATIONS:
        # Check processed SPL data first
        spl_file = DATA_ROOT / "processed" / "deprecated" / f"01_spl_{station}_{YEAR}.parquet"
        
        if spl_file.exists():
            try:
                df_spl = pd.read_parquet(spl_file)
                spl_data[station] = df_spl
                spl_info[station] = {
                    'rows': len(df_spl),
                    'columns': len(df_spl.columns),
                    'file_type': 'parquet_processed'
                }
                print(f"✓ {station}: {len(df_spl)} rows from processed parquet")
            except Exception as e:
                print(f"✗ {station}: Error loading processed SPL - {e}")
        else:
            # Check raw SPL data
            spl_raw_file = DATA_DIR / str(YEAR) / "rms_spl" / f"Master_rmsSPL_{station}_1h_{YEAR}.xlsx"
            if spl_raw_file.exists():
                try:
                    df_spl = pd.read_excel(spl_raw_file, sheet_name="Data")
                    spl_data[station] = df_spl
                    spl_info[station] = {
                        'rows': len(df_spl),
                        'columns': len(df_spl.columns), 
                        'file_type': 'xlsx_raw'
                    }
                    print(f"✓ {station}: {len(df_spl)} rows from raw Excel")
                except Exception as e:
                    print(f"✗ {station}: Error loading raw SPL - {e}")
            else:
                print(f"⚠️ {station}: SPL data not found")
    
    print(f"SPL data loaded for {len(spl_data)}/{len(STATIONS)} stations")
    print()
    return spl_data, spl_info

def create_temporal_alignment(indices_data, detection_data, temp_data, depth_data, spl_data):
    """Align all data streams to 2-hour intervals matching manual detections"""
    print("5. TEMPORAL ALIGNMENT TO 2-HOUR INTERVALS")
    print("-" * 40)
    
    aligned_data = {}
    
    for station in STATIONS:
        print(f"Aligning data for station {station}...")
        station_data = []
        
        # Start with manual detections as the reference (already 2-hour intervals)
        if station in detection_data:
            base_df = detection_data[station].copy()
            
            # Handle datetime creation properly - Date column already contains full datetime
            # Handle Station 37M which has 'Date ' with trailing space
            date_col = 'Date' if 'Date' in base_df.columns else 'Date '
            if date_col in base_df.columns:
                try:
                    base_df['datetime'] = pd.to_datetime(base_df[date_col], errors='coerce')
                    valid_datetimes = (~base_df['datetime'].isna()).sum()
                    print(f"  ✓ Created {valid_datetimes} valid datetimes from {len(base_df)} rows")
                except Exception as e:
                    print(f"  ⚠️ Warning: Could not create datetime for {station}: {e}")
                    continue
            else:
                print(f"  ⚠️ Warning: No Date column found for {station}")
                continue
                
            # Convert Time column to string to avoid Parquet serialization issues  
            if 'Time' in base_df.columns:
                base_df['Time'] = base_df['Time'].astype(str)
            
            # Convert non-numeric object columns to string to avoid Arrow conversion issues
            # but keep species detection columns as numeric
            object_cols = base_df.select_dtypes(include=['object']).columns
            for col in object_cols:
                if col not in ['Date', 'Date ', 'datetime', 'station']:  # Skip date/datetime/station columns
                    # Try to convert to numeric first, if it fails then convert to string
                    try:
                        base_df[col] = pd.to_numeric(base_df[col], errors='coerce')
                    except:
                        base_df[col] = base_df[col].astype(str)
            
            # Add station identifier AFTER data type conversion to prevent it from being converted
            base_df['station'] = station
            
            # Start with detection data as base
            station_df = base_df.copy()
            
        else:
            print(f"  ⚠️ Warning: No detection data for {station}")
            continue
        
        # TODO: Add acoustic indices aggregation (hourly to 2-hourly)
        if station in indices_data:
            print(f"  - Adding acoustic indices...")
            # For now, just note that indices need aggregation
            # This will be implemented in the actual alignment logic
        
        # TODO: Add temperature aggregation (20-min to 2-hourly)  
        if station in temp_data:
            print(f"  - Adding temperature data...")
            # Temperature needs aggregation from 20-minute to 2-hour intervals
            
        # TODO: Add depth aggregation (hourly to 2-hourly)
        if station in depth_data:
            print(f"  - Adding depth data...")
            # Depth needs aggregation from hourly to 2-hour intervals
            
        # TODO: Add SPL aggregation (depends on original resolution)
        if station in spl_data:
            print(f"  - Adding SPL data...")
            # SPL aggregation depends on original temporal resolution
        
        aligned_data[station] = station_df
        print(f"  ✓ Station {station}: {len(station_df)} aligned records")
    
    # Combine all stations
    if aligned_data:
        combined_df = pd.concat(aligned_data.values(), ignore_index=True)
        print(f"Combined dataset: {len(combined_df)} total records across {len(aligned_data)} stations")
        return combined_df
    else:
        print("⚠️ Warning: No data could be aligned")
        return pd.DataFrame()

def generate_quality_report(indices_info, detection_info, env_info, spl_info, combined_df):
    """Generate comprehensive data quality report"""
    print("6. GENERATING DATA QUALITY REPORT")
    print("-" * 40)
    
    quality_report = {
        'generation_timestamp': datetime.now().isoformat(),
        'analysis_parameters': {
            'year': YEAR,
            'stations': STATIONS,
            'total_expected_stations': len(STATIONS)
        },
        'data_sources': {
            'acoustic_indices': {
                'stations_loaded': len(indices_info),
                'total_rows': sum(info['rows'] for info in indices_info.values()),
                'average_columns': np.mean([info['columns'] for info in indices_info.values()]) if indices_info else 0,
                'details': indices_info
            },
            'manual_detections': {
                'stations_loaded': len(detection_info),
                'total_rows': sum(info['rows'] for info in detection_info.values()),
                'average_columns': np.mean([info['columns'] for info in detection_info.values()]) if detection_info else 0,
                'details': detection_info
            },
            'environmental': env_info,
            'spl': {
                'stations_loaded': len(spl_info),
                'total_rows': sum(info['rows'] for info in spl_info.values()),
                'details': spl_info
            }
        },
        'aligned_dataset': {
            'total_records': len(combined_df),
            'stations_in_final': combined_df['station'].nunique() if 'station' in combined_df.columns else 0,
            'date_range': (combined_df['datetime'].min().isoformat(), combined_df['datetime'].max().isoformat()) if 'datetime' in combined_df.columns and len(combined_df) > 0 else None,
            'columns': list(combined_df.columns) if len(combined_df) > 0 else []
        },
        'data_completeness': {
            'indices_success_rate': len(indices_info) / len(STATIONS),
            'detection_success_rate': len(detection_info) / len(STATIONS),
            'environmental_success_rate': len(env_info['temperature_stations']) / len(STATIONS),
            'spl_success_rate': len(spl_info) / len(STATIONS)
        }
    }
    
    # Save quality report
    report_file = OUTPUT_DIR / "data_quality_report.json"
    with open(report_file, 'w') as f:
        json.dump(quality_report, f, indent=2, default=str)
    
    print(f"✓ Quality report saved: {report_file}")
    
    # Print summary
    print("\nDATA QUALITY SUMMARY:")
    print(f"Acoustic indices: {len(indices_info)}/{len(STATIONS)} stations")
    print(f"Manual detections: {len(detection_info)}/{len(STATIONS)} stations") 
    print(f"Environmental: {len(env_info['temperature_stations'])}/{len(STATIONS)} temperature, {len(env_info['depth_stations'])}/{len(STATIONS)} depth")
    print(f"SPL: {len(spl_info)}/{len(STATIONS)} stations")
    print(f"Final aligned dataset: {len(combined_df)} records")
    
    return quality_report

def create_coverage_plots(combined_df, quality_report):
    """Create temporal coverage and missing data visualizations"""
    print("7. CREATING COVERAGE VISUALIZATIONS")
    print("-" * 40)
    
    if len(combined_df) == 0:
        print("⚠️ No data available for plotting")
        return
    
    # Set up plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create temporal coverage summary plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Data Coverage Summary - {YEAR}', fontsize=16, fontweight='bold')
    
    # Plot 1: Data sources by station
    ax1 = axes[0, 0]
    source_counts = pd.DataFrame({
        'Acoustic Indices': [1 if station in quality_report['data_sources']['acoustic_indices']['details'] else 0 for station in STATIONS],
        'Manual Detections': [1 if station in quality_report['data_sources']['manual_detections']['details'] else 0 for station in STATIONS], 
        'Temperature': [1 if station in quality_report['data_sources']['environmental']['temperature_stations'] else 0 for station in STATIONS],
        'SPL': [1 if station in quality_report['data_sources']['spl']['details'] else 0 for station in STATIONS]
    }, index=STATIONS)
    
    source_counts.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title('Data Sources Available by Station')
    ax1.set_xlabel('Station')
    ax1.set_ylabel('Data Available (1=Yes, 0=No)')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.tick_params(axis='x', rotation=0)
    
    # Plot 2: Records per station over time (if datetime available)
    ax2 = axes[0, 1]
    if 'datetime' in combined_df.columns and 'station' in combined_df.columns:
        for station in combined_df['station'].unique():
            station_data = combined_df[combined_df['station'] == station]
            if len(station_data) > 0:
                monthly_counts = station_data.set_index('datetime').resample('M').size()
                ax2.plot(monthly_counts.index, monthly_counts.values, marker='o', label=f'Station {station}')
        
        ax2.set_title('Records per Month by Station')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Number of Records')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
    else:
        ax2.text(0.5, 0.5, 'No temporal data available', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Temporal Coverage (Data Not Available)')
    
    # Plot 3: Data completeness rates
    ax3 = axes[1, 0]
    completeness = quality_report['data_completeness']
    sources = list(completeness.keys())
    rates = [completeness[source] * 100 for source in sources]
    
    bars = ax3.bar(range(len(sources)), rates)
    ax3.set_title('Data Completeness by Source')
    ax3.set_xlabel('Data Source')
    ax3.set_ylabel('Completeness (%)')
    ax3.set_xticks(range(len(sources)))
    ax3.set_xticklabels([s.replace('_', ' ').title() for s in sources], rotation=45)
    ax3.set_ylim(0, 100)
    
    # Add percentage labels on bars
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 1, f'{rate:.0f}%', 
                ha='center', va='bottom')
    
    # Plot 4: Summary statistics
    ax4 = axes[1, 1]
    summary_text = f"""
DATASET SUMMARY
Total Records: {quality_report['aligned_dataset']['total_records']:,}
Stations: {quality_report['aligned_dataset']['stations_in_final']}/{len(STATIONS)}
Date Range: {quality_report['aligned_dataset']['date_range'][0][:10] if quality_report['aligned_dataset']['date_range'] else 'N/A'} to 
           {quality_report['aligned_dataset']['date_range'][1][:10] if quality_report['aligned_dataset']['date_range'] else 'N/A'}

DATA SOURCES LOADED:
• Acoustic Indices: {quality_report['data_sources']['acoustic_indices']['stations_loaded']}/{len(STATIONS)} stations
• Manual Detections: {quality_report['data_sources']['manual_detections']['stations_loaded']}/{len(STATIONS)} stations  
• Environmental: {len(quality_report['data_sources']['environmental']['temperature_stations'])}/{len(STATIONS)} stations
• SPL: {quality_report['data_sources']['spl']['stations_loaded']}/{len(STATIONS)} stations
"""
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10, 
             verticalalignment='top', fontfamily='monospace')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    coverage_file = FIGURE_DIR / "01_data_coverage_summary.png"
    plt.savefig(coverage_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Coverage summary saved: {coverage_file}")
    
    # Create missing data heatmap if we have aligned data
    if len(combined_df) > 0 and len(combined_df.columns) > 5:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Filter out redundant metadata columns for cleaner visualization
        exclude_cols = ['Time', 'Date', 'Date ', 'Deployment ID', 'File']
        analysis_cols = [col for col in combined_df.columns if col not in exclude_cols]
        df_analysis = combined_df[analysis_cols]
        
        # Calculate missing data percentage for analytical columns only
        missing_pct = df_analysis.isnull().sum() / len(df_analysis) * 100
        missing_pct = missing_pct.sort_values(ascending=False)
        
        # Create heatmap data using filtered analysis columns (1=present, 0=missing)
        heatmap_data = df_analysis[missing_pct.index].notnull().T
        
        # Plot heatmap (sample if too many rows)
        if len(heatmap_data.columns) > 1000:
            # Sample every nth row to make it manageable
            step = len(heatmap_data.columns) // 1000
            heatmap_data = heatmap_data.iloc[:, ::step]
        
        # Use proper binary colormap for data presence (1=present, 0=missing)
        sns.heatmap(heatmap_data, cbar=True, cmap='RdYlGn', ax=ax, 
                   cbar_kws={'label': 'Data Availability (1=Present, 0=Missing)'}, vmin=0, vmax=1)
        ax.set_title(f'Missing Data Pattern - {YEAR}\n(Analytical Variables Only)', fontweight='bold')
        ax.set_xlabel('Time Points (sampled)')
        ax.set_ylabel('Analytical Variables')
        
        # Add missing percentage annotations
        for i, (var, pct) in enumerate(missing_pct.items()):
            if i < 20:  # Only annotate first 20 to avoid crowding
                ax.text(len(heatmap_data.columns) + 10, i + 0.5, f'{pct:.1f}%', 
                       va='center', fontsize=8)
        
        plt.tight_layout()
        missing_file = FIGURE_DIR / "01_missing_data_heatmap.png" 
        plt.savefig(missing_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Missing data heatmap saved: {missing_file}")
    else:
        print("⚠️ Insufficient data for missing data heatmap")

def main():
    """Main execution function"""
    print("Starting data preparation pipeline...")
    
    # Load all data sources
    indices_data, indices_info = load_acoustic_indices()
    detection_data, detection_info = load_manual_detections()
    temp_data, depth_data, env_info = load_environmental_data()
    spl_data, spl_info = load_spl_data()
    
    # Perform temporal alignment
    combined_df = create_temporal_alignment(indices_data, detection_data, temp_data, depth_data, spl_data)
    
    # Generate quality report
    quality_report = generate_quality_report(indices_info, detection_info, env_info, spl_info, combined_df)
    
    # Create visualizations
    create_coverage_plots(combined_df, quality_report)
    
    # Save aligned dataset
    if len(combined_df) > 0:
        output_file = OUTPUT_DIR / "aligned_dataset_2021.parquet"
        combined_df.to_parquet(output_file, index=False)
        print(f"✓ Aligned dataset saved: {output_file}")
    else:
        print("⚠️ Warning: No aligned dataset to save")
    
    print()
    print("="*60)
    print("DATA PREPARATION COMPLETE")
    print("="*60)
    print(f"Key outputs:")
    print(f"- Aligned dataset: {OUTPUT_DIR / 'aligned_dataset_2021.parquet'}")
    print(f"- Quality report: {OUTPUT_DIR / 'data_quality_report.json'}")
    print(f"- Coverage summary: {FIGURE_DIR / '01_data_coverage_summary.png'}")
    print(f"- Missing data heatmap: {FIGURE_DIR / '01_missing_data_heatmap.png'}")

if __name__ == "__main__":
    main()