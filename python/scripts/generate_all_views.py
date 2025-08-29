#!/usr/bin/env python3
"""Generate all view files for the dashboard."""

from pathlib import Path
import sys
from mbon_analysis.views.stations import StationsViewGenerator
from mbon_analysis.views.datasets_summary import DatasetsSummaryViewGenerator
from mbon_analysis.views.indices_reference import IndicesReferenceViewGenerator
from mbon_analysis.views.project_metadata import ProjectMetadataViewGenerator


def main():
    """Generate all views."""
    print("🏗️  Generating all dashboard views")
    print("=" * 50)
    
    # Get data root directory
    current_dir = Path(__file__).parent.parent
    data_root = current_dir / "data"
    
    # Track results
    results = []
    errors = []
    
    # Define all view generators
    generators = [
        ("stations.json", StationsViewGenerator),
        ("datasets_summary.json", DatasetsSummaryViewGenerator),
        ("indices_reference.json", IndicesReferenceViewGenerator),
        ("project_metadata.json", ProjectMetadataViewGenerator),
    ]
    
    # Generate each view
    for filename, GeneratorClass in generators:
        print(f"\n📊 Generating {filename}...")
        try:
            generator = GeneratorClass(data_root)
            result = generator.create_view(filename)
            
            print(f"   ✅ Success: {result['size_kb']} KB")
            results.append(result)
            
        except Exception as e:
            error_msg = f"   ❌ Failed: {str(e)}"
            print(error_msg)
            errors.append((filename, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 Generation Summary:")
    print(f"   ✅ Successfully generated: {len(results)} views")
    if errors:
        print(f"   ❌ Failed: {len(errors)} views")
        for filename, error in errors:
            print(f"      - {filename}: {error}")
    
    # Check total size
    total_size = sum(r['size_kb'] for r in results)
    print(f"\n📦 Total view size: {total_size:.2f} KB")
    
    if total_size < 200:  # Reasonable total for initial views
        print("   ✅ Total size is optimal for fast loading")
    else:
        print("   ⚠️  Consider optimizing view sizes for performance")
    
    # List generated files
    print("\n📁 Generated files:")
    views_dir = data_root / "views"
    for result in results:
        print(f"   - {result['filename']}: {result['size_kb']} KB")
    
    print("\n🎉 View generation complete!")
    
    # Exit with error code if any failures
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()