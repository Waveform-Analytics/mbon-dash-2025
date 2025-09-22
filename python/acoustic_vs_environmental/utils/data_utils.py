"""
Data loading utilities for acoustic vs environmental analysis.

Uses cleaned data from notebook 1 outputs to avoid datetime/alignment issues.
Focuses on simple, robust data loading patterns.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class CleanDataLoader:
    """
    Load and prepare data from notebook 1 processed outputs.
    
    Avoids the temporal alignment complexities of notebook 2 by working
    with clean but not yet temporally aligned data.
    """
    
    def __init__(self, data_dir: str = "../../data/processed"):
        self.data_dir = Path(data_dir)
        self.stations = ["9M", "14M", "37M"]
        self.year = "2021"
        
    def load_acoustic_indices(self) -> pd.DataFrame:
        """Load cleaned acoustic indices from all stations."""
        print("Loading acoustic indices...")
        
        all_indices = []
        for station in self.stations:
            file_path = self.data_dir / f"01_indices_{station}_{self.year}.parquet"
            
            if not file_path.exists():
                print(f"⚠️  Missing: {file_path}")
                continue
                
            df = pd.read_parquet(file_path)
            
            # Add station identifier
            df['station'] = station
            
            # Clean up datetime column (use the properly parsed one)
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            else:
                print(f"⚠️  No datetime column in {station}")
                continue
                
            # Remove non-numeric columns that cause issues
            columns_to_drop = ['Date', 'Filename']  # String columns
            columns_to_drop += [col for col in df.columns if '_by_band' in col]  # Array columns
            df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
            
            all_indices.append(df)
            print(f"✓ Loaded {station}: {df.shape}")
        
        if not all_indices:
            raise ValueError("No acoustic indices data found")
            
        combined = pd.concat(all_indices, ignore_index=True)
        print(f"✓ Combined acoustic indices: {combined.shape}")
        
        return combined
    
    def load_detections(self) -> pd.DataFrame:
        """Load detection/biological activity data from all stations."""
        print("Loading detection data...")
        
        all_detections = []
        for station in self.stations:
            file_path = self.data_dir / f"01_detections_{station}_{self.year}.parquet"
            
            if not file_path.exists():
                print(f"⚠️  Missing: {file_path}")
                continue
                
            df = pd.read_parquet(file_path)
            df['station'] = station
            
            # Clean up datetime
            if 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
            elif 'Date' in df.columns and 'Time' in df.columns:
                # Sometimes datetime needs to be reconstructed
                df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
            else:
                print(f"⚠️  Cannot parse datetime for {station}")
                continue
            
            all_detections.append(df)
            print(f"✓ Loaded {station}: {df.shape}")
        
        if not all_detections:
            raise ValueError("No detection data found")
            
        combined = pd.concat(all_detections, ignore_index=True)
        print(f"✓ Combined detections: {combined.shape}")
        
        return combined
    
    def load_environmental(self) -> pd.DataFrame:
        """Load environmental data (temperature, depth, SPL) from all stations."""
        print("Loading environmental data...")
        
        # Load temperature data
        temp_data = []
        for station in self.stations:
            file_path = self.data_dir / f"01_temperature_{station}_{self.year}.parquet"
            if file_path.exists():
                df = pd.read_parquet(file_path)
                df['station'] = station
                df['datetime'] = pd.to_datetime(df['datetime'])
                temp_data.append(df)
                print(f"✓ Temperature {station}: {df.shape}")
        
        # Load depth data  
        depth_data = []
        for station in self.stations:
            file_path = self.data_dir / f"01_depth_{station}_{self.year}.parquet"
            if file_path.exists():
                df = pd.read_parquet(file_path)
                df['station'] = station
                df['datetime'] = pd.to_datetime(df['datetime'])
                depth_data.append(df)
                print(f"✓ Depth {station}: {df.shape}")
        
        # Load SPL data
        spl_data = []
        for station in self.stations:
            file_path = self.data_dir / f"01_spl_{station}_{self.year}.parquet"
            if file_path.exists():
                df = pd.read_parquet(file_path)
                df['station'] = station  
                df['datetime'] = pd.to_datetime(df['datetime'])
                spl_data.append(df)
                print(f"✓ SPL {station}: {df.shape}")
        
        # Combine all environmental data
        env_dfs = []
        if temp_data:
            env_dfs.append(pd.concat(temp_data, ignore_index=True))
        if depth_data:
            env_dfs.append(pd.concat(depth_data, ignore_index=True))
        if spl_data:
            env_dfs.append(pd.concat(spl_data, ignore_index=True))
            
        if not env_dfs:
            raise ValueError("No environmental data found")
        
        # Merge environmental data by station and datetime
        combined_env = env_dfs[0]
        for df in env_dfs[1:]:
            combined_env = combined_env.merge(
                df, 
                on=['datetime', 'station'], 
                how='outer'
            )
        
        print(f"✓ Combined environmental: {combined_env.shape}")
        return combined_env
    
    def get_acoustic_index_names(self, indices_df: pd.DataFrame) -> List[str]:
        """Extract acoustic index column names (exclude metadata)."""
        exclude_cols = ['datetime', 'station', 'year', 'Date', 'Filename']
        acoustic_cols = [col for col in indices_df.columns 
                        if col not in exclude_cols and not col.endswith('_by_band')]
        
        # Only keep numeric columns
        numeric_cols = []
        for col in acoustic_cols:
            if indices_df[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                numeric_cols.append(col)
                
        print(f"Found {len(numeric_cols)} acoustic index columns")
        return numeric_cols
    
    def get_species_names(self, detections_df: pd.DataFrame) -> List[str]:
        """Extract species/detection column names."""
        exclude_cols = ['datetime', 'station', 'Date', 'Time', 'Deployment ID', 'File']
        species_cols = [col for col in detections_df.columns 
                       if col not in exclude_cols]
        
        print(f"Found {len(species_cols)} species/detection columns")
        return species_cols


def test_data_loading():
    """Test the data loading functionality."""
    print("🧪 TESTING DATA LOADING")
    print("="*50)
    
    try:
        loader = CleanDataLoader()
        
        # Test acoustic indices loading
        indices_df = loader.load_acoustic_indices()
        acoustic_cols = loader.get_acoustic_index_names(indices_df)
        print(f"✅ Acoustic indices loaded: {indices_df.shape}")
        print(f"   Acoustic columns: {len(acoustic_cols)}")
        print(f"   Sample columns: {acoustic_cols[:5]}")
        print(f"   Date range: {indices_df['datetime'].min()} to {indices_df['datetime'].max()}")
        
        # Test detections loading
        detections_df = loader.load_detections()
        species_cols = loader.get_species_names(detections_df)
        print(f"✅ Detections loaded: {detections_df.shape}")
        print(f"   Species columns: {len(species_cols)}")
        print(f"   Sample columns: {species_cols[:5]}")
        
        # Test environmental loading
        env_df = loader.load_environmental()
        print(f"✅ Environmental loaded: {env_df.shape}")
        print(f"   Columns: {list(env_df.columns)}")
        
        print(f"\n🎉 All data loading tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Run tests when script is executed directly
    test_data_loading()