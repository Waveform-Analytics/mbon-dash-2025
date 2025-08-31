"""Dashboard testing utilities for MBON project."""

import json
import requests
from pathlib import Path
import logging
from typing import Dict, Any, Optional


class DashboardDataTester:
    """Test dashboard data access and API endpoints."""
    
    def __init__(self, data_root: Path, verbose: bool = False):
        """Initialize the dashboard tester.
        
        Args:
            data_root: Path to the data directory
            verbose: Enable verbose logging
        """
        self.data_root = data_root
        self.verbose = verbose
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def test_view_file_access(self) -> Dict[str, Any]:
        """Test that view files can be accessed from expected locations."""
        # Define possible view file locations
        possible_view_paths = [
            self.data_root / "views",  # Top-level location
            Path(__file__).parent.parent.parent / "data" / "views",  # Legacy python/data location
        ]
        
        # Expected view files
        expected_views = [
            "stations.json",
            "datasets_summary.json", 
            "indices_reference.json",
            "project_metadata.json",
            "acoustic_indices_distributions.json"
        ]
        
        self.logger.info("Testing view file accessibility...")
        
        results = {}
        
        for view_path in possible_view_paths:
            self.logger.info(f"Checking location: {view_path}")
            
            if not view_path.exists():
                self.logger.warning(f"  Directory does not exist: {view_path}")
                continue
            
            view_results = {}
            for view_file in expected_views:
                file_path = view_path / view_file
                if file_path.exists():
                    try:
                        # Try to read and parse the JSON
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        
                        file_size_kb = file_path.stat().st_size / 1024
                        view_results[view_file] = {
                            "exists": True,
                            "readable": True,
                            "size_kb": round(file_size_kb, 2),
                            "has_data": len(str(data)) > 0
                        }
                        self.logger.info(f"  ✅ {view_file}: {file_size_kb:.2f} KB")
                        
                    except Exception as e:
                        view_results[view_file] = {
                            "exists": True,
                            "readable": False,
                            "error": str(e)
                        }
                        self.logger.error(f"  ❌ {view_file}: Error reading - {e}")
                else:
                    view_results[view_file] = {
                        "exists": False,
                        "readable": False
                    }
                    self.logger.warning(f"  ⚠️  {view_file}: Not found")
            
            results[str(view_path)] = view_results
        
        return results
    
    def test_dashboard_api_access(self) -> Dict[str, Any]:
        """Test that the dashboard API can access view files."""
        self.logger.info("Testing dashboard API access...")
        
        # Test API endpoints
        base_url = "http://localhost:3000"
        api_endpoints = [
            "/api/views/stations.json",
            "/api/views/datasets_summary.json",
            "/api/views/indices_reference.json",
            "/api/views/project_metadata.json",
            "/api/views/acoustic_indices_distributions.json"
        ]
        
        results = {}
        
        for endpoint in api_endpoints:
            try:
                self.logger.info(f"Testing endpoint: {endpoint}")
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results[endpoint] = {
                        "status": response.status_code,
                        "accessible": True,
                        "has_data": len(str(data)) > 0,
                        "content_type": response.headers.get('content-type', 'unknown')
                    }
                    self.logger.info(f"  ✅ {endpoint}: Accessible")
                else:
                    results[endpoint] = {
                        "status": response.status_code,
                        "accessible": False,
                        "error": f"HTTP {response.status_code}"
                    }
                    self.logger.error(f"  ❌ {endpoint}: HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                results[endpoint] = {
                    "status": "N/A",
                    "accessible": False,
                    "error": "Dashboard not running"
                }
                self.logger.warning(f"  ⚠️  {endpoint}: Dashboard not running")
            except Exception as e:
                results[endpoint] = {
                    "status": "N/A", 
                    "accessible": False,
                    "error": str(e)
                }
                self.logger.error(f"  ❌ {endpoint}: Error - {e}")
        
        return results
    
    def print_summary(self, file_results: Dict[str, Any], api_results: Optional[Dict[str, Any]] = None):
        """Print a summary of test results."""
        print("\n" + "="*60)
        print("DASHBOARD DATA ACCESS TEST SUMMARY")
        print("="*60)
        
        # File access summary
        print("\n📁 FILE ACCESS RESULTS:")
        for location, views in file_results.items():
            print(f"\nLocation: {location}")
            accessible_count = sum(1 for v in views.values() if v.get("exists", False))
            total_count = len(views)
            print(f"  Accessible: {accessible_count}/{total_count} view files")
            
            for view_name, result in views.items():
                if result.get("exists", False):
                    if result.get("readable", False):
                        size = result.get("size_kb", 0)
                        print(f"    ✅ {view_name}: {size} KB")
                    else:
                        print(f"    ❌ {view_name}: Not readable")
                else:
                    print(f"    ⚠️  {view_name}: Not found")
        
        # API access summary
        print("\n🌐 API ACCESS RESULTS:")
        if api_results:
            accessible_count = sum(1 for r in api_results.values() if r.get("accessible", False))
            total_count = len(api_results)
            print(f"  Accessible: {accessible_count}/{total_count} API endpoints")
            
            for endpoint, result in api_results.items():
                if result.get("accessible", False):
                    print(f"    ✅ {endpoint}")
                else:
                    error = result.get("error", "Unknown error")
                    print(f"    ❌ {endpoint}: {error}")
        else:
            print("  No API results available")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        # Check if data is in both locations
        has_top_level = any("data/views" in loc for loc in file_results.keys())
        has_legacy = any("python/data/views" in loc for loc in file_results.keys())
        
        if has_top_level and has_legacy:
            print("  ✅ Data exists in both locations - migration successful")
            print("  💡 Consider removing legacy python/data directory")
        elif has_top_level:
            print("  ✅ Data exists in top-level location - migration successful")
        elif has_legacy:
            print("  ⚠️  Data only exists in legacy location - migration may be needed")
        else:
            print("  ❌ No data found in expected locations")
        
        # Check API accessibility
        if api_results:
            api_success_rate = sum(1 for r in api_results.values() if r.get("accessible", False)) / len(api_results)
            if api_success_rate > 0.8:
                print("  ✅ Dashboard API is working correctly")
            elif api_success_rate > 0:
                print("  ⚠️  Some API endpoints are not accessible")
            else:
                print("  ❌ Dashboard API is not accessible - check if dashboard is running")
