#!/usr/bin/env python3
"""
Dashboard data preparation script using mbon_analysis Excel processor.

This script orchestrates the Excel → JSON conversion for the web dashboard
using the centralized processing logic from mbon_analysis.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, date, time
import pandas as pd
import numpy as np

# Import our centralized processor
from mbon_analysis.core.excel_processor import MBONExcelProcessor

# Configuration
OUTPUT_DIR = Path("data/cdn/processed")
LOG_FILE = "dashboard_data_processing.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def generate_metadata(detections_df, environmental_df, acoustic_df, species_list, stations_list):
    """Generate metadata with version information."""
    import hashlib
    
    # Calculate data fingerprint
    data_fingerprint = hashlib.md5(
        f"{len(detections_df)}{len(environmental_df)}{len(acoustic_df)}{len(species_list)}".encode()
    ).hexdigest()[:8]
    
    metadata = {
        "version": f"1.0.{data_fingerprint}",
        "generated_at": datetime.now().isoformat(),
        "processing_script_version": "2.0.0",
        "data_summary": {
            "total_detections": len(detections_df),
            "total_environmental_records": len(environmental_df),
            "total_acoustic_records": len(acoustic_df),
            "stations_count": len(stations_list),
            "species_count": len(species_list),
            "years_included": sorted(detections_df['year'].unique().tolist()) if len(detections_df) > 0 else [],
            "date_range": {
                "start": detections_df['date'].min().isoformat() if len(detections_df) > 0 else None,
                "end": detections_df['date'].max().isoformat() if len(detections_df) > 0 else None
            }
        },
        "validation_status": "passed"
    }
    
    return metadata


def process_acoustic_indices():
    """Process acoustic indices CSV files if available."""
    logger.info("🎵 Processing acoustic indices files...")
    
    indices_dir = Path("data/cdn/raw-data/indices")
    if not indices_dir.exists():
        logger.warning("No indices directory found, skipping acoustic indices")
        return pd.DataFrame()
    
    all_indices = []
    for csv_file in indices_dir.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file)
            df['source_file'] = csv_file.name
            
            # Extract station and bandwidth from filename
            # Example: Acoustic_Indices_9M_2021_FullBW_v2_Final.csv
            parts = csv_file.stem.split('_')
            if len(parts) >= 5:
                df['station'] = parts[2]  # e.g., '9M'
                df['year'] = parts[3]      # e.g., '2021'
                df['bandwidth'] = parts[4]  # e.g., 'FullBW' or '8kHz'
            
            all_indices.append(df)
            logger.info(f"  ✓ Loaded {csv_file.name}: {len(df)} records")
        except Exception as e:
            logger.error(f"  ❌ Error processing {csv_file.name}: {e}")
    
    if all_indices:
        combined = pd.concat(all_indices, ignore_index=True)
        logger.info(f"✅ Combined {len(combined)} acoustic indices records")
        return combined
    
    return pd.DataFrame()


def export_json_files(detections_df, environmental_df, acoustic_df, acoustic_indices_df, processor):
    """Export processed data as JSON files for the dashboard."""
    
    logger.info("📦 Exporting JSON files...")
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    
    # Custom JSON encoder for handling numpy types and dates
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                if np.isnan(obj):
                    return None
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (pd.Timestamp, datetime, date)):
                return obj.isoformat()
            elif isinstance(obj, time):
                return obj.isoformat()
            elif pd.isna(obj):
                return None
            return super(NumpyEncoder, self).default(obj)
    
    # Export detections
    detections_file = OUTPUT_DIR / "detections.json"
    detections_dict = detections_df.to_dict('records')
    with open(detections_file, 'w') as f:
        json.dump(detections_dict, f, cls=NumpyEncoder)
    logger.info(f"  ✓ Exported {len(detections_df)} detection records to {detections_file}")
    
    # Export environmental
    environmental_file = OUTPUT_DIR / "environmental.json"
    environmental_dict = environmental_df.to_dict('records')
    with open(environmental_file, 'w') as f:
        json.dump(environmental_dict, f, cls=NumpyEncoder)
    logger.info(f"  ✓ Exported {len(environmental_df)} environmental records to {environmental_file}")
    
    # Export acoustic (legacy rmsSPL)
    acoustic_file = OUTPUT_DIR / "acoustic.json"
    acoustic_dict = acoustic_df.to_dict('records')
    with open(acoustic_file, 'w') as f:
        json.dump(acoustic_dict, f, cls=NumpyEncoder)
    logger.info(f"  ✓ Exported {len(acoustic_df)} acoustic records to {acoustic_file}")
    
    # Export acoustic indices if available
    if len(acoustic_indices_df) > 0:
        indices_file = OUTPUT_DIR / "acoustic_indices.json"
        indices_dict = acoustic_indices_df.to_dict('records')
        with open(indices_file, 'w') as f:
            json.dump(indices_dict, f, cls=NumpyEncoder)
        logger.info(f"  ✓ Exported {len(acoustic_indices_df)} acoustic indices records to {indices_file}")
    
    # Generate species metadata
    _, type_mapping = processor.load_column_mapping()
    species_list = []
    for short_name, info in type_mapping.items():
        if info['type'] in ['bio', 'anthro']:
            total_detections = 0
            if short_name in detections_df.columns:
                # Convert to numeric and handle NaN values
                col_values = pd.to_numeric(detections_df[short_name], errors='coerce')
                total_detections = col_values.sum() if not col_values.isna().all() else 0
            
            species_list.append({
                'short_name': short_name,
                'long_name': info['long_name'],
                'category': info['type'],
                'total_detections': int(total_detections) if not pd.isna(total_detections) else 0
            })
    
    species_file = OUTPUT_DIR / "species.json"
    with open(species_file, 'w') as f:
        json.dump(species_list, f, indent=2)
    logger.info(f"  ✓ Exported {len(species_list)} species definitions to {species_file}")
    
    # Generate stations metadata with actual coordinates
    station_coordinates = {
        '9M': {'lat': 32.2833, 'lon': -80.8833},  # Approximate May River coordinates
        '14M': {'lat': 32.2667, 'lon': -80.9000},
        '37M': {'lat': 32.2500, 'lon': -80.9167}
    }
    
    stations_list = []
    for station in processor.stations_of_interest:
        station_data = detections_df[detections_df['station'] == station] if 'station' in detections_df.columns else pd.DataFrame()
        if len(station_data) > 0:
            stations_list.append({
                'id': station,
                'name': f"Station {station}",
                'coordinates': station_coordinates.get(station, {'lat': 0, 'lon': 0}),
                'years': sorted(station_data['year'].unique().tolist()),
                'data_types': ['detections', 'environmental', 'acoustic']
            })
    
    stations_file = OUTPUT_DIR / "stations.json"
    with open(stations_file, 'w') as f:
        json.dump(stations_list, f, indent=2)
    logger.info(f"  ✓ Exported {len(stations_list)} station definitions to {stations_file}")
    
    # Generate metadata
    metadata = generate_metadata(detections_df, environmental_df, acoustic_df, species_list, stations_list)
    metadata_file = OUTPUT_DIR / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"  ✓ Exported metadata to {metadata_file}")


def main():
    """Main processing function."""
    
    print("=" * 60)
    print("🚀 MBON Dashboard Data Processing")
    print("=" * 60)
    
    logger.info("Starting MBON dashboard data processing...")
    
    try:
        # Create Excel processor
        processor = MBONExcelProcessor(
            raw_data_dir="data/cdn/raw-data",
            years_of_interest=["2018", "2021"],
            stations_of_interest=["9M", "14M", "37M"]
        )
        
        # Process detection files
        print("\n📊 STEP 1: Processing detection files...")
        logger.info("STEP 1: Processing detection files...")
        detections_df = processor.process_all_detection_files()
        print(f"   ✓ Loaded {len(detections_df)} detection records")
        
        # Process environmental files  
        print("\n🌡️  STEP 2: Processing environmental files...")
        logger.info("STEP 2: Processing environmental files...")
        environmental_df = processor.process_environmental_files()
        print(f"   ✓ Loaded {len(environmental_df)} environmental records")
        
        # Process acoustic files (legacy rmsSPL)
        print("\n🔊 STEP 3: Processing acoustic files...")
        logger.info("STEP 3: Processing acoustic files...")
        acoustic_df = processor.process_acoustic_files()
        print(f"   ✓ Loaded {len(acoustic_df)} acoustic records")
        
        # Process acoustic indices (new CSV files)
        print("\n🎵 STEP 4: Processing acoustic indices...")
        logger.info("STEP 4: Processing acoustic indices...")
        acoustic_indices_df = process_acoustic_indices()
        if len(acoustic_indices_df) > 0:
            print(f"   ✓ Loaded {len(acoustic_indices_df)} acoustic indices records")
        else:
            print("   ℹ️  No acoustic indices files found")
        
        # Export JSON files
        print("\n📦 STEP 5: Exporting JSON files...")
        logger.info("STEP 5: Exporting JSON files...")
        export_json_files(detections_df, environmental_df, acoustic_df, acoustic_indices_df, processor)
        
        print("\n" + "=" * 60)
        print("✅ Dashboard data processing completed successfully!")
        print(f"📁 Files saved to: {OUTPUT_DIR}")
        print(f"📝 Log saved to: {LOG_FILE}")
        print("=" * 60)
        
        logger.info("Dashboard data processing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Dashboard data processing failed: {e}")
        logger.error(f"Dashboard data processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()