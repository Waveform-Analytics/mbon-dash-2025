#!/usr/bin/env python3
"""
Prepare Netlify Deployment Folder

This script:
1. Creates a netlify_deploy/ folder
2. Copies the HTML report 
3. Copies all generated figures
4. Updates HTML to use local image paths
5. Creates a complete folder ready for Netlify Drop

Usage:
    python prepare_netlify_deploy.py
"""

import shutil
import re
from pathlib import Path
import sys

def prepare_netlify_deployment():
    """Prepare complete netlify deployment folder."""
    
    print("🌐 PREPARING NETLIFY DEPLOYMENT")
    print("="*50)
    
    # Create deployment directory
    deploy_dir = Path("netlify_deploy")
    deploy_dir.mkdir(exist_ok=True)
    
    # Step 1: Copy HTML file
    html_file = Path("Marine_Acoustic_Discovery_Report_v2.html")
    if html_file.exists():
        shutil.copy2(html_file, deploy_dir / "index.html")
        print(f"✅ Copied HTML report -> index.html")
    else:
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    # Step 2: Copy all PNG figures
    figure_count = 0
    for png_file in Path("output").rglob("*.png"):
        # Create a clean filename for web deployment
        clean_name = f"{png_file.parent.name}_{png_file.name}".replace(" ", "_")
        dest_path = deploy_dir / clean_name
        shutil.copy2(png_file, dest_path)
        print(f"✅ Copied: {png_file} -> {clean_name}")
        figure_count += 1
    
    # Step 3: Update HTML to use local image paths
    index_file = deploy_dir / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace output/path/to/file.png with local filename
        def replace_image_path(match):
            original_path = match.group(1)
            if 'output' in original_path:
                # Convert output/phase6_temporal_correlation/figures/file.png 
                # to phase6_temporal_correlation_figures_file.png
                clean_path = original_path.replace('output/', '').replace('/', '_')
                return f'src="{clean_path}"'
            return match.group(0)
        
        # Update image source paths
        html_content = re.sub(r'src="([^"]*output[^"]*\.png)"', replace_image_path, html_content)
        
        # Write updated HTML
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Updated image paths in HTML")
    
    # Step 4: Create simple file listing
    files_in_deploy = list(deploy_dir.glob("*"))
    
    print(f"\n📊 DEPLOYMENT SUMMARY")
    print(f"="*30)
    print(f"📁 Deployment folder: {deploy_dir}")
    print(f"📄 Files created: {len(files_in_deploy)}")
    print(f"🖼️  Images: {figure_count}")
    print(f"📝 HTML: {'✅' if (deploy_dir / 'index.html').exists() else '❌'}")
    
    print(f"\n📂 Contents of {deploy_dir}:")
    for file in sorted(files_in_deploy):
        size_kb = file.stat().st_size / 1024
        print(f"   {file.name} ({size_kb:.1f}KB)")
    
    print(f"\n🚀 READY FOR NETLIFY!")
    print("Next steps:")
    print("1. Go to https://app.netlify.com/drop")
    print(f"2. Drag the entire '{deploy_dir}' folder to the drop zone")
    print("3. Get your live URL instantly!")
    
    return True

if __name__ == "__main__":
    success = prepare_netlify_deployment()
    sys.exit(0 if success else 1)