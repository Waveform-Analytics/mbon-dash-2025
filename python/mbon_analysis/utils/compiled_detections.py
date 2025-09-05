"""Utilities for working with compiled detections/annotations data."""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

from ..data.loaders import create_loader
from .species_filter import SpeciesFilter


def compile_detections_data(data_root: Path, output_path: Path) -> Dict[str, Any]:
    """Compile all detections/annotations data into a single structure.
    
    Args:
        data_root: Path to the data directory
        output_path: Path where the compiled JSON should be saved
        
    Returns:
        Dictionary containing all compiled detections data
    """
    logger = logging.getLogger(__name__)
    
    # Create loader
    loader = create_loader(data_root)
    
    # Initialize species filter
    species_filter = SpeciesFilter()
    logger.info(f"Species filtering enabled: {species_filter.is_enabled()}")
    
    # Get available stations
    stations = loader.get_available_stations()
    logger.info(f"Found stations: {stations}")
    
    # Get column name mappings
    try:
        column_mappings = loader.load_species_mapping()
        logger.info(f"Loaded column mappings with {len(column_mappings)} species")
        
        # Apply species filtering to column mappings
        if species_filter.is_enabled():
            original_count = len(column_mappings)
            column_mappings = species_filter.get_filtered_species_mapping(column_mappings)
            logger.info(f"Filtered species mappings: {original_count} -> {len(column_mappings)}")
            
    except Exception as e:
        logger.warning(f"Could not load column mappings: {e}")
        column_mappings = pd.DataFrame()
    
    compiled_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Compiled detections/annotations data from all available Excel files",
            "version": "1.0.0",
            "total_files_processed": 0,
            "total_records": 0,
            "column_mappings": column_mappings.to_dict('records') if not column_mappings.empty else [],
            "species_filtering": {
                "enabled": species_filter.is_enabled(),
                "config_path": str(species_filter.config_path),
                "keep_species": list(species_filter.get_keep_species()) if species_filter.is_enabled() else []
            }
        },
        "stations": {},
        "summary": {
            "stations": {},
            "years": {},
            "species": {},
            "total_files": 0,
            "total_records": 0
        }
    }
    
    total_files = 0
    total_records = 0
    
    # Process each station and year combination
    for station in stations:
        logger.info(f"Processing station: {station}")
        compiled_data["stations"][station] = {}
        compiled_data["summary"]["stations"][station] = {
            "total_records": 0,
            "years": {}
        }
        
        # Find all available years for this station
        station_years = set()
        for year_dir in data_root.glob("raw/*"):
            if year_dir.is_dir() and year_dir.name.isdigit():
                year = year_dir.name
                detection_file = year_dir / "detections" / f"Master_Manual_{station}_2h_{year}.xlsx"
                if detection_file.exists():
                    station_years.add(year)
        
        if not station_years:
            logger.warning(f"No detection files found for station {station}")
            continue
            
        for year in sorted(station_years):
            logger.info(f"  Processing year: {year}")
            compiled_data["stations"][station][year] = {}
            compiled_data["summary"]["stations"][station]["years"][year] = {
                "total_records": 0,
                "species_detected": set()
            }
            
            try:
                logger.info(f"    Loading detection data for {station} {year}")
                
                # Load the detection data for this specific year
                detection_file = data_root / "raw" / year / "detections" / f"Master_Manual_{station}_2h_{year}.xlsx"
                
                if not detection_file.exists():
                    logger.warning(f"    File not found: {detection_file}")
                    compiled_data["stations"][station][year] = {
                        "error": "File not found",
                        "data": [],
                        "columns": [],
                        "shape": (0, 0),
                        "file_info": {
                            "filename": f"Master_Manual_{station}_2h_{year}.xlsx",
                            "records_count": 0,
                            "columns_count": 0
                        }
                    }
                    continue
                
                # Load the Excel file from the 'Data' sheet
                df = pd.read_excel(detection_file, sheet_name='Data')
                
                # Apply species filtering
                if species_filter.is_enabled():
                    logger.info(f"      Applying species filtering to {station} {year} data")
                    original_columns = len(df.columns)
                    df = species_filter.filter_species_columns(df, column_mappings)
                    logger.info(f"      Columns after filtering: {original_columns} -> {len(df.columns)}")
                
                # Convert DataFrame to records (list of dictionaries)
                records = df.to_dict('records')
                
                # Identify species columns (biological detections)
                species_columns = []
                if not column_mappings.empty:
                    bio_mappings = column_mappings[column_mappings['type'] == 'bio']
                    species_columns = bio_mappings['long_name'].tolist()
                
                # Count detections by species
                species_counts = {}
                for col in species_columns:
                    if col in df.columns:
                        # Count non-null, non-zero detections
                        detections = df[col].dropna()
                        if detections.dtype in ['int64', 'float64']:
                            detections = detections[detections > 0]
                        species_counts[col] = len(detections)
                        
                        if len(detections) > 0:
                            compiled_data["summary"]["stations"][station]["years"][year]["species_detected"].add(col)
                
                # Apply species filtering to species counts if enabled
                if species_filter.is_enabled():
                    original_species_count = len(species_counts)
                    species_counts = species_filter.filter_species_counts(species_counts, column_mappings)
                    logger.info(f"      Species counts after filtering: {original_species_count} -> {len(species_counts)}")
                
                # Store the data
                compiled_data["stations"][station][year] = {
                    "data": records,
                    "columns": list(df.columns),
                    "shape": df.shape,
                    "species_counts": species_counts,
                    "file_info": {
                        "filename": f"Master_Manual_{station}_2h_{year}.xlsx",
                        "records_count": len(records),
                        "columns_count": len(df.columns)
                    }
                }
                
                # Update summary statistics
                compiled_data["summary"]["stations"][station]["years"][year]["total_records"] = len(records)
                compiled_data["summary"]["stations"][station]["total_records"] += len(records)
                
                if year not in compiled_data["summary"]["years"]:
                    compiled_data["summary"]["years"][year] = 0
                compiled_data["summary"]["years"][year] += len(records)
                
                # Update species summary
                for species, count in species_counts.items():
                    if species not in compiled_data["summary"]["species"]:
                        compiled_data["summary"]["species"][species] = 0
                    compiled_data["summary"]["species"][species] += count
                
                total_files += 1
                total_records += len(records)
                
                logger.info(f"      Loaded {len(records)} records from {year} data")
                logger.info(f"      Species detected: {list(species_counts.keys())}")
                
            except Exception as e:
                logger.error(f"      Error processing {station} {year}: {e}")
                compiled_data["stations"][station][year] = {
                    "error": str(e),
                    "data": [],
                    "columns": [],
                    "shape": (0, 0),
                    "file_info": {
                        "filename": f"Master_Manual_{station}_2h_{year}.xlsx",
                        "records_count": 0,
                        "columns_count": 0
                    }
                }
    
    # Convert sets to lists for JSON serialization
    for station in compiled_data["summary"]["stations"]:
        for year in compiled_data["summary"]["stations"][station]["years"]:
            species_set = compiled_data["summary"]["stations"][station]["years"][year]["species_detected"]
            compiled_data["summary"]["stations"][station]["years"][year]["species_detected"] = list(species_set)
    
    # Update final metadata
    compiled_data["metadata"]["total_files_processed"] = total_files
    compiled_data["metadata"]["total_records"] = total_records
    compiled_data["summary"]["total_files"] = total_files
    compiled_data["summary"]["total_records"] = total_records
    
    logger.info(f"Compilation complete: {total_files} files, {total_records} total records")
    
    return compiled_data


def save_compiled_detections_data(data: Dict[str, Any], output_path: Path):
    """Save compiled detections data to JSON file.
    
    Args:
        data: Compiled data dictionary
        output_path: Path where to save the JSON file
    """
    logger = logging.getLogger(__name__)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save with pretty formatting for readability (though file will be large)
    logger.info(f"Saving compiled detections data to: {output_path}")
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    # Get file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"File saved successfully. Size: {file_size_mb:.2f} MB")


class CompiledDetectionsManager:
    """Manager class for working with compiled detections data."""
    
    def __init__(self, json_file_path: Union[str, Path]):
        """Initialize with path to compiled detections JSON file.
        
        Args:
            json_file_path: Path to the compiled_detections.json file
        """
        self.json_file_path = Path(json_file_path)
        self._data = None
        self._metadata = None
        
    def load_data(self) -> Dict[str, Any]:
        """Load the compiled detections data from JSON file.
        
        Returns:
            Dictionary containing all compiled detections data
        """
        if self._data is None:
            if not self.json_file_path.exists():
                raise FileNotFoundError(f"Compiled detections file not found: {self.json_file_path}")
            
            logging.info(f"Loading compiled detections data from: {self.json_file_path}")
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
    
    def get_years(self) -> List[str]:
        """Get list of available years.
        
        Returns:
            List of year identifiers
        """
        data = self.load_data()
        return list(data.get('summary', {}).get('years', {}).keys())
    
    def get_species(self) -> List[str]:
        """Get list of available species.
        
        Returns:
            List of species identifiers
        """
        data = self.load_data()
        return list(data.get('summary', {}).get('species', {}).keys())
    
    def get_station_data(self, station: str, year: Optional[str] = None) -> Dict[str, Any]:
        """Get data for a specific station and optionally specific year.
        
        Args:
            station: Station identifier (e.g., '9M', '14M', '37M')
            year: Optional year filter (e.g., '2018', '2021')
            
        Returns:
            Dictionary with station data
        """
        data = self.load_data()
        stations = data.get('stations', {})
        
        if station not in stations:
            raise ValueError(f"Station '{station}' not found. Available stations: {list(stations.keys())}")
        
        station_data = stations[station]
        
        if year is not None:
            if year not in station_data:
                raise ValueError(f"Year '{year}' not found for station '{station}'. "
                               f"Available years: {list(station_data.keys())}")
            return station_data[year]
        
        return station_data
    
    def get_station_dataframe(self, station: str, year: str) -> pd.DataFrame:
        """Get data for a specific station and year as a pandas DataFrame.
        
        Args:
            station: Station identifier (e.g., '9M', '14M', '37M')
            year: Year (e.g., '2018', '2021')
            
        Returns:
            DataFrame with the station's detection data
        """
        station_data = self.get_station_data(station, year)
        
        if 'error' in station_data:
            raise ValueError(f"Error in data for {station} {year}: {station_data['error']}")
        
        records = station_data.get('data', [])
        if not records:
            return pd.DataFrame()
        
        return pd.DataFrame(records)
    
    def get_species_detections(self, species: str) -> Dict[str, Any]:
        """Get detection data for a specific species across all stations and years.
        
        Args:
            species: Species name (long name from column mappings)
            
        Returns:
            Dictionary with detection data by station and year
        """
        data = self.load_data()
        stations = data.get('stations', {})
        
        species_data = {}
        
        for station in stations:
            species_data[station] = {}
            for year in stations[station]:
                year_data = stations[station][year]
                if 'error' not in year_data:
                    species_counts = year_data.get('species_counts', {})
                    if species in species_counts:
                        species_data[station][year] = {
                            'count': species_counts[species],
                            'total_records': year_data.get('file_info', {}).get('records_count', 0)
                        }
        
        return species_data
    
    def get_detection_summary(self, station: str, year: str) -> Dict[str, Any]:
        """Get summary statistics for detections in a station/year combination.
        
        Args:
            station: Station identifier
            year: Year (e.g., '2018', '2021')
            
        Returns:
            Dictionary with summary statistics
        """
        df = self.get_station_dataframe(station, year)
        
        if df.empty:
            return {"error": "No data available"}
        
        # Get metadata about the data
        station_data = self.get_station_data(station, year)
        species_counts = station_data.get('species_counts', {})
        
        summary = {
            "station": station,
            "year": year,
            "total_records": len(df),
            "total_columns": len(df.columns),
            "column_names": list(df.columns),
            "species_detected": len([s for s in species_counts.values() if s > 0]),
            "species_counts": species_counts,
            "detection_rate": sum(species_counts.values()) / len(df) if len(df) > 0 else 0
        }
        
        return summary
    
    def export_station_to_csv(self, station: str, year: str, 
                            output_path: Union[str, Path]) -> bool:
        """Export a station's data to CSV file.
        
        Args:
            station: Station identifier
            year: Year (e.g., '2018', '2021')
            output_path: Path where to save the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            df = self.get_station_dataframe(station, year)
            
            if df.empty:
                logging.warning(f"No data to export for {station} {year}")
                return False
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            logging.info(f"Exported {len(df)} records to {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error exporting {station} {year} to CSV: {e}")
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
