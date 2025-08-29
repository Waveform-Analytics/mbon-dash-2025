#!/usr/bin/env python3
"""
Clean Excel → JSON processor for MBON dashboard.

Converts raw Excel files to core JSON files for the dashboard.
This is Step 1 of the 3-step data pipeline.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Import from existing working processor
from mbon_analysis.processing.excel_to_json import MBONExcelProcessor

# Configuration
OUTPUT_DIR = Path("data/cdn/processed")
INPUT_DIR = Path("data/cdn/raw-data")

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_metadata(detections_df, environmental_df, acoustic_df, species_list, stations_list):
    """Generate dashboard metadata."""
    return {
        "generated_at": datetime.now().isoformat(),
        "data_summary": {
            "total_detections": len(detections_df),
            "total_environmental_records": len(environmental_df),
            "total_acoustic_records": len(acoustic_df),
            "stations_count": len(stations_list),
            "species_count": len(species_list),
            "years_included": sorted([int(y) for y in detections_df['year'].unique()]) if len(detections_df) > 0 and 'year' in detections_df.columns else [],
            "date_range": {
                "start": detections_df['date'].min().isoformat() if len(detections_df) > 0 else None,
                "end": detections_df['date'].max().isoformat() if len(detections_df) > 0 else None
            }
        },
        "column_mapping": {}  # Will be populated by processor
    }


def main():
    """Convert Excel files to core JSON files."""
    try:
        logger.info("🚀 Starting Excel → JSON conversion...")
        
        # Initialize processor with existing working logic
        processor = MBONExcelProcessor(INPUT_DIR)
        
        # Process all data using existing methods
        logger.info("📊 Processing detection data...")
        detections_df = processor.process_all_detection_files()
        
        logger.info("🌡️ Processing environmental data...")
        environmental_df = processor.process_environmental_files()
        
        logger.info("🎵 Processing acoustic indices...")
        acoustic_df = processor.process_acoustic_files()
        
        # Generate metadata from processed data
        logger.info("📋 Extracting metadata...")
        name_mapping, type_mapping = processor.load_column_mapping()
        
        # Generate species and stations lists from the data
        try:
            species_list = []
            if not detections_df.empty and name_mapping:
                # Get species columns (skip datetime/metadata columns)
                metadata_cols = {'date', 'time', 'datetime', 'station', 'year', 'source_file'}
                species_cols = [col for col in detections_df.columns if col not in metadata_cols]
                
                for col in species_cols:
                    if col in name_mapping:
                        detection_count = int(detections_df[col].sum()) if col in detections_df.columns else 0
                        species_list.append({
                            "short_name": col,
                            "long_name": str(name_mapping[col]),  # Ensure string
                            "total_detections": detection_count,
                            "category": str(type_mapping.get(col, {}).get("type", "unknown")) if type_mapping else "unknown"
                        })
            
            # Generate stations list
            stations_list = []
            if not detections_df.empty:
                unique_stations = detections_df['station'].unique() if 'station' in detections_df.columns else []
                for station in unique_stations:
                    station_years = []
                    if 'year' in detections_df.columns:
                        station_data = detections_df[detections_df['station'] == station]
                        station_years = sorted([int(y) for y in station_data['year'].unique()])
                    
                    stations_list.append({
                        "id": str(station),
                        "name": f"Station {station}",
                        "coordinates": {"lat": 0, "lon": 0},  # Placeholder - would need deployment metadata
                        "years": station_years,
                        "data_types": ["detections", "environmental"]
                    })
        except Exception as e:
            logger.error(f"Error generating metadata lists: {e}")
            species_list = []
            stations_list = []
        
        # Create output directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save core JSON files (6 essential files only)
        files_saved = []
        
        # 1. Detections
        detections_file = OUTPUT_DIR / "detections.json"
        detections_df.to_json(detections_file, orient='records', date_format='iso')
        files_saved.append(f"detections.json ({len(detections_df)} records)")
        
        # 2. Environmental
        if not environmental_df.empty:
            env_file = OUTPUT_DIR / "environmental.json"
            environmental_df.to_json(env_file, orient='records', date_format='iso')
            files_saved.append(f"environmental.json ({len(environmental_df)} records)")
        
        # 3. Acoustic indices (if available)
        if not acoustic_df.empty:
            acoustic_file = OUTPUT_DIR / "acoustic_indices.json"
            acoustic_df.to_json(acoustic_file, orient='records', date_format='iso')
            files_saved.append(f"acoustic_indices.json ({len(acoustic_df)} records)")
        
        # 4. Species list
        species_file = OUTPUT_DIR / "species.json"
        with open(species_file, 'w') as f:
            json.dump(species_list, f, indent=2)
        files_saved.append(f"species.json ({len(species_list)} species)")
        
        # 5. Stations
        stations_file = OUTPUT_DIR / "stations.json"
        with open(stations_file, 'w') as f:
            json.dump(stations_list, f, indent=2)
        files_saved.append(f"stations.json ({len(stations_list)} stations)")
        
        # 6. Metadata
        metadata = generate_metadata(detections_df, environmental_df, acoustic_df, species_list, stations_list)
        metadata["column_mapping"] = name_mapping
        
        metadata_file = OUTPUT_DIR / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        files_saved.append("metadata.json")
        
        # Success report
        logger.info("✅ Excel → JSON conversion complete!")
        logger.info(f"📁 Output: {OUTPUT_DIR}")
        for file_info in files_saved:
            logger.info(f"  ✓ {file_info}")
            
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error in Excel → JSON conversion: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())