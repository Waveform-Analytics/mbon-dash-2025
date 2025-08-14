#!/usr/bin/env python3
"""
Enhanced data processing script for MBON Marine Biodiversity Dashboard.
Processes Excel files from 2018 and 2021 into optimized JSON files for the web dashboard.

Based on examples.py but with additional functionality:
- Combines detection, environmental, and acoustic data
- Generates metadata and station information
- Creates optimized JSON files for client-side loading
- Validates data integrity and generates summary statistics
"""

import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import numpy as np

# Configuration - Updated for new structure
RAW_DATA_DIR = Path("data/cdn/raw-data")
OUTPUT_DIR = Path("data/cdn/processed")  # Output to CDN processed folder
COLUMN_MAPPING_FILE = RAW_DATA_DIR / "det_column_names.csv"

# FOCUSED SCOPE: Only process these years and stations
YEARS_OF_INTEREST = ["2018", "2021"]
STATIONS_OF_INTEREST = ["9M", "14M", "37M"]

# File patterns for different data types
DETECTION_PATTERN = "Master_Manual_*_2h_*.xlsx"
TEMP_PATTERN = "Master_*_Temp_*.xlsx"
DEPTH_PATTERN = "Master_*_Depth_*.xlsx"
ACOUSTIC_PATTERN = "Master_rmsSPL_*_1h_*.xlsx"

def load_column_mapping():
    """Load column name mapping from CSV file."""
    print("📋 Loading column mappings...")
    df = pd.read_csv(COLUMN_MAPPING_FILE)
    
    # Create mapping from short_name to long_name
    name_mapping = dict(zip(df["short_name"], df["long_name"]))
    
    # Also create mapping with type information for metadata
    type_mapping = {}
    for _, row in df.iterrows():
        type_mapping[row["short_name"]] = {
            "long_name": row["long_name"],
            "type": row["type"]
        }
    
    return name_mapping, type_mapping

def extract_metadata_from_filename(filepath):
    """Extract year and station information from filename."""
    parts = str(filepath).split('/')
    year = parts[-2]  # e.g., "2018" or "2021"
    filename = parts[-1]
    
    # Extract station from filename (e.g., "Master_Manual_9M_2h_2018.xlsx" -> "9M")
    if "Manual" in filename:
        station_part = filename.split('_')[2]
    else:
        station_part = filename.split('_')[1]
    
    return year, station_part

def process_detection_files():
    """Process all detection files and combine into single dataset."""
    print("🐟 Processing species detection files...")
    
    column_lookup, type_mapping = load_column_mapping()
    short_column_names = list(column_lookup.keys())
    
    # Find all detection files (FILTERED TO YEARS OF INTEREST)
    detection_files = []
    for year in YEARS_OF_INTEREST:  # Only 2018, 2021
        year_dir = RAW_DATA_DIR / year
        if year_dir.exists():
            detection_files.extend(year_dir.glob("Master_Manual_*_2h_*.xlsx"))
    
    print(f"Found {len(detection_files)} detection files")
    
    all_dfs = []
    for file in detection_files:
        print(f"  Processing: {file.name}")
        try:
            # Read Excel file (sheet 1, as in examples.py)
            df = pd.read_excel(file, sheet_name=1)
            
            # Apply column mapping
            if len(df.columns) == len(short_column_names):
                df.columns = short_column_names
            else:
                print(f"  ⚠️  Column count mismatch in {file.name}: expected {len(short_column_names)}, got {len(df.columns)}")
                continue
            
            # Extract metadata
            year, station = extract_metadata_from_filename(file)
            
            # FILTER: Only process stations of interest
            if station not in STATIONS_OF_INTEREST:
                print(f"  ⏭️  Skipping station {station} (not in stations of interest: {STATIONS_OF_INTEREST})")
                continue
                
            df['year'] = year
            df['station'] = station
            df['source_file'] = file.name
            
            all_dfs.append(df)
            
        except Exception as e:
            print(f"  ❌ Error processing {file.name}: {e}")
    
    if not all_dfs:
        raise ValueError("No detection files were successfully processed!")
    
    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Process dates
    combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
    combined_df = combined_df.dropna(subset=['date'])  # Remove rows with invalid dates
    
    print(f"✅ Combined {len(combined_df)} detection records from {len(all_dfs)} files")
    return combined_df, column_lookup, type_mapping

def process_environmental_files():
    """Process temperature and depth files - merge by timestamp where possible."""
    print("🌡️  Processing environmental data files...")
    
    merged_data = []
    
    for year in YEARS_OF_INTEREST:  # Only 2018, 2021
        year_dir = RAW_DATA_DIR / year
        if not year_dir.exists():
            continue
        
        for station in STATIONS_OF_INTEREST:
            # Try to load both temperature and depth for this station/year
            temp_file = year_dir / f"Master_{station}_Temp_{year}.xlsx"
            depth_file = year_dir / f"Master_{station}_Depth_{year}.xlsx"
            
            temp_df = None
            depth_df = None
            
            # Load temperature data
            if temp_file.exists():
                try:
                    temp_df = pd.read_excel(temp_file, sheet_name=1)
                    temp_df = temp_df.rename(columns={'Date and time': 'datetime'})
                    # Round timestamps to nearest second to handle millisecond differences
                    temp_df['datetime'] = pd.to_datetime(temp_df['datetime']).dt.round('s')
                    print(f"  📊 Loaded temperature: {temp_file.name}")
                except Exception as e:
                    print(f"  ❌ Error processing {temp_file.name}: {e}")
            
            # Load depth data
            if depth_file.exists():
                try:
                    depth_df = pd.read_excel(depth_file, sheet_name=1)
                    depth_df = depth_df.rename(columns={'Date and time': 'datetime'})
                    # Round timestamps to nearest second to handle millisecond differences
                    depth_df['datetime'] = pd.to_datetime(depth_df['datetime']).dt.round('s')
                    print(f"  📊 Loaded depth: {depth_file.name}")
                except Exception as e:
                    print(f"  ❌ Error processing {depth_file.name}: {e}")
            
            # Merge or append based on what's available
            if temp_df is not None and depth_df is not None:
                # Merge on datetime where possible
                merged = pd.merge(temp_df, depth_df, on='datetime', how='outer', suffixes=('_temp', '_depth'))
                
                # Set measurement_type based on what data is actually present in each row
                conditions = [
                    (merged['Water temp (°C)'].notna() & merged['Water depth (m)'].notna()),
                    (merged['Water temp (°C)'].notna() & merged['Water depth (m)'].isna()),
                    (merged['Water temp (°C)'].isna() & merged['Water depth (m)'].notna())
                ]
                choices = ['combined', 'temperature', 'depth']
                merged['measurement_type'] = np.select(conditions, choices, default='none')
                
                print(f"  🔗 Merged temp & depth for {station} {year}: {len(merged)} records")
                
                # Report merge quality
                combined_count = (merged['measurement_type'] == 'combined').sum()
                temp_only = (merged['measurement_type'] == 'temperature').sum()
                depth_only = (merged['measurement_type'] == 'depth').sum()
                print(f"     Combined: {combined_count}, Temp only: {temp_only}, Depth only: {depth_only}")
                
            elif temp_df is not None:
                merged = temp_df
                merged['measurement_type'] = 'temperature'
                merged['Water depth (m)'] = None
            elif depth_df is not None:
                merged = depth_df
                merged['measurement_type'] = 'depth'
                merged['Water temp (°C)'] = None
            else:
                continue
            
            # Add metadata
            merged['year'] = year
            merged['station'] = station
            # datetime is already converted and rounded above
            merged_data.append(merged)
    
    if merged_data:
        combined_env = pd.concat(merged_data, ignore_index=True)
        print(f"✅ Combined {len(combined_env)} environmental records")
        
        # Report on data completeness using measurement_type field
        combined_count = (combined_env['measurement_type'] == 'combined').sum()
        temp_only = (combined_env['measurement_type'] == 'temperature').sum()
        depth_only = (combined_env['measurement_type'] == 'depth').sum()
        none_count = (combined_env['measurement_type'] == 'none').sum() if 'none' in combined_env['measurement_type'].values else 0
        
        print(f"  📊 Data completeness (by measurement_type):")
        print(f"     - Combined (both): {combined_count:,} records")
        print(f"     - Temperature only: {temp_only:,} records")
        print(f"     - Depth only: {depth_only:,} records")
        if none_count > 0:
            print(f"     - None/missing: {none_count:,} records")
        
        # Rename datetime back for consistency
        combined_env = combined_env.rename(columns={'datetime': 'Date and time'})
        return combined_env
    else:
        print("⚠️  No environmental data files found")
        return pd.DataFrame()

def process_acoustic_files():
    """Process acoustic index (rmsSPL) files."""
    print("🔊 Processing acoustic data files...")
    
    acoustic_data = []
    
    for year in YEARS_OF_INTEREST:  # Only 2018, 2021
        year_dir = RAW_DATA_DIR / year
        if not year_dir.exists():
            continue
            
        acoustic_files = list(year_dir.glob("Master_rmsSPL_*_1h_*.xlsx"))
        for file in acoustic_files:
            try:
                year, station = extract_metadata_from_filename(file)
                
                # FILTER: Only process stations of interest
                if station not in STATIONS_OF_INTEREST:
                    print(f"  ⏭️  Skipping acoustic {station} (not in stations of interest)")
                    continue
                    
                # FIX: Use sheet 1 instead of sheet 0
                df = pd.read_excel(file, sheet_name=1)
                df['year'] = year
                df['station'] = station
                df['source_file'] = file.name
                acoustic_data.append(df)
                print(f"  🎵 Processed acoustic: {file.name}")
            except Exception as e:
                print(f"  ❌ Error processing {file.name}: {e}")
    
    if acoustic_data:
        combined_acoustic = pd.concat(acoustic_data, ignore_index=True)
        print(f"✅ Combined {len(combined_acoustic)} acoustic records")
        return combined_acoustic
    else:
        print("⚠️  No acoustic data files found")
        return pd.DataFrame()

def process_acoustic_indices_files():
    """Process acoustic indices CSV files."""
    print("🎵 Processing acoustic indices files...")
    
    indices_dir = RAW_DATA_DIR / "indices"
    if not indices_dir.exists():
        print("⚠️  Indices directory not found")
        return pd.DataFrame()
    
    # Find all CSV files in indices directory
    indices_files = list(indices_dir.glob("*.csv"))
    if not indices_files:
        print("⚠️  No indices CSV files found")
        return pd.DataFrame()
    
    print(f"Found {len(indices_files)} indices files")
    
    all_indices_data = []
    
    for file in indices_files:
        try:
            print(f"  Processing: {file.name}")
            
            # Parse filename to extract metadata
            # Expected format: Acoustic_Indices_[STATION]_[YEAR]_[BANDWIDTH]_v[VERSION]_Final.csv
            filename_parts = file.stem.split('_')
            
            if len(filename_parts) >= 5:
                station = filename_parts[2]  # e.g., "9M"
                year = filename_parts[3]     # e.g., "2021"
                bandwidth = filename_parts[4] # e.g., "FullBW" or "8kHz"
                
                # Filter by stations and years of interest
                if station not in STATIONS_OF_INTEREST:
                    print(f"  ⏭️  Skipping station {station} (not in stations of interest)")
                    continue
                    
                if year not in YEARS_OF_INTEREST:
                    print(f"  ⏭️  Skipping year {year} (not in years of interest)")
                    continue
                
                # Read CSV file
                df = pd.read_csv(file)
                
                # Add metadata columns
                df['year'] = year
                df['station'] = station
                df['bandwidth'] = bandwidth
                df['source_file'] = file.name
                
                # Parse date column if it exists
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df = df.dropna(subset=['Date'])  # Remove rows with invalid dates
                
                all_indices_data.append(df)
                print(f"  🎵 Processed {len(df)} indices records from {file.name}")
                
            else:
                print(f"  ⚠️  Unexpected filename format: {file.name}")
                
        except Exception as e:
            print(f"  ❌ Error processing {file.name}: {e}")
    
    if all_indices_data:
        combined_indices = pd.concat(all_indices_data, ignore_index=True)
        print(f"✅ Combined {len(combined_indices)} acoustic indices records")
        
        # Report on what we processed
        stations_processed = combined_indices['station'].unique()
        years_processed = combined_indices['year'].unique()
        bandwidths_processed = combined_indices['bandwidth'].unique()
        
        print(f"  📊 Processed data:")
        print(f"     - Stations: {', '.join(sorted(stations_processed))}")
        print(f"     - Years: {', '.join(sorted(years_processed))}")
        print(f"     - Bandwidths: {', '.join(sorted(bandwidths_processed))}")
        
        return combined_indices
    else:
        print("⚠️  No acoustic indices data was successfully processed")
        return pd.DataFrame()

def process_deployment_metadata():
    """Process deployment metadata Excel file."""
    print("📋 Processing deployment metadata...")
    
    metadata_file = RAW_DATA_DIR / "1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
    if not metadata_file.exists():
        print(f"⚠️  Metadata file not found: {metadata_file}")
        return pd.DataFrame()
    
    try:
        # Read the metadata Excel file
        # Note: You may need to adjust sheet_name based on the actual structure
        metadata_df = pd.read_excel(metadata_file, sheet_name=0)
        
        # Clean up column names (remove spaces, lowercase)
        metadata_df.columns = [col.strip().lower().replace(' ', '_') for col in metadata_df.columns]
        
        print(f"📋 Read {len(metadata_df)} total metadata records")
        
        # FILTER: Only keep records for years and stations of interest
        before_count = len(metadata_df)
        
        # Filter by year (if year column exists)
        if 'year' in metadata_df.columns:
            metadata_df = metadata_df[metadata_df['year'].isin([2018, 2021])]
            print(f"  📅 Filtered to years {YEARS_OF_INTEREST}: {len(metadata_df)} records")
        
        # Filter by station (if station column exists)
        if 'station' in metadata_df.columns:
            metadata_df = metadata_df[metadata_df['station'].isin(STATIONS_OF_INTEREST)]
            print(f"  📍 Filtered to stations {STATIONS_OF_INTEREST}: {len(metadata_df)} records")
        
        print(f"✅ Processed metadata: {before_count} → {len(metadata_df)} records (filtered)")
        return metadata_df
    except Exception as e:
        print(f"❌ Error processing metadata file: {e}")
        return pd.DataFrame()

def generate_station_metadata(detections_df, environmental_df, acoustic_df, deployment_metadata_df):
    """Generate station metadata including coordinates and data availability."""
    print("📍 Generating station metadata...")
    
    stations = []
    all_stations = set()
    
    # Collect all unique stations
    for df in [detections_df, environmental_df, acoustic_df]:
        if not df.empty and 'station' in df.columns:
            all_stations.update(df['station'].unique())
    
    for station in sorted(all_stations):
        station_info = {
            'id': station,
            'name': f'Station {station}',
            'coordinates': get_station_coordinates(station),  # TODO: Add real coordinates
            'years': [],
            'data_types': [],
            'metadata': {}  # New field for additional metadata
        }
        
        # Check data availability
        if not detections_df.empty and station in detections_df['station'].values:
            station_info['data_types'].append('detections')
            years = detections_df[detections_df['station'] == station]['year'].unique()
            station_info['years'].extend(years)
            
        if not environmental_df.empty and station in environmental_df['station'].values:
            station_info['data_types'].append('environmental')
            years = environmental_df[environmental_df['station'] == station]['year'].unique()
            station_info['years'].extend(years)
            
        if not acoustic_df.empty and station in acoustic_df['station'].values:
            station_info['data_types'].append('acoustic')
            years = acoustic_df[acoustic_df['station'] == station]['year'].unique()
            station_info['years'].extend(years)
        
        # Add deployment metadata if available
        if not deployment_metadata_df.empty:
            # Assuming the metadata has a 'station' or similar column
            # You may need to adjust the column name based on the actual structure
            station_column = next((col for col in deployment_metadata_df.columns 
                                if 'station' in col.lower()), None)
            
            if station_column:
                station_metadata = deployment_metadata_df[
                    deployment_metadata_df[station_column].astype(str).str.strip() == station
                ]
                
                if not station_metadata.empty:
                    # Convert metadata to dictionary, excluding NaN values
                    for _, row in station_metadata.iterrows():
                        for col in station_metadata.columns:
                            if pd.notna(row[col]):
                                station_info['metadata'][col] = row[col]
        
        station_info['years'] = sorted(list(set(station_info['years'])))
        stations.append(station_info)
    
    print(f"✅ Generated metadata for {len(stations)} stations")
    return stations

def get_station_coordinates(station):
    """Get coordinates for station (placeholder - replace with real coordinates)."""
    # TODO: Replace with actual station coordinates
    coordinate_map = {
        '9M': {'lat': 33.5, 'lon': -118.2},
        '14M': {'lat': 33.6, 'lon': -118.3},
        '37M': {'lat': 33.7, 'lon': -118.4},
        'B': {'lat': 33.8, 'lon': -118.5},
        'C': {'lat': 33.9, 'lon': -118.6},
        'CC4': {'lat': 34.0, 'lon': -118.7},
        'CR1': {'lat': 34.1, 'lon': -118.8},
        'D': {'lat': 34.2, 'lon': -118.9},
        'WB': {'lat': 34.3, 'lon': -119.0},
    }
    return coordinate_map.get(station, {'lat': 33.5, 'lon': -118.5})

def generate_species_metadata(detections_df, column_lookup, type_mapping):
    """Generate detection metadata with detection counts and proper categorization."""
    print("🐠 Generating detection metadata...")
    
    detection_columns = [col for col in detections_df.columns 
                        if col in column_lookup and col not in ['id', 'file', 'date', 'time', 'analyzer']]
    
    detection_list = []
    for short_name in detection_columns:
        long_name = column_lookup.get(short_name, short_name)
        detection_type = type_mapping.get(short_name, {}).get('type', 'unknown')
        
        # Calculate detection counts (handle mixed data types)
        if short_name in detections_df.columns:
            column_data = pd.to_numeric(detections_df[short_name], errors='coerce')
            total_detections = column_data.sum()
        else:
            total_detections = 0
        
        # Map type to category for backwards compatibility
        category_mapping = {
            'bio': 'biological',
            'anthro': 'anthropogenic_environmental',
            'info': 'metadata',
            'none': 'other'
        }
        
        detection_info = {
            'short_name': short_name,
            'long_name': long_name,
            'type': detection_type,
            'category': category_mapping.get(detection_type, 'other'),
            'total_detections': int(total_detections) if pd.notna(total_detections) else 0
        }
        detection_list.append(detection_info)
    
    # Sort by detection count
    detection_list.sort(key=lambda x: x['total_detections'], reverse=True)
    print(f"✅ Generated metadata for {len(detection_list)} detections/annotations")
    return detection_list

def categorize_species(species_name):
    """Categorize species by type."""
    name_lower = species_name.lower()
    if 'dolphin' in name_lower:
        return 'marine_mammal'
    elif 'whale' in name_lower:
        return 'marine_mammal'
    elif 'manatee' in name_lower:
        return 'marine_mammal'
    elif any(fish in name_lower for fish in ['perch', 'toadfish', 'drum', 'trout', 'croaker', 'weakfish']):
        return 'fish'
    elif 'alligator' in name_lower:
        return 'reptile'
    elif any(sound in name_lower for sound in ['vessel', 'rain', 'waves', 'chain', 'static']):
        return 'anthropogenic_environmental'
    else:
        return 'other'

def save_json_files(detections_df, environmental_df, acoustic_df, acoustic_indices_df, stations, species, column_lookup, deployment_metadata_df):
    """Save all processed data as JSON files."""
    print("💾 Saving JSON files...")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Convert DataFrames to JSON-serializable format
    def clean_for_json(df):
        """Clean DataFrame for JSON serialization."""
        if df.empty:
            return []
        
        # Handle datetime columns
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Replace NaN with None
        df = df.replace({np.nan: None})
        return df.to_dict(orient='records')
    
    # Save main datasets
    files_to_save = {
        'detections.json': clean_for_json(detections_df),
        'environmental.json': clean_for_json(environmental_df),
        'acoustic.json': clean_for_json(acoustic_df),
        'acoustic_indices.json': clean_for_json(acoustic_indices_df),  # New file
        'deployment_metadata.json': clean_for_json(deployment_metadata_df),
        'stations.json': stations,
        'species.json': species,
        'metadata.json': {
            'generated_at': datetime.now().isoformat(),
            'column_mapping': column_lookup,
            'data_summary': {
                'total_detections': len(detections_df),
                'total_environmental_records': len(environmental_df),
                'total_acoustic_records': len(acoustic_df),
                'total_acoustic_indices_records': len(acoustic_indices_df),  # New line
                'total_deployment_metadata_records': len(deployment_metadata_df),
                'stations_count': len(stations),
                'species_count': len(species),
                'date_range': {
                    'start': str(detections_df['date'].min())[:10] if not detections_df.empty and pd.notna(detections_df['date'].min()) else None,
                    'end': str(detections_df['date'].max())[:10] if not detections_df.empty and pd.notna(detections_df['date'].max()) else None
                }
            }
        }
    }
    
    for filename, data in files_to_save.items():
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  ✅ Saved {filepath} ({len(str(data))} chars)")
    
    print(f"✅ All data saved to {OUTPUT_DIR}")

def main():
    """Main processing function."""
    print("🚀 Starting MBON data processing...")
    print(f"📂 Input directory: {RAW_DATA_DIR}")
    print(f"📂 Output directory: {OUTPUT_DIR}")
    
    try:
        # Process detection files (main dataset)
        detections_df, column_lookup, type_mapping = process_detection_files()
        
        # Process environmental data
        environmental_df = process_environmental_files()
        
        # Process acoustic data
        acoustic_df = process_acoustic_files()
        
        # Process acoustic indices data (new)
        acoustic_indices_df = process_acoustic_indices_files()
        
        # Process deployment metadata
        deployment_metadata_df = process_deployment_metadata()
        
        # Generate metadata
        stations = generate_station_metadata(detections_df, environmental_df, acoustic_df, deployment_metadata_df)
        species = generate_species_metadata(detections_df, column_lookup, type_mapping)
        
        # Save all data as JSON
        save_json_files(detections_df, environmental_df, acoustic_df, acoustic_indices_df, stations, species, column_lookup, deployment_metadata_df)
        
        print("\n🎉 Data processing completed successfully!")
        print(f"📊 Summary:")
        print(f"   • {len(detections_df):,} detection records")
        print(f"   • {len(environmental_df):,} environmental records")  
        print(f"   • {len(acoustic_df):,} acoustic records")
        print(f"   • {len(acoustic_indices_df):,} acoustic indices records")  # New line
        print(f"   • {len(deployment_metadata_df):,} deployment metadata records")
        print(f"   • {len(stations)} stations")
        print(f"   • {len(species)} species")
        print(f"\n💡 Next step: Run 'npm run dev' to start the dashboard!")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()