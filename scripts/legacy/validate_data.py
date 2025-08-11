#!/usr/bin/env python3
"""
Data validation script for MBON Dashboard
Validates processed JSON data for completeness and integrity
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import sys

class DataValidator:
    def __init__(self, data_dir: str = "data/cdn"):
        self.data_dir = Path(data_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_file_exists(self, filename: str) -> bool:
        """Check if a required file exists"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            self.errors.append(f"Missing required file: {filename}")
            return False
        if filepath.stat().st_size == 0:
            self.errors.append(f"Empty file: {filename}")
            return False
        return True
    
    def validate_json_structure(self, filename: str) -> Dict[str, Any]:
        """Validate JSON file can be parsed"""
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {filename}: {e}")
            return {}
        except Exception as e:
            self.errors.append(f"Error reading {filename}: {e}")
            return {}
    
    def validate_detections(self) -> None:
        """Validate detection data structure and content"""
        if not self.validate_file_exists("detections.json"):
            return
            
        data = self.validate_json_structure("detections.json")
        if not data:
            return
            
        # Check expected structure
        if not isinstance(data, list):
            self.errors.append("detections.json should be a list")
            return
            
        if len(data) == 0:
            self.warnings.append("detections.json is empty")
            return
            
        # Validate each detection record
        required_fields = ['station', 'year', 'date_time']
        for i, record in enumerate(data[:10]):  # Check first 10 records
            for field in required_fields:
                if field not in record:
                    self.errors.append(f"Detection record {i} missing field: {field}")
                    
        # Check stations and years match expected values
        stations = set(d.get('station') for d in data if 'station' in d)
        years = set(d.get('year') for d in data if 'year' in d)
        
        expected_stations = {'9M', '14M', '37M'}
        expected_years = {2018, 2021}
        
        if stations - expected_stations:
            self.warnings.append(f"Unexpected stations: {stations - expected_stations}")
        if years - expected_years:
            self.warnings.append(f"Unexpected years: {years - expected_years}")
            
        print(f"✓ Detections: {len(data)} records from {len(stations)} stations")
    
    def validate_environmental(self) -> None:
        """Validate environmental data"""
        if not self.validate_file_exists("environmental.json"):
            return
            
        data = self.validate_json_structure("environmental.json")
        if not data:
            return
            
        if not isinstance(data, list):
            self.errors.append("environmental.json should be a list")
            return
            
        # Check for temperature and depth fields
        has_temp = any('temperature' in d for d in data[:100] if isinstance(d, dict))
        has_depth = any('depth' in d for d in data[:100] if isinstance(d, dict))
        
        if not has_temp:
            self.warnings.append("No temperature data found in environmental.json")
        if not has_depth:
            self.warnings.append("No depth data found in environmental.json")
            
        print(f"✓ Environmental: {len(data)} records")
    
    def validate_acoustic(self) -> None:
        """Validate acoustic indices data"""
        if not self.validate_file_exists("acoustic.json"):
            return
            
        data = self.validate_json_structure("acoustic.json")
        if not data:
            return
            
        if not isinstance(data, list):
            self.errors.append("acoustic.json should be a list")
            return
            
        if len(data) == 0:
            self.warnings.append("acoustic.json is empty - rmsSPL data may be missing")
            
        print(f"✓ Acoustic: {len(data)} records")
    
    def validate_metadata(self) -> None:
        """Validate metadata file"""
        if not self.validate_file_exists("metadata.json"):
            return
            
        data = self.validate_json_structure("metadata.json")
        if not data:
            return
            
        expected_fields = ['lastUpdated', 'dataStats']
        for field in expected_fields:
            if field not in data:
                self.warnings.append(f"metadata.json missing field: {field}")
                
        if 'dataStats' in data:
            stats = data['dataStats']
            print(f"✓ Metadata: {stats.get('totalRecords', 0)} total records, "
                  f"{stats.get('stationCount', 0)} stations, "
                  f"{stats.get('speciesCount', 0)} species")
    
    def validate_stations(self) -> None:
        """Validate station data"""
        if not self.validate_file_exists("stations.json"):
            return
            
        data = self.validate_json_structure("stations.json")
        if not data:
            return
            
        if not isinstance(data, list):
            self.errors.append("stations.json should be a list")
            return
            
        expected_stations = ['9M', '14M', '37M']
        station_ids = [s.get('id') for s in data if isinstance(s, dict)]
        
        for expected in expected_stations:
            if expected not in station_ids:
                self.errors.append(f"Missing expected station: {expected}")
                
        print(f"✓ Stations: {len(data)} stations configured")
    
    def validate_species(self) -> None:
        """Validate species list"""
        if not self.validate_file_exists("species.json"):
            return
            
        data = self.validate_json_structure("species.json")
        if not data:
            return
            
        if not isinstance(data, list):
            self.errors.append("species.json should be a list")
            return
            
        print(f"✓ Species: {len(data)} species identified")
    
    def run_validation(self) -> bool:
        """Run all validation checks"""
        print("\n" + "="*50)
        print("MBON Dashboard Data Validation")
        print("="*50 + "\n")
        
        # Check data directory exists
        if not self.data_dir.exists():
            print(f"❌ Data directory not found: {self.data_dir}")
            return False
            
        # Run all validations
        self.validate_detections()
        self.validate_environmental()
        self.validate_acoustic()
        self.validate_metadata()
        self.validate_stations()
        self.validate_species()
        
        # Report results
        print("\n" + "-"*50)
        
        if self.errors:
            print(f"\n❌ Found {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            print("\n✅ All data validation checks passed!")
            
        print("\n" + "="*50 + "\n")
        
        return len(self.errors) == 0

if __name__ == "__main__":
    validator = DataValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)