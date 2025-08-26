"""Station view generators for dashboard frontend."""

from pathlib import Path
from typing import Dict, Any


def generate_station_overview(processed_data_dir: Path) -> Dict[str, Any]:
    """Generate station overview optimized for interactive map.
    
    This is a minimal implementation to make tests pass initially.
    Will be enhanced in subsequent TDD iterations.
    
    Args:
        processed_data_dir: Path to directory with processed JSON files
        
    Returns:
        Dictionary with stations and metadata for frontend consumption
    """
    # Minimal implementation to pass basic structure tests
    return {
        'stations': [],
        'metadata': {
            'generated_at': '2024-01-01T12:00:00Z',
            'data_sources': [],
            'total_stations': 0
        }
    }