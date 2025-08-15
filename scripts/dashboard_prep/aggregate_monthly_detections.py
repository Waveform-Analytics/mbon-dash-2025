#!/usr/bin/env python3
"""
Monthly Detections Aggregation Script

Aggregates detection data by month, station, and detection type for timeline visualization.
Creates zero-filled monthly data for complete 12-month timeline.

Input: data/cdn/processed/detections.json, species.json
Output: data/cdn/processed/monthly_detections.json
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def load_data():
    """Load detections and species metadata"""
    data_dir = project_root / "data" / "cdn" / "processed"
    
    print("Loading detections data...")
    with open(data_dir / "detections.json", 'r') as f:
        detections = json.load(f)
    
    print("Loading species metadata...")
    with open(data_dir / "species.json", 'r') as f:
        species = json.load(f)
    
    return detections, species

def prepare_species_mapping(species):
    """Create mapping of detection types to categories"""
    mapping = {}
    biological_types = []
    anthropogenic_types = []
    
    for species_info in species:
        short_name = species_info['short_name']
        type_category = species_info['type']
        
        mapping[short_name] = {
            'long_name': species_info['long_name'],
            'type': type_category,
            'category': species_info['category']
        }
        
        if type_category == 'bio':
            biological_types.append(short_name)
        elif type_category == 'anthro':
            anthropogenic_types.append(short_name)
    
    return mapping, biological_types, anthropogenic_types

def aggregate_monthly_detections(detections, species_mapping, biological_types, anthropogenic_types):
    """Aggregate detections by month, station, and detection type"""
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(detections)
    
    # Parse dates and extract month
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['year'] = df['year'].astype(int)
    
    print(f"Processing {len(df)} detection records...")
    print(f"Years: {sorted(df['year'].unique())}")
    print(f"Stations: {sorted(df['station'].unique())}")
    print(f"Months: {sorted(df['month'].unique())}")
    
    # Get all detection type columns (exclude metadata columns)
    metadata_cols = ['id', 'file', 'date', 'time', 'analyzer', 'year', 'station', 'source_file', 'month']
    detection_cols = [col for col in df.columns if col not in metadata_cols]
    
    # Filter to only columns that exist in species mapping
    valid_detection_cols = [col for col in detection_cols if col in species_mapping]
    
    # Convert detection columns to numeric, handling mixed types
    for col in valid_detection_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"Valid detection types: {len(valid_detection_cols)}")
    
    results = []
    
    # Get all combinations of year, month, station for zero-filling
    years = sorted(df['year'].unique())
    months = range(1, 13)  # All 12 months
    stations = sorted(df['station'].unique())
    
    print(f"Creating aggregations for {len(years)} years, 12 months, {len(stations)} stations...")
    
    for year in years:
        year_data = df[df['year'] == year]
        
        for month in months:
            month_data = year_data[year_data['month'] == month]
            
            for station in stations:
                station_data = month_data[month_data['station'] == station]
                
                # Calculate totals for this month/station combination
                if len(station_data) == 0:
                    # Zero-fill for missing data
                    all_count = 0
                    bio_count = 0
                    anthro_count = 0
                    individual_counts = {col: 0 for col in valid_detection_cols}
                else:
                    # Sum detections across all records for this month/station
                    all_count = int(station_data[valid_detection_cols].sum().sum())
                    bio_count = int(station_data[biological_types].sum().sum())
                    anthro_count = int(station_data[anthropogenic_types].sum().sum())
                    individual_counts = {col: int(station_data[col].sum()) for col in valid_detection_cols}
                
                # Add summary records (convert numpy types to native Python types)
                results.append({
                    "year": int(year),
                    "month": int(month),
                    "station": str(station),
                    "detection_type": "all",
                    "count": int(all_count)
                })
                
                results.append({
                    "year": int(year),
                    "month": int(month),
                    "station": str(station),
                    "detection_type": "biological",
                    "count": int(bio_count)
                })
                
                results.append({
                    "year": int(year),
                    "month": int(month),
                    "station": str(station),
                    "detection_type": "anthropogenic",
                    "count": int(anthro_count)
                })
                
                # Add individual detection types
                for detection_type, count in individual_counts.items():
                    # Rename 'all' species to avoid conflict with summary 'all'
                    final_detection_type = 'all_species' if detection_type == 'all' else detection_type
                    results.append({
                        "year": int(year),
                        "month": int(month),
                        "station": str(station),
                        "detection_type": str(final_detection_type),
                        "count": int(count)
                    })
    
    return results

def create_output_structure(monthly_data, species_mapping):
    """Create final JSON structure for frontend"""
    
    # Create list of detection types for dropdown
    detection_types = ["all", "biological", "anthropogenic"]
    
    # Add individual species, sorted by total detections (from species.json)
    # Use 'all_species' instead of 'all' to avoid conflict with our summary category
    individual_types = []
    for short_name in species_mapping.keys():
        if species_mapping[short_name]['type'] in ['bio', 'anthro']:
            if short_name == 'all':
                individual_types.append('all_species')  # Rename to avoid conflict
            else:
                individual_types.append(short_name)
    
    detection_types.extend(individual_types)
    
    # Create detection type labels for dropdown
    type_labels = {
        "all": "All Detections",
        "biological": "All Biological", 
        "anthropogenic": "All Anthropogenic"
    }
    
    # Add individual species labels (but avoid overwriting our summary labels)
    for display_name in individual_types:
        if display_name not in type_labels:  # Don't overwrite summary labels
            # Handle the renamed 'all_species'
            if display_name == 'all_species':
                type_labels[display_name] = species_mapping['all']['long_name']
            else:
                type_labels[display_name] = species_mapping[display_name]['long_name']
    
    return {
        "monthly_summary": monthly_data,
        "detection_types": detection_types,
        "type_labels": type_labels,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Monthly detection aggregations by year, month, station, and detection type",
            "years_included": sorted(list(set(record['year'] for record in monthly_data))),
            "stations_included": sorted(list(set(record['station'] for record in monthly_data))),
            "total_records": len(monthly_data)
        }
    }

def main():
    """Main aggregation function"""
    print("Starting monthly detections aggregation...")
    
    # Load data
    detections, species = load_data()
    
    # Prepare species mapping
    species_mapping, biological_types, anthropogenic_types = prepare_species_mapping(species)
    
    print(f"Biological types: {len(biological_types)}")
    print(f"Anthropogenic types: {len(anthropogenic_types)}")
    
    # Aggregate monthly data
    monthly_data = aggregate_monthly_detections(detections, species_mapping, biological_types, anthropogenic_types)
    
    # Create output structure
    output = create_output_structure(monthly_data, species_mapping)
    
    # Save output
    output_path = project_root / "data" / "cdn" / "processed" / "monthly_detections.json"
    
    print(f"Saving {len(monthly_data)} monthly aggregation records to {output_path}")
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nAggregation Summary:")
    print(f"- Total records: {output['metadata']['total_records']}")
    print(f"- Years: {output['metadata']['years_included']}")
    print(f"- Stations: {output['metadata']['stations_included']}")
    print(f"- Detection types available: {len(output['detection_types'])}")
    
    print("\nAggregation complete!")

if __name__ == "__main__":
    main()