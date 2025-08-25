"""
Tests for the data validation script.
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_validate_good_json_file():
    """Test validation passes for good JSON file."""
    from scripts.utils.validate_processed_data import validate_json_file
    
    # Create temporary good JSON file
    good_data = [{"id": 1, "value": "test"} for _ in range(1000)]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(good_data, f)
        temp_path = Path(f.name)
    
    try:
        result = validate_json_file(temp_path, expected_records=500)
        assert result == True
    finally:
        temp_path.unlink()  # Clean up

def test_validate_empty_json_file():
    """Test validation fails for empty JSON file."""
    from scripts.utils.validate_processed_data import validate_json_file
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([], f)
        temp_path = Path(f.name)
    
    try:
        result = validate_json_file(temp_path, expected_records=100)
        assert result == False
    finally:
        temp_path.unlink()

def test_validate_malformed_json_file():
    """Test validation fails for malformed JSON."""
    from scripts.utils.validate_processed_data import validate_json_file
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json content")
        temp_path = Path(f.name)
    
    try:
        result = validate_json_file(temp_path)
        assert result == False
    finally:
        temp_path.unlink()


# Manual test runner (since pytest may not be available)
if __name__ == "__main__":
    print("Testing validation script functions...")
    print("=" * 50)
    
    try:
        print("Testing good JSON file validation...")
        test_validate_good_json_file()
        print("  ✓ Good JSON validation test passed")
    except Exception as e:
        print(f"  ✗ Good JSON validation test failed: {e}")
    
    try:
        print("Testing empty JSON file validation...")
        test_validate_empty_json_file()
        print("  ✓ Empty JSON validation test passed")
    except Exception as e:
        print(f"  ✗ Empty JSON validation test failed: {e}")
    
    try:
        print("Testing malformed JSON file validation...")
        test_validate_malformed_json_file()
        print("  ✓ Malformed JSON validation test passed")
    except Exception as e:
        print(f"  ✗ Malformed JSON validation test failed: {e}")
    
    print("\n✅ All validation script tests completed!")