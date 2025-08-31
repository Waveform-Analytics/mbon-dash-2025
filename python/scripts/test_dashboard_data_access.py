#!/usr/bin/env python3
"""Test script to verify dashboard data access after migration.

This script tests that the dashboard can still access view files
after migrating data to the top-level directory.
"""

import json
import requests
import time
from pathlib import Path
import sys
import logging


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def test_view_file_access():
    """Test that view files can be accessed from expected locations."""
    logger = logging.getLogger(__name__)
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Define possible view file locations
    possible_view_paths = [
        project_root / "data" / "views",  # New top-level location
        script_dir.parent / "data" / "views",  # Legacy python/data location
    ]
    
    # Expected view files
    expected_views = [
        "stations.json",
        "datasets_summary.json", 
        "indices_reference.json",
        "project_metadata.json",
        "acoustic_indices_distributions.json"
    ]
    
    logger.info("Testing view file accessibility...")
    
    results = {}
    
    for view_path in possible_view_paths:
        logger.info(f"Checking location: {view_path}")
        
        if not view_path.exists():
            logger.warning(f"  Directory does not exist: {view_path}")
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
                    logger.info(f"  ✅ {view_file}: {file_size_kb:.2f} KB")
                    
                except Exception as e:
                    view_results[view_file] = {
                        "exists": True,
                        "readable": False,
                        "error": str(e)
                    }
                    logger.error(f"  ❌ {view_file}: Error reading - {e}")
            else:
                view_results[view_file] = {
                    "exists": False,
                    "readable": False
                }
                logger.warning(f"  ⚠️  {view_file}: Not found")
        
        results[str(view_path)] = view_results
    
    return results


def test_dashboard_api_access():
    """Test that the dashboard API can access view files."""
    logger = logging.getLogger(__name__)
    
    # Start dashboard if not running
    logger.info("Testing dashboard API access...")
    
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
            logger.info(f"Testing endpoint: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results[endpoint] = {
                    "status": response.status_code,
                    "accessible": True,
                    "has_data": len(str(data)) > 0,
                    "content_type": response.headers.get('content-type', 'unknown')
                }
                logger.info(f"  ✅ {endpoint}: Accessible")
            else:
                results[endpoint] = {
                    "status": response.status_code,
                    "accessible": False,
                    "error": f"HTTP {response.status_code}"
                }
                logger.error(f"  ❌ {endpoint}: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            results[endpoint] = {
                "status": "N/A",
                "accessible": False,
                "error": "Dashboard not running"
            }
            logger.warning(f"  ⚠️  {endpoint}: Dashboard not running")
        except Exception as e:
            results[endpoint] = {
                "status": "N/A", 
                "accessible": False,
                "error": str(e)
            }
            logger.error(f"  ❌ {endpoint}: Error - {e}")
    
    return results


def print_summary(file_results, api_results):
    """Print a summary of test results."""
    logger = logging.getLogger(__name__)
    
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


def main():
    """Main test function."""
    logger = setup_logging()
    
    print("🧪 Testing Dashboard Data Access")
    print("="*50)
    
    # Test file access
    file_results = test_view_file_access()
    
    # Test API access
    api_results = test_dashboard_api_access()
    
    # Print summary
    print_summary(file_results, api_results)
    
    # Return appropriate exit code
    if not file_results:
        logger.error("No view files found in any location")
        sys.exit(1)
    
    # Check if at least one location has data
    has_data = any(
        any(view.get("exists", False) for view in views.values())
        for views in file_results.values()
    )
    
    if not has_data:
        logger.error("No view files found in any location")
        sys.exit(1)
    
    logger.info("Test completed successfully")


if __name__ == "__main__":
    main()
