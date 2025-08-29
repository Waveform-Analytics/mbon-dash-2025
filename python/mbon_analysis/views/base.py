"""Base view generator class."""

import json
from pathlib import Path
from typing import Any, Dict, Union


class BaseViewGenerator:
    """Base class for generating optimized view files for the dashboard."""
    
    def __init__(self, data_root: Union[str, Path], views_root: Union[str, Path] = None):
        """Initialize view generator.
        
        Args:
            data_root: Path to the data directory
            views_root: Path to views output directory (defaults to data_root/views)
        """
        self.data_root = Path(data_root)
        self.views_root = Path(views_root) if views_root else self.data_root / "views"
        
        # Ensure views directory exists
        self.views_root.mkdir(parents=True, exist_ok=True)
    
    def save_view(self, filename: str, data: Dict[str, Any]) -> Path:
        """Save view data to JSON file.
        
        Args:
            filename: Name of the view file (e.g., 'stations.json')
            data: Data to save
            
        Returns:
            Path to saved file
        """
        output_path = self.views_root / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return output_path
    
    def get_file_size_kb(self, filepath: Path) -> float:
        """Get file size in KB.
        
        Args:
            filepath: Path to file
            
        Returns:
            File size in KB
        """
        return filepath.stat().st_size / 1024
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate view data. Override in subclasses.
        
        Returns:
            View data dictionary
        """
        raise NotImplementedError("Subclasses must implement generate_view()")
    
    def create_view(self, filename: str) -> Dict[str, str]:
        """Generate and save a view file.
        
        Args:
            filename: Output filename
            
        Returns:
            Dictionary with file info
        """
        # Generate the view data
        view_data = self.generate_view()
        
        # Save to file
        output_path = self.save_view(filename, view_data)
        
        # Return file info
        return {
            "filename": filename,
            "path": str(output_path),
            "size_kb": round(self.get_file_size_kb(output_path), 2),
            "records": len(view_data) if isinstance(view_data, (list, dict)) else 0
        }