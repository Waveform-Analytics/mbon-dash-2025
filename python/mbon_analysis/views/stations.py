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
        
        # Get available stations from detection files (stations with data)
        stations_with_detection_data = loader.get_available_stations()
        available_years = loader.get_available_years()
        
        # Get ALL unique stations from deployment metadata
        all_unique_stations = deployment_df['Station'].dropna().unique()
        
        # Process station data for ALL stations
        stations = []
        
        for station_id in all_unique_stations:
            # Find deployment records for this station
            station_deployments = deployment_df[
                deployment_df['Station'] == station_id
            ]
            
            if not station_deployments.empty:
                # Get the first deployment record with valid GPS coordinates
                deployment = None
                for _, dep in station_deployments.iterrows():
                    if pd.notna(dep.get('GPS Lat')) and pd.notna(dep.get('GPS Long')):
                        deployment = dep
                        break
                
                # If no valid GPS found, use first record
                if deployment is None:
                    deployment = station_deployments.iloc[0]
                
                # Determine data availability
                has_detection_data = station_id in stations_with_detection_data
                has_acoustic_indices = station_id in ['9M', '14M', '37M']
                
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
                        "years": available_years if has_detection_data else [],
                        "detection_data": has_detection_data,
                        "environmental_data": has_detection_data,  # Environmental data available where detection data exists
                        "acoustic_indices": has_acoustic_indices
                    }
                }
                
                # Add deployment periods
                for _, dep in station_deployments.iterrows():
                    if pd.notna(dep.get('Start date')):
                        period = {
                            "deploy_date": str(dep.get('Start date')) if pd.notna(dep.get('Start date')) else None,
                            "recover_date": str(dep.get('End date')) if pd.notna(dep.get('End date')) else None,
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