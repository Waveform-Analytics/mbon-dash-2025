"""Exploratory Analysis Script 02: Biological Event Extraction and Characterization

This script extracts and characterizes biological calling events from manual detection data,
focusing on identifying continuous periods of calling activity, chorus events, and their
temporal patterns (diel cycles, duration, intensity transitions).

Key outputs:
1. List of all biological events with start/end times, duration, and peak intensity
2. Diel pattern analysis showing when different species typically call
3. Event type classification (rapid onset, gradual buildup, sustained chorus, etc.)
4. Visualization of event timelines and patterns
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
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
repo_root = project_root.parent

from mbon_analysis.data.loaders import create_loader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

class BiologicalEventExtractor:
    """Extract and characterize biological calling events from detection data."""
    
    def __init__(self, data_root: Optional[Path] = None):
        """Initialize with data loader."""
        self.loader = create_loader(data_root)
        self.detections = None
        self.species_mapping = None
        self.events = None
        self.event_stats = None
        
    def load_data(self) -> pd.DataFrame:
        """Load and prepare detection data."""
        logger.info("Loading detection data...")
        
        all_detections = []
        stations = self.loader.get_available_stations()
        
        for station in stations:
            for year in [2018, 2021]:
                try:
                    df = self.loader.load_detection_data(station, year)
                    df['station'] = station
                    df['year'] = year
                    
                    # Ensure datetime column
                    if 'Date' in df.columns:
                        df['datetime'] = pd.to_datetime(df['Date'])
                    
                    all_detections.append(df)
                    logger.info(f"Loaded {len(df)} records from {station} {year}")
                    
                except Exception as e:
                    logger.warning(f"Could not load {station} {year}: {e}")
                    continue
        
        self.detections = pd.concat(all_detections, ignore_index=True)
        
        # Load species mapping
        self.species_mapping = self.loader.load_species_mapping()
        
        # Add time-based features
        self.detections['hour'] = self.detections['datetime'].dt.hour
        self.detections['date'] = self.detections['datetime'].dt.date
        self.detections['month'] = self.detections['datetime'].dt.month
        self.detections['day_of_year'] = self.detections['datetime'].dt.dayofyear
        
        logger.info(f"Total detection records loaded: {len(self.detections)}")
        return self.detections
    
    def extract_events(self, species: str, min_duration_hours: int = 4, 
                      min_intensity: int = 2) -> pd.DataFrame:
        """Extract continuous calling events for a species.
        
        Args:
            species: Species column name
            min_duration_hours: Minimum event duration (in hours)
            min_intensity: Minimum intensity to consider as active calling
            
        Returns:
            DataFrame of events with start/end times and characteristics
        """
        if species not in self.detections.columns:
            logger.warning(f"Species {species} not found in data")
            return pd.DataFrame()
        
        events = []
        
        for station in self.detections['station'].unique():
            for year in self.detections['year'].unique():
                station_data = self.detections[
                    (self.detections['station'] == station) & 
                    (self.detections['year'] == year)
                ].sort_values('datetime').copy()
                
                if len(station_data) == 0:
                    continue
                
                # Convert species column to numeric
                station_data[species] = pd.to_numeric(station_data[species], errors='coerce').fillna(0)
                
                # Identify periods of active calling
                active = station_data[species] >= min_intensity
                
                # Find continuous runs of active calling
                # Change points where activity starts or stops
                changes = active != active.shift()
                run_groups = changes.cumsum()
                
                # Process each run
                for run_id in run_groups[active].unique():
                    run_data = station_data[run_groups == run_id]
                    
                    # Check duration (remember: 2-hour intervals)
                    duration_hours = len(run_data) * 2
                    
                    if duration_hours >= min_duration_hours:
                        # Characterize the event
                        peak_intensity = run_data[species].max()
                        
                        # Check if this reaches chorus level (3)
                        is_chorus = peak_intensity >= 3
                        
                        # Analyze buildup and decay
                        intensities = run_data[species].values
                        buildup_hours = self._calculate_buildup_time(intensities) * 2
                        decay_hours = self._calculate_decay_time(intensities) * 2
                        
                        # Time of day analysis
                        start_hour = run_data.iloc[0]['hour']
                        end_hour = run_data.iloc[-1]['hour']
                        peak_hours = run_data[run_data[species] == peak_intensity]['hour'].values
                        
                        events.append({
                            'species': species,
                            'station': station,
                            'year': year,
                            'start_time': run_data['datetime'].iloc[0],
                            'end_time': run_data['datetime'].iloc[-1],
                            'duration_hours': duration_hours,
                            'peak_intensity': peak_intensity,
                            'mean_intensity': run_data[species].mean(),
                            'is_chorus': is_chorus,
                            'buildup_hours': buildup_hours,
                            'decay_hours': decay_hours,
                            'start_hour': start_hour,
                            'end_hour': end_hour,
                            'peak_hours': peak_hours.tolist(),
                            'n_observations': len(run_data),
                            'month': run_data['month'].iloc[0],
                            'day_of_year': run_data['day_of_year'].iloc[0]
                        })
        
        events_df = pd.DataFrame(events)
        
        if len(events_df) > 0:
            # Classify event types
            events_df['event_type'] = events_df.apply(self._classify_event, axis=1)
            
            # Add diel period classification
            events_df['diel_period'] = events_df['start_hour'].apply(self._classify_diel_period)
        
        logger.info(f"Extracted {len(events_df)} events for {species}")
        return events_df
    
    def _calculate_buildup_time(self, intensities: np.ndarray) -> int:
        """Calculate time to reach peak from start (in observations)."""
        if len(intensities) == 0:
            return 0
        peak_idx = np.argmax(intensities)
        return peak_idx
    
    def _calculate_decay_time(self, intensities: np.ndarray) -> int:
        """Calculate time from peak to end (in observations)."""
        if len(intensities) == 0:
            return 0
        peak_idx = np.argmax(intensities)
        return len(intensities) - peak_idx - 1
    
    def _classify_event(self, event: pd.Series) -> str:
        """Classify event type based on characteristics."""
        if event['duration_hours'] <= 6:
            return 'brief'
        elif event['buildup_hours'] <= 2:
            return 'rapid_onset'
        elif event['buildup_hours'] >= 6:
            return 'gradual_buildup'
        elif event['duration_hours'] >= 12 and event['is_chorus']:
            return 'sustained_chorus'
        else:
            return 'standard'
    
    def _classify_diel_period(self, hour: int) -> str:
        """Classify time of day into diel periods."""
        if 4 <= hour < 8:
            return 'dawn'
        elif 8 <= hour < 16:
            return 'day'
        elif 16 <= hour < 20:
            return 'dusk'
        else:
            return 'night'
    
    def extract_all_species_events(self, min_duration_hours: int = 4) -> pd.DataFrame:
        """Extract events for all fish species."""
        if self.species_mapping is None:
            logger.error("Species mapping not loaded")
            return pd.DataFrame()
        
        # Get fish species
        fish_species = self.species_mapping[
            (self.species_mapping['group'] == 'fish') & 
            (self.species_mapping['keep_species'] == 1)
        ]['long_name'].tolist()
        
        all_events = []
        
        for species in fish_species:
            if species in self.detections.columns:
                species_events = self.extract_events(species, min_duration_hours)
                all_events.append(species_events)
                
        if all_events:
            self.events = pd.concat(all_events, ignore_index=True)
        else:
            self.events = pd.DataFrame()
            
        logger.info(f"Total events extracted: {len(self.events)}")
        return self.events
    
    def analyze_diel_patterns(self) -> Dict[str, pd.DataFrame]:
        """Analyze when different species are active during the day."""
        if self.events is None or len(self.events) == 0:
            logger.warning("No events to analyze")
            return {}
        
        diel_patterns = {}
        
        for species in self.events['species'].unique():
            species_events = self.events[self.events['species'] == species]
            
            # Count events by hour of day
            hour_counts = pd.DataFrame({
                'hour': range(24),
                'event_starts': 0,
                'chorus_events': 0
            })
            
            for hour in range(24):
                hour_counts.loc[hour, 'event_starts'] = len(
                    species_events[species_events['start_hour'] == hour]
                )
                hour_counts.loc[hour, 'chorus_events'] = len(
                    species_events[
                        (species_events['is_chorus']) & 
                        (species_events['start_hour'] == hour)
                    ]
                )
            
            # Calculate percentages
            total_events = hour_counts['event_starts'].sum()
            if total_events > 0:
                hour_counts['pct_events'] = hour_counts['event_starts'] / total_events * 100
            
            diel_patterns[species] = hour_counts
            
        return diel_patterns
    
    def calculate_event_statistics(self) -> pd.DataFrame:
        """Calculate summary statistics for events."""
        if self.events is None or len(self.events) == 0:
            logger.warning("No events to analyze")
            return pd.DataFrame()
        
        stats = []
        
        for species in self.events['species'].unique():
            species_events = self.events[self.events['species'] == species]
            
            stats.append({
                'species': species,
                'n_events': len(species_events),
                'n_chorus_events': len(species_events[species_events['is_chorus']]),
                'mean_duration_hours': species_events['duration_hours'].mean(),
                'max_duration_hours': species_events['duration_hours'].max(),
                'mean_peak_intensity': species_events['peak_intensity'].mean(),
                'pct_chorus': len(species_events[species_events['is_chorus']]) / len(species_events) * 100,
                'most_common_diel': species_events['diel_period'].mode().iloc[0] if len(species_events['diel_period'].mode()) > 0 else 'unknown',
                'peak_month': species_events['month'].mode().iloc[0] if len(species_events['month'].mode()) > 0 else 0,
                'stations': species_events['station'].unique().tolist()
            })
        
        self.event_stats = pd.DataFrame(stats)
        return self.event_stats
    
    def plot_event_timeline(self, species: str, station: str = None, save_path: str = None):
        """Create timeline visualization of events."""
        if self.events is None or len(self.events) == 0:
            logger.warning("No events to plot")
            return
        
        # Filter events
        events_to_plot = self.events[self.events['species'] == species]
        if station:
            events_to_plot = events_to_plot[events_to_plot['station'] == station]
        
        if len(events_to_plot) == 0:
            logger.warning(f"No events found for {species} at {station}")
            return
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 8))
        
        # Timeline plot
        ax1 = axes[0]
        for idx, event in events_to_plot.iterrows():
            y_pos = event['year'] + (0.2 if event['station'] == '9M' else 
                                     0 if event['station'] == '14M' else -0.2)
            
            color = 'red' if event['is_chorus'] else 'orange'
            ax1.barh(y_pos, event['duration_hours'], 
                    left=event['start_time'], height=0.15,
                    color=color, alpha=0.7, 
                    label=f"{event['station']} - {'Chorus' if event['is_chorus'] else 'Active'}")
        
        ax1.set_ylabel('Year/Station')
        ax1.set_xlabel('Date')
        ax1.set_title(f'Calling Events Timeline - {species}')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # Diel pattern plot
        ax2 = axes[1]
        hour_counts = pd.DataFrame({'hour': range(24), 'count': 0})
        for hour in events_to_plot['start_hour']:
            hour_counts.loc[hour, 'count'] += 1
        
        ax2.bar(hour_counts['hour'], hour_counts['count'], color='darkblue', alpha=0.7)
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Number of Events Starting')
        ax2.set_title(f'Diel Pattern - When {species} Events Begin')
        ax2.set_xticks(range(0, 24, 2))
        ax2.grid(True, alpha=0.3)
        
        # Add shading for night hours
        ax2.axvspan(-0.5, 6.5, alpha=0.1, color='gray', label='Night')
        ax2.axvspan(18.5, 23.5, alpha=0.1, color='gray')
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Timeline saved to {save_path}")
        
        plt.show()
    
    def save_events(self, output_dir: Path = None):
        """Save extracted events to CSV."""
        if output_dir is None:
            output_dir = Path.cwd() / "event_analysis"
        
        output_dir.mkdir(exist_ok=True)
        
        if self.events is not None and len(self.events) > 0:
            self.events.to_csv(output_dir / "biological_events.csv", index=False)
            logger.info(f"Events saved to {output_dir / 'biological_events.csv'}")
        
        if self.event_stats is not None:
            self.event_stats.to_csv(output_dir / "event_statistics.csv", index=False)
            logger.info(f"Statistics saved to {output_dir / 'event_statistics.csv'}")
    
    def generate_summary_report(self) -> str:
        """Generate text summary of event analysis."""
        if self.events is None or len(self.events) == 0:
            return "No events extracted"
        
        report = []
        report.append("=" * 60)
        report.append("BIOLOGICAL EVENT EXTRACTION SUMMARY")
        report.append("=" * 60)
        report.append("")
        report.append(f"Total events extracted: {len(self.events)}")
        report.append(f"Species analyzed: {self.events['species'].nunique()}")
        report.append(f"Stations: {self.events['station'].unique().tolist()}")
        report.append(f"Years: {self.events['year'].unique().tolist()}")
        report.append("")
        
        # Event type breakdown
        report.append("EVENT TYPES:")
        for event_type, count in self.events['event_type'].value_counts().items():
            report.append(f"  {event_type}: {count} events")
        report.append("")
        
        # Diel period breakdown
        report.append("DIEL PATTERNS:")
        for period, count in self.events['diel_period'].value_counts().items():
            pct = count / len(self.events) * 100
            report.append(f"  {period}: {count} events ({pct:.1f}%)")
        report.append("")
        
        # Species-specific patterns
        if self.event_stats is not None and len(self.event_stats) > 0:
            report.append("SPECIES-SPECIFIC PATTERNS:")
            for _, species_stats in self.event_stats.iterrows():
                report.append(f"\n{species_stats['species']}:")
                report.append(f"  Events: {species_stats['n_events']}")
                report.append(f"  Chorus events: {species_stats['n_chorus_events']} ({species_stats['pct_chorus']:.1f}%)")
                report.append(f"  Mean duration: {species_stats['mean_duration_hours']:.1f} hours")
                report.append(f"  Most active: {species_stats['most_common_diel']} period")
                report.append(f"  Peak month: {species_stats['peak_month']}")
        
        report.append("")
        report.append("KEY FINDINGS:")
        
        # Find most active species
        most_events = self.events['species'].value_counts().iloc[0]
        most_active_species = self.events['species'].value_counts().index[0]
        report.append(f"  Most active species: {most_active_species} ({most_events} events)")
        
        # Find longest event
        longest_event = self.events.loc[self.events['duration_hours'].idxmax()]
        report.append(f"  Longest event: {longest_event['species']} for {longest_event['duration_hours']} hours")
        
        # Chorus statistics
        chorus_events = self.events[self.events['is_chorus']]
        if len(chorus_events) > 0:
            report.append(f"  Total chorus events: {len(chorus_events)} ({len(chorus_events)/len(self.events)*100:.1f}%)")
            report.append(f"  Mean chorus duration: {chorus_events['duration_hours'].mean():.1f} hours")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)

def main():
    """Run event extraction analysis."""
    print("Starting Biological Event Extraction Analysis...")
    print("=" * 60)
    
    # Initialize extractor
    extractor = BiologicalEventExtractor(repo_root / "data")
    
    # Load data
    print("\n1. Loading detection data...")
    detections = extractor.load_data()
    print(f"   Loaded {len(detections)} detection records")
    
    # Extract events for all species
    print("\n2. Extracting biological events...")
    events = extractor.extract_all_species_events(min_duration_hours=4)
    print(f"   Extracted {len(events)} events")
    
    # Calculate statistics
    print("\n3. Calculating event statistics...")
    stats = extractor.calculate_event_statistics()
    print(f"   Analyzed {len(stats)} species")
    
    # Analyze diel patterns
    print("\n4. Analyzing diel patterns...")
    diel_patterns = extractor.analyze_diel_patterns()
    
    # Generate report
    print("\n5. Generating summary report...")
    report = extractor.generate_summary_report()
    print("\n" + report)
    
    # Save results
    print("\n6. Saving results...")
    extractor.save_events()
    
    # Create visualization for most active species
    if len(events) > 0:
        most_active = events['species'].value_counts().index[0]
        print(f"\n7. Creating timeline for {most_active}...")
        extractor.plot_event_timeline(most_active, save_path="event_timeline.png")
    
    print("\nEvent extraction complete!")
    print("Results saved to event_analysis/")

if __name__ == "__main__":
    main()