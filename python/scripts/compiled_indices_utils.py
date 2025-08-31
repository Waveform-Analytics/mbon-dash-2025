#!/usr/bin/env python3
"""Utilities for working with the compiled indices JSON file.

This module provides helper functions to work with the large compiled indices
JSON file, including querying, filtering, and analyzing the data.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime


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


def main():
    """Example usage of the CompiledIndicesManager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Work with compiled indices JSON file")
    parser.add_argument("json_file", help="Path to compiled_indices.json file")
    parser.add_argument("--action", choices=["summary", "stations", "export"], 
                       default="summary", help="Action to perform")
    parser.add_argument("--station", help="Station identifier (for export)")
    parser.add_argument("--bandwidth", help="Bandwidth (for export)")
    parser.add_argument("--output", help="Output path (for export)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        manager = CompiledIndicesManager(args.json_file)
        
        if args.action == "summary":
            summary = manager.get_summary()
            print("Compiled Indices Summary:")
            print(f"  Total files: {summary.get('total_files', 0)}")
            print(f"  Total records: {summary.get('total_records', 0):,}")
            print(f"  Stations: {list(summary.get('stations', {}).keys())}")
            print(f"  Bandwidths: {list(summary.get('bandwidths', {}).keys())}")
            
            # File info
            file_info = manager.get_file_info()
            print(f"\nFile Information:")
            print(f"  Size: {file_info.get('file_size_mb', 0)} MB")
            print(f"  Last modified: {file_info.get('last_modified', 'Unknown')}")
        
        elif args.action == "stations":
            stations = manager.get_stations()
            print("Available stations:")
            for station in stations:
                print(f"  - {station}")
        
        elif args.action == "export":
            if not all([args.station, args.bandwidth, args.output]):
                print("Error: --station, --bandwidth, and --output are required for export")
                return
            
            success = manager.export_station_to_csv(args.station, args.bandwidth, args.output)
            if success:
                print(f"Successfully exported {args.station} {args.bandwidth} to {args.output}")
            else:
                print("Export failed")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
