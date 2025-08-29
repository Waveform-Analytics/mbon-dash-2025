"""Stations view generator."""

from typing import Dict, Any, List
import pandas as pd
from .base import BaseViewGenerator
from ..data.loaders import create_loader


class StationsViewGenerator(BaseViewGenerator):
    """Generate stations.json view with station metadata and deployment info."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate stations view data.
        
        Returns:
            Dictionary with stations data optimized for dashboard
        """
        loader = create_loader(self.data_root)
        
        # Load deployment metadata
        deployment_df = loader.load_deployment_metadata()
        
        # Get available stations from detection files
        available_stations = loader.get_available_stations()
        available_years = loader.get_available_years()
        
        # Process station data
        stations = []
        
        for station_id in available_stations:
            # Find deployment records for this station
            station_deployments = deployment_df[
                deployment_df['Station'].str.contains(station_id, na=False)
            ]
            
            if not station_deployments.empty:
                # Get the most complete deployment record
                deployment = station_deployments.iloc[0]
                
                station_data = {
                    "id": station_id,
                    "name": f"Station {station_id}",
                    "coordinates": {
                        "latitude": float(deployment.get('GPS Lat', 0)) if pd.notna(deployment.get('GPS Lat')) else None,
                        "longitude": float(deployment.get('GPS Long', 0)) if pd.notna(deployment.get('GPS Long')) else None
                    },
                    "depth_m": float(deployment.get('Depth (m)', 0)) if pd.notna(deployment.get('Depth (m)')) else None,
                    "platform": deployment.get('Platform Type', 'Unknown'),
                    "deployment_periods": [],
                    "data_availability": {
                        "years": available_years,
                        "detection_data": True,  # All available stations have detection data
                        "environmental_data": True,  # All available stations have environmental data
                        "acoustic_indices": station_id in ['9M', '14M', '37M']  # Based on indices files
                    }
                }
                
                # Add deployment periods
                for _, dep in station_deployments.iterrows():
                    if pd.notna(dep.get('Start date')):
                        period = {
                            "deploy_date": dep.get('Start date'),
                            "recover_date": dep.get('End date'),
                            "duration_days": float(dep.get('Duration', 0)) if pd.notna(dep.get('Duration')) else None
                        }
                        station_data["deployment_periods"].append(period)
                
                stations.append(station_data)
        
        # Generate summary statistics
        summary = {
            "total_stations": len(stations),
            "years_covered": available_years,
            "stations_with_indices": len([s for s in stations if s["data_availability"]["acoustic_indices"]]),
            "coordinate_bounds": self._calculate_bounds([s for s in stations if s["coordinates"]["latitude"] and s["coordinates"]["longitude"]])
        }
        
        return {
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "version": "1.0.0",
                "description": "Station metadata and deployment information for MBON dashboard"
            },
            "summary": summary,
            "stations": stations
        }
    
    def _calculate_bounds(self, stations_with_coords: List[Dict]) -> Dict[str, float]:
        """Calculate coordinate bounds for map centering.
        
        Args:
            stations_with_coords: Stations that have valid coordinates
            
        Returns:
            Dictionary with coordinate bounds
        """
        if not stations_with_coords:
            return {"north": None, "south": None, "east": None, "west": None}
        
        lats = [s["coordinates"]["latitude"] for s in stations_with_coords]
        lons = [s["coordinates"]["longitude"] for s in stations_with_coords]
        
        return {
            "north": max(lats),
            "south": min(lats),
            "east": max(lons),
            "west": min(lons)
        }