#!/usr/bin/env python3
"""Pipeline validation script - quick health check for the entire data pipeline."""

import os
import sys
from pathlib import Path
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

# Add the project root to the path so we can import mbon_analysis
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mbon_analysis.data.loaders import create_loader


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline_validation.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


class PipelineValidator:
    """Validate the entire data pipeline."""
    
    def __init__(self):
        self.logger = setup_logging()
        self.errors = []
        self.warnings = []
        # Data is at project root, not in python folder
        self.data_root = project_root.parent / "data"
        self.loader = create_loader(self.data_root)
    
    def log_error(self, message: str):
        """Log an error."""
        self.errors.append(message)
        self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        self.logger.warning(message)
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def validate_environment(self) -> bool:
        """Validate required environment variables."""
        self.log_info("🔍 Validating environment variables...")
        
        required_vars = [
            'CLOUDFLARE_R2_ACCOUNT_ID',
            'CLOUDFLARE_R2_ACCESS_KEY_ID',
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
            'CLOUDFLARE_R2_BUCKET_NAME',
            'CLOUDFLARE_R2_ENDPOINT',
            'NEXT_PUBLIC_CDN_BASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_error(f"Missing environment variables: {missing_vars}")
            return False
        
        self.log_info("✅ All required environment variables are present")
        return True
    
    def validate_directory_structure(self) -> bool:
        """Validate expected directory structure exists."""
        self.log_info("🔍 Validating directory structure...")
        
        required_dirs = [
            "raw",
            "raw/metadata",
            "raw/indices",
            "processed",
            "views"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.data_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.log_error(f"Missing directories: {missing_dirs}")
            return False
        
        # Check for year directories
        for year in [2018, 2021]:
            year_dir = self.data_root / "raw" / str(year)
            if not year_dir.exists():
                self.log_warning(f"Year directory missing: {year}")
            else:
                for subdir in ["detections", "environmental"]:
                    subpath = year_dir / subdir
                    if not subpath.exists():
                        self.log_warning(f"Missing subdirectory: {subpath}")
        
        self.log_info("✅ Directory structure validation complete")
        return True
    
    def validate_metadata_files(self) -> bool:
        """Validate core metadata files exist and are readable."""
        self.log_info("🔍 Validating metadata files...")
        
        success = True
        
        # Test species mapping
        try:
            species_mapping = self.loader.load_species_mapping()
            self.log_info(f"✅ Species mapping loaded: {len(species_mapping)} species")
        except Exception as e:
            self.log_error(f"Failed to load species mapping: {e}")
            success = False
        
        # Test deployment metadata
        try:
            deployment_metadata = self.loader.load_deployment_metadata()
            self.log_info(f"✅ Deployment metadata loaded: {len(deployment_metadata)} records")
        except Exception as e:
            self.log_error(f"Failed to load deployment metadata: {e}")
            success = False
        
        # Test indices reference
        try:
            indices_reference = self.loader.load_indices_reference()
            self.log_info(f"✅ Indices reference loaded: {len(indices_reference)} indices")
        except Exception as e:
            self.log_error(f"Failed to load indices reference: {e}")
            success = False
        
        return success
    
    def validate_data_availability(self) -> bool:
        """Validate core data files are available."""
        self.log_info("🔍 Validating data availability...")
        
        # Check available stations and years
        try:
            stations = self.loader.get_available_stations()
            years = self.loader.get_available_years()
            
            self.log_info(f"📊 Available stations: {stations}")
            self.log_info(f"📊 Available years: {years}")
            
            if not stations:
                self.log_error("No stations found")
                return False
            
            if not years:
                self.log_error("No years found")
                return False
            
            # Test loading some data files
            for station in stations[:2]:  # Test first 2 stations
                for year in years[:2]:     # Test first 2 years
                    try:
                        detection_data = self.loader.load_detection_data(station, year)
                        self.log_info(f"✅ Detection data {station}/{year}: {len(detection_data)} records")
                    except Exception as e:
                        self.log_warning(f"Could not load detection data for {station}/{year}: {e}")
                    
                    try:
                        env_data = self.loader.load_environmental_data(station, year, "Temp")
                        self.log_info(f"✅ Environmental data {station}/{year}: {len(env_data)} records")
                    except Exception as e:
                        self.log_warning(f"Could not load environmental data for {station}/{year}: {e}")
            
            # Test acoustic indices
            for station in ["9M", "14M"]:  # Known stations with indices
                for bandwidth in ["FullBW", "8kHz"]:
                    try:
                        indices_data = self.loader.load_acoustic_indices(station, bandwidth)
                        self.log_info(f"✅ Acoustic indices {station}/{bandwidth}: {len(indices_data)} records")
                    except Exception as e:
                        self.log_warning(f"Could not load acoustic indices for {station}/{bandwidth}: {e}")
            
        except Exception as e:
            self.log_error(f"Failed to check data availability: {e}")
            return False
        
        return True
    
    def validate_view_files(self) -> bool:
        """Validate view files exist and are well-formed."""
        self.log_info("🔍 Validating view files...")
        
        views_dir = self.data_root / "views"
        if not views_dir.exists():
            self.log_error("Views directory does not exist")
            return False
        
        expected_view_files = [
            "stations.json",
            "datasets_summary.json",
            "indices_reference.json",
            "heatmap.json",
            "acoustic_indices_distributions.json",
            "project_metadata.json"
        ]
        
        success = True
        for filename in expected_view_files:
            view_file = views_dir / filename
            if not view_file.exists():
                self.log_warning(f"View file missing: {filename}")
                continue
            
            try:
                with open(view_file) as f:
                    data = json.load(f)
                
                file_size = view_file.stat().st_size
                size_limit = 50 * 1024  # 50KB
                
                if file_size > size_limit:
                    self.log_warning(f"View file {filename} is {file_size} bytes (exceeds {size_limit} byte limit)")
                else:
                    self.log_info(f"✅ View file {filename}: {file_size} bytes, valid JSON")
                    
            except json.JSONDecodeError as e:
                self.log_error(f"Invalid JSON in {filename}: {e}")
                success = False
            except Exception as e:
                self.log_error(f"Error reading {filename}: {e}")
                success = False
        
        return success
    
    def validate_processed_files(self) -> bool:
        """Validate processed data files."""
        self.log_info("🔍 Validating processed files...")
        
        processed_dir = self.data_root / "processed"
        if not processed_dir.exists():
            self.log_warning("Processed directory does not exist")
            return True  # Not critical for basic operation
        
        # Check for compiled files
        compiled_files = [
            "compiled_detections.json",
            "compiled_indices.json"
        ]
        
        for filename in compiled_files:
            file_path = processed_dir / filename
            if file_path.exists():
                try:
                    file_size = file_path.stat().st_size
                    # Test that it's valid JSON without loading the whole thing
                    with open(file_path) as f:
                        first_char = f.read(1)
                        if first_char not in ['{', '[']:
                            raise ValueError("Not valid JSON")
                    
                    self.log_info(f"✅ Processed file {filename}: {file_size} bytes")
                except Exception as e:
                    self.log_error(f"Error with processed file {filename}: {e}")
                    return False
            else:
                self.log_info(f"ℹ️  Processed file {filename} not found (may not be generated yet)")
        
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "status": "PASS" if len(self.errors) == 0 else "FAIL"
        }
    
    def run_validation(self) -> bool:
        """Run complete pipeline validation."""
        self.log_info("🚀 Starting pipeline validation...")
        self.log_info(f"📁 Data root: {self.data_root}")
        
        validations = [
            ("Environment", self.validate_environment),
            ("Directory Structure", self.validate_directory_structure), 
            ("Metadata Files", self.validate_metadata_files),
            ("Data Availability", self.validate_data_availability),
            ("View Files", self.validate_view_files),
            ("Processed Files", self.validate_processed_files),
        ]
        
        results = {}
        for name, validator_func in validations:
            self.log_info(f"\n--- {name} Validation ---")
            try:
                results[name] = validator_func()
            except Exception as e:
                self.log_error(f"Validation {name} failed with exception: {e}")
                results[name] = False
        
        # Generate summary
        self.log_info("\n" + "="*50)
        self.log_info("🔍 VALIDATION SUMMARY")
        self.log_info("="*50)
        
        for name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log_info(f"{status} {name}")
        
        self.log_info(f"\n📊 Total Errors: {len(self.errors)}")
        self.log_info(f"⚠️  Total Warnings: {len(self.warnings)}")
        
        overall_success = len(self.errors) == 0
        overall_status = "✅ PIPELINE HEALTHY" if overall_success else "❌ PIPELINE HAS ISSUES"
        self.log_info(f"\n{overall_status}")
        
        # Save report
        report = self.generate_report()
        report_file = Path("pipeline_validation_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_info(f"📄 Report saved to: {report_file}")
        
        return overall_success


def main():
    """Main entry point."""
    validator = PipelineValidator()
    success = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()