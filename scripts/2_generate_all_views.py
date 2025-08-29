#!/usr/bin/env python3
"""
Consolidated view generator for MBON dashboard.

Generates all optimized view files from core JSON data.
This is Step 2 of the 3-step data pipeline.

Auto-discovers view generators in mbon_analysis.views module.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import importlib
import inspect

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configuration
INPUT_DIR = Path("data/cdn/processed")
OUTPUT_DIR = Path("data/cdn/views")


def discover_view_generators():
    """Auto-discover all view generator functions."""
    generators = {}
    
    try:
        # Import all view modules
        view_modules = [
            'mbon_analysis.views.station_views',
            'mbon_analysis.views.species_views', 
            'mbon_analysis.views.acoustic_views',
            'mbon_analysis.views.chart_views'
        ]
        
        for module_name in view_modules:
            try:
                module = importlib.import_module(module_name)
                
                # Find all functions that start with 'generate_'
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    if name.startswith('generate_') and func.__module__ == module_name:
                        view_name = name.replace('generate_', '').replace('_', '-')
                        generators[view_name] = func
                        
            except ImportError as e:
                logger.warning(f"Could not import {module_name}: {e}")
                
    except Exception as e:
        logger.error(f"Error discovering view generators: {e}")
        
    return generators


def main():
    """Generate all dashboard view files."""
    try:
        logger.info("🔄 Starting JSON → Views generation...")
        
        # Check input directory exists
        if not INPUT_DIR.exists():
            logger.error(f"❌ Input directory not found: {INPUT_DIR}")
            logger.error("   Run '1_process_excel_to_json.py' first")
            return 1
            
        # Create output directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Auto-discover view generators
        logger.info("🔍 Discovering view generators...")
        generators = discover_view_generators()
        
        if not generators:
            logger.error("❌ No view generators found!")
            return 1
            
        logger.info(f"   Found {len(generators)} generators: {list(generators.keys())}")
        
        # Generate each view
        views_generated = []
        total_size = 0
        
        for view_name, generator_func in generators.items():
            try:
                logger.info(f"📊 Generating {view_name} view...")
                
                # Call generator with input directory
                view_data = generator_func(INPUT_DIR)
                
                # Determine output filename
                filename = f"{view_name.replace('-', '_')}.json"
                output_path = OUTPUT_DIR / filename
                
                # Save view file
                with open(output_path, 'w') as f:
                    json.dump(view_data, f, indent=2)
                
                # Calculate size
                file_size = output_path.stat().st_size
                total_size += file_size
                
                views_generated.append({
                    'name': view_name,
                    'file': filename,
                    'size': file_size,
                    'size_kb': round(file_size / 1024, 1)
                })
                
                logger.info(f"   ✓ {filename} ({round(file_size/1024, 1)} KB)")
                
            except Exception as e:
                logger.error(f"   ❌ Failed to generate {view_name}: {e}")
        
        # Create manifest for views
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "total_views": len(views_generated),
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 1),
            "views": views_generated
        }
        
        manifest_path = OUTPUT_DIR / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Success report
        logger.info("✅ JSON → Views generation complete!")
        logger.info(f"📁 Output: {OUTPUT_DIR}")
        logger.info(f"📊 Generated {len(views_generated)} views ({round(total_size/1024, 1)} KB total)")
        for view in views_generated:
            logger.info(f"  ✓ {view['file']} ({view['size_kb']} KB)")
            
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error in view generation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())