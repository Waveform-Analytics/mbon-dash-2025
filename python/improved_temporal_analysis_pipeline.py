#!/usr/bin/env python3
"""
IMPROVED TEMPORAL ANALYSIS PIPELINE

Addresses fundamental issues with the current approach:
1. Preserve fine temporal resolution before aggregation
2. Activity-informed feature selection (not clustering-based)
3. Fair temporal feature comparison between acoustic and environmental
4. Biological relevance-driven index reduction

Key improvements:
- Create lags at native resolution, then aggregate
- Select indices based on biological prediction power
- Match temporal complexity between acoustic and environmental
- Systematic evaluation of temporal vs non-temporal approaches
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import cross_val_score, StratifiedKFold, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_classif, SelectKBest, f_classif
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class ImprovedTemporalAnalysis:
    """
    Systematic approach to temporal analysis of marine acoustic data.
    
    Methodology:
    1. Load data at native temporal resolution
    2. Identify biologically-relevant acoustic indices first
    3. Create temporal features at fine resolution
    4. Aggregate to detection resolution with preserved temporal information
    5. Fair comparison between acoustic and environmental predictors
    """
    
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.results = {}
        
    def load_native_resolution_data(self):
        """Load data at original temporal resolution before aggregation."""
        print("🔄 PHASE 1: LOADING DATA AT NATIVE RESOLUTION")
        print("="*60)
        
        # Load raw 1-hour acoustic indices (before 2-hour aggregation)
        indices_files = list(self.data_dir.glob("01_indices_*_2021.parquet"))
        
        if not indices_files:
            print("❌ No native resolution acoustic indices found")
            print("   Looking for files matching: 01_indices_*_2021.parquet")
            return None
            
        # Combine all station data
        indices_data = []
        for file_path in indices_files:
            station = file_path.stem.split('_')[2]  # Extract station from filename
            df = pd.read_parquet(file_path)
            df['station'] = station
            indices_data.append(df)
            print(f"✓ Loaded {station}: {df.shape}")
        
        self.indices_native = pd.concat(indices_data, ignore_index=True)
        
        # Load 2-hour detection data (ground truth)
        bio_file = self.data_dir / "02_biological_activity_features_2021.parquet"
        if bio_file.exists():
            self.bio_data = pd.read_parquet(bio_file)
            print(f"✓ Loaded biological data: {self.bio_data.shape}")
        else:
            print("❌ Biological activity data not found")
            return None
            
        # Load environmental data (already aggregated to 2-hour)
        env_file = self.data_dir / "02_environmental_aligned_2021.parquet"
        if env_file.exists():
            self.env_data = pd.read_parquet(env_file)
            print(f"✓ Loaded environmental data: {self.env_data.shape}")
        else:
            print("❌ Environmental data not found")
            return None
        
        print(f"\n📊 Data Summary:")
        print(f"  Acoustic indices: {self.indices_native.shape} (1-hour resolution)")
        print(f"  Biological data: {self.bio_data.shape} (2-hour resolution)")  
        print(f"  Environmental data: {self.env_data.shape} (2-hour resolution)")
        
        return True
        
    def identify_predictive_indices(self, n_top_indices=8):
        """
        Identify acoustic indices most predictive of biological activity.
        This replaces clustering-based reduction with activity-based selection.
        """
        print(f"\n🎯 PHASE 2: ACTIVITY-INFORMED INDEX SELECTION")
        print("="*60)
        print("Goal: Select indices based on biological prediction power")
        print("(Not clustering-based dimensionality reduction)")
        
        # First, align acoustic indices to 2-hour resolution for initial screening
        # Filter to only numeric acoustic index columns (exclude strings like 'Date', 'Filename', 'ACI_by_band')
        acoustic_cols = []
        for col in self.indices_native.columns:
            if col not in ['datetime', 'station', 'year', 'Date', 'Filename']:
                if self.indices_native[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                    acoustic_cols.append(col)
                elif col.endswith('_by_band'):  # Skip complex array columns
                    continue
                else:
                    acoustic_cols.append(col)
        
        print(f"Screening {len(acoustic_cols)} acoustic indices...")
        
        # Aggregate acoustic indices to 2-hour resolution
        self.indices_native['datetime'] = pd.to_datetime(self.indices_native['datetime'])
        self.indices_native['datetime_2h'] = self.indices_native['datetime'].dt.floor('2h')
        
        indices_2h = (self.indices_native
                     .groupby(['station', 'datetime_2h'])[acoustic_cols]
                     .mean()
                     .reset_index())
        indices_2h.rename(columns={'datetime_2h': 'datetime'}, inplace=True)
        
        # Merge with biological data for screening
        merged_screening = indices_2h.merge(
            self.bio_data[['datetime', 'station', 'any_activity']], 
            on=['datetime', 'station'], 
            how='inner'
        ).dropna()
        
        if merged_screening.empty:
            print("❌ No overlapping data for screening")
            return None
            
        print(f"Screening dataset: {merged_screening.shape}")
        
        # Calculate mutual information for all indices
        X_screen = merged_screening[acoustic_cols]
        y_screen = merged_screening['any_activity']
        
        mi_scores = mutual_info_classif(X_screen, y_screen, random_state=42)
        
        # Create index ranking
        index_ranking = pd.DataFrame({
            'index': acoustic_cols,
            'mi_score': mi_scores
        }).sort_values('mi_score', ascending=False)
        
        print(f"\n🏆 TOP 15 ACOUSTIC INDICES (by biological prediction):")
        for i, (_, row) in enumerate(index_ranking.head(15).iterrows(), 1):
            print(f"  {i:2d}. {row['index']:20} | MI: {row['mi_score']:.3f}")
        
        # Select top indices
        self.top_indices = index_ranking.head(n_top_indices)['index'].tolist()
        self.index_ranking = index_ranking
        
        print(f"\n✅ Selected top {n_top_indices} indices for temporal feature engineering:")
        print(f"   {self.top_indices}")
        
        return True
        
    def create_fine_resolution_temporal_features(self):
        """
        Create temporal features at native 1-hour resolution before aggregation.
        This preserves fine-grained temporal patterns.
        """
        print(f"\n⏰ PHASE 3: FINE-RESOLUTION TEMPORAL FEATURES")
        print("="*60)
        print("Creating temporal features at 1-hour resolution, then aggregating")
        print("(Preserves fine-grained temporal dynamics)")
        
        # Sort by station and datetime
        self.indices_native = self.indices_native.sort_values(['station', 'datetime'])
        
        temporal_features_native = []
        
        # Process each station separately to maintain temporal order
        for station in self.indices_native['station'].unique():
            print(f"\nProcessing station {station}...")
            
            station_mask = self.indices_native['station'] == station
            station_df = self.indices_native[station_mask].copy().reset_index(drop=True)
            station_df['datetime'] = pd.to_datetime(station_df['datetime'])
            station_df = station_df.sort_values('datetime')
            
            # Create temporal features for selected indices only
            for idx_name in self.top_indices:
                if idx_name in station_df.columns:
                    # 1-3 hour lags (at native 1-hour resolution)
                    station_df[f'{idx_name}_lag_1h'] = station_df[idx_name].shift(1)
                    station_df[f'{idx_name}_lag_2h'] = station_df[idx_name].shift(2) 
                    station_df[f'{idx_name}_lag_3h'] = station_df[idx_name].shift(3)
                    
                    # Rolling means (preserve fine structure)
                    station_df[f'{idx_name}_mean_3h'] = station_df[idx_name].rolling(window=3, min_periods=1).mean()
                    station_df[f'{idx_name}_mean_6h'] = station_df[idx_name].rolling(window=6, min_periods=1).mean()
                    station_df[f'{idx_name}_mean_12h'] = station_df[idx_name].rolling(window=12, min_periods=1).mean()
                    
                    # Change features (trend detection)
                    station_df[f'{idx_name}_change_2h'] = station_df[idx_name] - station_df[f'{idx_name}_lag_2h']
                    station_df[f'{idx_name}_change_4h'] = station_df[idx_name] - station_df[idx_name].shift(4)
            
            temporal_features_native.append(station_df)
        
        # Combine all stations
        self.indices_with_temporal = pd.concat(temporal_features_native, ignore_index=True)
        
        # Now aggregate to 2-hour resolution (preserving the temporal feature information)
        self.indices_with_temporal['datetime_2h'] = self.indices_with_temporal['datetime'].dt.floor('2h')
        
        # Get all feature columns (original + temporal) - only numeric ones
        feature_cols = []
        for col in self.indices_with_temporal.columns:
            if col not in ['datetime', 'datetime_2h', 'station', 'Date', 'Filename']:
                if self.indices_with_temporal[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                    feature_cols.append(col)
                elif not col.endswith('_by_band') and not isinstance(self.indices_with_temporal[col].iloc[0], str):
                    feature_cols.append(col)
        
        # Aggregate to 2-hour resolution using only numeric columns
        self.indices_aggregated = (self.indices_with_temporal
                                  .groupby(['station', 'datetime_2h'])[feature_cols]
                                  .mean(numeric_only=True)
                                  .reset_index())
        self.indices_aggregated.rename(columns={'datetime_2h': 'datetime'}, inplace=True)
        
        # Count temporal features created
        temporal_cols = [col for col in feature_cols if any(x in col for x in ['_lag_', '_mean_', '_change_'])]
        
        print(f"\n✅ Created temporal features:")
        print(f"   Original indices: {len(self.top_indices)}")
        print(f"   Temporal features: {len(temporal_cols)}")
        print(f"   Total features: {len(feature_cols)}")
        print(f"   Aggregated shape: {self.indices_aggregated.shape}")
        
        return True
        
    def create_analysis_dataset(self):
        """Combine all data sources with proper temporal alignment."""
        print(f"\n🔗 PHASE 4: CREATE ANALYSIS DATASET")
        print("="*60)
        
        # Start with biological data as the base (2-hour ground truth)
        analysis_df = self.bio_data.copy()
        
        # Merge acoustic indices with temporal features
        analysis_df = analysis_df.merge(
            self.indices_aggregated, 
            on=['datetime', 'station'], 
            how='left'
        )
        
        # Merge environmental data  
        analysis_df = analysis_df.merge(
            self.env_data,
            on=['datetime', 'station'],
            how='left'
        )
        
        # Clean up
        analysis_df = analysis_df.dropna()
        
        # Define feature groups
        self.feature_groups = {
            'acoustic_base': self.top_indices,
            'acoustic_temporal': [col for col in analysis_df.columns 
                                if any(idx in col for idx in self.top_indices) 
                                and any(temp in col for temp in ['_lag_', '_mean_', '_change_'])],
            'environmental_base': [col for col in analysis_df.columns if col in [
                'Water temp (°C)', 'Water depth (m)', 'Broadband (1-40000 Hz)',
                'Low (50-1200 Hz)', 'High (7000-40000 Hz)'
            ]],
            'environmental_temporal': [col for col in analysis_df.columns
                                     if any(x in col for x in ['temp_lag', 'temp_mean', 'temp_change',
                                                              'depth_lag', 'depth_mean', 'depth_change', 
                                                              'spl_broadband_lag', 'spl_broadband_mean'])]
        }
        
        # Add categorical features
        categorical_features = []
        for cat_col, prefix in [('season', 'season'), ('time_period', 'time_period'), ('station', 'station')]:
            if cat_col in analysis_df.columns:
                dummies = pd.get_dummies(analysis_df[cat_col], prefix=prefix)
                analysis_df = pd.concat([analysis_df, dummies], axis=1)
                categorical_features.extend(dummies.columns.tolist())
        
        self.feature_groups['categorical'] = categorical_features
        self.analysis_df = analysis_df
        
        print(f"📊 Final analysis dataset: {self.analysis_df.shape}")
        print(f"\nFeature group sizes:")
        for group, features in self.feature_groups.items():
            print(f"  {group}: {len(features)} features")
        
        print(f"\nTarget distribution: {self.analysis_df['any_activity'].value_counts().to_dict()}")
        
        return True
        
    def comparative_analysis(self):
        """
        Fair comparison between acoustic and environmental predictors.
        """
        print(f"\n🤖 PHASE 5: COMPARATIVE ANALYSIS")
        print("="*60)
        
        # Define comparison scenarios
        scenarios = {
            'acoustic_base_only': {
                'features': self.feature_groups['acoustic_base'],
                'description': 'Acoustic Indices (Base)'
            },
            'acoustic_with_temporal': {
                'features': self.feature_groups['acoustic_base'] + self.feature_groups['acoustic_temporal'],
                'description': 'Acoustic + Temporal Features'
            },
            'environmental_base_only': {
                'features': self.feature_groups['environmental_base'] + self.feature_groups['categorical'],
                'description': 'Environmental (Base) + Context'
            },
            'environmental_with_temporal': {
                'features': (self.feature_groups['environmental_base'] + 
                           self.feature_groups['environmental_temporal'] + 
                           self.feature_groups['categorical']),
                'description': 'Environmental + Temporal + Context'
            },
            'combined_fair': {
                'features': (self.feature_groups['acoustic_base'] + 
                           self.feature_groups['acoustic_temporal'] +
                           self.feature_groups['environmental_base'] + 
                           self.feature_groups['environmental_temporal'] +
                           self.feature_groups['categorical']),
                'description': 'All Features (Fair Comparison)'
            }
        }
        
        # Models for comparison
        models = {
            'Logistic': LogisticRegression(random_state=42, max_iter=1000),
            'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        }
        
        # Cross-validation methods
        cv_methods = {
            'standard': StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            'temporal': TimeSeriesSplit(n_splits=5)
        }
        
        self.results = {}
        target = 'any_activity'
        
        for model_name, model in models.items():
            print(f"\n📈 {model_name.upper()} ANALYSIS:")
            print("-" * 40)
            
            model_results = {}
            
            for cv_name, cv_splitter in cv_methods.items():
                print(f"\n{cv_name.title()} Cross-Validation:")
                cv_results = {}
                
                for scenario_name, scenario_config in scenarios.items():
                    available_features = [f for f in scenario_config['features'] if f in self.analysis_df.columns]
                    
                    if len(available_features) == 0:
                        continue
                        
                    X = self.analysis_df[available_features]
                    y = self.analysis_df[target]
                    
                    # Scale features
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    
                    # Cross-validation
                    cv_scores = cross_val_score(model, X_scaled, y, cv=cv_splitter, scoring='f1')
                    
                    cv_results[scenario_name] = {
                        'mean_f1': cv_scores.mean(),
                        'std_f1': cv_scores.std(),
                        'n_features': len(available_features)
                    }
                    
                    print(f"  {scenario_config['description']:30} | F1: {cv_scores.mean():.3f}±{cv_scores.std():.3f} | n={len(available_features)}")
                
                model_results[cv_name] = cv_results
            
            self.results[model_name] = model_results
        
        return True
        
    def generate_insights(self):
        """Generate actionable insights from the analysis."""
        print(f"\n🎯 INSIGHTS & RECOMMENDATIONS")
        print("="*60)
        
        # Key comparisons for each model
        for model_name, model_results in self.results.items():
            if 'standard' not in model_results:
                continue
                
            standard_results = model_results['standard']
            
            print(f"\n📊 {model_name} Key Findings:")
            
            # Extract key scenarios
            acoustic_base = standard_results.get('acoustic_base_only', {}).get('mean_f1', 0)
            acoustic_temporal = standard_results.get('acoustic_with_temporal', {}).get('mean_f1', 0)
            env_base = standard_results.get('environmental_base_only', {}).get('mean_f1', 0)
            env_temporal = standard_results.get('environmental_with_temporal', {}).get('mean_f1', 0)
            combined = standard_results.get('combined_fair', {}).get('mean_f1', 0)
            
            # Calculate improvements
            acoustic_temporal_boost = acoustic_temporal - acoustic_base
            env_temporal_boost = env_temporal - env_base
            env_advantage = env_temporal - acoustic_temporal
            
            print(f"  Acoustic (base):        F1 = {acoustic_base:.3f}")
            print(f"  Acoustic + temporal:    F1 = {acoustic_temporal:.3f} (Δ: {acoustic_temporal_boost:+.3f})")
            print(f"  Environmental + temporal: F1 = {env_temporal:.3f} (Δ: {env_temporal_boost:+.3f})")
            print(f"  Combined:               F1 = {combined:.3f}")
            
            # Insights
            if acoustic_temporal_boost > 0.02:
                print(f"  ✅ Temporal acoustic features provide meaningful improvement!")
            else:
                print(f"  ⚠️  Limited benefit from temporal acoustic features")
                
            if env_advantage > 0.05:
                print(f"  🌡️  Environmental features significantly outperform acoustic")
            elif abs(env_advantage) < 0.02:
                print(f"  🤝 Acoustic and environmental features are comparable")
            else:
                print(f"  🎵 Acoustic features outperform environmental")
                
            # Temporal validation check
            if 'temporal' in model_results:
                temporal_combined = model_results['temporal'].get('combined_fair', {}).get('mean_f1', 0)
                leakage_check = combined - temporal_combined
                
                if leakage_check > 0.05:
                    print(f"  ⚠️  Potential temporal leakage detected (Δ: {leakage_check:.3f})")
                else:
                    print(f"  ✅ Temporal validation passes (Δ: {leakage_check:.3f})")
        
        # Overall recommendation
        print(f"\n📋 OVERALL RECOMMENDATION:")
        print("-" * 30)
        
        # Check if acoustic temporal features are generally helpful
        acoustic_temporal_helpful = False
        env_dominates = True
        
        for model_name, model_results in self.results.items():
            if 'standard' in model_results:
                results = model_results['standard']
                acoustic_base = results.get('acoustic_base_only', {}).get('mean_f1', 0)
                acoustic_temporal = results.get('acoustic_with_temporal', {}).get('mean_f1', 0)
                env_temporal = results.get('environmental_with_temporal', {}).get('mean_f1', 0)
                
                if acoustic_temporal - acoustic_base > 0.015:  # 1.5% improvement threshold
                    acoustic_temporal_helpful = True
                    
                if abs(env_temporal - acoustic_temporal) < 0.03:  # Within 3% is comparable
                    env_dominates = False
        
        if acoustic_temporal_helpful:
            print("✅ TEMPORAL ACOUSTIC FEATURES ARE VALUABLE")
            print("   → Include lag and moving average features for acoustic indices")
        else:
            print("⚠️  LIMITED VALUE FROM TEMPORAL ACOUSTIC FEATURES") 
            print("   → Focus on environmental temporal features")
            
        if env_dominates:
            print("🌡️  ENVIRONMENTAL FEATURES DOMINATE PREDICTION")
            print("   → Prioritize temperature, depth, and sound pressure patterns")
        else:
            print("🎵 ACOUSTIC INDICES PROVIDE MEANINGFUL PREDICTION")
            print("   → Both acoustic and environmental features are important")

def main():
    """Run the improved temporal analysis pipeline."""
    
    data_dir = Path("../data/processed")
    
    print("🚀 IMPROVED TEMPORAL ANALYSIS PIPELINE")
    print("=" * 80)
    print("Addressing fundamental methodological issues:")
    print("1. Preserve fine temporal resolution before aggregation")
    print("2. Activity-informed (not clustering-based) feature selection")  
    print("3. Fair comparison between acoustic and environmental features")
    print("4. Systematic evaluation with proper temporal validation")
    print()
    
    # Initialize analysis
    analyzer = ImprovedTemporalAnalysis(data_dir)
    
    # Execute pipeline
    if not analyzer.load_native_resolution_data():
        print("❌ Failed to load data")
        return
        
    if not analyzer.identify_predictive_indices():
        print("❌ Failed to identify predictive indices")
        return
        
    if not analyzer.create_fine_resolution_temporal_features():
        print("❌ Failed to create temporal features")
        return
        
    if not analyzer.create_analysis_dataset():
        print("❌ Failed to create analysis dataset")
        return
        
    if not analyzer.comparative_analysis():
        print("❌ Failed to run comparative analysis")
        return
        
    analyzer.generate_insights()
    
    print(f"\n🎯 ANALYSIS COMPLETE!")
    print("This improved approach addresses the methodological issues")
    print("and provides a fair comparison of acoustic vs environmental predictors.")

if __name__ == "__main__":
    main()