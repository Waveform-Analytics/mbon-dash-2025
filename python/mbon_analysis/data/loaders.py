"""Data loading utilities for Excel and CSV files."""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


class DataLoader:
    """Base class for loading MBON data files."""
    
    def __init__(self, data_root: Union[str, Path]):
        """Initialize with path to data root directory.
        
        Args:
            data_root: Path to the data directory
        """
        self.data_root = Path(data_root)
        self.raw_data_path = self.data_root / "raw"
    
    def load_deployment_metadata(self) -> pd.DataFrame:
        """Load deployment metadata from Excel file.
        
        Returns:
            DataFrame with deployment information
        """
        metadata_file = (
            self.raw_data_path / "metadata" / 
            "1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
        )
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
            
        df = pd.read_excel(metadata_file)
        return df
    
    def load_species_mapping(self) -> pd.DataFrame:
        """Load species detection column name mappings.
        
        Returns:
            DataFrame with species code mappings
        """
        mapping_file = self.raw_data_path / "metadata" / "det_column_names.csv"
        
        if not mapping_file.exists():
            raise FileNotFoundError(f"Species mapping file not found: {mapping_file}")
            
        df = pd.read_csv(mapping_file)
        return df
    
    def load_indices_reference(self) -> pd.DataFrame:
        """Load acoustic indices reference information.
        
        Returns:
            DataFrame with indices descriptions and categories
        """
        indices_file = self.raw_data_path / "metadata" / "Updated_Index_Categories_v2.csv"
        
        if not indices_file.exists():
            raise FileNotFoundError(f"Indices reference file not found: {indices_file}")
            
        df = pd.read_csv(indices_file)
        return df
    
    def load_detection_data(self, station: str, year: int) -> pd.DataFrame:
        """Load species detection data for a specific station and year.
        
        Args:
            station: Station identifier (e.g., '9M', '14M', '37M')
            year: Year (2018 or 2021)
            
        Returns:
            DataFrame with detection data
        """
        detection_file = (
            self.raw_data_path / str(year) / "detections" / 
            f"Master_Manual_{station}_2h_{year}.xlsx"
        )
        
        if not detection_file.exists():
            raise FileNotFoundError(f"Detection file not found: {detection_file}")
            
        df = pd.read_excel(detection_file, sheet_name="Data")
        # Add station name and year columns
        df['station'] = station
        df['year'] = year
        return df
    
    def load_environmental_data(self, station: str, year: int, data_type: str) -> pd.DataFrame:
        """Load environmental data (temperature or depth) for a station and year.
        
        Args:
            station: Station identifier (e.g., '9M', '14M', '37M')
            year: Year (2018 or 2021)
            data_type: Either 'Temp' or 'Depth'
            
        Returns:
            DataFrame with environmental data
        """
        env_file = (
            self.raw_data_path / str(year) / "environmental" / 
            f"Master_{station}_{data_type}_{year}.xlsx"
        )
        
        if not env_file.exists():
            raise FileNotFoundError(f"Environmental file not found: {env_file}")
            
        df = pd.read_excel(env_file)
        return df
    
    def load_acoustic_indices(self, station: str, bandwidth: str = "FullBW") -> pd.DataFrame:
        """Load acoustic indices data for a station.
        
        Args:
            station: Station identifier (e.g., '9M', '14M', '37M')
            bandwidth: Either 'FullBW' or '8kHz'
            
        Returns:
            DataFrame with acoustic indices data
        """
        indices_file = (
            self.raw_data_path / "indices" / 
            f"Acoustic_Indices_{station}_2021_{bandwidth}_v2_Final.csv"
        )
        
        if not indices_file.exists():
            raise FileNotFoundError(f"Acoustic indices file not found: {indices_file}")
            
        df = pd.read_csv(indices_file)
        return df
    
    def get_available_stations(self) -> List[str]:
        """Get list of available stations based on detection files.
        
        Returns:
            List of station identifiers
        """
        stations = set()
        
        for year in [2018, 2021]:
            detections_path = self.raw_data_path / str(year) / "detections"
            if detections_path.exists():
                for file in detections_path.glob("Master_Manual_*_2h_*.xlsx"):
                    # Extract station from filename
                    parts = file.stem.split('_')
                    if len(parts) >= 3:
                        station = parts[2]  # e.g., '9M', '14M', '37M'
                        stations.add(station)
        
        return sorted(list(stations))
    
    def get_available_years(self) -> List[int]:
        """Get list of available years.
        
        Returns:
            List of available years
        """
        years = []
        for year_dir in self.raw_data_path.glob("[0-9][0-9][0-9][0-9]"):
            if year_dir.is_dir():
                years.append(int(year_dir.name))
        
        return sorted(years)
    
    def load_compiled_detections(self) -> Dict[str, Any]:
        """Load compiled detections data from JSON file.
        
        Returns:
            Dictionary with compiled detections data
        """
        import json
        
        compiled_file = self.data_root / "processed" / "compiled_detections.json"
        
        if not compiled_file.exists():
            raise FileNotFoundError(f"Compiled detections file not found: {compiled_file}")
            
        with open(compiled_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data


def create_loader(data_root: Optional[Union[str, Path]] = None) -> DataLoader:
    """Create a DataLoader instance.
    
    Args:
        data_root: Path to data directory. If None, uses default location.
        
    Returns:
        Configured DataLoader instance
    """
    if data_root is None:
        # Default to data directory at repo root
        current_file = Path(__file__)
        # Go up from python/mbon_analysis/data to repo root then to data
        data_root = current_file.parent.parent.parent.parent / "data"
    
    return DataLoader(data_root)