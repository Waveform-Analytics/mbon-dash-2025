#!/usr/bin/env python3
"""
Excel data processing utilities for MBON project.

This module handles the raw Excel → DataFrame conversion that's needed by both
dashboard preparation scripts and analysis workflows.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class MBONExcelProcessor:
    """
    Centralized processor for MBON Excel files.
    
    This class handles all the common Excel processing operations:
    - Loading column mappings
    - Processing detection files  
    - Processing environmental data
    - Extracting metadata from filenames
    - Data validation and cleaning
    """
    
    def __init__(self, 
                 raw_data_dir: Union[str, Path] = "data/cdn/raw-data",
                 years_of_interest: List[str] = None,
                 stations_of_interest: List[str] = None):
        """
        Initialize the processor.
        
        Args:
            raw_data_dir: Path to raw data directory
            years_of_interest: List of years to process (default: ["2018", "2021"])
            stations_of_interest: List of stations to process (default: ["9M", "14M", "37M"])
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.years_of_interest = years_of_interest or ["2018", "2021"]
        self.stations_of_interest = stations_of_interest or ["9M", "14M", "37M"]
        self.column_mapping_file = self.raw_data_dir / "det_column_names.csv"
        
        # Cache for loaded mappings
        self._column_mapping = None
        self._type_mapping = None
    
    def load_column_mapping(self) -> Tuple[Dict[str, str], Dict[str, Dict]]:
        """
        Load column name mappings from CSV file.
        
        Returns:
            Tuple of (name_mapping, type_mapping)
            - name_mapping: Dict[short_name] = long_name
            - type_mapping: Dict[short_name] = {"long_name": str, "type": str}
        
        Raises:
            FileNotFoundError: If column mapping file doesn't exist
        """
        if self._column_mapping is not None:
            return self._column_mapping, self._type_mapping
        
        if not self.column_mapping_file.exists():
            raise FileNotFoundError(f"Column mapping file not found: {self.column_mapping_file}")
        
        logger.info(f"Loading column mappings from {self.column_mapping_file}")
        df = pd.read_csv(self.column_mapping_file)
        
        # Create name mapping
        name_mapping = dict(zip(df["short_name"], df["long_name"]))
        
        # Create type mapping
        type_mapping = {}
        for _, row in df.iterrows():
            type_mapping[row["short_name"]] = {
                "long_name": row["long_name"],
                "type": row["type"]
            }
        
        # Cache the mappings
        self._column_mapping = name_mapping
        self._type_mapping = type_mapping
        
        logger.info(f"Loaded {len(name_mapping)} column mappings")
        return name_mapping, type_mapping
    
    def extract_metadata_from_filename(self, filepath: Path) -> Tuple[str, str]:
        """
        Extract year and station from filename.
        
        Handles various filename patterns:
        - Master_Manual_9M_2h_2018.xlsx → ("2018", "9M")
        - Master_9M_Temp_2021.xlsx → ("2021", "9M")
        
        Args:
            filepath: Path to file
            
        Returns:
            Tuple of (year, station)
            
        Raises:
            ValueError: If filename format is not recognized
        """
        parts = str(filepath).split('/')
        year = parts[-2]  # Second to last part (e.g., "2018" or "2021")
        filename = parts[-1]
        
        # Extract station from filename
        filename_parts = filename.split('_')
        
        if "Manual" in filename:
            # Pattern: Master_Manual_9M_2h_2018.xlsx
            if len(filename_parts) >= 3:
                station = filename_parts[2]
            else:
                raise ValueError(f"Cannot extract station from Manual file: {filename}")
        else:
            # Pattern: Master_9M_Temp_2018.xlsx
            if len(filename_parts) >= 2:
                station = filename_parts[1]
            else:
                raise ValueError(f"Cannot extract station from file: {filename}")
        
        # Validate extracted values
        if year not in self.years_of_interest:
            logger.debug(f"Year {year} not in years of interest: {self.years_of_interest}")
        
        if station not in self.stations_of_interest:
            logger.debug(f"Station {station} not in stations of interest: {self.stations_of_interest}")
        
        return year, station
    
    def process_single_excel_file(self, 
                                  filepath: Path, 
                                  sheet_index: int = 1,
                                  validate_columns: bool = True) -> pd.DataFrame:
        """
        Process a single Excel file into a DataFrame with proper column mapping.
        
        Args:
            filepath: Path to Excel file
            sheet_index: Which sheet to read (0-based, so 1 = second sheet)
            validate_columns: Whether to validate column count matches mapping
            
        Returns:
            Processed DataFrame with metadata columns added
            
        Raises:
            ValueError: If file processing fails
        """
        logger.info(f"Processing Excel file: {filepath.name}")
        
        try:
            # Load column mappings
            name_mapping, type_mapping = self.load_column_mapping()
            expected_columns = list(name_mapping.keys())
            
            # Check file size
            file_size_mb = filepath.stat().st_size / (1024 * 1024)
            if file_size_mb > 100:
                logger.warning(f"Large file detected ({file_size_mb:.1f}MB): {filepath.name}")
            
            # Read Excel file
            try:
                df = pd.read_excel(filepath, sheet_name=sheet_index)
            except ValueError as e:
                logger.error(f"Sheet {sheet_index} not found in {filepath.name}: {e}")
                logger.info("Trying sheet 0 instead...")
                df = pd.read_excel(filepath, sheet_name=0)
            
            # Validate dataframe
            if df.empty:
                raise ValueError(f"Empty dataframe from {filepath.name}")
            
            # Validate columns
            if validate_columns and len(df.columns) != len(expected_columns):
                raise ValueError(
                    f"Column mismatch in {filepath.name}: "
                    f"expected {len(expected_columns)}, got {len(df.columns)}"
                )
            
            # Apply column mapping
            if validate_columns:
                df.columns = expected_columns
            
            # Extract and add metadata
            year, station = self.extract_metadata_from_filename(filepath)
            df['year'] = year
            df['station'] = station
            df['source_file'] = filepath.name
            
            # Process dates
            if 'date' in df.columns:
                before_count = len(df)
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.dropna(subset=['date'])
                after_count = len(df)
                
                if before_count - after_count > 0:
                    logger.debug(f"Dropped {before_count - after_count} rows with invalid dates from {filepath.name}")
            
            # Validate data quality if this appears to be a detection file
            if validate_columns and not self.validate_detection_data(df):
                logger.warning(f"Data validation failed for {filepath.name}, but continuing...")
            
            logger.info(f"✓ Successfully processed {filepath.name} ({len(df)} rows)")
            return df
            
        except Exception as e:
            logger.error(f"Failed to process {filepath.name}: {str(e)}")
            raise ValueError(f"Excel processing failed for {filepath.name}: {e}") from e
    
    def find_detection_files(self) -> List[Path]:
        """
        Find all detection files matching the pattern for specified years and stations.
        
        Returns:
            List of Path objects for detection files
        """
        detection_files = []
        pattern = "Master_Manual_*_2h_*.xlsx"
        
        for year in self.years_of_interest:
            year_dir = self.raw_data_dir / year
            if year_dir.exists():
                files = list(year_dir.glob(pattern))
                # Filter by station
                for file in files:
                    try:
                        _, station = self.extract_metadata_from_filename(file)
                        if station in self.stations_of_interest:
                            detection_files.append(file)
                    except ValueError as e:
                        logger.warning(f"Skipping file with invalid name: {file} ({e})")
        
        logger.info(f"Found {len(detection_files)} detection files")
        return detection_files
    
    def process_all_detection_files(self) -> pd.DataFrame:
        """
        Process all detection files and combine into a single DataFrame.
        
        Returns:
            Combined DataFrame with all detection data
            
        Raises:
            ValueError: If no files were successfully processed
        """
        logger.info("Processing all detection files...")
        
        detection_files = self.find_detection_files()
        if not detection_files:
            raise ValueError(f"No detection files found in {self.raw_data_dir}")
        
        successful_dfs = []
        failed_files = []
        
        for file in detection_files:
            try:
                df = self.process_single_excel_file(file)
                successful_dfs.append(df)
            except Exception as e:
                logger.error(f"Failed to process {file.name}: {e}")
                failed_files.append(file.name)
        
        if not successful_dfs:
            raise ValueError("No detection files were successfully processed!")
        
        # Combine all dataframes
        combined_df = pd.concat(successful_dfs, ignore_index=True)
        
        logger.info(f"✅ Combined {len(combined_df)} detection records from {len(successful_dfs)} files")
        if failed_files:
            logger.warning(f"Failed to process {len(failed_files)} files: {failed_files}")
        
        return combined_df
    
    def process_environmental_files(self) -> pd.DataFrame:
        """
        Process temperature and depth files and combine into environmental DataFrame.
        
        Returns:
            Combined environmental DataFrame
        """
        logger.info("Processing environmental data files...")
        
        environmental_records = []
        
        for year in self.years_of_interest:
            year_dir = self.raw_data_dir / year
            if not year_dir.exists():
                logger.warning(f"Year directory not found: {year_dir}")
                continue
            
            for station in self.stations_of_interest:
                # Process temperature file
                temp_file = year_dir / f"Master_{station}_Temp_{year}.xlsx"
                if temp_file.exists():
                    try:
                        temp_df = pd.read_excel(temp_file, sheet_name=1)
                        temp_df = temp_df.rename(columns={'Date and time': 'datetime'})
                        
                        # Round timestamps to seconds for better merging
                        if 'datetime' in temp_df.columns:
                            temp_df['datetime'] = pd.to_datetime(temp_df['datetime']).dt.round('s')
                        
                        temp_df['year'] = year
                        temp_df['station'] = station
                        temp_df['data_type'] = 'temperature'
                        temp_df['source_file'] = temp_file.name
                        
                        environmental_records.append(temp_df)
                        logger.info(f"✓ Processed temperature data: {temp_file.name}")
                    except Exception as e:
                        logger.error(f"Failed to process temperature file {temp_file.name}: {e}")
                
                # Process depth file  
                depth_file = year_dir / f"Master_{station}_Depth_{year}.xlsx"
                if depth_file.exists():
                    try:
                        depth_df = pd.read_excel(depth_file, sheet_name=1)
                        depth_df = depth_df.rename(columns={'Date and time': 'datetime'})
                        
                        # Round timestamps to seconds for better merging
                        if 'datetime' in depth_df.columns:
                            depth_df['datetime'] = pd.to_datetime(depth_df['datetime']).dt.round('s')
                        
                        depth_df['year'] = year
                        depth_df['station'] = station
                        depth_df['data_type'] = 'depth'
                        depth_df['source_file'] = depth_file.name
                        
                        environmental_records.append(depth_df)
                        logger.info(f"✓ Processed depth data: {depth_file.name}")
                    except Exception as e:
                        logger.error(f"Failed to process depth file {depth_file.name}: {e}")
        
        if not environmental_records:
            logger.warning("No environmental files were successfully processed")
            return pd.DataFrame()
        
        combined_environmental = pd.concat(environmental_records, ignore_index=True)
        logger.info(f"✅ Combined {len(combined_environmental)} environmental records")
        
        return combined_environmental
    
    def process_acoustic_files(self) -> pd.DataFrame:
        """
        Process acoustic indices CSV files and combine into acoustic DataFrame.
        
        Returns:
            Combined acoustic indices DataFrame
        """
        logger.info("Processing acoustic indices CSV files...")
        
        acoustic_records = []
        
        # Look for acoustic indices CSV files in the indices directory
        indices_dir = self.raw_data_dir / "indices"
        if not indices_dir.exists():
            logger.warning(f"Indices directory not found: {indices_dir}")
            return pd.DataFrame()
        
        # Pattern: Acoustic_Indices_{station}_{year}_{bandwidth}_v2_Final.csv
        pattern = "Acoustic_Indices_*.csv"
        
        for csv_file in indices_dir.glob(pattern):
            try:
                # Extract metadata from filename
                # Format: Acoustic_Indices_9M_2021_FullBW_v2_Final.csv
                filename_parts = csv_file.stem.split('_')
                
                if len(filename_parts) < 5:
                    logger.warning(f"Cannot parse filename format: {csv_file.name}")
                    continue
                
                station = filename_parts[2]  # "9M"
                year = filename_parts[3]     # "2021"
                bandwidth = filename_parts[4] # "FullBW" or "8kHz"
                
                # Filter by our criteria
                if year not in self.years_of_interest:
                    logger.debug(f"Skipping year {year} not in {self.years_of_interest}")
                    continue
                    
                if station not in self.stations_of_interest:
                    logger.debug(f"Skipping station {station} not in {self.stations_of_interest}")
                    continue
                
                # Read CSV file
                acoustic_df = pd.read_csv(csv_file)
                
                # Add metadata columns
                acoustic_df['source_file'] = csv_file.name
                acoustic_df['station'] = station
                acoustic_df['year'] = year
                acoustic_df['bandwidth'] = bandwidth
                
                # Standardize datetime column if it exists
                if 'Date' in acoustic_df.columns:
                    # Convert to datetime and round to seconds for consistency
                    acoustic_df['datetime'] = pd.to_datetime(acoustic_df['Date'], errors='coerce').dt.round('s')
                
                acoustic_records.append(acoustic_df)
                logger.info(f"✓ Processed acoustic indices: {csv_file.name} ({len(acoustic_df)} records)")
                
            except Exception as e:
                logger.error(f"Failed to process acoustic indices file {csv_file.name}: {e}")
        
        if not acoustic_records:
            logger.warning("No acoustic indices files were successfully processed")
            return pd.DataFrame()
        
        combined_acoustic = pd.concat(acoustic_records, ignore_index=True)
        logger.info(f"✅ Combined {len(combined_acoustic)} acoustic indices records from {len(acoustic_records)} files")
        
        return combined_acoustic
    
    def validate_detection_data(self, df: pd.DataFrame) -> bool:
        """
        Validate detection data ranges and quality.
        
        Args:
            df: Detection DataFrame to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        validation_issues = []
        
        # Check date range
        if 'date' in df.columns:
            date_col = pd.to_datetime(df['date'], errors='coerce')
            valid_dates = date_col.dropna()
            
            if len(valid_dates) < len(df) * 0.95:  # 95% of dates should be valid
                validation_issues.append(f"Only {len(valid_dates)/len(df)*100:.1f}% of dates are valid")
            
            if len(valid_dates) > 0:
                date_range = valid_dates.max() - valid_dates.min()
                if date_range.days > 400:  # Reasonable for a year of data
                    validation_issues.append(f"Date range is {date_range.days} days (seems too long)")
        
        # Check for completely empty detection columns
        name_mapping, type_mapping = self.load_column_mapping()
        detection_cols = [k for k, v in type_mapping.items() if v['type'] in ['bio', 'anthro']]
        
        non_zero_detections = 0
        for col in detection_cols:
            if col in df.columns:
                col_sum = pd.to_numeric(df[col], errors='coerce').sum()
                if not pd.isna(col_sum) and col_sum > 0:
                    non_zero_detections += 1
        
        if non_zero_detections == 0:
            validation_issues.append("No detection columns have any positive values")
        
        # Report validation issues
        if validation_issues:
            for issue in validation_issues:
                logger.warning(f"Validation issue: {issue}")
            return False
        
        return True


# Convenience functions for backward compatibility
def load_column_mapping(raw_data_dir: Union[str, Path] = "data/cdn/raw-data") -> Tuple[Dict[str, str], Dict[str, Dict]]:
    """Convenience function for loading column mappings."""
    processor = MBONExcelProcessor(raw_data_dir)
    return processor.load_column_mapping()

def extract_metadata_from_filename(filepath: Path) -> Tuple[str, str]:
    """Convenience function for extracting metadata from filenames."""
    processor = MBONExcelProcessor()
    return processor.extract_metadata_from_filename(filepath)


# Example usage
if __name__ == "__main__":
    """Example usage of Excel processor."""
    
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    print("MBON Excel Processor Example")
    print("=" * 50)
    
    # Create processor
    processor = MBONExcelProcessor()
    
    try:
        # Process all detection files
        print("\n1. Processing detection files...")
        detections = processor.process_all_detection_files()
        print(f"   Loaded {len(detections)} detection records")
        print(f"   Years: {sorted(detections['year'].unique())}")
        print(f"   Stations: {sorted(detections['station'].unique())}")
        
        # Process environmental files
        print("\n2. Processing environmental files...")
        environmental = processor.process_environmental_files()
        print(f"   Loaded {len(environmental)} environmental records")
        
        # Process acoustic files
        print("\n3. Processing acoustic files...")
        acoustic = processor.process_acoustic_files()
        print(f"   Loaded {len(acoustic)} acoustic records")
        
        print("\n✅ Excel processing examples completed!")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()