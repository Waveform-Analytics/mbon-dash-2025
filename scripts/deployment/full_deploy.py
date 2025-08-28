#!/usr/bin/env python3
"""
Full deployment script for MBON dashboard views.

This script orchestrates the complete deployment pipeline:
1. Generate all view files
2. Sync to CDN with hash-based change detection
3. Validate deployment
4. Report results

Usage:
    python scripts/deployment/full_deploy.py [--check-only] [--dry-run]
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.views.station_views import generate_station_overview
from mbon_analysis.views.species_views import generate_species_timeline
from mbon_analysis.deployment.cdn_sync import CDNDeployer
from mbon_analysis.deployment.validation import validate_deployment
from mbon_analysis.deployment.manifest_generator import generate_manifest, save_manifest


def generate_all_views(output_dir: Path) -> dict:
    """Generate all dashboard view files."""
    print("🔄 Generating view files...")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Generate station overview
    try:
        station_data = generate_station_overview(Path('data/cdn/processed'))
        station_file = output_dir / 'station_overview.json'
        
        import json
        with open(station_file, 'w') as f:
            json.dump(station_data, f, indent=2)
        
        results['station_overview'] = {
            'success': True,
            'size_kb': station_file.stat().st_size / 1024,
            'file': str(station_file)
        }
        print(f"  ✅ station_overview.json ({results['station_overview']['size_kb']:.1f} KB)")
        
    except Exception as e:
        results['station_overview'] = {'success': False, 'error': str(e)}
        print(f"  ❌ station_overview.json failed: {e}")
    
    # Generate species timeline
    try:
        species_data = generate_species_timeline(Path('data/cdn/processed'))
        species_file = output_dir / 'species_timeline.json'
        
        with open(species_file, 'w') as f:
            json.dump(species_data, f, indent=2)
        
        results['species_timeline'] = {
            'success': True,
            'size_kb': species_file.stat().st_size / 1024,
            'file': str(species_file)
        }
        print(f"  ✅ species_timeline.json ({results['species_timeline']['size_kb']:.1f} KB)")
        
    except Exception as e:
        results['species_timeline'] = {'success': False, 'error': str(e)}
        print(f"  ❌ species_timeline.json failed: {e}")
    
    return results


def deploy_to_cdn(views_dir: Path, args) -> tuple:
    """Deploy views to CDN with smart sync."""
    print("🚀 Deploying to CDN...")
    
    # Load environment variables from .env.local
    import os
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    
    provider = os.getenv('CDN_PROVIDER', 'local_dev')
    base_url = os.getenv('CDN_BASE_URL', 'http://localhost:3000')
    
    deployer = CDNDeployer(
        provider=provider,
        base_url=base_url,
        dry_run=args.dry_run
    )
    
    # Perform deployment
    result = deployer.sync_views(views_dir)
    
    print(f"  📊 {result.get_summary()}")
    
    if result.errors:
        for error in result.errors:
            print(f"  ❌ {error}")
    
    return result.success, result


def validate_cdn_deployment(base_url: str, expected_files: list) -> tuple:
    """Validate CDN deployment."""
    print("🔍 Validating deployment...")
    
    result = validate_deployment(
        base_url=base_url,
        expected_files=expected_files,
        timeout=10.0,
        validate_content=True
    )
    
    print(f"  📊 {result.get_summary()}")
    
    if result.errors:
        for error in result.errors[:5]:  # Show first 5 errors
            print(f"  ❌ {error}")
        if len(result.errors) > 5:
            print(f"  ... and {len(result.errors) - 5} more errors")
    
    if result.warnings:
        for warning in result.warnings[:3]:  # Show first 3 warnings
            print(f"  ⚠️  {warning}")
        if len(result.warnings) > 3:
            print(f"  ... and {len(result.warnings) - 3} more warnings")
    
    return result.success, result


def main():
    """Main deployment orchestration."""
    parser = argparse.ArgumentParser(description='Deploy MBON dashboard views to CDN')
    parser.add_argument('--check-only', action='store_true', help='Only check what would be deployed')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without actual deployment')
    args = parser.parse_args()
    
    print("🌊 MBON Dashboard CDN Deployment")
    print("=" * 40)
    
    # Set up paths
    views_dir = Path('data/cdn/views')
    
    if args.check_only:
        print("🔍 Check mode: Analyzing what would be deployed")
        
        # Generate manifest to show current state
        if views_dir.exists():
            manifest = generate_manifest(views_dir)
            print(f"📁 Found {manifest['total_files']} view files:")
            for file_info in manifest['files']:
                print(f"  • {file_info['filename']} ({file_info['size'] / 1024:.1f} KB)")
        else:
            print("📁 No views directory found. Run without --check-only to generate files.")
        
        return
    
    success_count = 0
    total_steps = 3
    
    # Step 1: Generate view files
    view_results = generate_all_views(views_dir)
    successful_views = [name for name, result in view_results.items() if result.get('success')]
    
    if successful_views:
        success_count += 1
        print(f"✅ Step 1/3: Generated {len(successful_views)} view files")
    else:
        print("❌ Step 1/3: Failed to generate view files")
        sys.exit(1)
    
    # Generate manifest
    manifest = generate_manifest(views_dir)
    manifest_file = views_dir / 'manifest.json'
    save_manifest(manifest, manifest_file)
    print(f"📄 Generated manifest with {manifest['total_files']} files")
    
    # Step 2: Deploy to CDN
    deployment_success, deploy_result = deploy_to_cdn(views_dir, args)
    
    if deployment_success:
        success_count += 1
        print("✅ Step 2/3: CDN deployment successful")
    else:
        print("❌ Step 2/3: CDN deployment failed")
        if not args.dry_run:
            sys.exit(1)
    
    # Step 3: Validate deployment (skip for local dev and dry runs)
    import os
    base_url = os.getenv('CDN_BASE_URL', 'http://localhost:3000')
    provider = os.getenv('CDN_PROVIDER', 'local_dev')
    
    if not args.dry_run and provider != 'local_dev':
        expected_files = [f['filename'] for f in manifest['files']]
        validation_success, validation_result = validate_cdn_deployment(base_url, expected_files)
        
        if validation_success:
            success_count += 1
            print("✅ Step 3/3: Deployment validation passed")
        else:
            print("❌ Step 3/3: Deployment validation failed")
    else:
        success_count += 1  # Skip validation for local dev
        print("⏭️  Step 3/3: Skipped validation (local dev mode)")
    
    # Final summary
    print("=" * 40)
    if success_count == total_steps:
        print("🎉 Deployment completed successfully!")
        
        # Show summary stats
        total_size = sum(r.get('size_kb', 0) for r in view_results.values() if r.get('success'))
        print(f"📊 Deployed {len(successful_views)} views, {total_size:.1f} KB total")
        
        if deploy_result.files_uploaded > 0:
            print(f"🔄 {deploy_result.files_uploaded} files uploaded, {deploy_result.files_skipped} unchanged")
    else:
        print(f"⚠️  Deployment completed with issues ({success_count}/{total_steps} steps successful)")
        sys.exit(1)


if __name__ == "__main__":
    main()