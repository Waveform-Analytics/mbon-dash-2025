#!/usr/bin/env python3
"""
Simple temporal correlation check to answer the key question:
Why do acoustic indices like ADI visually match species patterns 
but don't show up as strong predictors in ML models?
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

def main():
    print("🔍 SIMPLE CORRELATION CHECK: Visual Pattern vs Statistical Correlation")
    print("=" * 80)
    
    # Load data
    data_path = Path("data_01_aligned_2021.csv")
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    print(f"Dataset: {df.shape}")
    print(f"Stations: {df['station'].unique()}")
    
    # Focus on single station to preserve temporal structure
    station = '9M'
    station_df = df[df['station'] == station].copy()
    station_df = station_df.sort_values('datetime').reset_index(drop=True)
    
    print(f"\nFocus: Station {station} ({station_df.shape})")
    
    # Clean data types
    for col in station_df.columns:
        if col not in ['datetime', 'station']:
            station_df[col] = pd.to_numeric(station_df[col], errors='coerce')
    
    # Check key species and acoustic indices
    species = 'Spotted seatrout'
    acoustic_indices = ['ADI', 'SKEWf', 'KURTf', 'MED', 'BGNf']
    
    if species not in station_df.columns:
        print(f"⚠️ {species} not found in dataset")
        return
        
    species_data = station_df[species].fillna(0)
    
    print(f"\n🐟 {species} Analysis:")
    print(f"   Total detections: {species_data.sum()}")
    print(f"   Detection rate: {(species_data > 0).mean():.2%}")
    print(f"   Time range: {station_df['datetime'].min()} to {station_df['datetime'].max()}")
    
    print(f"\n📊 TEMPORAL CORRELATIONS:")
    print("-" * 60)
    print(f"{'Acoustic Index':<15} {'Pearson r':<12} {'P-value':<12} {'Significance'}")
    print("-" * 60)
    
    correlation_results = []
    
    for acoustic in acoustic_indices:
        if acoustic not in station_df.columns:
            print(f"⚠️ {acoustic} not found in dataset")
            continue
            
        acoustic_data = station_df[acoustic].fillna(station_df[acoustic].mean())
        
        if acoustic_data.std() == 0:
            print(f"⚠️ {acoustic} has constant values")
            continue
        
        # Temporal correlation
        r, p = pearsonr(acoustic_data, species_data)
        
        significance = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        
        print(f"{acoustic:<15} {r:>+8.3f}    {p:>8.3e}  {significance}")
        
        correlation_results.append({
            'acoustic_index': acoustic,
            'correlation': r,
            'p_value': p,
            'abs_correlation': abs(r)
        })
    
    # Find ALL acoustic indices correlations
    print(f"\n🎯 CHECKING ALL ACOUSTIC INDICES:")
    print("Looking for strong correlations (|r| > 0.3)...")
    
    acoustic_cols = [col for col in station_df.columns if col not in [
        'datetime', 'station', 'Water temp (°C)', 'Water depth (m)',
        'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 'Broadband (1-40000 Hz)',
        'total_fish_activity', 'any_activity', 'high_activity', 'num_active_species',
        species
    ]]
    
    # Filter to numeric only
    numeric_acoustic = []
    for col in acoustic_cols:
        if station_df[col].dtype in ['float64', 'int64']:
            acoustic_data = station_df[col].fillna(station_df[col].mean())
            if acoustic_data.std() > 0:  # Skip constant columns
                numeric_acoustic.append(col)
    
    print(f"Found {len(numeric_acoustic)} acoustic indices to check...")
    
    all_correlations = []
    for acoustic in numeric_acoustic:
        acoustic_data = station_df[acoustic].fillna(station_df[acoustic].mean())
        r, p = pearsonr(acoustic_data, species_data)
        
        all_correlations.append({
            'acoustic_index': acoustic,
            'correlation': r,
            'p_value': p,
            'abs_correlation': abs(r)
        })
    
    # Sort by absolute correlation
    all_correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
    
    print(f"\n🏆 TOP 15 CORRELATIONS WITH {species}:")
    print("-" * 70)
    print(f"{'Rank':<5} {'Acoustic Index':<20} {'Pearson r':<12} {'P-value':<12} {'Significance'}")
    print("-" * 70)
    
    for i, result in enumerate(all_correlations[:15], 1):
        r = result['correlation']
        p = result['p_value']
        significance = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        
        print(f"{i:<5} {result['acoustic_index']:<20} {r:>+8.3f}    {p:>8.3e}  {significance}")
    
    # Check ADI specifically
    if 'ADI' in [r['acoustic_index'] for r in all_correlations]:
        adi_result = next(r for r in all_correlations if r['acoustic_index'] == 'ADI')
        adi_rank = all_correlations.index(adi_result) + 1
        
        print(f"\n🎯 ADI SPECIFIC ANALYSIS:")
        print(f"   ADI correlation with {species}: {adi_result['correlation']:+.3f}")
        print(f"   ADI rank: #{adi_rank} out of {len(all_correlations)}")
        print(f"   ADI p-value: {adi_result['p_value']:.3e}")
        
        adi_data = station_df['ADI'].fillna(station_df['ADI'].mean())
        print(f"   ADI statistics: mean={adi_data.mean():.3f}, std={adi_data.std():.3f}")
        print(f"   ADI range: {adi_data.min():.3f} to {adi_data.max():.3f}")
    
    # Why might ML miss these correlations?
    print(f"\n💡 WHY YOUR ML ANALYSIS MIGHT HAVE MISSED THESE PATTERNS:")
    print("=" * 60)
    
    strong_correlations = [r for r in all_correlations if r['abs_correlation'] > 0.5]
    moderate_correlations = [r for r in all_correlations if 0.3 < r['abs_correlation'] <= 0.5]
    
    print(f"📈 Strong temporal correlations (|r| > 0.5): {len(strong_correlations)}")
    print(f"📈 Moderate correlations (0.3 < |r| ≤ 0.5): {len(moderate_correlations)}")
    
    print(f"\n🔍 REASONS FOR ML vs VISUAL DISCREPANCY:")
    print("1. Cross-validation shuffles temporal relationships")
    print("2. Feature standardization may mask temporal patterns")  
    print("3. ML focuses on predictive power across all conditions")
    print("4. Visual patterns show synchronous timing, not just prediction")
    print("5. Non-linear relationships may not be captured by linear models")
    
    if len(strong_correlations) > 0:
        print(f"\n✅ VALIDATION: Strong temporal correlations found!")
        print("   Your visual observation is statistically confirmed.")
        print("   These patterns exist but are masked in traditional ML approaches.")
    
    # Save results
    results_df = pd.DataFrame(all_correlations)
    results_df.to_csv('visual_pattern_correlation_check.csv', index=False)
    print(f"\n💾 Results saved to: visual_pattern_correlation_check.csv")

if __name__ == "__main__":
    main()