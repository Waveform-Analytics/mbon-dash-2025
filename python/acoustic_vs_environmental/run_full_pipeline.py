#!/usr/bin/env python3
"""
MASTER PIPELINE RUNNER
Marine Acoustic Discovery Analysis - Full Reproducible Pipeline

This script runs the complete analysis pipeline from start to finish,
generating all figures and outputs needed for the report.

Usage:
    python run_full_pipeline.py

Requirements:
    - data_01_aligned_2021.csv (the aligned dataset)
    - All Python dependencies installed
"""

import sys
import os
import subprocess
import time
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def run_phase(phase_name, script_name, description):
    """Run a single phase of the analysis pipeline."""
    print(f"\n{'='*60}")
    print(f"🔄 PHASE: {phase_name}")
    print(f"📝 {description}")
    print(f"📄 Running: {script_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Check if script exists
        if not Path(script_name).exists():
            print(f"❌ ERROR: Script {script_name} not found!")
            return False
            
        # Run the script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True)
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {phase_name} completed in {elapsed_time:.1f}s")
            if result.stdout:
                print(f"📊 Output: {result.stdout[-500:]}")  # Last 500 chars
            return True
        else:
            print(f"❌ FAILED: {phase_name}")
            print(f"❌ Error: {result.stderr}")
            print(f"❌ Output: {result.stdout}")
            return False
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ EXCEPTION in {phase_name} after {elapsed_time:.1f}s: {str(e)}")
        return False

def check_dependencies():
    """Check that all required files and dependencies exist."""
    print("🔍 CHECKING DEPENDENCIES")
    print("="*40)
    
    # Check required files
    required_files = [
        "data_01_aligned_2021.csv",
        "01_data_loading.py",
        "02_baseline_comparison.py", 
        "06_temporal_correlation_analysis.py",
        "09_detection_guidance.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print(f"\n❌ MISSING FILES:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    # Check Python packages
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy', 
        'sklearn', 'pathlib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ MISSING PACKAGES:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install " + " ".join(missing_packages))
        return False
    
    print(f"\n✅ All dependencies satisfied!")
    return True

def create_output_structure():
    """Create the output directory structure."""
    print("\n🏗️  CREATING OUTPUT STRUCTURE")
    print("="*40)
    
    dirs_to_create = [
        "output",
        "output/phase1_data",
        "output/phase1_data/figures",
        "output/phase2_baseline", 
        "output/phase2_baseline/figures",
        "output/phase6_temporal_correlation",
        "output/phase6_temporal_correlation/figures",
        "output/phase9_detection_guidance",
        "output/phase9_detection_guidance/figures",
        "output/phase9_detection_guidance/tables",
        "netlify_deploy"  # For final deployment
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")
    
    print("✅ Output structure created!")

def main():
    """Run the complete pipeline."""
    print("🚀 MARINE ACOUSTIC DISCOVERY - FULL PIPELINE")
    print("="*60)
    print("This will run the complete analysis from start to finish.")
    print("Estimated time: 5-10 minutes")
    print("="*60)
    
    start_time = time.time()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please fix issues above.")
        return False
    
    # Step 2: Create output structure
    create_output_structure()
    
    # Step 3: Define the pipeline phases
    pipeline_phases = [
        {
            "name": "Data Loading & Verification",
            "script": "01_data_loading.py",
            "description": "Load and verify the aligned dataset, basic stats"
        },
        {
            "name": "Baseline Machine Learning Analysis", 
            "script": "02_baseline_comparison.py",
            "description": "Traditional ML analysis showing seasonal limitations"
        },
        {
            "name": "Temporal Correlation Analysis",
            "script": "06_temporal_correlation_analysis.py", 
            "description": "Create acoustic vs manual detection comparison heatmaps"
        },
        {
            "name": "Detection Guidance System",
            "script": "09_detection_guidance.py",
            "description": "Build 2D probability surfaces and guidance system"
        }
    ]
    
    # Step 4: Run each phase
    successful_phases = 0
    for i, phase in enumerate(pipeline_phases, 1):
        success = run_phase(
            f"{i}. {phase['name']}", 
            phase['script'], 
            phase['description']
        )
        
        if success:
            successful_phases += 1
        else:
            print(f"\n⚠️  Phase {i} failed, but continuing...")
            # Don't stop - let other phases try to run
    
    # Step 5: Generate final report assets
    print(f"\n{'='*60}")
    print("📊 GENERATING FINAL REPORT ASSETS")
    print(f"{'='*60}")
    
    # Copy key figures to netlify deploy folder
    try:
        import shutil
        
        netlify_dir = Path("netlify_deploy")
        netlify_dir.mkdir(exist_ok=True)
        
        # Find and copy all PNG files
        for png_file in Path("output").rglob("*.png"):
            dest_file = netlify_dir / f"fig_{png_file.parent.name}_{png_file.name}"
            shutil.copy2(png_file, dest_file)
            print(f"✅ Copied: {png_file} -> {dest_file.name}")
        
        print(f"✅ Figures ready for deployment in netlify_deploy/")
        
    except Exception as e:
        print(f"⚠️  Could not copy figures: {e}")
    
    # Step 6: Summary
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("📋 PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f"⏱️  Total runtime: {total_time/60:.1f} minutes")
    print(f"✅ Successful phases: {successful_phases}/{len(pipeline_phases)}")
    
    if successful_phases == len(pipeline_phases):
        print("🎉 COMPLETE SUCCESS! All phases completed.")
        print("\nNext steps:")
        print("1. Check output/ folder for all generated figures")
        print("2. Run 'quarto render Marine_Acoustic_Discovery_Report_v2.qmd' to generate HTML")
        print("3. Use netlify_deploy/ folder for web deployment")
        return True
    else:
        print("⚠️  Some phases had issues. Check output above.")
        print("You may still be able to generate the report with existing figures.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)