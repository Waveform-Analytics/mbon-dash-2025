#!/usr/bin/env python3
"""
Prepare GitHub Pages Deployment Structure

This script:
1. Creates a docs/ folder at the project root for GitHub Pages
2. Copies HTML report and figures to docs/
3. Updates HTML paths for GitHub Pages structure
4. Creates a clean, accessible structure for automatic deployment

Usage:
    python prepare_github_pages.py
"""

import subprocess
import shutil
import re
from pathlib import Path
import sys
import os

def find_project_root():
    """Find project root by looking for the data folder."""
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent
    return project_root

def render_qmd_to_html():
    """Render the QMD file using Quarto."""
    print("📝 RENDERING QMD TO HTML")
    print("=" * 40)
    
    qmd_file = Path("Marine_Acoustic_Discovery_Report_v2.qmd")
    if not qmd_file.exists():
        print(f"❌ QMD file not found: {qmd_file}")
        return False
    
    # Render using Quarto
    try:
        result = subprocess.run(
            ["quarto", "render", str(qmd_file)], 
            capture_output=True, text=True, cwd=Path.cwd()
        )
        if result.returncode == 0:
            print(f"✅ Successfully rendered {qmd_file}")
            return True
        else:
            print(f"❌ Quarto render failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running Quarto: {e}")
        return False

def prepare_github_pages_structure():
    """Create GitHub Pages deployment structure."""
    
    print("\n🌐 PREPARING GITHUB PAGES STRUCTURE")
    print("=" * 45)
    
    # Find project root
    project_root = find_project_root()
    print(f"📁 Project root: {project_root}")
    
    # Create docs directory at project root
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
        print(f"🗑️  Cleaned existing docs directory")
    docs_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (docs_dir / "images").mkdir(exist_ok=True)
    
    # Step 1: Copy HTML file
    html_file = Path("Marine_Acoustic_Discovery_Report_v2.html")
    if html_file.exists():
        shutil.copy2(html_file, docs_dir / "index.html")
        print(f"✅ Copied HTML report -> docs/index.html")
    else:
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    # Step 2: Copy figures from multiple locations
    figure_count = 0
    
    # Copy from local output/ directory (if exists)
    output_dir = Path("output")
    if output_dir.exists():
        for png_file in output_dir.rglob("*.png"):
            rel_path = png_file.relative_to(output_dir)
            clean_name = str(rel_path).replace('/', '_').replace(' ', '_')
            dest_path = docs_dir / "images" / clean_name
            shutil.copy2(png_file, dest_path)
            print(f"✅ Copied: {png_file} -> images/{clean_name}")
            figure_count += 1
    
    # Copy from dashboard/public/views/notebooks (relative to project root)
    notebook_figures = project_root / "dashboard/public/views/notebooks"
    if notebook_figures.exists():
        for png_file in notebook_figures.glob("*.png"):
            dest_path = docs_dir / "images" / png_file.name
            shutil.copy2(png_file, dest_path)
            print(f"✅ Copied: {png_file} -> images/{png_file.name}")
            figure_count += 1
    
    # Step 3: Update HTML to use GitHub Pages paths
    index_file = docs_dir / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace different image path patterns
        def replace_image_path(match):
            original_path = match.group(1)
            
            # Handle output/phase/figures/file.png patterns
            if 'output' in original_path:
                # Convert output/phase6_temporal_correlation/figures/file.png
                # to images/phase6_temporal_correlation_figures_file.png
                clean_path = original_path.replace('output/', '').replace('/', '_')
                return f'src="images/{clean_path}"'
            
            # Handle dashboard/public/views/notebooks/file.png patterns  
            elif 'dashboard/public/views/notebooks' in original_path:
                filename = Path(original_path).name
                return f'src="images/{filename}"'
                
            # Handle direct notebook references
            elif original_path.endswith('.png') and not original_path.startswith('http'):
                filename = Path(original_path).name
                return f'src="images/{filename}"'
                
            return match.group(0)
        
        # Update image source paths
        original_img_count = len(re.findall(r'src="[^"]*\.png"', html_content))
        html_content = re.sub(r'src="([^"]*\.png)"', replace_image_path, html_content)
        updated_img_count = len(re.findall(r'src="images/', html_content))
        
        # Write updated HTML
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Updated {updated_img_count} image paths in HTML")
    
    # Step 4: Create .nojekyll file (GitHub Pages optimization)
    nojekyll_file = docs_dir / ".nojekyll"
    nojekyll_file.touch()
    print("✅ Created .nojekyll file for GitHub Pages")
    
    # Step 5: Create README for docs folder
    readme_content = """# Marine Acoustic Discovery Report

This folder contains the automatically generated GitHub Pages deployment of the Marine Acoustic Discovery Report.

- **Source**: `python/acoustic_vs_environmental/Marine_Acoustic_Discovery_Report_v2.qmd`
- **Generated**: Automatically via GitHub Actions on every push
- **Live Site**: https://[your-username].github.io/[repository-name]/

## Contents

- `index.html` - The main report
- `images/` - All figures and visualizations

## Deployment

This folder is automatically updated by GitHub Actions whenever the QMD source file is modified.
"""
    
    readme_file = docs_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print("✅ Created README.md for docs folder")
    
    # Step 6: Create deployment summary
    files_in_docs = list(docs_dir.rglob("*"))
    total_files = len([f for f in files_in_docs if f.is_file()])
    
    print(f"\n📊 GITHUB PAGES STRUCTURE READY")
    print("=" * 35)
    print(f"📁 Docs folder: {docs_dir.relative_to(project_root)}")
    print(f"📄 Total files: {total_files}")
    print(f"🖼️  Images: {figure_count}")
    print(f"📝 HTML: {'✅' if (docs_dir / 'index.html').exists() else '❌'}")
    
    # Show size breakdown
    total_size = sum(f.stat().st_size for f in files_in_docs if f.is_file())
    print(f"💾 Total size: {total_size / (1024*1024):.1f} MB")
    
    return docs_dir, figure_count

def main():
    """Main build and prepare workflow."""
    print("🚀 PREPARE GITHUB PAGES DEPLOYMENT")
    print("=" * 50)
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Working in: {Path.cwd()}")
    
    success_count = 0
    total_steps = 2
    
    # Step 1: Render QMD to HTML
    if render_qmd_to_html():
        success_count += 1
        print("✅ Step 1 Complete: QMD rendered to HTML")
    else:
        print("❌ Step 1 Failed: QMD rendering failed")
        return False
    
    # Step 2: Prepare GitHub Pages structure
    result = prepare_github_pages_structure()
    if result:
        docs_dir, figure_count = result
        success_count += 1
        print("✅ Step 2 Complete: GitHub Pages structure prepared")
    else:
        print("❌ Step 2 Failed: Structure preparation failed")
        return False
    
    # Final success message
    print(f"\n🎉 GITHUB PAGES PREPARATION COMPLETE!")
    print(f"✅ {success_count}/{total_steps} steps completed successfully")
    
    project_root = find_project_root()
    docs_path = docs_dir.relative_to(project_root)
    
    print(f"\n📋 NEXT STEPS FOR GITHUB PAGES:")
    print("=" * 40)
    print("1. Commit and push the new docs/ folder:")
    print(f"   git add {docs_path}")
    print("   git commit -m 'Add GitHub Pages deployment structure'")
    print("   git push")
    print("\n2. Enable GitHub Pages in repository settings:")
    print("   • Go to Settings > Pages")
    print("   • Source: Deploy from a branch")
    print("   • Branch: main")
    print(f"   • Folder: /{docs_path}")
    print("\n3. Set up GitHub Actions (next step)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)