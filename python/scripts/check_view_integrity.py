#!/usr/bin/env python3
"""
Quick script to check view data integrity and detect potential simulated data.

This script is designed to catch the problem where fake/simulated data accidentally 
gets mixed into your marine science dashboard views instead of real data from your 
Excel/CSV files.

It looks for patterns that suggest:
1. Computer-generated fake data (too perfect patterns, obvious placeholders)
2. Development/test data that wasn't removed (strings like "TODO", numbers like 999)
3. Corrupted processing that created unrealistic values

It WILL flag some legitimate patterns (like time sequences), but those are usually 
safe to ignore. The goal is to catch obvious problems before they make it to your plots.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import Counter
import numpy as np


class ViewIntegrityChecker:
    """Check view files for signs of simulated or corrupted data."""
    
    def __init__(self, views_dir: Path):
        self.views_dir = views_dir
        self.issues = []
        self.warnings = []
        
    def check_all_views(self) -> Tuple[List[str], List[str]]:
        """Check all view files for integrity issues."""
        
        view_files = list(self.views_dir.glob("*.json"))
        print(f"🔍 Checking {len(view_files)} view files for integrity issues...\n")
        
        for view_file in view_files:
            print(f"Checking {view_file.name}...")
            self.check_view_file(view_file)
        
        return self.issues, self.warnings
    
    def check_view_file(self, filepath: Path):
        """Check a single view file for integrity issues."""
        
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            # Run various checks - keeping only the essential ones
            self.check_for_obvious_placeholders(data, filepath.name)
            self.check_for_test_data(data, filepath.name)
            
        except json.JSONDecodeError as e:
            self.issues.append(f"❌ {filepath.name}: Invalid JSON - {e}")
        except Exception as e:
            self.issues.append(f"❌ {filepath.name}: Error reading file - {e}")
    
    def check_for_obvious_placeholders(self, data: Any, filename: str, path: str = ""):
        """Check for obviously problematic placeholder values only."""
        
        # Only flag clearly problematic strings
        suspicious_strings = {
            "todo", "fixme", "xxx", "fake", "dummy", "lorem", "ipsum",
            "placeholder", "delete_me", "test_data", "replace_me"
        }
        
        # Only flag obviously fake numbers
        suspicious_numbers = {
            123456, 1234567, 987654321,  # Obviously fake numbers
            111111, 222222, 333333,     # Repeated digit placeholders
        }
        
        def check_value(value, current_path=""):
            if isinstance(value, str):
                lower_value = value.lower().strip()
                # Only flag if the entire value is suspicious, or if it's an exact word match
                if lower_value in suspicious_strings or any(
                    f" {sus} " in f" {lower_value} " for sus in suspicious_strings
                ):
                    self.warnings.append(
                        f"⚠️  {filename}: Suspicious string '{value}' at {current_path}"
                    )
                        
            elif isinstance(value, (int, float)) and not np.isnan(value):
                if value in suspicious_numbers:
                    self.warnings.append(
                        f"⚠️  {filename}: Suspicious number {value} at {current_path}"
                    )
                    
            elif isinstance(value, dict):
                for k, v in value.items():
                    new_path = f"{current_path}.{k}" if current_path else k
                    check_value(v, new_path)
                    
            elif isinstance(value, list):
                for i, item in enumerate(value[:100]):  # Check first 100 items
                    new_path = f"{current_path}[{i}]"
                    check_value(item, new_path)
        
        check_value(data, path)
    
    
    def check_for_test_data(self, data: Any, filename: str):
        """Check for patterns specific to test/demo data."""
        
        # Check for sequential IDs
        if isinstance(data, dict) and "data" in data:
            items = data["data"]
            if isinstance(items, list) and len(items) > 0:
                # Check if IDs are too sequential
                ids = []
                for item in items[:20]:  # Check first 20
                    if isinstance(item, dict) and "id" in item:
                        try:
                            ids.append(int(item["id"]))
                        except (ValueError, TypeError):
                            pass
                
                if len(ids) > 5:
                    # Check if perfectly sequential
                    if ids == list(range(ids[0], ids[0] + len(ids))):
                        self.warnings.append(
                            f"⚠️  {filename}: Perfectly sequential IDs detected (might be generated data)"
                        )
        
        # Check for dates that are too regular
        def check_dates(obj, dates=None):
            """Extract date strings."""
            if dates is None:
                dates = []
            
            if isinstance(obj, str) and any(sep in obj for sep in ["-", "/"]):
                # Might be a date
                if len(obj) >= 8 and any(char.isdigit() for char in obj):
                    dates.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    check_dates(value, dates)
            elif isinstance(obj, list):
                for item in obj[:100]:  # Check first 100
                    check_dates(item, dates)
            
            return dates
        
        dates = check_dates(data)
        if len(dates) > 10:
            # Check if dates are too regular (all same day of month, etc.)
            date_patterns = Counter()
            for date in dates[:50]:  # Check first 50
                try:
                    # Extract day from date (rough parsing)
                    parts = date.replace("-", "/").split("/")
                    if len(parts) >= 3:
                        day = parts[-1].split()[0] if " " in parts[-1] else parts[-1]
                        date_patterns[day] += 1
                except:
                    pass
            
            if date_patterns and max(date_patterns.values()) / len(dates) > 0.5:
                most_common_day = date_patterns.most_common(1)[0][0]
                self.warnings.append(
                    f"⚠️  {filename}: Suspicious date pattern - day '{most_common_day}' appears too frequently"
                )
    
    
    def print_report(self):
        """Print the integrity check report."""
        
        print("\n" + "="*60)
        print("📊 VIEW INTEGRITY CHECK REPORT")
        print("="*60)
        print("This checks for obvious fake/test data in your marine science views.")
        print("🔍 CRITICAL ISSUES = definitely fix these")  
        print("⚠️  WARNINGS = might be OK, use your judgment")
        
        if not self.issues and not self.warnings:
            print("✅ All checks passed! No integrity issues detected.")
        else:
            if self.issues:
                print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
                for issue in self.issues:
                    print(f"  {issue}")
            
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for warning in self.warnings[:10]:  # Show first 10
                    print(f"  {warning}")
                if len(self.warnings) > 10:
                    print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        print("\n" + "="*60)
        
        return len(self.issues) == 0


def main():
    """Main entry point."""
    # Find views directory - data is at project root, not in python folder
    project_root = Path(__file__).parent.parent.parent  # Go up to project root
    views_dir = project_root / "data" / "views"
    
    if not views_dir.exists():
        print(f"❌ Views directory not found: {views_dir}")
        sys.exit(1)
    
    # Run integrity check
    checker = ViewIntegrityChecker(views_dir)
    issues, warnings = checker.check_all_views()
    
    # Print report
    success = checker.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()