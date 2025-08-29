"""Project metadata view generator."""

from typing import Dict, Any
import pandas as pd
from .base import BaseViewGenerator


class ProjectMetadataViewGenerator(BaseViewGenerator):
    """Generate project_metadata.json with research context and methods."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate project metadata view data.
        
        Returns:
            Dictionary with project information and research context
        """
        return {
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "version": "1.0.0",
                "description": "Project information and research context for MBON dashboard"
            },
            "project": {
                "title": "MBON Marine Biodiversity Dashboard",
                "subtitle": "Exploring Acoustic Indices as Marine Biodiversity Predictors",
                "organization": "Marine Biodiversity Observation Network (MBON)",
                "principal_investigators": [
                    "Montie Lab Research Team"
                ],
                "funding_sources": [
                    "National Science Foundation",
                    "NOAA Ocean Exploration"
                ],
                "project_period": {
                    "start": "2016",
                    "end": "2023",
                    "data_years": [2018, 2021]
                }
            },
            "research_context": {
                "primary_question": "Can computed acoustic indices help us understand or even predict marine biodiversity patterns as an alternative to labor-intensive manual species detection methods?",
                "objectives": [
                    {
                        "id": "index_reduction",
                        "title": "Index Reduction",
                        "description": "Reduce 56+ acoustic indices to 3-5 'super indices' via Principal Component Analysis",
                        "status": "in_progress"
                    },
                    {
                        "id": "biodiversity_prediction",
                        "title": "Biodiversity Prediction",
                        "description": "Identify indices that best predict species detection patterns",
                        "status": "in_progress"
                    },
                    {
                        "id": "environmental_effects",
                        "title": "Environmental Effects",
                        "description": "Quantify temperature and depth influence on acoustic patterns",
                        "status": "planned"
                    },
                    {
                        "id": "spatial_analysis",
                        "title": "Spatial Analysis",
                        "description": "Compare acoustic environments between monitoring stations",
                        "status": "planned"
                    },
                    {
                        "id": "temporal_stability",
                        "title": "Temporal Stability",
                        "description": "Assess multi-year pattern consistency and seasonal variations",
                        "status": "planned"
                    }
                ],
                "significance": "This research could revolutionize marine biodiversity monitoring by providing automated, continuous assessment methods that complement traditional species surveys."
            },
            "methodology": {
                "data_collection": {
                    "equipment": {
                        "hydrophones": "High-frequency recording units deployed at fixed stations",
                        "environmental_sensors": "Temperature and depth loggers",
                        "deployment_platforms": "Shoreline attachments and fixed moorings"
                    },
                    "sampling_strategy": {
                        "recording_schedule": "Continuous recordings with 2-minute samples every hour",
                        "deployment_duration": "3-month intervals with quarterly maintenance",
                        "spatial_coverage": "3 stations across different habitat types"
                    }
                },
                "data_processing": {
                    "manual_analysis": {
                        "description": "Expert annotation of species vocalizations",
                        "temporal_resolution": "2-hour analysis windows",
                        "species_detected": 33
                    },
                    "acoustic_analysis": {
                        "description": "Automated computation of acoustic indices",
                        "temporal_resolution": "Hourly calculations",
                        "indices_computed": 56,
                        "frequency_bands": ["Full bandwidth", "8 kHz limited"]
                    }
                },
                "analytical_approach": {
                    "dimensionality_reduction": "Principal Component Analysis (PCA) to identify key index combinations",
                    "correlation_analysis": "Pearson and Spearman correlations between indices and species detections",
                    "predictive_modeling": "Random Forest and linear regression for biodiversity prediction",
                    "validation": "Cross-validation with held-out time periods"
                }
            },
            "study_area": {
                "location": "Coastal waters of South Carolina, USA",
                "ecosystem": "Subtropical estuarine and nearshore marine environments",
                "coordinates": {
                    "center": {
                        "latitude": 32.21,
                        "longitude": -80.85
                    },
                    "bounding_box": {
                        "north": 32.23,
                        "south": 32.19,
                        "east": -80.79,
                        "west": -80.91
                    }
                },
                "stations": {
                    "count": 3,
                    "names": ["Station 9M", "Station 14M", "Station 37M"],
                    "habitat_types": ["Shallow estuary", "Deep channel", "Nearshore reef"]
                }
            },
            "data_availability": {
                "raw_data": {
                    "audio_recordings": "Available upon request (>1TB)",
                    "processed_data": "Included in dashboard views",
                    "metadata": "Fully available"
                },
                "data_products": [
                    "Species detection matrices",
                    "Acoustic index time series",
                    "Environmental measurements",
                    "Statistical summaries"
                ],
                "access_policy": "Open access for research and educational purposes"
            },
            "citations": {
                "recommended_citation": "MBON Marine Biodiversity Dashboard (2024). Marine Biodiversity Observation Network. https://mbon-dashboard.org",
                "related_publications": [
                    {
                        "authors": "Montie et al.",
                        "year": 2021,
                        "title": "Acoustic indices as proxies for marine biodiversity assessment",
                        "journal": "Marine Ecology Progress Series",
                        "doi": "10.3354/meps00000"
                    }
                ],
                "data_doi": "10.5281/zenodo.0000000"
            }
        }