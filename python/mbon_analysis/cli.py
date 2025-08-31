"""Command-line interface for MBON analysis tools."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .views.stations import StationsViewGenerator
from .views.datasets_summary import DatasetsSummaryViewGenerator
from .views.indices_reference import IndicesReferenceViewGenerator
from .views.project_metadata import ProjectMetadataViewGenerator
from .views.acoustic_indices_distributions import AcousticIndicesDistributionsViewGenerator
from .utils.compiled_indices import CompiledIndicesManager
from .utils.data_migration import DataMigrator
from .utils.dashboard_testing import DashboardDataTester


def setup_parser() -> argparse.ArgumentParser:
    """Setup the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="mbon-analysis",
        description="MBON Marine Biodiversity Dashboard - Data processing and analysis tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mbon-process --help                    # Show help for data processing
  mbon-generate-views --all             # Generate all view files
  mbon-generate-views --view stations   # Generate only stations view
  mbon-generate-views --data-root /path/to/data  # Use custom data path
  mbon-compile-indices                  # Compile all indices into single JSON
  mbon-migrate-data                     # Migrate data to top-level directory
  mbon-test-dashboard                   # Test dashboard data access
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process command
    process_parser = subparsers.add_parser(
        "process",
        help="Process raw data files"
    )
    process_parser.add_argument(
        "--data-root",
        type=Path,
        help="Path to data directory (default: auto-detect)"
    )
    process_parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for processed files"
    )
    
    # Generate views command
    views_parser = subparsers.add_parser(
        "generate-views",
        help="Generate dashboard view files"
    )
    views_parser.add_argument(
        "--data-root",
        type=Path,
        help="Path to data directory (default: auto-detect)"
    )
    views_parser.add_argument(
        "--view",
        choices=["stations", "datasets", "indices", "metadata", "acoustic", "all"],
        default="all",
        help="Specific view to generate (default: all)"
    )
    views_parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of existing files"
    )
    views_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Compile indices command
    indices_parser = subparsers.add_parser(
        "compile-indices",
        help="Compile all acoustic indices into single JSON file"
    )
    indices_parser.add_argument(
        "--data-root",
        type=Path,
        help="Path to data directory (default: auto-detect)"
    )
    indices_parser.add_argument(
        "--output",
        type=Path,
        help="Output path for compiled JSON (default: data/processed/compiled_indices.json)"
    )
    indices_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Migrate data command
    migrate_parser = subparsers.add_parser(
        "migrate-data",
        help="Migrate data from python/data to top-level data directory"
    )
    migrate_parser.add_argument(
        "--force",
        action="store_true",
        help="Force migration even if target exists"
    )
    migrate_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Test dashboard command
    test_parser = subparsers.add_parser(
        "test-dashboard",
        help="Test dashboard data access and API endpoints"
    )
    test_parser.add_argument(
        "--data-root",
        type=Path,
        help="Path to data directory (default: auto-detect)"
    )
    test_parser.add_argument(
        "--check-api",
        action="store_true",
        help="Also test dashboard API endpoints"
    )
    test_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Compiled indices utilities command
    utils_parser = subparsers.add_parser(
        "indices-utils",
        help="Work with compiled indices JSON file"
    )
    utils_parser.add_argument(
        "json_file",
        type=Path,
        help="Path to compiled_indices.json file"
    )
    utils_parser.add_argument(
        "--action",
        choices=["summary", "stations", "export"],
        default="summary",
        help="Action to perform"
    )
    utils_parser.add_argument(
        "--station",
        help="Station identifier (for export)"
    )
    utils_parser.add_argument(
        "--bandwidth",
        help="Bandwidth (for export)"
    )
    utils_parser.add_argument(
        "--output",
        help="Output path (for export)"
    )
    
    return parser


def get_data_root(custom_path: Optional[Path] = None) -> Path:
    """Get the data root directory, with fallback logic."""
    if custom_path:
        return custom_path
    
    # Try to auto-detect data directory
    current_dir = Path(__file__).parent.parent
    
    # Check for top-level data directory (recommended)
    top_level_data = current_dir.parent / "data"
    if top_level_data.exists():
        return top_level_data
    
    # Fallback to python/data directory
    python_data = current_dir / "data"
    if python_data.exists():
        return python_data
    
    # Default to current directory
    return current_dir


def process_data(data_root: Path, output_dir: Optional[Path] = None) -> int:
    """Process raw data files."""
    print(f"🔧 Processing data from: {data_root}")
    
    if output_dir is None:
        output_dir = data_root / "processed"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # TODO: Implement data processing logic
    print(f"📁 Output directory: {output_dir}")
    print("✅ Data processing completed")
    
    return 0


def generate_views(
    data_root: Path,
    view_name: str = "all",
    force: bool = False,
    verbose: bool = False
) -> int:
    """Generate dashboard view files."""
    print(f"🏗️  Generating views from: {data_root}")
    
    # Define view generators
    generators = {
        "stations": StationsViewGenerator,
        "datasets": DatasetsSummaryViewGenerator,
        "indices": IndicesReferenceViewGenerator,
        "metadata": ProjectMetadataViewGenerator,
        "acoustic": AcousticIndicesDistributionsViewGenerator,
    }
    
    if view_name == "all":
        views_to_generate = list(generators.keys())
    else:
        views_to_generate = [view_name]
    
    results = []
    errors = []
    
    for view_key in views_to_generate:
        if view_key not in generators:
            print(f"❌ Unknown view: {view_key}")
            continue
        
        GeneratorClass = generators[view_key]
        filename = f"{view_key}.json"
        
        if verbose:
            print(f"\n📊 Generating {filename}...")
        
        try:
            generator = GeneratorClass(data_root)
            result = generator.create_view(filename)
            
            if verbose:
                print(f"   ✅ Success: {result['size_kb']:.2f} KB")
            else:
                print(f"✅ {filename}: {result['size_kb']:.2f} KB")
            
            results.append(result)
            
        except Exception as e:
            error_msg = f"   ❌ Failed: {str(e)}"
            if verbose:
                print(error_msg)
            else:
                print(f"❌ {filename}: {str(e)}")
            errors.append((filename, str(e)))
    
    # Summary
    if verbose:
        print(f"\n📈 Generation Summary:")
        print(f"   ✅ Successfully generated: {len(results)} views")
        if errors:
            print(f"   ❌ Failed: {len(errors)} views")
            for filename, error in errors:
                print(f"      - {filename}: {error}")
    
    # Check total size
    total_size = sum(r['size_kb'] for r in results)
    if verbose:
        print(f"\n📦 Total view size: {total_size:.2f} KB")
    
    return 0 if not errors else 1


def compile_indices(data_root: Path, output_path: Optional[Path] = None, verbose: bool = False) -> int:
    """Compile all acoustic indices into single JSON file."""
    from .utils.compiled_indices import compile_indices_data, save_compiled_data
    
    if output_path is None:
        output_path = data_root / "processed" / "compiled_indices.json"
    
    print(f"📊 Compiling indices from: {data_root}")
    print(f"📁 Output: {output_path}")
    
    try:
        compiled_data = compile_indices_data(data_root, output_path)
        save_compiled_data(compiled_data, output_path)
        
        # Print summary
        summary = compiled_data["summary"]
        print(f"\n✅ Compilation complete!")
        print(f"   📁 Files processed: {summary['total_files']}")
        print(f"   📊 Total records: {summary['total_records']:,}")
        print(f"   🗂️  Stations: {list(summary['stations'].keys())}")
        print(f"   📡 Bandwidths: {list(summary['bandwidths'].keys())}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during compilation: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def migrate_data(force: bool = False, verbose: bool = False) -> int:
    """Migrate data from python/data to top-level data directory."""
    from .utils.data_migration import DataMigrator
    
    migrator = DataMigrator(verbose=verbose)
    
    try:
        success = migrator.migrate(force=force)
        if success:
            print("✅ Data migration completed successfully!")
            return 0
        else:
            print("❌ Data migration failed!")
            return 1
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def test_dashboard(data_root: Path, check_api: bool = False, verbose: bool = False) -> int:
    """Test dashboard data access and API endpoints."""
    from .utils.dashboard_testing import DashboardDataTester
    
    tester = DashboardDataTester(data_root, verbose=verbose)
    
    try:
        file_results = tester.test_view_file_access()
        api_results = None
        
        if check_api:
            api_results = tester.test_dashboard_api_access()
        
        tester.print_summary(file_results, api_results)
        
        # Return success if at least one location has data
        has_data = any(
            any(view.get("exists", False) for view in views.values())
            for views in file_results.values()
        )
        
        return 0 if has_data else 1
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def indices_utils(json_file: Path, action: str, **kwargs) -> int:
    """Work with compiled indices JSON file."""
    manager = CompiledIndicesManager(json_file)
    
    try:
        if action == "summary":
            summary = manager.get_summary()
            print("Compiled Indices Summary:")
            print(f"  Total files: {summary.get('total_files', 0)}")
            print(f"  Total records: {summary.get('total_records', 0):,}")
            print(f"  Stations: {list(summary.get('stations', {}).keys())}")
            print(f"  Bandwidths: {list(summary.get('bandwidths', {}).keys())}")
            
            file_info = manager.get_file_info()
            print(f"\nFile Information:")
            print(f"  Size: {file_info.get('file_size_mb', 0)} MB")
            print(f"  Last modified: {file_info.get('last_modified', 'Unknown')}")
        
        elif action == "stations":
            stations = manager.get_stations()
            print("Available stations:")
            for station in stations:
                print(f"  - {station}")
        
        elif action == "export":
            station = kwargs.get('station')
            bandwidth = kwargs.get('bandwidth')
            output = kwargs.get('output')
            
            if not all([station, bandwidth, output]):
                print("Error: --station, --bandwidth, and --output are required for export")
                return 1
            
            success = manager.export_station_to_csv(station, bandwidth, output)
            if success:
                print(f"✅ Successfully exported {station} {bandwidth} to {output}")
            else:
                print("❌ Export failed")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "process":
            data_root = get_data_root(getattr(args, 'data_root', None))
            return process_data(data_root, getattr(args, 'output', None))
        
        elif args.command == "generate-views":
            data_root = get_data_root(getattr(args, 'data_root', None))
            return generate_views(
                data_root,
                getattr(args, 'view', 'all'),
                getattr(args, 'force', False),
                getattr(args, 'verbose', False)
            )
        
        elif args.command == "compile-indices":
            data_root = get_data_root(getattr(args, 'data_root', None))
            return compile_indices(
                data_root,
                getattr(args, 'output', None),
                getattr(args, 'verbose', False)
            )
        
        elif args.command == "migrate-data":
            return migrate_data(
                getattr(args, 'force', False),
                getattr(args, 'verbose', False)
            )
        
        elif args.command == "test-dashboard":
            data_root = get_data_root(getattr(args, 'data_root', None))
            return test_dashboard(
                data_root,
                getattr(args, 'check_api', False),
                getattr(args, 'verbose', False)
            )
        
        elif args.command == "indices-utils":
            return indices_utils(
                args.json_file,
                args.action,
                station=getattr(args, 'station', None),
                bandwidth=getattr(args, 'bandwidth', None),
                output=getattr(args, 'output', None)
            )
        
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        return 1


def generate_views_cli() -> int:
    """CLI entry point specifically for view generation."""
    parser = argparse.ArgumentParser(
        description="Generate MBON dashboard view files"
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        help="Path to data directory (default: auto-detect)"
    )
    parser.add_argument(
        "--view",
        choices=["stations", "datasets", "indices", "metadata", "acoustic", "all"],
        default="all",
        help="Specific view to generate (default: all)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of existing files"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        data_root = get_data_root(args.data_root)
        return generate_views(data_root, args.view, args.force, args.verbose)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
