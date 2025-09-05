"""Species filtering utilities for MBON analysis."""

import yaml
import pandas as pd
from pathlib import Path
from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)


class SpeciesFilter:
    """Handles species filtering configuration and application."""
    
    def __init__(self, config_path: Path = None):
        """Initialize species filter.
        
        Args:
            config_path: Path to species filter YAML config file. 
                        If None, will look for config/species_filter.yaml
        """
        if config_path is None:
            # Auto-detect config file location
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            config_path = project_root / "config" / "species_filter.yaml"
        
        self.config_path = Path(config_path)
        self._filter_config = None
        self._keep_species = None
        
    def _load_config(self) -> Dict:
        """Load species filter configuration from YAML file."""
        if self._filter_config is None:
            if not self.config_path.exists():
                logger.warning(f"Species filter config not found: {self.config_path}")
                logger.warning("No species filtering will be applied")
                self._filter_config = {"keep_species": []}
            else:
                logger.info(f"Loading species filter from: {self.config_path}")
                with open(self.config_path, 'r') as f:
                    self._filter_config = yaml.safe_load(f)
                    
                keep_count = len(self._filter_config.get('keep_species', []))
                logger.info(f"Species filter loaded: keeping {keep_count} species")
                
        return self._filter_config
    
    def get_keep_species(self) -> Set[str]:
        """Get set of species short codes to keep.
        
        Returns:
            Set of species short codes that should be kept in analysis
        """
        if self._keep_species is None:
            config = self._load_config()
            keep_list = config.get('keep_species', [])
            self._keep_species = set(keep_list)
            logger.info(f"Species to keep: {sorted(self._keep_species)}")
            
        return self._keep_species
    
    def is_enabled(self) -> bool:
        """Check if species filtering is enabled (config file exists and has species).
        
        Returns:
            True if filtering should be applied, False otherwise
        """
        if not self.config_path.exists():
            return False
            
        keep_species = self.get_keep_species()
        return len(keep_species) > 0
    
    def filter_species_columns(self, dataframe: pd.DataFrame, 
                              column_mappings: pd.DataFrame) -> pd.DataFrame:
        """Filter a dataframe to only include specified species columns.
        
        Args:
            dataframe: DataFrame with detection data
            column_mappings: DataFrame with species column mappings (from det_column_names.csv)
            
        Returns:
            DataFrame with only the specified species columns retained
        """
        if not self.is_enabled():
            logger.info("Species filtering disabled - returning original dataframe")
            return dataframe
            
        if column_mappings.empty:
            logger.warning("No column mappings available - cannot filter species")
            return dataframe
            
        keep_species = self.get_keep_species()
        
        # Get the mapping from short codes to long names (column headers)
        species_mapping = dict(zip(column_mappings['short_name'], column_mappings['long_name']))
        
        # Find columns to keep (non-species columns + specified species)
        columns_to_keep = []
        species_columns_removed = []
        species_columns_kept = []
        
        for col in dataframe.columns:
            # Check if this is a species column by looking for it in long_name mappings
            is_species_column = col in column_mappings['long_name'].values
            
            if not is_species_column:
                # Keep non-species columns (Date, Time, etc.)
                columns_to_keep.append(col)
            else:
                # This is a species column - check if we should keep it
                # Find the short code for this long name
                short_code = None
                for short, long_name in species_mapping.items():
                    if long_name == col:
                        short_code = short
                        break
                
                if short_code and short_code in keep_species:
                    columns_to_keep.append(col)
                    species_columns_kept.append(col)
                else:
                    species_columns_removed.append(col)
        
        # Filter the dataframe
        filtered_df = dataframe[columns_to_keep].copy()
        
        logger.info(f"Species filtering applied:")
        logger.info(f"  - Species columns kept: {len(species_columns_kept)} ({species_columns_kept})")
        logger.info(f"  - Species columns removed: {len(species_columns_removed)} ({species_columns_removed})")
        logger.info(f"  - Total columns: {len(dataframe.columns)} -> {len(filtered_df.columns)}")
        
        return filtered_df
    
    def filter_species_counts(self, species_counts: Dict[str, int], 
                            column_mappings: pd.DataFrame) -> Dict[str, int]:
        """Filter species counts dictionary to only include specified species.
        
        Args:
            species_counts: Dictionary mapping species long names to detection counts
            column_mappings: DataFrame with species column mappings
            
        Returns:
            Filtered species counts dictionary
        """
        if not self.is_enabled():
            return species_counts
            
        if column_mappings.empty:
            logger.warning("No column mappings available - cannot filter species counts")
            return species_counts
            
        keep_species = self.get_keep_species()
        
        # Get the mapping from short codes to long names
        species_mapping = dict(zip(column_mappings['short_name'], column_mappings['long_name']))
        
        # Filter the species counts
        filtered_counts = {}
        for long_name, count in species_counts.items():
            # Find the short code for this long name
            short_code = None
            for short, mapped_long in species_mapping.items():
                if mapped_long == long_name:
                    short_code = short
                    break
            
            if short_code and short_code in keep_species:
                filtered_counts[long_name] = count
        
        logger.debug(f"Species counts filtered: {len(species_counts)} -> {len(filtered_counts)}")
        return filtered_counts
    
    def get_filtered_species_mapping(self, column_mappings: pd.DataFrame) -> pd.DataFrame:
        """Get filtered species mapping containing only the species to keep.
        
        Args:
            column_mappings: DataFrame with all species column mappings
            
        Returns:
            DataFrame with only the species to keep
        """
        if not self.is_enabled():
            return column_mappings
            
        keep_species = self.get_keep_species()
        
        # Filter the mappings to only include species we want to keep
        filtered_mappings = column_mappings[
            column_mappings['short_name'].isin(keep_species)
        ].copy()
        
        logger.info(f"Species mappings filtered: {len(column_mappings)} -> {len(filtered_mappings)}")
        return filtered_mappings