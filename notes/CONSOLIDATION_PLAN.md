# Excel Processing Consolidation Plan

## Overview

This plan consolidates duplicated Excel processing logic into the `mbon_analysis` package, creating a cleaner separation between data processing utilities and application scripts.

**Goal**: Move Excel → DataFrame processing into `mbon_analysis`, keep JSON export in application scripts.

**Time Estimate**: 2-3 hours (before implementing other Phase 1 fixes)

---

## Current State Analysis

### Files with Duplication:
```
scripts/dashboard_prep/process_excel_to_json.py  ← Main production script (537+ lines)
scripts/examples.py                              ← Legacy proof-of-concept (41 lines)
mbon_analysis/core/data_loader.py               ← Loads JSON (no Excel processing)
mbon_analysis/core/data_prep.py                 ← Prepares DataFrames (no Excel loading)
```

### Duplicated Functions:
1. **Column mapping loading** - 3 different implementations
2. **File metadata extraction** - 2+ different implementations  
3. **Date processing** - Similar logic scattered across files
4. **Station/year filtering** - Repeated logic

---

## Step 1: Create Excel Processor Module

Create `mbon_analysis/core/excel_processor.py`:

```python
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
            logger.warning(f"Year {year} not in years of interest: {self.years_of_interest}")
        
        if station not in self.stations_of_interest:
            logger.warning(f"Station {station} not in stations of interest: {self.stations_of_interest}")
        
        return year, station
    
    def process_single_excel_file(self, 
                                  filepath: Path, 
                                  sheet_index: int = 1,
                                  validate_columns: bool = True) -> pd.DataFrame:
        """
        Process a single Excel file into a DataFrame with proper column mapping.
        
        Args:
            filepath: Path to Excel file
            sheet_index: Which sheet to read (1-based, so 1 = second sheet)
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
                    logger.warning(f"Dropped {before_count - after_count} rows with invalid dates from {filepath.name}")
            
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
                        temp_df = self.process_single_excel_file(temp_file, validate_columns=False)
                        temp_df = temp_df.rename(columns={'Date and time': 'datetime'})
                        temp_df['data_type'] = 'temperature'
                        environmental_records.append(temp_df)
                        logger.info(f"✓ Processed temperature data: {temp_file.name}")
                    except Exception as e:
                        logger.error(f"Failed to process temperature file {temp_file.name}: {e}")
                
                # Process depth file  
                depth_file = year_dir / f"Master_{station}_Depth_{year}.xlsx"
                if depth_file.exists():
                    try:
                        depth_df = self.process_single_excel_file(depth_file, validate_columns=False)
                        depth_df = depth_df.rename(columns={'Date and time': 'datetime'})
                        depth_df['data_type'] = 'depth'
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
    logging.basicConfig(level=logging.INFO)
    
    print("MBON Excel Processor Example")
    print("=" * 50)
    
    # Create processor
    processor = MBONExcelProcessor()
    
    # Process all detection files
    detections = processor.process_all_detection_files()
    print(f"Loaded {len(detections)} detection records")
    print(f"Years: {sorted(detections['year'].unique())}")
    print(f"Stations: {sorted(detections['station'].unique())}")
    
    # Process environmental files
    environmental = processor.process_environmental_files()
    print(f"Loaded {len(environmental)} environmental records")
    
    print("\n✅ Excel processing examples completed!")
```

---

## Step 2: Update process_excel_to_json.py

Simplify the main script to use the new processor:

```python
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
from datetime import datetime

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


def generate_metadata(detections_df, environmental_df, species_list, stations_list):
    """Generate metadata with version information."""
    import hashlib
    
    # Calculate data fingerprint
    data_fingerprint = hashlib.md5(
        f"{len(detections_df)}{len(environmental_df)}{len(species_list)}".encode()
    ).hexdigest()[:8]
    
    metadata = {
        "version": f"1.0.{data_fingerprint}",
        "generated_at": datetime.now().isoformat(),
        "processing_script_version": "2.0.0",
        "data_summary": {
            "total_detections": len(detections_df),
            "total_environmental_records": len(environmental_df),
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


def export_json_files(detections_df, environmental_df, processor):
    """Export processed data as JSON files for the dashboard."""
    
    logger.info("Exporting JSON files...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Export detections
    detections_file = OUTPUT_DIR / "detections.json"
    with open(detections_file, 'w') as f:
        json.dump(detections_df.to_dict('records'), f)
    logger.info(f"✓ Exported {len(detections_df)} detection records to {detections_file}")
    
    # Export environmental
    environmental_file = OUTPUT_DIR / "environmental.json"
    with open(environmental_file, 'w') as f:
        json.dump(environmental_df.to_dict('records'), f)
    logger.info(f"✓ Exported {len(environmental_df)} environmental records to {environmental_file}")
    
    # Generate species metadata
    _, type_mapping = processor.load_column_mapping()
    species_list = []
    for short_name, info in type_mapping.items():
        if info['type'] in ['bio', 'anthro']:
            total_detections = detections_df[short_name].sum() if short_name in detections_df.columns else 0
            species_list.append({
                'short_name': short_name,
                'long_name': info['long_name'],
                'category': info['type'],
                'total_detections': int(total_detections)
            })
    
    species_file = OUTPUT_DIR / "species.json"
    with open(species_file, 'w') as f:
        json.dump(species_list, f, indent=2)
    logger.info(f"✓ Exported {len(species_list)} species definitions to {species_file}")
    
    # Generate stations metadata
    stations_list = []
    for station in processor.stations_of_interest:
        station_data = detections_df[detections_df['station'] == station]
        if len(station_data) > 0:
            stations_list.append({
                'id': station,
                'name': f"Station {station}",
                'coordinates': {'lat': 0, 'lon': 0},  # TODO: Get real coordinates
                'years': sorted(station_data['year'].unique().tolist()),
                'data_types': ['detections', 'environmental']
            })
    
    stations_file = OUTPUT_DIR / "stations.json"
    with open(stations_file, 'w') as f:
        json.dump(stations_list, f, indent=2)
    logger.info(f"✓ Exported {len(stations_list)} station definitions to {stations_file}")
    
    # Generate metadata
    metadata = generate_metadata(detections_df, environmental_df, species_list, stations_list)
    metadata_file = OUTPUT_DIR / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"✓ Exported metadata to {metadata_file}")


def main():
    """Main processing function."""
    
    logger.info("Starting MBON dashboard data processing...")
    logger.info("=" * 60)
    
    try:
        # Create Excel processor
        processor = MBONExcelProcessor(
            raw_data_dir="data/cdn/raw-data",
            years_of_interest=["2018", "2021"],
            stations_of_interest=["9M", "14M", "37M"]
        )
        
        # Process detection files
        logger.info("STEP 1: Processing detection files...")
        detections_df = processor.process_all_detection_files()
        
        # Process environmental files  
        logger.info("STEP 2: Processing environmental files...")
        environmental_df = processor.process_environmental_files()
        
        # Export JSON files
        logger.info("STEP 3: Exporting JSON files...")
        export_json_files(detections_df, environmental_df, processor)
        
        logger.info("=" * 60)
        logger.info("✅ Dashboard data processing completed successfully!")
        logger.info(f"📁 Files saved to: {OUTPUT_DIR}")
        logger.info(f"📝 Log saved to: {LOG_FILE}")
        
    except Exception as e:
        logger.error(f"❌ Dashboard data processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Step 3: Delete examples.py

The `examples.py` file is clearly superseded by the new consolidated approach:

```bash
# Remove the legacy file
rm scripts/examples.py
```

---

## Step 4: Update Import Statements

Any existing scripts that import from the old locations need to be updated:

```python
# OLD
from scripts.dashboard_prep.process_excel_to_json import load_column_mapping

# NEW  
from mbon_analysis.core.excel_processor import load_column_mapping
```

---

## Step 5: Add Tests for the New Module

Create `tests/test_excel_processor.py`:

```python
"""
Tests for the Excel processor module.
"""

import pytest
import pandas as pd
from pathlib import Path
from mbon_analysis.core.excel_processor import MBONExcelProcessor


class TestMBONExcelProcessor:
    
    def test_extract_metadata_from_filename(self):
        """Test metadata extraction from various filename patterns."""
        processor = MBONExcelProcessor()
        
        test_cases = [
            (Path("data/2018/Master_Manual_9M_2h_2018.xlsx"), ("2018", "9M")),
            (Path("data/2021/Master_Manual_14M_2h_2021.xlsx"), ("2021", "14M")),
            (Path("data/2021/Master_9M_Temp_2021.xlsx"), ("2021", "9M")),
            (Path("data/2018/Master_37M_Depth_2018.xlsx"), ("2018", "37M")),
        ]
        
        for filepath, expected in test_cases:
            year, station = processor.extract_metadata_from_filename(filepath)
            assert (year, station) == expected, f"Failed for {filepath}"
    
    def test_load_column_mapping(self):
        """Test column mapping loading."""
        processor = MBONExcelProcessor()
        
        # This will only work if the actual files exist
        try:
            name_mapping, type_mapping = processor.load_column_mapping()
            
            assert isinstance(name_mapping, dict)
            assert isinstance(type_mapping, dict)
            assert len(name_mapping) > 0
            assert len(type_mapping) > 0
            
            # Check for critical columns
            assert "date" in name_mapping
            assert "time" in name_mapping
            
        except FileNotFoundError:
            pytest.skip("Column mapping file not found - skipping test")
    
    def test_processor_configuration(self):
        """Test processor initialization with custom configuration."""
        processor = MBONExcelProcessor(
            raw_data_dir="custom/path",
            years_of_interest=["2019", "2020"],
            stations_of_interest=["1M", "2M"]
        )
        
        assert processor.raw_data_dir == Path("custom/path")
        assert processor.years_of_interest == ["2019", "2020"]
        assert processor.stations_of_interest == ["1M", "2M"]
```

---

## Migration Steps

### **Phase 0: Preparation (30 minutes)**

1. **Backup current working files**:
   ```bash
   cp scripts/dashboard_prep/process_excel_to_json.py scripts/dashboard_prep/process_excel_to_json.py.backup
   cp scripts/examples.py scripts/examples.py.backup
   ```

2. **Make sure current system works**:
   ```bash
   npm run process-data  # Test current system
   ```

### **Phase 1: Create New Module (1 hour)**

3. **Create the Excel processor**:
   ```bash
   # Create the new module file
   touch mbon_analysis/core/excel_processor.py
   ```

4. **Copy the code** from Step 1 above into the new file

5. **Test the new module**:
   ```bash
   cd mbon_analysis/core
   python excel_processor.py  # Run the example at the bottom
   ```

### **Phase 2: Update Main Script (30 minutes)**

6. **Replace process_excel_to_json.py** with the simplified version from Step 2

7. **Test the updated script**:
   ```bash
   npm run process-data  # Should work the same as before
   ```

### **Phase 3: Cleanup (30 minutes)**

8. **Delete legacy file**:
   ```bash
   rm scripts/examples.py
   ```

9. **Add tests**:
   ```bash
   mkdir -p tests
   # Copy test code from Step 5
   uv run pytest tests/test_excel_processor.py -v
   ```

10. **Update package.json** to include the new test:
    ```json
    "scripts": {
      "test:excel-processor": "uv run python mbon_analysis/core/excel_processor.py"
    }
    ```

---

## Validation Checklist

After migration, verify:

- [ ] `npm run process-data` still works
- [ ] Same JSON files are generated (compare file sizes and record counts)
- [ ] No import errors in any scripts
- [ ] New Excel processor can run independently
- [ ] Tests pass for the new module

---

## Benefits After Consolidation

1. **Single source of truth** for Excel processing logic
2. **Reusable** by both dashboard scripts and analysis scripts
3. **Testable** - Excel processing logic can be tested independently
4. **Better error handling** - Centralized logging and error handling
5. **Configuration-driven** - Easy to change years/stations without code changes
6. **Less duplication** - Eliminate 200+ lines of duplicated code

---

## Risk Mitigation

**Low Risk**: This consolidation moves code but doesn't change the core logic significantly.

**Backup Strategy**: Keep `.backup` files until you're confident the new system works.

**Rollback Plan**: If anything breaks, copy the backup files back and you're restored.

**Testing**: The new module includes example code that validates it works correctly.

This consolidation will make the Phase 1 error handling improvements much cleaner to implement, since you'll be working with a single, well-organized codebase instead of scattered duplicate functions.