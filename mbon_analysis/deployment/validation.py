"""
CDN deployment validation utilities.

Validates deployments by checking file accessibility,
content integrity, and performance metrics.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import requests


@dataclass
class ValidationResult:
    """Result of deployment validation."""
    success: bool
    total_files: int = 0
    files_validated: int = 0
    files_failed: int = 0
    average_response_time_ms: float = 0.0
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    def get_summary(self) -> str:
        """Get a human-readable summary of validation results."""
        return (
            f"Validation: {self.files_validated}/{self.total_files} files OK, "
            f"{self.files_failed} failed, "
            f"avg response {self.average_response_time_ms:.0f}ms"
        )


def validate_deployment(
    base_url: str,
    expected_files: List[str],
    timeout: float = 10.0,
    validate_content: bool = True
) -> ValidationResult:
    """
    Validate CDN deployment by checking file accessibility and integrity.
    
    Args:
        base_url: Base URL of the CDN
        expected_files: List of filenames that should be accessible
        timeout: Request timeout in seconds
        validate_content: Whether to validate JSON content structure
        
    Returns:
        ValidationResult with validation details
    """
    result = ValidationResult(
        success=False,
        total_files=len(expected_files)
    )
    
    response_times = []
    
    for filename in expected_files:
        file_url = f"{base_url.rstrip('/')}/views/{filename}"
        
        try:
            start_time = time.time()
            response = requests.get(file_url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            response_times.append(response_time)
            
            if response.status_code == 200:
                if validate_content and filename.endswith('.json'):
                    # Validate JSON structure
                    try:
                        json_data = response.json()
                        validation_errors = _validate_json_structure(filename, json_data)
                        if validation_errors:
                            result.warnings.extend(validation_errors)
                    except json.JSONDecodeError:
                        result.errors.append(f"{filename}: Invalid JSON content")
                        result.files_failed += 1
                        continue
                
                result.files_validated += 1
            else:
                result.errors.append(f"{filename}: HTTP {response.status_code}")
                result.files_failed += 1
                
        except requests.RequestException as e:
            result.errors.append(f"{filename}: {str(e)}")
            result.files_failed += 1
    
    # Calculate average response time
    if response_times:
        result.average_response_time_ms = sum(response_times) / len(response_times)
    
    # Determine overall success
    result.success = result.files_failed == 0 and result.files_validated == result.total_files
    
    return result


def validate_manifest_accessibility(base_url: str, timeout: float = 10.0) -> bool:
    """
    Check if the manifest file is accessible.
    
    Args:
        base_url: Base URL of the CDN
        timeout: Request timeout in seconds
        
    Returns:
        True if manifest is accessible and valid
    """
    manifest_url = f"{base_url.rstrip('/')}/views/manifest.json"
    
    try:
        response = requests.get(manifest_url, timeout=timeout)
        if response.status_code == 200:
            # Try to parse as JSON
            manifest_data = response.json()
            return 'files' in manifest_data and 'generated_at' in manifest_data
        return False
    except (requests.RequestException, json.JSONDecodeError):
        return False


def validate_performance(
    base_url: str,
    filenames: List[str],
    max_response_time_ms: float = 2000.0,
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    Validate performance characteristics of CDN deployment.
    
    Args:
        base_url: Base URL of the CDN
        filenames: List of files to test
        max_response_time_ms: Maximum acceptable response time
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with performance metrics
    """
    results = {
        'files_tested': len(filenames),
        'response_times': {},
        'slow_files': [],
        'average_response_time_ms': 0.0,
        'max_response_time_ms': 0.0,
        'performance_ok': False
    }
    
    response_times = []
    
    for filename in filenames:
        file_url = f"{base_url.rstrip('/')}/views/{filename}"
        
        try:
            start_time = time.time()
            response = requests.get(file_url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000
            
            response_times.append(response_time)
            results['response_times'][filename] = response_time
            
            if response_time > max_response_time_ms:
                results['slow_files'].append({
                    'filename': filename,
                    'response_time_ms': response_time
                })
                
        except requests.RequestException:
            # Skip failed requests for performance testing
            results['response_times'][filename] = None
    
    if response_times:
        results['average_response_time_ms'] = sum(response_times) / len(response_times)
        results['max_response_time_ms'] = max(response_times)
        results['performance_ok'] = results['average_response_time_ms'] <= max_response_time_ms
    
    return results


def _validate_json_structure(filename: str, json_data: Dict[str, Any]) -> List[str]:
    """
    Validate the structure of view JSON files.
    
    Args:
        filename: Name of the file being validated
        json_data: Parsed JSON data
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Common validation for all view files
    if 'metadata' not in json_data:
        errors.append(f"{filename}: Missing 'metadata' field")
    elif isinstance(json_data['metadata'], dict):
        if 'generated_at' not in json_data['metadata']:
            errors.append(f"{filename}: Missing 'metadata.generated_at' field")
    
    # Specific validation based on filename
    if filename == 'station_overview.json':
        if 'stations' not in json_data:
            errors.append(f"{filename}: Missing 'stations' field")
        elif not isinstance(json_data['stations'], list):
            errors.append(f"{filename}: 'stations' should be a list")
    
    elif filename == 'species_timeline.json':
        if 'species_timeline' not in json_data:
            errors.append(f"{filename}: Missing 'species_timeline' field")
        elif not isinstance(json_data['species_timeline'], list):
            errors.append(f"{filename}: 'species_timeline' should be a list")
        
        if 'temporal_aggregation' not in json_data:
            errors.append(f"{filename}: Missing 'temporal_aggregation' field")
    
    return errors