#!/usr/bin/env python3
"""
Generate the notebooks documentation page from marimo_notebooks.txt

This script reads the marimo notebook registry and automatically generates
the MkDocs notebooks page with embedded iframe viewers.

Usage:
    uv run scripts/build_notebook_docs.py
    
Or automatically during MkDocs build (if configured)
"""

from pathlib import Path
import sys
from datetime import datetime
from typing import List, Dict, Optional


def parse_notebook_registry(registry_path: Path) -> List[Dict[str, str]]:
    """
    Parse the marimo_notebooks.txt file to extract notebook information.
    
    Args:
        registry_path: Path to the marimo_notebooks.txt file
        
    Returns:
        List of dictionaries with notebook info
    """
    notebooks = []
    
    if not registry_path.exists():
        print(f"Warning: {registry_path} not found!")
        return notebooks
    
    with open(registry_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse pipe-delimited format
            parts = [part.strip() for part in line.split('|')]
            
            if len(parts) < 3:
                print(f"Warning: Line {line_num} has insufficient parts, skipping: {line}")
                continue
            
            notebook = {
                'title': parts[0],
                'description': parts[1],
                'url': parts[2],
                'local_file': parts[3] if len(parts) > 3 else None
            }
            
            # Basic URL validation
            if not notebook['url'].startswith('https://static.marimo.app/'):
                print(f"Warning: Line {line_num} doesn't look like a marimo static URL: {notebook['url']}")
                continue
            
            notebooks.append(notebook)
    
    return notebooks


def generate_notebook_embed(notebook: Dict[str, str]) -> str:
    """
    Generate the HTML/markdown for embedding a single notebook.
    
    Args:
        notebook: Dictionary with notebook info (title, description, url, local_file)
        
    Returns:
        Markdown string with iframe embed
    """
    # Create a clean ID for anchoring
    notebook_id = notebook['title'].lower().replace(' ', '-').replace('_', '-')
    
    # Build the embed HTML
    embed_html = f'''
### {notebook['title']}

{notebook['description']}

<div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin: 20px 0;">
  <div style="background: #f5f5f5; padding: 10px; font-weight: bold;">
    📓 {notebook['title']}
  </div>
  <iframe src="{notebook['url']}" 
          width="100%" height="700px" frameborder="0" 
          style="display: block;"
          loading="lazy">
    <p>Your browser does not support iframes. <a href="{notebook['url']}" target="_blank">View notebook directly</a></p>
  </iframe>
  <div style="padding: 10px; text-align: center; background: #fafafa; font-size: 0.9em;">
    <a href="{notebook['url']}" target="_blank">View full notebook →</a>'''
    
    # Add local file link if available
    if notebook['local_file']:
        embed_html += f''' | <a href="https://github.com/Waveform-Analytics/mbon-dash-2025/blob/main/{notebook['local_file']}" target="_blank">Source code →</a>'''
    
    embed_html += '''
  </div>
</div>

---
'''
    
    return embed_html


def generate_notebooks_page(notebooks: List[Dict[str, str]]) -> str:
    """
    Generate the complete notebooks.md page content.
    
    Args:
        notebooks: List of notebook dictionaries
        
    Returns:
        Complete markdown content for the page
    """
    # Page header
    content = '''# Interactive Notebooks

Welcome to the MBON interactive notebook collection! These notebooks demonstrate key workflows and analysis patterns using the `mbon_analysis` package.

!!! info "About These Notebooks"
    These are [marimo](https://marimo.io) notebooks hosted on marimo's static platform. They provide interactive Python code with preserved outputs and can be viewed directly in your browser.

!!! tip "Working with Notebooks"
    - **View online**: Click any notebook below to explore interactively
    - **Run locally**: Install marimo (`pip install marimo`) and run the source files
    - **Create your own**: Upload to [static.marimo.app](https://static.marimo.app) and add to the registry

'''
    
    if not notebooks:
        content += '''
!!! warning "No Notebooks Available"
    No notebooks are currently registered. To add notebooks:
    
    1. Create a marimo notebook locally
    2. Upload to [static.marimo.app](https://static.marimo.app)
    3. Add the URL to `docs_site/marimo_notebooks.txt`
    4. Run `uv run scripts/build_notebook_docs.py` to regenerate this page

'''
        return content
    
    # Table of contents
    content += f"## Available Notebooks ({len(notebooks)})\n\n"
    
    for i, notebook in enumerate(notebooks, 1):
        notebook_id = notebook['title'].lower().replace(' ', '-').replace('_', '-')
        content += f"{i}. **[{notebook['title']}](#{notebook_id})** - {notebook['description']}\n"
    
    content += "\n---\n\n"
    
    # Add each notebook embed
    for notebook in notebooks:
        content += generate_notebook_embed(notebook)
    
    # Footer
    content += '''
## Creating New Notebooks

To add a new notebook to this collection:

1. **Create locally**: `marimo new scripts/notebooks/your_notebook.py`
2. **Develop**: `marimo edit scripts/notebooks/your_notebook.py`
3. **Upload**: Go to [static.marimo.app](https://static.marimo.app) and upload your notebook
4. **Register**: Add the static URL to `docs_site/marimo_notebooks.txt`
5. **Build**: Run `uv run scripts/build_notebook_docs.py` to update this page

### Local Development

To work with these notebooks locally:

```bash
# Install marimo
pip install marimo

# Run a notebook interactively
marimo run scripts/notebooks/0.0_loading_data.py

# Edit a notebook
marimo edit scripts/notebooks/0.0_loading_data.py
```
'''
    
    return content


def main():
    """Main execution function."""
    print("MBON Notebook Documentation Generator")
    print("=" * 50)
    
    # Find project root and files
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    registry_file = project_root / "docs_site" / "marimo_notebooks.txt"
    docs_file = project_root / "docs_site" / "notebooks.md"
    
    print(f"Reading notebook registry: {registry_file}")
    print(f"Output documentation: {docs_file}")
    
    # Parse the notebook registry
    notebooks = parse_notebook_registry(registry_file)
    
    if not notebooks:
        print("⚠️  No notebooks found in registry!")
    else:
        print(f"✓ Found {len(notebooks)} registered notebooks:")
        for notebook in notebooks:
            print(f"  - {notebook['title']}")
    
    # Generate the documentation page
    print(f"\n📝 Generating notebooks.md...")
    page_content = generate_notebooks_page(notebooks)
    
    # Write the file
    with open(docs_file, 'w') as f:
        f.write(page_content)
    
    print(f"✅ Documentation generated successfully!")
    print(f"   Output: {docs_file}")
    print(f"   Notebooks: {len(notebooks)} embedded")
    
    # Summary
    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. Review the generated notebooks.md file")
    print("2. Run 'uv run mkdocs serve' to preview the documentation")
    print("3. Add more notebooks to marimo_notebooks.txt as needed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())