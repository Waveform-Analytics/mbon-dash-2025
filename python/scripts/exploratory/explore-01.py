"""Exploratory Analysis Script 01: Multi-Species Acoustic Index Analysis

Implementation of Analysis Approach 3 from notes/ANALYSIS_APPROACH_3.md.
This script systematically analyzes relationships between 50+ acoustic indices 
and 7-8 detection types to identify which acoustic features best predict 
different types of biological activity.

Methodology:
1. Data Preparation: Load manual detections and create overall fish presence
2. Index Reduction: Reduce acoustic indices using correlation analysis
3. Automated Screening: Test all species × index combinations
4. Transition Analysis: Focus on promising combinations for detailed analysis
5. Pattern Discovery: Identify species groupings and index categorizations

Scientific Goal:
Identify 3-5 "super indices" that can reliably predict species presence
and provide 2-6 hour lead time for chorus events with >70% detection rate.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import cohen_kappa_score
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

repo_root = project_root.parent

try:
    from mbon_analysis.data.loaders import create_loader
    from mbon_analysis.analysis.correlation import CorrelationAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Project root: {project_root}")
    print(f"Looking for mbon_analysis at: {project_root / 'mbon_analysis'}")
    print(f"mbon_analysis exists: {(project_root / 'mbon_analysis').exists()}")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('explore_01_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

class MultiSpeciesAcousticAnalyzer:
    """Comprehensive analyzer for multi-species acoustic index relationships.
    
    This class implements the complete pipeline from Analysis Approach 3:
    - Data loading and preparation
    - Species aggregation (overall fish presence)
    - Acoustic index reduction via correlation analysis
    - Automated screening of species × index combinations
    - Transition analysis for chorus events
    - Performance metrics and visualization generation
    """
    
    def __init__(self, data_root: Optional[Path] = None):
        """Initialize analyzer with data loader and empty containers.
        
        Args:
            data_root: Path to data directory. If None, uses default.
        """
        self.loader = create_loader(data_root)
        self.manual_detections = None
        self.acoustic_indices = None
        self.species_mapping = None
        self.reduced_indices = None
        self.screening_results = None
        
        logger.info("MultiSpeciesAcousticAnalyzer initialized")
    
    def load_manual_detections(self) -> pd.DataFrame:
        """Load manual detections from all stations and years into single DataFrame.
        
        Returns:
            Combined DataFrame with manual detections from all available stations/years
        """
        logger.info("Loading manual detection data from all stations and years...")
        
        all_detections = []
        stations = self.loader.get_available_stations()
        years = self.loader.get_available_years()
        
        logger.info(f"Available stations: {stations}")
        logger.info(f"Available years: {years}")
        
        for station in stations:
            for year in years:
                try:
                    df = self.loader.load_detection_data(station, year)
                    
                    # Add metadata columns
                    df['station'] = station
                    df['year'] = year
                    
                    # Ensure datetime column
                    if 'Date' in df.columns or 'Date ' in df.columns:
                        date_col = 'Date' if 'Date' in df.columns else 'Date '
                        df['datetime'] = pd.to_datetime(df[date_col])
                    elif 'Date' not in df.columns:
                        raise ValueError(
                            f"Required column 'Date' not found in detection data for {station} {year}")

                    all_detections.append(df)
                    logger.info(f"Loaded {len(df)} records from {station} {year}")
                    
                except FileNotFoundError as e:
                    logger.warning(f"File not found for {station} {year}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error loading data for {station} {year}: {e}")
                    continue
        
        if not all_detections:
            raise ValueError("No detection data could be loaded")
        
        # Combine all dataframes
        self.manual_detections = pd.concat(all_detections, ignore_index=True)
        logger.info(f"Combined manual detections: {len(self.manual_detections)} total records")
        
        # Load species mapping for column interpretation
        try:
            self.species_mapping = self.loader.load_species_mapping()
            species_names = self.species_mapping["long_name"][
                self.species_mapping["keep_species"] == 1].tolist()
            logger.info(f"Loaded species mapping for {len(self.species_mapping)} species")
            # Filter manual detections for info type or keep_species=1
            info_mask = self.species_mapping[self.species_mapping['type'] == 'info']["long_name"].tolist()
            keep_species_mask = self.species_mapping[self.species_mapping['keep_species'] == 1]["long_name"].tolist()
            self.manual_detections = self.manual_detections[info_mask + keep_species_mask]
            logger.info(f"Species to include: {species_names}")

            # Extract station from Deployment Info column
            if 'Deployment ID' in self.manual_detections.columns:
                self.manual_detections['station'] = \
                self.manual_detections['Deployment ID'].str.split('_').str[0]

            # Extract year from datetime column
            if 'Date' in self.manual_detections.columns:
                self.manual_detections['year'] = self.manual_detections[
                    'Date'].dt.year

            logger.info(f"Added station and year columns to manual detections")
        except Exception as e:
            logger.warning(f"Could not load species mapping: {e}")
        
        return self.manual_detections
    
    def identify_species_columns(self) -> List[str]:
        """Identify species detection columns from the manual detections.
        
        Returns:
            List of column names that contain species detection data
        """
        if self.manual_detections is None:
            raise ValueError("Manual detections not loaded. Call load_manual_detections() first.")


        # Find species to include in the analysis
        if self.species_mapping is not None:
            # Use keep_species mapping (1 = keep, 0 = exclude) 
            species_columns = list(
                self.species_mapping[self.species_mapping['keep_species'] == 1][
                    'long_name'])
        else:
            species_columns = []

        logger.info(f"Identified {len(species_columns)} species columns: {species_columns[:10]}{'...' if len(species_columns) > 10 else ''}")
        return species_columns
    
    def create_overall_fish_presence(self) -> pd.DataFrame:
        """Create overall fish presence variable by aggregating across all species.
        
        Implementation of Step 1.1 from Analysis Approach 3.
        Creates three aggregate measures:
        - intensity: Maximum intensity across all species
        - diversity: Number of species present (>0)
        - total_activity: Sum of all intensities
        
        Returns:
            DataFrame with original data plus overall fish presence columns
        """
        logger.info("Creating overall fish presence variables...")
        
        species_columns = self.identify_species_columns()
        
        if not species_columns:
            logger.warning("No species columns identified")
            return self.manual_detections

        # Create species detection matrix (ensure numeric, fill NaN with 0)
        species_data = self.manual_detections[
            species_columns].apply(pd.to_numeric,errors='coerce').fillna(0)

        # Create species detection matrix (ensure numeric, fill NaN with 0)
        species_data = self.manual_detections[
            species_columns].apply(pd.to_numeric, errors='coerce').fillna(0)

        # Split species by group based on species_mapping
        fish_columns = []
        dolphin_columns = []
        vessel_columns = []

        for col in species_columns:
            group = self.species_mapping[self.species_mapping['long_name'] == col][
                'group'].iloc[0]
            if group == 'fish':
                fish_columns.append(col)
            elif group == 'dolphin':
                dolphin_columns.append(col)
            elif group == 'vessel':
                vessel_columns.append(col)

        # Calculate group-specific metrics
        fish_presence = {
            'overall_fish_intensity': species_data[fish_columns].max(axis=1),
            'overall_fish_diversity': (species_data[fish_columns] > 0).sum(axis=1),
            'overall_dolphin_counts': species_data[dolphin_columns].sum(axis=1),
            'overall_vessel_presence': species_data[vessel_columns].max(axis=1),
            'overall_species_diversity': (
                    (species_data[fish_columns] > 0).sum(
                        axis=1) +  # Number of fish species
                    (species_data[dolphin_columns] > 0).sum(axis=1)
                # Number of dolphin species
            )}

        # Add to main dataframe
        for metric, values in fish_presence.items():
            self.manual_detections[metric] = values
            logger.info(f"Created {metric}: mean={values.mean():.3f}, max={values.max()}, non-zero={(values > 0).sum()}")

        
        
        logger.info("Overall fish presence variables created successfully")
        return self.manual_detections
    
    def load_acoustic_indices(self, stations: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Load acoustic indices data for specified stations.
        
        Args:
            stations: List of stations to load. If None, loads all available.
            
        Returns:
            Dictionary mapping station names to acoustic indices DataFrames
        """
        logger.info("Loading acoustic indices data...")
        
        if stations is None:
            stations = ['9M', '14M', '37M']
        
        indices_data = {}
        
        for station in stations:
            try:
                # Load full bandwidth indices (primary dataset)
                df_full = self.loader.load_acoustic_indices(station, 'FullBW')
                df_full['bandwidth'] = 'FullBW'
                df_full['station'] = station
                
                # Load 8kHz indices as secondary dataset
                try:
                    df_8k = self.loader.load_acoustic_indices(station, '8kHz')
                    df_8k['bandwidth'] = '8kHz'
                    df_8k['station'] = station
                    
                    # Combine both bandwidths
                    indices_data[station] = {
                        'FullBW': df_full,
                        '8kHz': df_8k,
                        'combined': pd.concat([df_full, df_8k], ignore_index=True)
                    }
                except Exception as e:
                    logger.warning(f"Could not load 8kHz data for {station}: {e}")
                    indices_data[station] = {
                        'FullBW': df_full,
                        'combined': df_full
                    }
                
                logger.info(f"Loaded acoustic indices for {station}: {len(df_full)} FullBW records")
                
            except Exception as e:
                logger.error(f"Could not load acoustic indices for {station}: {e}")
                continue
        
        self.acoustic_indices = indices_data
        return indices_data
    
    def reduce_acoustic_indices(self, correlation_threshold: float = 0.85) -> List[str]:
        """Reduce acoustic indices by grouping highly correlated indices.
        
        Implementation of Step 1.2 from Analysis Approach 3.
        Groups indices with correlation > threshold and selects most representative.
        
        Args:
            correlation_threshold: Correlation above which indices are considered redundant
            
        Returns:
            List of reduced index names (expected: 10-15 from ~60)
        """
        logger.info(f"Reducing acoustic indices with correlation threshold {correlation_threshold}...")
        
        if not self.acoustic_indices:
            raise ValueError("Acoustic indices not loaded. Call load_acoustic_indices() first.")
        
        # Combine data from all stations for correlation analysis
        all_indices_data = []
        for station, data in self.acoustic_indices.items():
            # Use FullBW data for primary analysis
            df = data['FullBW'].copy()
            all_indices_data.append(df)
        
        combined_indices = pd.concat(all_indices_data, ignore_index=True)
        
        # Identify acoustic index columns (exclude metadata)
        exclude_cols = {
            'Date_Time', 'datetime', 'Date', 'Time', 'station', 'bandwidth',
            'deployment', 'filename', 'segment'
        }
        
        index_columns = [col for col in combined_indices.columns 
                        if col not in exclude_cols and combined_indices[col].dtype in ['float64', 'int64']]
        
        logger.info(f"Analyzing correlations among {len(index_columns)} acoustic indices...")
        
        # Calculate correlation matrix
        indices_matrix = combined_indices[index_columns].fillna(0)
        correlation_matrix = indices_matrix.corr().abs()
        
        # Find groups of highly correlated indices
        corr_groups = []
        used_indices = set()
        
        for idx in correlation_matrix.index:
            if idx in used_indices:
                continue
                
            # Find indices highly correlated with this one
            high_corr = correlation_matrix[idx][correlation_matrix[idx] > correlation_threshold]
            group = list(high_corr.index)
            
            if len(group) > 1:
                corr_groups.append(group)
                used_indices.update(group)
        
        # Select representative from each group (highest mean correlation with group)
        selected_indices = []
        
        for group in corr_groups:
            if len(group) == 1:
                selected_indices.append(group[0])
            else:
                # Calculate mean correlation with other group members
                group_corr = correlation_matrix.loc[group, group]
                mean_corr = group_corr.mean(axis=1)
                representative = mean_corr.idxmax()
                selected_indices.append(representative)
                
                logger.info(f"Group {group[:3]}{'...' if len(group) > 3 else ''} → {representative}")
        
        # Add remaining uncorrelated indices
        remaining_indices = [idx for idx in index_columns if idx not in used_indices]
        selected_indices.extend(remaining_indices)
        
        self.reduced_indices = selected_indices
        
        logger.info(f"Reduced {len(index_columns)} indices to {len(selected_indices)} representatives")
        logger.info(f"Reduction ratio: {len(selected_indices)/len(index_columns):.2%}")
        
        return selected_indices
    
    def calculate_screening_metrics(self, species: str, index: str, 
                                  detection_data: pd.DataFrame, 
                                  indices_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate quick performance metrics for species × index combination.
        
        Implementation of Step 2.1 from Analysis Approach 3.
        
        Args:
            species: Species column name
            index: Acoustic index name
            detection_data: Manual detection data (2-hour intervals)
            indices_data: Acoustic indices data (1-hour intervals)
            
        Returns:
            Dictionary with correlation, discrimination, detection_rate, lead_time
        """
        try:
            # Align timestamps (both should have datetime columns)
            if 'Date' not in detection_data.columns or 'Date' not in indices_data.columns:
                return {'correlation': np.nan, 'discrimination': np.nan, 
                       'detection_rate': np.nan, 'mean_lead_time': np.nan}
            
            # Clean detection data - remove rows with null dates
            detection_data_clean = detection_data[['Date', species]].copy()
            detection_data_clean['Date'] = pd.to_datetime(detection_data_clean['Date'], errors='coerce')
            detection_data_clean = detection_data_clean.dropna(subset=['Date'])
            
            if len(detection_data_clean) == 0:
                return {'correlation': np.nan, 'discrimination': np.nan, 
                       'detection_rate': np.nan, 'mean_lead_time': np.nan}
            
            # Decimate indices data from 1-hour to 2-hour intervals to match detections
            # Keep every other hour (e.g., 00:00, 02:00, 04:00, etc.)
            indices_data_copy = indices_data.copy()
            indices_data_copy['Date'] = pd.to_datetime(indices_data_copy['Date'], errors='coerce')
            indices_data_copy = indices_data_copy.dropna(subset=['Date'])
            indices_data_copy['hour'] = indices_data_copy['Date'].dt.hour
            
            # Filter to even hours only (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22)
            indices_decimated = indices_data_copy[indices_data_copy['hour'] % 2 == 0].copy()
            indices_decimated = indices_decimated.drop('hour', axis=1)
            
            if len(indices_decimated) == 0:
                return {'correlation': np.nan, 'discrimination': np.nan, 
                       'detection_rate': np.nan, 'mean_lead_time': np.nan}
            
            # Merge on datetime with tolerance for slight time differences
            merged = pd.merge_asof(
                detection_data_clean.sort_values('Date'),
                indices_decimated[['Date', index]].sort_values('Date'),
                on='Date',
                tolerance=pd.Timedelta('30min'),  # Reduced tolerance since we're now aligned
                direction='nearest'
            ).dropna()
            
            if len(merged) < 10:  # Minimum data requirement
                return {'correlation': np.nan, 'discrimination': np.nan, 
                       'detection_rate': np.nan, 'mean_lead_time': np.nan}
            
            species_vals = merged[species]
            index_vals = merged[index]
            
            # 1. Correlation (Spearman for non-parametric)
            correlation, _ = stats.spearmanr(species_vals, index_vals)
            
            # 2. Discrimination (effect size between quiet and chorus)
            quiet_mask = species_vals == 0
            chorus_mask = species_vals >= 3
            
            if quiet_mask.sum() > 0 and chorus_mask.sum() > 0:
                quiet_values = index_vals[quiet_mask]
                chorus_values = index_vals[chorus_mask]
                
                # Cohen's d effect size
                pooled_std = np.sqrt(((len(quiet_values) - 1) * quiet_values.var() + 
                                    (len(chorus_values) - 1) * chorus_values.var()) / 
                                   (len(quiet_values) + len(chorus_values) - 2))
                
                discrimination = abs(chorus_values.mean() - quiet_values.mean()) / pooled_std if pooled_std > 0 else 0
            else:
                discrimination = np.nan
            
            # 3. Detection Rate (% of high-intensity events with acoustic anomaly)
            high_intensity_mask = species_vals >= 2
            if high_intensity_mask.sum() > 0:
                # Define "acoustic anomaly" as index value > 75th percentile
                index_threshold = np.percentile(index_vals, 75)
                anomaly_mask = index_vals > index_threshold
                
                detection_rate = (high_intensity_mask & anomaly_mask).sum() / high_intensity_mask.sum()
            else:
                detection_rate = np.nan
            
            # 4. Lead Time (simplified: look for index increases before intensity increases)
            # This is a placeholder - full implementation would require more sophisticated time series analysis
            lead_time = np.nan  # Would need sliding window analysis
            
            return {
                'correlation': correlation,
                'discrimination': discrimination,
                'detection_rate': detection_rate,
                'mean_lead_time': lead_time
            }
            
        except Exception as e:
            logger.warning(f"Error calculating metrics for {species} × {index}: {e}")
            return {'correlation': np.nan, 'discrimination': np.nan, 
                   'detection_rate': np.nan, 'mean_lead_time': np.nan}
    
    def automated_screening(self) -> pd.DataFrame:
        """Run automated screening across all species × index combinations.
        
        Implementation of Step 2.2 from Analysis Approach 3.
        
        Returns:
            DataFrame with screening results matrix
        """
        logger.info("Starting automated screening of species × index combinations...")
        
        if self.manual_detections is None or not self.acoustic_indices or not self.reduced_indices:
            raise ValueError("Data not prepared. Run data loading and index reduction first.")
        
        # Get species list (including overall fish presence)
        species_columns = self.identify_species_columns()
        species_list = species_columns + [
            'overall_fish_intensity', 
            'overall_fish_diversity',
            'overall_dolphin_counts',
            'overall_vessel_presence',
            'overall_species_diversity' # fish + dolphins
        ]
        
        screening_results = []
        
        # Screen each station separately first
        for station, indices_dict in self.acoustic_indices.items():
            station_detections = self.manual_detections[self.manual_detections['station'] == station].copy()
            
            if len(station_detections) == 0:
                logger.warning(f"No detection data for station {station}")
                continue
            
            indices_data = indices_dict['FullBW'].copy()
            
            # Ensure datetime columns exist
            if 'Date' in indices_data.columns:
                indices_data['datetime'] = pd.to_datetime(indices_data['Date'])
            
            logger.info(f"Screening {len(species_list)} detection types × {len(self.reduced_indices)} indices for station {station}")
            
            for species in species_list:
                if species not in station_detections.columns:
                    continue
                    
                for index in self.reduced_indices:
                    if index not in indices_data.columns:
                        continue
                    
                    metrics = self.calculate_screening_metrics(
                        species, index, station_detections, indices_data
                    )
                    
                    result = {
                        'station': station,
                        'species': species,
                        'index': index,
                        **metrics
                    }
                    
                    screening_results.append(result)
        
        self.screening_results = pd.DataFrame(screening_results)
        
        logger.info(f"Screening completed: {len(self.screening_results)} combinations analyzed")
        logger.info(f"Valid correlations: {(~self.screening_results['correlation'].isna()).sum()}")
        
        return self.screening_results
    
    def identify_top_performers(self, n_top: int = 3) -> Dict[str, Any]:
        """Identify top-performing species × index combinations.
        
        Implementation of Step 2.3 from Analysis Approach 3.
        
        Args:
            n_top: Number of top performers to identify per category
            
        Returns:
            Dictionary with top performers by different criteria
        """
        logger.info("Identifying top-performing combinations...")
        
        if self.screening_results is None:
            raise ValueError("Screening not completed. Run automated_screening() first.")
        
        results = self.screening_results.dropna(subset=['correlation', 'discrimination', 'detection_rate'])
        
        if len(results) == 0:
            logger.warning("No valid screening results found")
            return {}
        
        top_performers = {
            # Top indices per species (highest correlation)
            'top_indices_per_species': {},
            
            # Top species per index
            'top_species_per_index': {},
            
            # Universal performers (good across multiple species)
            'universal_performers': [],
            
            # Best discrimination (chorus vs quiet)
            'best_discrimination': results.nlargest(n_top, 'discrimination'),
            
            # Best detection rate
            'best_detection_rate': results.nlargest(n_top, 'detection_rate'),
            
            # Best correlation
            'best_correlation': results.nlargest(n_top, 'correlation')
        }
        
        # Top indices per species
        for species in results['species'].unique():
            species_results = results[results['species'] == species]
            top_for_species = species_results.nlargest(n_top, 'correlation')
            top_performers['top_indices_per_species'][species] = top_for_species
        
        # Top species per index
        for index in results['index'].unique():
            index_results = results[results['index'] == index]
            top_for_index = index_results.nlargest(n_top, 'correlation')
            top_performers['top_species_per_index'][index] = top_for_index
        
        # Universal performers (indices that work well for many species)
        index_performance = results.groupby('index').agg({
            'correlation': ['mean', 'count'],
            'detection_rate': 'mean',
            'discrimination': 'mean'
        }).round(3)
        
        index_performance.columns = ['_'.join(col).strip() for col in index_performance.columns]
        
        # Filter for indices tested on multiple species with good average performance
        universal_candidates = index_performance[
            (index_performance['correlation_count'] >= 3) &  # Tested on at least 3 species
            (index_performance['correlation_mean'] > 0.3)    # Average correlation > 0.3
        ].sort_values('correlation_mean', ascending=False)
        
        top_performers['universal_performers'] = universal_candidates.head(n_top)
        
        logger.info(f"Top performers identified:")
        logger.info(f"- Universal performers: {len(universal_candidates)}")
        logger.info(f"- Species analyzed: {len(top_performers['top_indices_per_species'])}")
        logger.info(f"- Indices analyzed: {len(top_performers['top_species_per_index'])}")
        
        return top_performers
    
    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report of analysis results.
        
        Returns:
            Formatted string report
        """
        if self.screening_results is None:
            return "Analysis not completed. Run full pipeline first."
        
        report_lines = [
            "=" * 80,
            "MULTI-SPECIES ACOUSTIC INDEX ANALYSIS REPORT",
            "=" * 80,
            "",
            f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "DATA SUMMARY:",
            f"- Manual detections loaded: {len(self.manual_detections) if self.manual_detections is not None else 0:,} records",
            f"- Species analyzed: {len(self.identify_species_columns()) if self.manual_detections is not None else 0}",
            f"- Acoustic indices (original): {len(self.acoustic_indices[list(self.acoustic_indices.keys())[0]]['FullBW'].columns) - 4 if self.acoustic_indices else 0} indices",
            f"- Acoustic indices (reduced): {len(self.reduced_indices) if self.reduced_indices else 0} indices",
            f"- Stations analyzed: {list(self.acoustic_indices.keys()) if self.acoustic_indices else []}",
            "",
            "SCREENING RESULTS:",
            f"- Total combinations tested: {len(self.screening_results):,}",
            f"- Valid correlations: {(~self.screening_results['correlation'].isna()).sum():,}",
            f"- Mean correlation: {self.screening_results['correlation'].mean():.3f} ± {self.screening_results['correlation'].std():.3f}",
            f"- Best correlation: {self.screening_results['correlation'].max():.3f}",
            f"- Best discrimination: {self.screening_results['discrimination'].max():.3f}",
            f"- Best detection rate: {self.screening_results['detection_rate'].max():.3f}",
            "",
        ]
        
        # Add top performers summary
        try:
            top_performers = self.identify_top_performers()
            
            report_lines.extend([
                "TOP PERFORMERS:",
                ""
            ])
            
            if 'best_correlation' in top_performers and len(top_performers['best_correlation']) > 0:
                report_lines.append("Best Correlations:")
                for _, row in top_performers['best_correlation'].head(5).iterrows():
                    report_lines.append(
                        f"  {row['species']} × {row['index']}: r={row['correlation']:.3f} "
                        f"(station {row['station']})"
                    )
                report_lines.append("")
            
            if 'universal_performers' in top_performers and len(top_performers['universal_performers']) > 0:
                report_lines.append("Universal Performers (good across multiple species):")
                for index, stats in top_performers['universal_performers'].head(5).iterrows():
                    report_lines.append(
                        f"  {index}: mean_r={stats['correlation_mean']:.3f} "
                        f"(tested on {int(stats['correlation_count'])} species)"
                    )
                report_lines.append("")
                
        except Exception as e:
            report_lines.append(f"Error generating top performers summary: {e}")
            report_lines.append("")
        
        report_lines.extend([
            "NEXT STEPS:",
            "1. Focus detailed transition analysis on top performers",
            "2. Implement lead time calculation for best combinations",
            "3. Generate species-specific detection rules",
            "4. Validate findings with independent data",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, output_dir: Path = None) -> None:
        """Save analysis results to files.
        
        Args:
            output_dir: Directory to save results. If None, uses current directory.
        """
        if output_dir is None:
            output_dir = Path.cwd() / "analysis_results"
        
        output_dir.mkdir(exist_ok=True)
        
        # Save screening results
        if self.screening_results is not None:
            self.screening_results.to_csv(output_dir / "screening_results.csv", index=False)
            logger.info(f"Screening results saved to {output_dir / 'screening_results.csv'}")
        
        # Save reduced indices list
        if self.reduced_indices is not None:
            pd.Series(self.reduced_indices).to_csv(
                output_dir / "reduced_indices.csv", header=['index'], index=False
            )
            logger.info(f"Reduced indices saved to {output_dir / 'reduced_indices.csv'}")
        
        # Save summary report
        report = self.generate_summary_report()
        with open(output_dir / "analysis_summary.txt", 'w') as f:
            f.write(report)
        
        logger.info(f"Summary report saved to {output_dir / 'analysis_summary.txt'}")

def main():
    """Run the complete multi-species acoustic analysis pipeline."""
    
    print("Starting Multi-Species Acoustic Index Analysis...")
    print("Implementation of Analysis Approach 3")
    print("=" * 60)
    
    try:
        # Initialize analyzer
        path_to_data = repo_root / "data"
        analyzer = MultiSpeciesAcousticAnalyzer(path_to_data)
        
        # Phase 1: Data Preparation
        print("\nPhase 1: Data Preparation and Reduction")
        print("-" * 40)
        
        # Load manual detections from all stations/years
        detections = analyzer.load_manual_detections()
        print(f"✓ Loaded {len(detections):,} manual detection records")
        
        # Create overall fish presence variable
        detections_with_fish = analyzer.create_overall_fish_presence()
        print("✓ Created overall fish presence variables")
        
        # Load acoustic indices
        indices = analyzer.load_acoustic_indices(['9M', '14M', '37M'])
        print(f"✓ Loaded acoustic indices for {len(indices)} stations")
        
        # Reduce acoustic indices via correlation analysis
        reduced_indices = analyzer.reduce_acoustic_indices(correlation_threshold=0.85)
        print(f"✓ Reduced indices from ~60 to {len(reduced_indices)}")
        
        # Phase 2: Automated Screening
        print("\nPhase 2: Automated Screening")
        print("-" * 30)
        
        # Run comprehensive screening
        screening_results = analyzer.automated_screening()
        print(f"✓ Screened {len(screening_results):,} species × index combinations")
        
        # Identify top performers
        top_performers = analyzer.identify_top_performers()
        print("✓ Identified top-performing combinations")
        
        # Phase 3: Results and Reporting
        print("\nPhase 3: Results and Reporting")
        print("-" * 32)
        
        # Generate and display summary report
        report = analyzer.generate_summary_report()
        print(report)
        
        # Save results
        analyzer.save_results()
        print("\n✓ Results saved to analysis_results/ directory")
        
        print("\nAnalysis completed successfully!")
        print("\nNext steps:")
        print("1. Review screening_results.csv for detailed metrics")
        print("2. Focus on top-performing combinations for detailed analysis")
        print("3. Implement transition analysis for chorus prediction")
        print("4. Generate species-specific detection rules")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\nError: {e}")
        print("Check explore_01_analysis.log for detailed error information.")
        raise

if __name__ == "__main__":
    main()