#!/usr/bin/env python3
"""
Prepare modeling dataset by combining PCA components with aggregated species detections.

This script creates target variables for predictive modeling:
- fish_intensity: Sum of fish species intensity scores per 2-hour window
- mammal_calls: Sum of mammal call counts per 2-hour window  
- vessel_presence: Binary vessel detection per 2-hour window
- total_biodiversity: Combined biological activity score

Outputs a modeling-ready dataset with 7 PCA components as features.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Project utilities not needed - loading JSON files directly


def load_pca_data() -> Dict[str, Any]:
    """Load the 7 PCA components data."""
    # Look for PCA file in project root data directory (not python/data)
    pca_file = Path(__file__).parent.parent.parent / "data" / "views" / "pca_analysis.json"
    
    if not pca_file.exists():
        raise FileNotFoundError(f"PCA data not found at {pca_file}")
    
    with open(pca_file, 'r') as f:
        pca_data = json.load(f)
    
    # Check if we have the necessary loadings data
    if 'loadings_heatmap' not in pca_data:
        raise KeyError("PCA data missing 'loadings_heatmap' - cannot compute features")
    
    total_components = pca_data['summary']['components_for_80_percent']
    print(f"✅ Loaded PCA data with {total_components} components for 80% variance")
    return pca_data


def load_detections_data() -> Dict[str, Any]:
    """Load compiled detections data."""
    # Look in project root data directory
    detections_file = Path(__file__).parent.parent.parent / "data" / "processed" / "compiled_detections.json"
    
    if not detections_file.exists():
        raise FileNotFoundError(f"Detections data not found at {detections_file}")
    
    with open(detections_file, 'r') as f:
        detections_data = json.load(f)
    
    total_records = detections_data['metadata']['total_records']
    print(f"✅ Loaded detections data with {total_records:,} total records")
    return detections_data


def load_indices_data() -> Dict[str, Any]:
    """Load compiled acoustic indices data (even hours, 2-hour resolution)."""
    # Look in project root data directory first, then python/data
    indices_file = Path(__file__).parent.parent.parent / "data" / "processed" / "compiled_indices_even_hours.json"
    if not indices_file.exists():
        indices_file = Path(__file__).parent.parent / "data" / "processed" / "compiled_indices_even_hours.json"
    
    if not indices_file.exists():
        raise FileNotFoundError(f"Indices data not found at {indices_file}")
    
    with open(indices_file, 'r') as f:
        indices_data = json.load(f)
    
    total_records = indices_data['metadata']['total_records']
    print(f"✅ Loaded acoustic indices data with {total_records:,} total records")
    return indices_data


def classify_species_by_type(detections_data: Dict) -> Dict[str, List[str]]:
    """Classify species columns by biological type using long names."""
    species_mapping = {}
    
    for mapping in detections_data['metadata']['column_mappings']:
        species_type = mapping['type']
        group = mapping.get('group', 'other')
        long_name = mapping['long_name']  # Use long_name instead of short_name
        
        if species_type == 'bio':
            if group == 'fish':
                species_mapping.setdefault('fish', []).append(long_name)
            elif group == 'mammal':
                species_mapping.setdefault('mammals', []).append(long_name)
        elif species_type == 'anth':
            species_mapping.setdefault('vessels', []).append(long_name)
    
    print(f"✅ Species classification:")
    for category, species_list in species_mapping.items():
        print(f"   {category}: {species_list}")
    
    return species_mapping


def create_target_variables(detections_df: pd.DataFrame, species_mapping: Dict[str, List[str]]) -> pd.DataFrame:
    """Create aggregated target variables from species detection data."""
    
    # Initialize target columns (using actual column names from data)
    # Note: 'Time' field has bogus 1900 dates, only 'Date' field is useful
    targets_df = detections_df[['station', 'year', 'Date']].copy()
    
    # Fish intensity: Sum all fish species intensity scores
    fish_columns = species_mapping.get('fish', [])
    if fish_columns:
        # Use intensity scores (assume non-zero values are intensity scores)
        targets_df['fish_intensity'] = detections_df[fish_columns].sum(axis=1)
        print(f"✅ Created fish_intensity from {len(fish_columns)} fish species")
    else:
        targets_df['fish_intensity'] = 0
        print("⚠️  No fish species found - setting fish_intensity to 0")
    
    # Mammal calls: Sum all mammal species call counts  
    mammal_columns = species_mapping.get('mammals', [])
    if mammal_columns:
        # Use call counts (assume non-zero values are call counts)
        targets_df['mammal_calls'] = detections_df[mammal_columns].sum(axis=1)
        print(f"✅ Created mammal_calls from {len(mammal_columns)} mammal species")
    else:
        targets_df['mammal_calls'] = 0
        print("⚠️  No mammal species found - setting mammal_calls to 0")
    
    # Vessel presence: Binary presence/absence for any vessel detection
    vessel_columns = species_mapping.get('vessels', [])
    if vessel_columns:
        # Binary: any vessel detection = 1, otherwise 0
        targets_df['vessel_presence'] = (detections_df[vessel_columns].sum(axis=1) > 0).astype(int)
        print(f"✅ Created vessel_presence from {len(vessel_columns)} vessel categories")
    else:
        targets_df['vessel_presence'] = 0
        print("⚠️  No vessel detections found - setting vessel_presence to 0")
    
    # Total biodiversity: Combined biological activity score
    targets_df['total_biodiversity'] = (
        (targets_df['fish_intensity'] > 0).astype(int) +
        (targets_df['mammal_calls'] > 0).astype(int) +
        (targets_df['vessel_presence'] > 0).astype(int)
    )
    print("✅ Created total_biodiversity as sum of active categories")
    
    return targets_df


def compute_pca_features(indices_df: pd.DataFrame, pca_data: Dict) -> pd.DataFrame:
    """Apply PCA transformation to get 7 component features."""
    
    # Extract loadings data from the heatmap structure
    loadings_data = pca_data['loadings_heatmap']['data']
    
    # Get unique index names and component names
    indices_list = pca_data['loadings_heatmap']['indices']
    components_list = pca_data['loadings_heatmap']['components']
    
    # Use first 7 components for 80% variance
    num_components = min(7, len(components_list))
    target_components = components_list[:num_components]
    
    print(f"✅ Using {num_components} components: {target_components}")
    print(f"✅ Available indices: {len(indices_list)} total")
    
    # Build loading matrix: rows=indices, columns=components
    loading_matrix = np.zeros((len(indices_list), num_components))
    
    for item in loadings_data:
        index_name = item['index']
        component = item['component']
        loading_value = item['loading']
        
        if index_name in indices_list and component in target_components:
            index_idx = indices_list.index(index_name)
            comp_idx = target_components.index(component)
            loading_matrix[index_idx, comp_idx] = loading_value
    
    print(f"✅ Built loadings matrix: {loading_matrix.shape}")
    
    # Select matching columns from indices data
    available_indices = list(indices_df.select_dtypes(include=[np.number]).columns)
    matching_indices = [idx for idx in indices_list if idx in available_indices]
    
    if len(matching_indices) < len(indices_list):
        print(f"⚠️  Only {len(matching_indices)}/{len(indices_list)} indices found in data")
        missing = set(indices_list) - set(matching_indices)
        print(f"   First few missing: {list(missing)[:5]}...")
    
    # Get the indices data matrix for matching indices only
    matching_idx_positions = [indices_list.index(idx) for idx in matching_indices if idx in indices_list]
    indices_matrix = indices_df[matching_indices].values
    reduced_loading_matrix = loading_matrix[matching_idx_positions, :]
    
    print(f"✅ Indices matrix: {indices_matrix.shape}")
    print(f"✅ Reduced loadings: {reduced_loading_matrix.shape}")
    
    # Apply PCA transformation (dot product with loadings)
    pca_features = indices_matrix @ reduced_loading_matrix
    
    # Create PCA features dataframe
    pca_df = indices_df[['station', 'year', 'Date']].copy()
    for i in range(num_components):
        pca_df[f'PC{i+1}'] = pca_features[:, i]
    
    print(f"✅ Created {num_components} PCA features from {len(matching_indices)} indices")
    return pca_df


def align_data_by_time(pca_df: pd.DataFrame, targets_df: pd.DataFrame) -> pd.DataFrame:
    """Align PCA features with target variables by time stamps."""
    
    # Parse and standardize timestamps
    # PCA data: "1/2/2021 0:00" format
    # Detection data: "2021-01-01 00:00:00" format (Date field has full datetime)
    
    def parse_indices_date(date_str):
        """Convert '1/2/2021 0:00' to '2021-01-02 00:00:00' format"""
        from datetime import datetime
        try:
            dt = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return None
    
    def parse_detections_date(date_str):
        """Detection Date field - round to nearest 2-hour mark"""
        from datetime import datetime, timedelta
        # Try to parse and standardize
        try:
            # Remove microseconds if present
            if '.' in date_str:
                date_str = date_str.split('.')[0]
            # Parse
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            # Round to nearest even hour (0, 2, 4, 6, etc)
            # Set minutes and seconds to 0
            dt = dt.replace(minute=0, second=0)
            # Round hour to nearest even hour
            if dt.hour % 2 == 1:
                dt = dt.replace(hour=dt.hour - 1)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return None
    
    # Create standardized time keys for matching
    pca_df['parsed_datetime'] = pca_df['Date'].apply(parse_indices_date)
    targets_df['parsed_datetime'] = targets_df['Date'].apply(parse_detections_date)
    
    # Remove any rows where parsing failed
    pca_df = pca_df[pca_df['parsed_datetime'].notna()]
    targets_df = targets_df[targets_df['parsed_datetime'].notna()]
    
    pca_df['time_key'] = pca_df['station'] + '_' + pca_df['year'].astype(str) + '_' + pca_df['parsed_datetime']
    targets_df['time_key'] = targets_df['station'] + '_' + targets_df['year'].astype(str) + '_' + targets_df['parsed_datetime']
    
    print(f"PCA data: {len(pca_df)} records with unique time keys: {pca_df['time_key'].nunique()}")
    print(f"Targets data: {len(targets_df)} records with unique time keys: {targets_df['time_key'].nunique()}")
    
    # Debug: Check date ranges before merge
    print(f"PCA date range: {pca_df['parsed_datetime'].min()} to {pca_df['parsed_datetime'].max()}")
    print(f"Targets date range: {targets_df['parsed_datetime'].min()} to {targets_df['parsed_datetime'].max()}")
    
    # Debug: Check coverage by station
    for station in ['9M', '14M', '37M']:
        pca_station = pca_df[pca_df['station'] == station]
        tgt_station = targets_df[targets_df['station'] == station]
        if len(pca_station) > 0:
            print(f"{station} - PCA: {pca_station['parsed_datetime'].min()} to {pca_station['parsed_datetime'].max()} ({len(pca_station)} records)")
        else:
            print(f"{station} - PCA: No records")
        if len(tgt_station) > 0:
            print(f"{station} - Targets: {tgt_station['parsed_datetime'].min()} to {tgt_station['parsed_datetime'].max()} ({len(tgt_station)} records)")
        else:
            print(f"{station} - Targets: No records")
    
    # Merge on time key
    modeling_df = pca_df.merge(
        targets_df, 
        on=['time_key', 'station', 'year'], 
        how='inner'
    )
    
    # Remove the helper time_key column but keep parsed_datetime for date range tracking
    modeling_df = modeling_df.drop('time_key', axis=1)
    # Rename one of the parsed_datetime columns (they should be identical after merge)
    if 'parsed_datetime_x' in modeling_df.columns:
        modeling_df = modeling_df.rename(columns={'parsed_datetime_x': 'parsed_datetime'})
    
    print(f"✅ Successfully aligned {len(modeling_df)} records")
    print(f"   Stations: {modeling_df['station'].unique()}")
    print(f"   Years: {modeling_df['year'].unique()}")
    
    return modeling_df


def generate_data_summary(modeling_df: pd.DataFrame) -> Dict[str, Any]:
    """Generate summary statistics for the modeling dataset."""
    
    summary = {
        'dataset_info': {
            'total_records': len(modeling_df),
            'stations': list(modeling_df['station'].unique()),
            'years': list(modeling_df['year'].unique()),
            'date_range': {
                'start': modeling_df['parsed_datetime'].min() if 'parsed_datetime' in modeling_df.columns else 'N/A',
                'end': modeling_df['parsed_datetime'].max() if 'parsed_datetime' in modeling_df.columns else 'N/A'
            }
        },
        'target_variables': {},
        'features': {},
        'class_balance': {}
    }
    
    # Target variable summaries
    target_columns = ['fish_intensity', 'mammal_calls', 'vessel_presence', 'total_biodiversity']
    for col in target_columns:
        if col in modeling_df.columns:
            summary['target_variables'][col] = {
                'mean': float(modeling_df[col].mean()),
                'std': float(modeling_df[col].std()),
                'min': float(modeling_df[col].min()),
                'max': float(modeling_df[col].max()),
                'non_zero_count': int((modeling_df[col] > 0).sum()),
                'non_zero_percentage': float((modeling_df[col] > 0).mean() * 100)
            }
    
    # PCA feature summaries
    pca_columns = [f'PC{i+1}' for i in range(7)]
    for col in pca_columns:
        if col in modeling_df.columns:
            summary['features'][col] = {
                'mean': float(modeling_df[col].mean()),
                'std': float(modeling_df[col].std()),
                'min': float(modeling_df[col].min()),
                'max': float(modeling_df[col].max())
            }
    
    # Class balance for binary/categorical targets
    for col in ['vessel_presence', 'total_biodiversity']:
        if col in modeling_df.columns:
            value_counts = modeling_df[col].value_counts()
            summary['class_balance'][col] = {
                int(k): int(v) for k, v in value_counts.items()
            }
    
    return summary


def main():
    """Main execution function."""
    print("🚀 Starting modeling data preparation...")
    print("=" * 60)
    
    # Load all required data
    print("\n1. Loading data files...")
    pca_data = load_pca_data()
    detections_data = load_detections_data()
    indices_data = load_indices_data()
    
    # Classify species by type
    print("\n2. Classifying species by biological type...")
    species_mapping = classify_species_by_type(detections_data)
    
    # Convert detections data to DataFrame
    print("\n3. Processing detections data...")
    detections_records = []
    for station_id, station_data in detections_data['stations'].items():
        for year, year_data in station_data.items():
            for record in year_data['data']:
                record['station'] = station_id
                record['year'] = int(year)
                detections_records.append(record)
    
    detections_df = pd.DataFrame(detections_records)
    print(f"✅ Created detections DataFrame with {len(detections_df)} records")
    
    # Convert indices data to DataFrame (focus on 2021 data only) 
    print("\n4. Processing acoustic indices data...")
    indices_records = []
    for station_id, station_data in indices_data['stations'].items():
        if '2021' in station_data:
            # Use FullBW bandwidth for consistency
            if 'FullBW' in station_data['2021']:
                for record in station_data['2021']['FullBW']['data']:
                    record['station'] = station_id
                    record['year'] = 2021
                    indices_records.append(record)
                print(f"   Station {station_id}: {len(station_data['2021']['FullBW']['data'])} records")
    
    indices_df = pd.DataFrame(indices_records)
    print(f"✅ Created indices DataFrame with {len(indices_df)} records (2021 FullBW only)")
    
    # Filter detections to 2021 only to match indices
    print("\n5. Filtering detections to 2021...")
    detections_df_2021 = detections_df[detections_df['year'] == 2021].copy()
    print(f"✅ Filtered to {len(detections_df_2021)} detection records for 2021")
    
    # Create target variables
    print("\n6. Creating target variables...")
    targets_df = create_target_variables(detections_df_2021, species_mapping)
    
    # Compute PCA features
    print("\n7. Computing PCA features...")
    pca_features_df = compute_pca_features(indices_df, pca_data)
    
    # Align data by timestamps
    print("\n8. Aligning data by timestamps...")
    modeling_df = align_data_by_time(pca_features_df, targets_df)
    
    # Generate summary statistics
    print("\n9. Generating summary statistics...")
    summary = generate_data_summary(modeling_df)
    
    # Save the modeling dataset
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir.mkdir(exist_ok=True)
    
    modeling_file = output_dir / "modeling_dataset.json"
    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'description': 'Modeling-ready dataset with 7 PCA components and aggregated species detection targets',
            'script': 'scripts/10_prepare_modeling_data.py',
            'data_sources': [
                'data/views/pca_analysis.json',
                'data/processed/compiled_detections.json', 
                'data/processed/compiled_indices_even_hours.json'
            ]
        },
        'summary': summary,
        'data': modeling_df.to_dict('records')
    }
    
    # Convert numpy types to native Python types for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    # Convert the data before saving
    output_data_clean = json.loads(json.dumps(output_data, default=convert_numpy_types))
    
    with open(modeling_file, 'w') as f:
        json.dump(output_data_clean, f, indent=2)
    
    print(f"\n✅ Saved modeling dataset to: {modeling_file}")
    print(f"   File size: {modeling_file.stat().st_size / (1024*1024):.1f} MB")
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 MODELING DATASET SUMMARY")
    print("=" * 60)
    print(f"Total records: {summary['dataset_info']['total_records']:,}")
    print(f"Stations: {', '.join(summary['dataset_info']['stations'])}")
    print(f"Years: {', '.join(map(str, summary['dataset_info']['years']))}")
    print(f"Date range: {summary['dataset_info']['date_range']['start']} to {summary['dataset_info']['date_range']['end']}")
    
    print(f"\nFeatures: 7 PCA components (PC1-PC7)")
    print(f"Target variables:")
    for var, stats in summary['target_variables'].items():
        non_zero_pct = stats['non_zero_percentage']
        print(f"  • {var}: {stats['non_zero_count']:,} non-zero ({non_zero_pct:.1f}%)")
    
    print(f"\n🎯 Ready for modeling! Next steps:")
    print(f"   1. Run train/test split (70/30)")
    print(f"   2. Train logistic regression models")
    print(f"   3. Train random forest models")
    print(f"   4. Evaluate performance metrics")


if __name__ == "__main__":
    main()