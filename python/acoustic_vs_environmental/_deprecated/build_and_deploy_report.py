#!/usr/bin/env python3
"""
Build and Deploy Marine Acoustic Discovery Report

This script:
1. Renders the QMD file to HTML using Quarto
2. Copies the HTML report and all figures to netlify_deploy/ folder
3. Updates HTML to use local image paths
4. Creates a complete folder ready for Netlify Drop

Usage:
    python build_and_deploy_report.py
    
Or with uv:
    uv run python build_and_deploy_report.py
"""

import subprocess
import shutil
import re
from pathlib import Path
import sys
import os

def run_command(cmd, description=""):
    """Run a command and return success status."""
    print(f"🔄 {description}")
    print(f"   Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path.cwd())
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Error (code {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def render_qmd_to_html():
    """Render the QMD file using Quarto."""
    print("\n📝 RENDERING QMD TO HTML")
    print("=" * 40)
    
    qmd_file = Path("Marine_Acoustic_Discovery_Report_v2.qmd")
    if not qmd_file.exists():
        print(f"❌ QMD file not found: {qmd_file}")
        return False
    
    # Render using Quarto
    cmd = f"quarto render {qmd_file}"
    success = run_command(cmd, f"Rendering {qmd_file} to HTML")
    
    # Check if HTML was created
    html_file = qmd_file.with_suffix('.html')
    if html_file.exists():
        print(f"✅ HTML file created: {html_file}")
        return True
    else:
        print(f"❌ HTML file not found after rendering: {html_file}")
        return False

def prepare_netlify_deployment():
    """Prepare complete netlify deployment folder."""
    
    print("\n🌐 PREPARING NETLIFY DEPLOYMENT")
    print("=" * 40)
    
    # Create deployment directory
    deploy_dir = Path("netlify_deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
        print(f"🗑️  Cleaned existing deployment directory")
    deploy_dir.mkdir(exist_ok=True)
    
    # Step 1: Copy HTML file
    html_file = Path("Marine_Acoustic_Discovery_Report_v2.html")
    if html_file.exists():
        shutil.copy2(html_file, deploy_dir / "index.html")
        print(f"✅ Copied HTML report -> index.html")
    else:
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    # Step 2: Copy figures from multiple locations
    figure_count = 0
    
    # Copy from output/ directory (older figures)
    output_dir = Path("output")
    if output_dir.exists():
        for png_file in output_dir.rglob("*.png"):
            # Create a clean filename for web deployment
            rel_path = png_file.relative_to(output_dir)
            clean_name = f"figures_{str(rel_path).replace('/', '_').replace(' ', '_')}"
            dest_path = deploy_dir / clean_name
            shutil.copy2(png_file, dest_path)
            print(f"✅ Copied: {png_file} -> {clean_name}")
            figure_count += 1
    
    # Copy from dashboard/public/views/notebooks (newer figures)
    notebook_figures = Path("../../dashboard/public/views/notebooks")
    if notebook_figures.exists():
        for png_file in notebook_figures.glob("*.png"):
            clean_name = f"figures_{png_file.name}"
            dest_path = deploy_dir / clean_name
            shutil.copy2(png_file, dest_path)
            print(f"✅ Copied: {png_file} -> {clean_name}")
            figure_count += 1
    
    # Step 3: Update HTML to use local image paths
    index_file = deploy_dir / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace different image path patterns
        def replace_image_path(match):
            original_path = match.group(1)
            
            # Handle output/phase/figures/file.png patterns
            if 'output' in original_path:
                clean_path = original_path.replace('output/', 'figures_').replace('/', '_')
                return f'src="{clean_path}"'
            
            # Handle dashboard/public/views/notebooks/file.png patterns  
            elif 'dashboard/public/views/notebooks' in original_path:
                filename = Path(original_path).name
                return f'src="figures_{filename}"'
                
            # Handle direct notebook references
            elif original_path.endswith('.png') and not original_path.startswith('http'):
                filename = Path(original_path).name
                return f'src="figures_{filename}"'
                
            return match.group(0)
        
        # Update image source paths
        html_content = re.sub(r'src="([^"]*\.png)"', replace_image_path, html_content)
        
        # Also handle any remaining relative paths
        html_content = html_content.replace('src="../', 'src="')
        html_content = html_content.replace('src="../../', 'src="')
        
        # Write updated HTML
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Updated {len(re.findall(r'src="figures_[^"]*"', html_content))} image paths in HTML")
    
    # Step 4: Create deployment summary
    files_in_deploy = list(deploy_dir.glob("*"))
    
    print(f"\n📊 DEPLOYMENT SUMMARY")
    print("=" * 30)
    print(f"📁 Deployment folder: {deploy_dir.absolute()}")
    print(f"📄 Total files: {len(files_in_deploy)}")
    print(f"🖼️  Images: {figure_count}")
    print(f"📝 HTML: {'✅' if (deploy_dir / 'index.html').exists() else '❌'}")
    
    # Show size breakdown
    total_size = sum(f.stat().st_size for f in files_in_deploy if f.is_file())
    print(f"💾 Total size: {total_size / (1024*1024):.1f} MB")
    
    print(f"\n📂 Contents of {deploy_dir}:")
    for file in sorted(files_in_deploy):
        if file.is_file():
            size_kb = file.stat().st_size / 1024
            print(f"   {file.name} ({size_kb:.1f}KB)")
    
    return True

def main():
    """Main build and deploy workflow."""
    print("🚀 MARINE ACOUSTIC DISCOVERY REPORT - BUILD & DEPLOY")
    print("=" * 60)
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Working directory: {Path.cwd()}")
    
    success_count = 0
    total_steps = 2
    
    # Step 1: Render QMD to HTML
    if render_qmd_to_html():
        success_count += 1
        print("✅ Step 1 Complete: QMD rendered to HTML")
    else:
        print("❌ Step 1 Failed: QMD rendering failed")
        print("\nTroubleshooting:")
        print("- Ensure Quarto is installed and in PATH")
        print("- Check QMD file syntax")
        print("- Verify all referenced images exist")
        return False
    
    # Step 2: Prepare Netlify deployment
    if prepare_netlify_deployment():
        success_count += 1
        print("✅ Step 2 Complete: Netlify deployment prepared")
    else:
        print("❌ Step 2 Failed: Deployment preparation failed")
        return False
    
    # Final success message
    print(f"\n🎉 BUILD & DEPLOY COMPLETE!")
    print(f"✅ {success_count}/{total_steps} steps completed successfully")
    
    deploy_dir = Path("netlify_deploy")
    print(f"\n🚀 READY FOR NETLIFY DEPLOYMENT!")
    print("=" * 40)
    print("Next steps:")
    print("1. Go to https://app.netlify.com/drop")
    print(f"2. Drag the entire '{deploy_dir}' folder to the drop zone")
    print("3. Get your live URL instantly!")
    print("\nOr use Netlify CLI:")
    print(f"   netlify deploy --dir={deploy_dir} --prod")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)