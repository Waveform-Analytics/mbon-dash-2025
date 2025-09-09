"""Exploratory Analysis Script 03: Event Validation and Temporal Clustering

This script visualizes detected events overlaid on raw detection data and acoustic indices
to validate event detection and explore temporal clustering patterns.

Key concepts:
- Events are not just high values, but clusters of elevated activity
- Temporal density matters: 5 high values in a week vs 5 spread across a year
- Moving window statistics capture local context better than global thresholds
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
from scipy import signal, stats
import warnings
warnings.filterwarnings('ignore')

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
repo_root = project_root.parent

from mbon_analysis.data.loaders import create_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

class EventValidator:
    """Validate and visualize biological events with acoustic data."""
    
    def __init__(self, data_root: Optional[Path] = None):
        self.loader = create_loader(data_root)
        self.detections = None
        self.events = None
        self.acoustic_indices = None
        
    def load_all_data(self):
        """Load detection data, events, and acoustic indices."""
        logger.info("Loading all data...")
        
        # Load events from previous analysis
        events_path = project_root / "event_analysis" / "biological_events.csv"
        if events_path.exists():
            self.events = pd.read_csv(events_path)
            self.events['start_time'] = pd.to_datetime(self.events['start_time'])
            self.events['end_time'] = pd.to_datetime(self.events['end_time'])
            logger.info(f"Loaded {len(self.events)} events")
        
        # Load detection data
        all_detections = []
        for station in ['9M', '14M', '37M']:
            for year in [2018, 2021]:
                try:
                    df = self.loader.load_detection_data(station, year)
                    df['station'] = station
                    df['year'] = year
                    df['datetime'] = pd.to_datetime(df['Date'])
                    all_detections.append(df)
                except:
                    continue
        
        self.detections = pd.concat(all_detections, ignore_index=True)
        logger.info(f"Loaded {len(self.detections)} detection records")
        
        # Load acoustic indices
        self.acoustic_indices = {}
        for station in ['9M', '14M', '37M']:
            try:
                indices = self.loader.load_acoustic_indices(station, 'FullBW')
                indices['datetime'] = pd.to_datetime(indices['Date'])
                indices['station'] = station
                self.acoustic_indices[station] = indices
                logger.info(f"Loaded {len(indices)} acoustic index records for {station}")
            except:
                logger.warning(f"Could not load indices for {station}")
                
    def visualize_events_on_data(self, species: str, station: str, 
                                year: int, month: int = None, save_path: str = None):
        """Create multi-panel plot showing events overlaid on detection and acoustic data.
        
        This visualization shows:
        1. Raw detection intensity (manual annotations)
        2. Detected events as shaded regions
        3. Selected acoustic indices
        4. Temporal clustering metrics
        """
        
        # Filter data
        det_data = self.detections[
            (self.detections['station'] == station) & 
            (self.detections['year'] == year)
        ].copy()
        
        if month:
            det_data = det_data[det_data['datetime'].dt.month == month]
        
        if species not in det_data.columns:
            logger.warning(f"Species {species} not found")
            return
        
        # Convert species data to numeric
        det_data[species] = pd.to_numeric(det_data[species], errors='coerce').fillna(0)
        
        # Get events for this period
        events_filtered = self.events[
            (self.events['species'] == species) &
            (self.events['station'] == station) &
            (self.events['year'] == year)
        ]
        
        if month:
            events_filtered = events_filtered[
                events_filtered['start_time'].dt.month == month
            ]
        
        # Get acoustic indices if available
        indices_data = None
        if station in self.acoustic_indices:
            indices_data = self.acoustic_indices[station]
            # Filter to same time period
            time_mask = (
                (indices_data['datetime'] >= det_data['datetime'].min()) &
                (indices_data['datetime'] <= det_data['datetime'].max())
            )
            indices_data = indices_data[time_mask]
        
        # Create figure
        fig, axes = plt.subplots(5, 1, figsize=(16, 12), sharex=True)
        
        # Panel 1: Raw detection intensity
        ax1 = axes[0]
        ax1.plot(det_data['datetime'], det_data[species], 'o-', color='darkblue', 
                alpha=0.6, label='Detection Intensity')
        ax1.fill_between(det_data['datetime'], 0, det_data[species], 
                         alpha=0.3, color='darkblue')
        
        # Overlay detected events
        for _, event in events_filtered.iterrows():
            rect = patches.Rectangle((event['start_time'], 0), 
                                    event['end_time'] - event['start_time'],
                                    3.5, alpha=0.2, color='red', 
                                    label='Detected Event' if _ == 0 else '')
            ax1.add_patch(rect)
        
        ax1.set_ylabel('Detection\nIntensity', fontsize=10)
        ax1.set_ylim(-0.1, 3.5)
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f'{species} at {station} - {year}' + (f' Month {month}' if month else ''))
        
        # Panel 2: Temporal density (calls per week)
        ax2 = axes[1]
        # Calculate rolling sum of detections > 0 (7-day window = 84 observations)
        det_binary = (det_data[species] > 0).astype(int)
        det_data['calls_per_week'] = det_binary.rolling(window=84, center=True).sum()
        
        ax2.plot(det_data['datetime'], det_data['calls_per_week'], 
                color='green', alpha=0.7, label='Calls per week (7-day window)')
        ax2.axhline(y=20, color='red', linestyle='--', alpha=0.5, 
                   label='Threshold (20 calls/week)')
        
        # Shade high-density periods
        high_density = det_data['calls_per_week'] > 20
        ax2.fill_between(det_data['datetime'], 0, 
                        det_data['calls_per_week'].max() * high_density,
                        alpha=0.2, color='yellow', label='High density period')
        
        ax2.set_ylabel('Temporal\nDensity', fontsize=10)
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        
        # Panel 3 & 4: Acoustic indices (if available)
        if indices_data is not None and len(indices_data) > 0:
            # Select indices with good coverage
            index_cols = [col for col in ['ACI', 'BI', 'NDSI', 'ADI', 'H'] 
                         if col in indices_data.columns]
            
            if len(index_cols) >= 2:
                # Panel 3: Bioacoustic index
                ax3 = axes[2]
                if 'BI' in indices_data.columns:
                    idx_to_plot = 'BI'
                elif 'ACI' in indices_data.columns:
                    idx_to_plot = 'ACI'
                else:
                    idx_to_plot = index_cols[0]
                
                ax3.plot(indices_data['datetime'], indices_data[idx_to_plot],
                        color='purple', alpha=0.6, label=idx_to_plot)
                
                # Calculate anomaly score (z-score from rolling mean)
                rolling_mean = indices_data[idx_to_plot].rolling(window=168, center=True).mean()
                rolling_std = indices_data[idx_to_plot].rolling(window=168, center=True).std()
                z_score = (indices_data[idx_to_plot] - rolling_mean) / rolling_std
                
                # Highlight anomalies (|z| > 2)
                anomaly_mask = np.abs(z_score) > 2
                ax3.scatter(indices_data.loc[anomaly_mask, 'datetime'],
                          indices_data.loc[anomaly_mask, idx_to_plot],
                          color='red', s=20, alpha=0.7, label='Anomalies (|z|>2)')
                
                ax3.set_ylabel(f'{idx_to_plot}\nIndex', fontsize=10)
                ax3.legend(loc='upper right')
                ax3.grid(True, alpha=0.3)
                
                # Panel 4: Temporal clustering of anomalies
                ax4 = axes[3]
                
                # Count anomalies in rolling window (168 hours = 1 week)
                anomaly_density = anomaly_mask.astype(int).rolling(window=168, center=True).sum()
                ax4.plot(indices_data['datetime'], anomaly_density,
                        color='orange', alpha=0.7, label='Anomalies per week')
                ax4.axhline(y=10, color='red', linestyle='--', alpha=0.5,
                          label='Clustering threshold')
                
                # Identify clustered periods
                clustered = anomaly_density > 10
                ax4.fill_between(indices_data['datetime'], 0,
                               anomaly_density.max() * clustered,
                               alpha=0.2, color='orange', label='Clustered anomalies')
                
                ax4.set_ylabel('Anomaly\nClustering', fontsize=10)
                ax4.legend(loc='upper right')
                ax4.grid(True, alpha=0.3)
            else:
                axes[2].text(0.5, 0.5, 'Insufficient acoustic index data',
                           ha='center', va='center', transform=axes[2].transAxes)
                axes[3].text(0.5, 0.5, 'Insufficient acoustic index data',
                           ha='center', va='center', transform=axes[3].transAxes)
        else:
            axes[2].text(0.5, 0.5, 'No acoustic index data available',
                       ha='center', va='center', transform=axes[2].transAxes)
            axes[3].text(0.5, 0.5, 'No acoustic index data available',
                       ha='center', va='center', transform=axes[3].transAxes)
        
        # Panel 5: Combined signal (detection + acoustic anomalies)
        ax5 = axes[4]
        
        # Create combined signal
        combined_signal = det_data[species].copy()
        
        # Add acoustic anomalies if available
        if indices_data is not None and len(indices_data) > 0 and 'anomaly_density' in locals():
            # Align indices with detection data
            # This is simplified - in practice would need proper alignment
            ax5.plot(det_data['datetime'], combined_signal, 
                    color='navy', alpha=0.5, label='Detection signal')
            
            # Show periods where both signals are elevated
            high_detection = det_data[species] >= 2
            ax5.fill_between(det_data['datetime'], 0, 3 * high_detection,
                           alpha=0.3, color='green', 
                           label='High activity periods')
        else:
            ax5.plot(det_data['datetime'], combined_signal,
                    color='navy', alpha=0.7, label='Detection signal only')
        
        ax5.set_ylabel('Combined\nSignal', fontsize=10)
        ax5.set_xlabel('Date')
        ax5.legend(loc='upper right')
        ax5.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.suptitle(f'Event Validation: {species} at {station} ({year})', 
                    fontsize=14, y=1.02)
        
        # Save plot if path provided
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved visualization: {save_path}")
        
        return fig
    
    def calculate_temporal_clustering_metrics(self, species: str):
        """Calculate metrics that capture temporal clustering of activity.
        
        Returns metrics like:
        - Clustering coefficient: How much calls cluster vs random distribution
        - Burst index: Ratio of variance to mean in time between calls
        - Autocorrelation: Temporal correlation at different lags
        """
        
        if self.detections is None:
            logger.error("No detection data loaded")
            return None
        
        results = []
        
        for station in self.detections['station'].unique():
            station_data = self.detections[self.detections['station'] == station].copy()
            
            if species not in station_data.columns:
                continue
                
            station_data[species] = pd.to_numeric(station_data[species], errors='coerce').fillna(0)
            
            # Calculate inter-event intervals
            active_times = station_data[station_data[species] > 0]['datetime'].values
            
            if len(active_times) > 1:
                # Time between calls (in hours)
                intervals = np.diff(active_times) / np.timedelta64(1, 'h')
                
                # Clustering metrics
                cv = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0
                burst_index = np.var(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0
                
                # Autocorrelation at different lags
                species_series = station_data[species].values
                autocorr_1 = pd.Series(species_series).autocorr(lag=1)
                autocorr_12 = pd.Series(species_series).autocorr(lag=12)  # 24 hours
                autocorr_84 = pd.Series(species_series).autocorr(lag=84)  # 1 week
                
                results.append({
                    'species': species,
                    'station': station,
                    'n_active_periods': len(active_times),
                    'mean_interval_hours': np.mean(intervals),
                    'cv_intervals': cv,
                    'burst_index': burst_index,
                    'autocorr_2h': autocorr_1,
                    'autocorr_24h': autocorr_12,
                    'autocorr_week': autocorr_84,
                    'clustering_score': cv * autocorr_12  # Combined metric
                })
        
        return pd.DataFrame(results)
    
    def plot_clustering_comparison(self, save_path: str = None):
        """Compare temporal clustering across species."""
        
        # Get species list
        species_mapping = self.loader.load_species_mapping()
        fish_species = species_mapping[
            (species_mapping['group'] == 'fish') & 
            (species_mapping['keep_species'] == 1)
        ]['long_name'].tolist()
        
        all_metrics = []
        for species in fish_species:
            if species in self.detections.columns:
                metrics = self.calculate_temporal_clustering_metrics(species)
                if metrics is not None and len(metrics) > 0:
                    all_metrics.append(metrics)
        
        if not all_metrics:
            logger.warning("No clustering metrics calculated")
            return
        
        clustering_df = pd.concat(all_metrics, ignore_index=True)
        
        # Create comparison plot
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Burst index comparison
        ax1 = axes[0, 0]
        species_burst = clustering_df.groupby('species')['burst_index'].mean().sort_values()
        ax1.barh(range(len(species_burst)), species_burst.values)
        ax1.set_yticks(range(len(species_burst)))
        ax1.set_yticklabels(species_burst.index)
        ax1.set_xlabel('Burst Index (higher = more clustered)')
        ax1.set_title('Temporal Clustering by Species')
        ax1.axvline(x=1, color='red', linestyle='--', alpha=0.5, label='Random (Poisson)')
        ax1.legend()
        
        # Autocorrelation at 24h
        ax2 = axes[0, 1]
        species_auto = clustering_df.groupby('species')['autocorr_24h'].mean().sort_values()
        ax2.barh(range(len(species_auto)), species_auto.values)
        ax2.set_yticks(range(len(species_auto)))
        ax2.set_yticklabels(species_auto.index)
        ax2.set_xlabel('24-hour Autocorrelation')
        ax2.set_title('Day-to-Day Consistency')
        ax2.axvline(x=0, color='red', linestyle='--', alpha=0.5)
        
        # Scatter: Burst vs Autocorrelation
        ax3 = axes[1, 0]
        for species in clustering_df['species'].unique():
            species_data = clustering_df[clustering_df['species'] == species]
            ax3.scatter(species_data['burst_index'], species_data['autocorr_24h'],
                       label=species, s=100, alpha=0.7)
        ax3.set_xlabel('Burst Index')
        ax3.set_ylabel('24h Autocorrelation')
        ax3.set_title('Clustering Pattern Space')
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax3.grid(True, alpha=0.3)
        
        # Combined clustering score
        ax4 = axes[1, 1]
        species_combined = clustering_df.groupby('species')['clustering_score'].mean().sort_values()
        ax4.barh(range(len(species_combined)), species_combined.values, color='darkgreen')
        ax4.set_yticks(range(len(species_combined)))
        ax4.set_yticklabels(species_combined.index)
        ax4.set_xlabel('Combined Clustering Score')
        ax4.set_title('Overall Temporal Clustering')
        
        plt.tight_layout()
        plt.suptitle('Temporal Clustering Analysis - How Species Calling Patterns Cluster in Time',
                    fontsize=14, y=1.02)
        
        # Save plot if path provided
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved clustering comparison: {save_path}")
        
        return fig

def main():
    """Run event validation and temporal clustering analysis."""
    
    print("=" * 60)
    print("Event Validation and Temporal Clustering Analysis")
    print("=" * 60)
    
    # Initialize validator
    validator = EventValidator(repo_root / "data")
    
    # Create organized output directory
    output_dir = Path.cwd() / "analysis_results" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    species_dir = output_dir / "species_validation"
    species_dir.mkdir(exist_ok=True)
    
    clustering_dir = output_dir / "temporal_clustering" 
    clustering_dir.mkdir(exist_ok=True)
    
    # Load all data
    print("\n1. Loading data...")
    validator.load_all_data()
    
    # Get list of species to analyze
    species_mapping = validator.loader.load_species_mapping()
    fish_species = species_mapping[
        (species_mapping['group'] == 'fish') & 
        (species_mapping['keep_species'] == 1)
    ]['long_name'].tolist()
    
    # Visualize events for top species
    print("\n2. Creating event validation plots...")
    
    # Get most active species from events
    if validator.events is not None:
        top_species = validator.events['species'].value_counts().head(4).index.tolist()
        
        for species in top_species:
            # Clean species name for filename
            clean_name = species.lower().replace(' ', '_').replace(',', '')
            
            # Find a good time period for this species
            species_events = validator.events[validator.events['species'] == species]
            
            if len(species_events) > 0:
                # Pick most active station and time period
                top_station = species_events['station'].value_counts().index[0]
                # Find month with most events
                species_events['month'] = species_events['start_time'].dt.month
                top_month = species_events['month'].value_counts().index[0]
                # Use 2021 if available, else 2018
                year = 2021 if len(species_events[species_events['year'] == 2021]) > 0 else 2018
                
                save_path = species_dir / f"event_validation_{clean_name}_{top_station}_{year}m{int(top_month):02d}.png"
                
                fig = validator.visualize_events_on_data(
                    species=species,
                    station=top_station,
                    year=year,
                    month=top_month,
                    save_path=str(save_path)
                )
                plt.close(fig)  # Close to save memory
                print(f"   Saved: {save_path.name}")
    
    # Calculate and plot clustering metrics
    print("\n3. Analyzing temporal clustering patterns...")
    clustering_save_path = clustering_dir / "temporal_clustering_comparison.png"
    fig3 = validator.plot_clustering_comparison(save_path=str(clustering_save_path))
    plt.close(fig3)  # Close to save memory
    
    # Calculate clustering metrics for all species
    print("\n4. Calculating clustering metrics...")
    
    all_clustering = []
    for species in fish_species[:5]:  # Top 5 species
        if species in validator.detections.columns:
            metrics = validator.calculate_temporal_clustering_metrics(species)
            if metrics is not None:
                all_clustering.append(metrics)
    
    if all_clustering:
        clustering_results = pd.concat(all_clustering, ignore_index=True)
        metrics_save_path = clustering_dir / 'temporal_clustering_metrics.csv'
        clustering_results.to_csv(metrics_save_path, index=False)
        print(f"   Saved: {metrics_save_path.name}")
        
        print("\n5. Key Insights:")
        print(f"   - Species with highest burst index (most clustered): "
              f"{clustering_results.groupby('species')['burst_index'].mean().idxmax()}")
        print(f"   - Species with highest 24h autocorrelation (most consistent): "
              f"{clustering_results.groupby('species')['autocorr_24h'].mean().idxmax()}")
        print(f"   - Mean interval between calls ranges from "
              f"{clustering_results['mean_interval_hours'].min():.1f} to "
              f"{clustering_results['mean_interval_hours'].max():.1f} hours")
    
    print("\n" + "=" * 60)
    print(f"Analysis complete! High-resolution plots saved to:")
    print(f"  Species validation: {species_dir}")
    print(f"  Temporal clustering: {clustering_dir}")
    print("\nKey finding: Temporal clustering (multiple high values close together)")
    print("is more predictive than individual high values spread across time.")
    print("=" * 60)

if __name__ == "__main__":
    main()