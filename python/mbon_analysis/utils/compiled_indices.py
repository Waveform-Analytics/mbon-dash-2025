"""Utilities for working with compiled indices data."""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

from ..data.loaders import create_loader


def compile_indices_data(data_root: Path, output_path: Path) -> Dict[str, Any]:
    """Compile all acoustic indices data into a single structure.
    
    Args:
        data_root: Path to the data directory
        output_path: Path where the compiled JSON should be saved
        
    Returns:
        Dictionary containing all compiled indices data
    """
    logger = logging.getLogger(__name__)
    
    # Create loader
    loader = create_loader(data_root)
    
    # Get available stations
    stations = loader.get_available_stations()
    logger.info(f"Found stations: {stations}")
    
    # Define bandwidths
    bandwidths = ["FullBW", "8kHz"]
    
    compiled_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Compiled acoustic indices data from all available CSV files",
            "version": "1.0.0",
            "total_files_processed": 0,
            "total_records": 0
        },
        "stations": {},
        "summary": {
            "stations": {},
            "bandwidths": {},
            "total_files": 0,
            "total_records": 0
        }
    }
    
    total_files = 0
    total_records = 0
    
    # Process each station and bandwidth combination
    for station in stations:
        logger.info(f"Processing station: {station}")
        compiled_data["stations"][station] = {}
        compiled_data["summary"]["stations"][station] = {
            "total_records": 0,
            "bandwidths": {}
        }
        
        for bandwidth in bandwidths:
            try:
                logger.info(f"  Loading {bandwidth} data for {station}")
                
                # Load the indices data
                df = loader.load_acoustic_indices(station, bandwidth)
                
                # Convert DataFrame to records (list of dictionaries)
                records = df.to_dict('records')
                
                # Store the data
                compiled_data["stations"][station][bandwidth] = {
                    "data": records,
                    "columns": list(df.columns),
                    "shape": df.shape,
                    "file_info": {
                        "filename": f"Acoustic_Indices_{station}_2021_{bandwidth}_v2_Final.csv",
                        "records_count": len(records),
                        "columns_count": len(df.columns)
                    }
                }
                
                # Update summary statistics
                compiled_data["summary"]["stations"][station]["bandwidths"][bandwidth] = len(records)
                compiled_data["summary"]["stations"][station]["total_records"] += len(records)
                
                if bandwidth not in compiled_data["summary"]["bandwidths"]:
                    compiled_data["summary"]["bandwidths"][bandwidth] = 0
                compiled_data["summary"]["bandwidths"][bandwidth] += len(records)
                
                total_files += 1
                total_records += len(records)
                
                logger.info(f"    Loaded {len(records)} records from {bandwidth} data")
                
            except FileNotFoundError as e:
                logger.warning(f"    File not found for {station} {bandwidth}: {e}")
                compiled_data["stations"][station][bandwidth] = {
                    "error": "File not found",
                    "data": [],
                    "columns": [],
                    "shape": (0, 0),
                    "file_info": {
                        "filename": f"Acoustic_Indices_{station}_2021_{bandwidth}_v2_Final.csv",
                        "records_count": 0,
                        "columns_count": 0
                    }
                }
            except Exception as e:
                logger.error(f"    Error processing {station} {bandwidth}: {e}")
                compiled_data["stations"][station][bandwidth] = {
                    "error": str(e),
                    "data": [],
                    "columns": [],
                    "shape": (0, 0),
                    "file_info": {
                        "filename": f"Acoustic_Indices_{station}_2021_{bandwidth}_v2_Final.csv",
                        "records_count": 0,
                        "columns_count": 0
                    }
                }
    
    # Update final metadata
    compiled_data["metadata"]["total_files_processed"] = total_files
    compiled_data["metadata"]["total_records"] = total_records
    compiled_data["summary"]["total_files"] = total_files
    compiled_data["summary"]["total_records"] = total_records
    
    logger.info(f"Compilation complete: {total_files} files, {total_records} total records")
    
    return compiled_data


def save_compiled_data(data: Dict[str, Any], output_path: Path):
    """Save compiled data to JSON file.
    
    Args:
        data: Compiled data dictionary
        output_path: Path where to save the JSON file
    """
    logger = logging.getLogger(__name__)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save with pretty formatting for readability (though file will be large)
    logger.info(f"Saving compiled data to: {output_path}")
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    # Get file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"File saved successfully. Size: {file_size_mb:.2f} MB")


class CompiledIndicesManager:
    """Manager class for working with compiled indices data."""
    
    def __init__(self, json_file_path: Union[str, Path]):
        """Initialize with path to compiled indices JSON file.
        
        Args:
            json_file_path: Path to the compiled_indices.json file
        """
        self.json_file_path = Path(json_file_path)
        self._data = None
        self._metadata = None
        
    def load_data(self) -> Dict[str, Any]:
        """Load the compiled indices data from JSON file.
        
        Returns:
            Dictionary containing all compiled indices data
        """
        if self._data is None:
            if not self.json_file_path.exists():
                raise FileNotFoundError(f"Compiled indices file not found: {self.json_file_path}")
            
            logging.info(f"Loading compiled indices data from: {self.json_file_path}")
            with open(self.json_file_path, 'r') as f:
                self._data = json.load(f)
            
            self._metadata = self._data.get('metadata', {})
            logging.info(f"Loaded data with {self._metadata.get('total_records', 0):,} total records")
        
        return self._data
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the compiled data.
        
        Returns:
            Dictionary with summary statistics
        """
        data = self.load_data()
        return data.get('summary', {})
    
    def get_stations(self) -> List[str]:
        """Get list of available stations.
        
        Returns:
            List of station identifiers
        """
        data = self.load_data()
        return list(data.get('stations', {}).keys())
    
    def get_bandwidths(self) -> List[str]:
        """Get list of available bandwidths.
        
        Returns:
            List of bandwidth identifiers
        """
        data = self.load_data()
        return list(data.get('summary', {}).get('bandwidths', {}).keys())
    
    def get_station_data(self, station: str, bandwidth: Optional[str] = None) -> Dict[str, Any]:
        """Get data for a specific station and optionally specific bandwidth.
        
        Args:
            station: Station identifier (e.g., '9M', '14M', '37M')
            bandwidth: Optional bandwidth filter ('FullBW' or '8kHz')
            
        Returns:
            Dictionary with station data
        """
        data = self.load_data()
        stations = data.get('stations', {})
        
        if station not in stations:
            raise ValueError(f"Station '{station}' not found. Available stations: {list(stations.keys())}")
        
        station_data = stations[station]
        
        if bandwidth is not None:
            if bandwidth not in station_data:
                raise ValueError(f"Bandwidth '{bandwidth}' not found for station '{station}'. "
                               f"Available bandwidths: {list(station_data.keys())}")
            return station_data[bandwidth]
        
        return station_data
    
    def get_station_dataframe(self, station: str, bandwidth: str) -> pd.DataFrame:
        """Get data for a specific station and bandwidth as a pandas DataFrame.
        
        Args:
            station: Station identifier (e.g., '9M', '14M', '37M')
            bandwidth: Bandwidth ('FullBW' or '8kHz')
            
        Returns:
            DataFrame with the station's indices data
        """
        station_data = self.get_station_data(station, bandwidth)
        
        if 'error' in station_data:
            raise ValueError(f"Error in data for {station} {bandwidth}: {station_data['error']}")
        
        records = station_data.get('data', [])
        if not records:
            return pd.DataFrame()
        
        return pd.DataFrame(records)
    
    def filter_by_date_range(self, station: str, bandwidth: str, 
                           start_date: str, end_date: str) -> pd.DataFrame:
        """Filter station data by date range.
        
        Args:
            station: Station identifier
            bandwidth: Bandwidth ('FullBW' or '8kHz')
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            DataFrame filtered by date range
        """
        df = self.get_station_dataframe(station, bandwidth)
        
        if df.empty:
            return df
        
        # Assuming there's a date column - you may need to adjust this
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        
        if not date_columns:
            logging.warning(f"No date columns found in {station} {bandwidth} data")
            return df
        
        # Use the first date column found
        date_col = date_columns[0]
        
        # Convert to datetime if needed
        if df[date_col].dtype == 'object':
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Filter by date range
        mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
        return df[mask]
    
    def get_indices_summary(self, station: str, bandwidth: str) -> Dict[str, Any]:
        """Get summary statistics for indices in a station/bandwidth combination.
        
        Args:
            station: Station identifier
            bandwidth: Bandwidth ('FullBW' or '8kHz')
            
        Returns:
            Dictionary with summary statistics
        """
        df = self.get_station_dataframe(station, bandwidth)
        
        if df.empty:
            return {"error": "No data available"}
        
        # Get numeric columns (exclude date/time columns)
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        # Remove date columns from numeric columns if they were included
        numeric_columns = [col for col in numeric_columns if col not in date_columns]
        
        summary = {
            "station": station,
            "bandwidth": bandwidth,
            "total_records": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_columns),
            "date_columns": len(date_columns),
            "column_names": list(df.columns),
            "numeric_summary": {}
        }
        
        # Calculate summary statistics for numeric columns
        for col in numeric_columns:
            summary["numeric_summary"][col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "null_count": int(df[col].isnull().sum())
            }
        
        return summary
    
    def export_station_to_csv(self, station: str, bandwidth: str, 
                            output_path: Union[str, Path]) -> bool:
        """Export a station's data to CSV file.
        
        Args:
            station: Station identifier
            bandwidth: Bandwidth ('FullBW' or '8kHz')
            output_path: Path where to save the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            df = self.get_station_dataframe(station, bandwidth)
            
            if df.empty:
                logging.warning(f"No data to export for {station} {bandwidth}")
                return False
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            logging.info(f"Exported {len(df)} records to {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting {station} {bandwidth} to CSV: {e}")
            return False
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about the compiled JSON file.
        
        Returns:
            Dictionary with file information
        """
        if not self.json_file_path.exists():
            return {"error": "File not found"}
        
        stat = self.json_file_path.stat()
        file_size_mb = stat.st_size / (1024 * 1024)
        
        return {
            "file_path": str(self.json_file_path),
            "file_size_mb": round(file_size_mb, 2),
            "file_size_bytes": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
