#!/usr/bin/env python3
"""
PHASE 7: TEMPORAL SYNCHRONY ANALYSIS WITH DIMENSION REDUCTION
============================================================
Goal: Rigorous analysis of temporal synchrony between acoustic indices and species
      with proper dimension reduction and multi-species comparison.

Key analyses:
1. Temporal correlation matrix for all species vs acoustic indices
2. Principal Component Analysis (PCA) to identify acoustic index clusters
3. Hierarchical clustering of indices by temporal patterns
4. Multi-species synchrony analysis
5. Identification of "acoustic signatures" for each species
6. Vessel detection temporal patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_data():
    """Load and clean the aligned dataset."""
    data_path = Path("data_01_aligned_2021.csv")
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Clean data types
    for col in df.columns:
        if col not in ['datetime', 'station']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"✓ Loaded and cleaned dataset: {df.shape}")
    return df

def identify_features_and_species(df):
    """Identify acoustic indices and species columns."""
    
    # Species of interest
    species_cols = [
        'Spotted seatrout', 'Atlantic croaker', 'Oyster toadfish boat whistle',
        'Bottlenose dolphin echolocation', 'Red drum', 'Silver perch',
        'Oyster toadfish grunt', 'Vessel', 'Bottlenose dolphin whistles',
        'Bottlenose dolphin burst pulses'
    ]
    available_species = [col for col in species_cols if col in df.columns]
    
    # Acoustic indices (exclude environmental and metadata)
    exclude_cols = [
        'datetime', 'station', 'Water temp (°C)', 'Water depth (m)',
        'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 'Broadband (1-40000 Hz)',
        'Mid (1200-7000 Hz)', 'total_fish_activity', 'any_activity', 
        'high_activity', 'num_active_species'
    ] + available_species
    
    acoustic_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Filter to numeric acoustic indices with variation
    valid_acoustic = []
    for col in acoustic_cols:
        if df[col].dtype in ['float64', 'int64']:
            if df[col].fillna(df[col].mean()).std() > 0:  # Has variation
                valid_acoustic.append(col)
    
    print(f"📊 Features identified:")
    print(f"   Species/targets: {len(available_species)}")
    print(f"   Acoustic indices: {len(valid_acoustic)}")
    
    return available_species, valid_acoustic

def compute_temporal_correlation_matrix(df, species_list, acoustic_list, station='9M'):
    """
    Compute comprehensive temporal correlation matrix.
    """
    print(f"\n🔍 COMPUTING TEMPORAL CORRELATION MATRIX - Station {station}")
    print("=" * 65)
    
    # Filter to single station
    station_df = df[df['station'] == station].copy()
    station_df = station_df.sort_values('datetime').reset_index(drop=True)
    
    # Initialize correlation matrix
    correlation_matrix = pd.DataFrame(
        index=acoustic_list,
        columns=species_list,
        dtype=float
    )
    
    p_value_matrix = pd.DataFrame(
        index=acoustic_list,
        columns=species_list,
        dtype=float
    )
    
    # Compute correlations
    for species in species_list:
        if species not in station_df.columns:
            continue
            
        species_data = station_df[species].fillna(0)
        
        # Skip species with very low activity
        if species_data.sum() < 20:
            print(f"   ⏭️ Skipping {species}: too few detections ({species_data.sum()})")
            continue
        
        print(f"   🐟 {species}: {species_data.sum()} detections ({(species_data > 0).mean():.1%})")
        
        for acoustic in acoustic_list:
            if acoustic not in station_df.columns:
                continue
                
            acoustic_data = station_df[acoustic].fillna(station_df[acoustic].mean())
            
            if acoustic_data.std() == 0:
                continue
            
            # Compute correlation
            r, p = pearsonr(acoustic_data, species_data)
            correlation_matrix.loc[acoustic, species] = r
            p_value_matrix.loc[acoustic, species] = p
    
    # Remove rows/columns with all NaN
    correlation_matrix = correlation_matrix.dropna(how='all').dropna(axis=1, how='all')
    p_value_matrix = p_value_matrix.loc[correlation_matrix.index, correlation_matrix.columns]
    
    print(f"   📊 Final matrix: {correlation_matrix.shape}")
    return correlation_matrix, p_value_matrix

def perform_acoustic_clustering(correlation_matrix, n_clusters=5):
    """
    Cluster acoustic indices based on their species correlation patterns.
    """
    print(f"\n🎯 CLUSTERING ACOUSTIC INDICES")
    print("=" * 40)
    
    # Use correlation patterns as features for clustering
    acoustic_features = correlation_matrix.fillna(0)  # Replace NaN with 0
    
    if acoustic_features.shape[0] < 2:
        print("   ⚠️ Too few acoustic indices for clustering")
        return None, None, None
    
    # Standardize features
    scaler = StandardScaler()
    acoustic_features_scaled = scaler.fit_transform(acoustic_features)
    
    # K-means clustering
    kmeans = KMeans(n_clusters=min(n_clusters, acoustic_features.shape[0]), random_state=42)
    cluster_labels = kmeans.fit_predict(acoustic_features_scaled)
    
    # Hierarchical clustering for dendrogram
    linkage_matrix = linkage(acoustic_features_scaled, method='ward')
    
    # Assign cluster labels
    acoustic_clusters = pd.DataFrame({
        'acoustic_index': acoustic_features.index,
        'cluster': cluster_labels
    })
    
    print(f"   📊 Clustered {len(acoustic_features)} indices into {len(set(cluster_labels))} groups")
    
    # Show cluster composition
    for cluster_id in sorted(set(cluster_labels)):
        cluster_indices = acoustic_clusters[acoustic_clusters['cluster'] == cluster_id]['acoustic_index'].tolist()
        print(f"   Cluster {cluster_id}: {len(cluster_indices)} indices")
        print(f"      {', '.join(cluster_indices[:5])}" + ("..." if len(cluster_indices) > 5 else ""))
    
    return acoustic_clusters, linkage_matrix, scaler

def identify_acoustic_signatures(correlation_matrix, p_value_matrix, threshold=0.5):
    """
    Identify acoustic signatures (indices strongly correlated with each species).
    """
    print(f"\n🎵 IDENTIFYING ACOUSTIC SIGNATURES")
    print("=" * 50)
    print(f"Using correlation threshold: |r| > {threshold}")
    
    signatures = {}
    
    for species in correlation_matrix.columns:
        species_correlations = correlation_matrix[species].dropna()
        species_pvalues = p_value_matrix[species].dropna()
        
        # Find strong correlations
        strong_correlations = species_correlations[
            (abs(species_correlations) > threshold) & 
            (species_pvalues < 0.05)
        ].sort_values(key=abs, ascending=False)
        
        if len(strong_correlations) > 0:
            signatures[species] = strong_correlations
            
            print(f"\n   🐟 {species} signature ({len(strong_correlations)} indices):")
            for idx, r in strong_correlations.head(5).items():
                significance = "***" if species_pvalues[idx] < 0.001 else "**" if species_pvalues[idx] < 0.01 else "*"
                print(f"      {idx:<20} r={r:+.3f} {significance}")
            
            if len(strong_correlations) > 5:
                print(f"      ... and {len(strong_correlations) - 5} more")
        else:
            print(f"\n   🐟 {species}: No strong acoustic signature found")
    
    return signatures

def perform_pca_analysis(correlation_matrix):
    """
    Perform PCA on the correlation matrix to find principal acoustic patterns.
    """
    print(f"\n🔬 PRINCIPAL COMPONENT ANALYSIS")
    print("=" * 45)
    
    # PCA on acoustic indices (rows) using species correlations as features
    acoustic_features = correlation_matrix.fillna(0)
    
    if acoustic_features.shape[1] < 2:
        print("   ⚠️ Too few species for meaningful PCA")
        return None, None
    
    # Standardize
    scaler = StandardScaler()
    acoustic_features_scaled = scaler.fit_transform(acoustic_features)
    
    # PCA
    n_components = min(5, acoustic_features.shape[1])
    pca = PCA(n_components=n_components)
    acoustic_pca = pca.fit_transform(acoustic_features_scaled)
    
    # Create results DataFrame
    pca_results = pd.DataFrame(
        acoustic_pca,
        index=acoustic_features.index,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )
    
    print(f"   📊 PCA Results:")
    print(f"      Components: {n_components}")
    print(f"      Explained variance:")
    for i, var_ratio in enumerate(pca.explained_variance_ratio_):
        print(f"         PC{i+1}: {var_ratio:.3f} ({var_ratio*100:.1f}%)")
    
    cumulative_var = np.cumsum(pca.explained_variance_ratio_)
    print(f"      Cumulative variance (PC1-PC{n_components}): {cumulative_var[-1]:.3f} ({cumulative_var[-1]*100:.1f}%)")
    
    # Show component loadings
    loadings = pd.DataFrame(
        pca.components_.T,
        index=acoustic_features.columns,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )
    
    print(f"\n   📊 Top loadings for first 2 components:")
    for pc in ['PC1', 'PC2']:
        if pc in loadings.columns:
            print(f"      {pc} (explains {pca.explained_variance_ratio_[int(pc[2:])-1]*100:.1f}% variance):")
            top_loadings = loadings[pc].abs().nlargest(3)
            for species, loading in top_loadings.items():
                actual_loading = loadings.loc[species, pc]
                print(f"         {species}: {actual_loading:+.3f}")
    
    return pca_results, pca

def compare_species_patterns(signatures, correlation_matrix):
    """
    Compare acoustic signature patterns between species.
    """
    print(f"\n🔍 COMPARING SPECIES ACOUSTIC PATTERNS")
    print("=" * 55)
    
    if len(signatures) < 2:
        print("   ⚠️ Need at least 2 species with signatures for comparison")
        return
    
    # Find shared acoustic indices between species
    species_indices = {species: set(sig.index) for species, sig in signatures.items()}
    
    print(f"   📊 Signature overlap analysis:")
    species_list = list(signatures.keys())
    
    for i in range(len(species_list)):
        for j in range(i+1, len(species_list)):
            species1, species2 = species_list[i], species_list[j]
            
            indices1 = species_indices[species1]
            indices2 = species_indices[species2]
            
            shared = indices1.intersection(indices2)
            total_unique = indices1.union(indices2)
            
            if len(shared) > 0:
                jaccard = len(shared) / len(total_unique)
                print(f"      {species1[:20]:20} ∩ {species2[:20]:20}: {len(shared):2d} shared indices (Jaccard: {jaccard:.3f})")
                
                # Show the shared indices with their correlations
                if len(shared) <= 3:
                    for idx in shared:
                        r1 = correlation_matrix.loc[idx, species1]
                        r2 = correlation_matrix.loc[idx, species2]
                        print(f"         {idx}: r1={r1:+.3f}, r2={r2:+.3f}")

def generate_summary_recommendations(signatures, correlation_matrix, pca_results=None):
    """
    Generate actionable recommendations based on the temporal synchrony analysis.
    """
    print(f"\n💡 TEMPORAL SYNCHRONY ANALYSIS RECOMMENDATIONS")
    print("=" * 70)
    
    # Count species with strong signatures
    species_with_signatures = len(signatures)
    total_species = len(correlation_matrix.columns)
    
    print(f"📊 SUMMARY STATISTICS:")
    print(f"   Species analyzed: {total_species}")
    print(f"   Species with acoustic signatures: {species_with_signatures}")
    print(f"   Coverage: {species_with_signatures/total_species*100:.1f}%")
    
    if species_with_signatures == 0:
        print(f"\n❌ NO ACOUSTIC SIGNATURES FOUND")
        print("   Recommendations:")
        print("   1. Lower correlation threshold (try 0.3 instead of 0.5)")
        print("   2. Check data quality and temporal alignment")
        print("   3. Consider different correlation methods (Spearman, Kendall)")
        return
    
    # Analyze signature strength
    max_correlations = []
    for species, sig in signatures.items():
        max_correlations.append(abs(sig).max())
    
    avg_max_correlation = np.mean(max_correlations)
    
    print(f"   Average strongest correlation per species: {avg_max_correlation:.3f}")
    
    print(f"\n🎯 SPECIES-SPECIFIC RECOMMENDATIONS:")
    
    for species, sig in signatures.items():
        n_indices = len(sig)
        max_r = abs(sig).max()
        top_index = abs(sig).idxmax()
        
        print(f"\n   🐟 {species}:")
        print(f"      Signature strength: {n_indices} indices, max |r|={max_r:.3f}")
        print(f"      Top acoustic index: {top_index} (r={sig[top_index]:+.3f})")
        
        if max_r > 0.7:
            print(f"      ✅ STRONG signature - excellent for temporal monitoring")
        elif max_r > 0.5:
            print(f"      ✅ GOOD signature - suitable for temporal analysis")
        else:
            print(f"      ⚠️ WEAK signature - may need combined indices")
    
    print(f"\n🔧 PREDICTIVE MODELING RECOMMENDATIONS:")
    print("   1. TEMPORAL-AWARE FEATURES:")
    print("      - Use top acoustic indices from signatures as raw features")
    print("      - Create temporal lag features (species detection follows acoustic patterns)")
    print("      - Preserve temporal structure in train/test splits")
    
    print("\n   2. SPECIES-SPECIFIC MODELS:")
    strong_signature_species = [s for s, sig in signatures.items() if abs(sig).max() > 0.6]
    if strong_signature_species:
        print(f"      Priority species (strong signatures): {len(strong_signature_species)}")
        for species in strong_signature_species:
            max_r = abs(signatures[species]).max()
            print(f"         {species} (max |r|={max_r:.3f})")
    
    print("\n   3. DIMENSION REDUCTION STRATEGY:")
    if pca_results is not None:
        print("      - Use PCA components as features (capture 80%+ variance)")
        print("      - Combine with temporal lag structure")
    else:
        print("      - Group correlated acoustic indices")
        print("      - Use cluster representatives as features")
    
    print("\n   4. VALIDATION STRATEGY:")
    print("      - Use temporal train/test splits (chronological order)")
    print("      - Validate temporal correlation preservation")
    print("      - Test on different seasons/time periods")

def main():
    print("🔄 PHASE 7: TEMPORAL SYNCHRONY ANALYSIS WITH DIMENSION REDUCTION")
    print("=" * 80)
    print("Goal: Rigorous temporal synchrony analysis with dimension reduction")
    print("      and multi-species acoustic signature identification")
    
    # Load and prepare data
    df = load_and_clean_data()
    species_list, acoustic_list = identify_features_and_species(df)
    
    if len(species_list) == 0 or len(acoustic_list) == 0:
        print("❌ No species or acoustic indices found!")
        return
    
    # Analysis for each station
    all_results = {}
    stations = df['station'].unique()
    
    for station in stations:
        print(f"\n{'='*25} STATION {station} {'='*25}")
        
        # Compute correlation matrix
        corr_matrix, p_matrix = compute_temporal_correlation_matrix(
            df, species_list, acoustic_list, station
        )
        
        if corr_matrix.empty:
            print(f"   ⚠️ No valid correlations for station {station}")
            continue
        
        # Acoustic clustering
        clusters, linkage_mat, scaler = perform_acoustic_clustering(corr_matrix)
        
        # Identify acoustic signatures
        signatures = identify_acoustic_signatures(corr_matrix, p_matrix, threshold=0.5)
        
        # PCA analysis
        pca_results, pca_model = perform_pca_analysis(corr_matrix)
        
        # Compare species patterns
        compare_species_patterns(signatures, corr_matrix)
        
        # Store results
        all_results[station] = {
            'correlation_matrix': corr_matrix,
            'p_value_matrix': p_matrix,
            'signatures': signatures,
            'clusters': clusters,
            'pca_results': pca_results,
            'pca_model': pca_model
        }
    
    # Generate summary recommendations
    if all_results:
        # Use first station for overall recommendations
        first_station = list(all_results.keys())[0]
        generate_summary_recommendations(
            all_results[first_station]['signatures'],
            all_results[first_station]['correlation_matrix'],
            all_results[first_station]['pca_results']
        )
    
    # Save results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    for station, results in all_results.items():
        # Save correlation matrices
        results['correlation_matrix'].to_csv(
            output_dir / f"phase7_correlation_matrix_{station}.csv"
        )
        
        # Save signatures
        if results['signatures']:
            signature_data = []
            for species, sig in results['signatures'].items():
                for idx, r in sig.items():
                    signature_data.append({
                        'station': station,
                        'species': species,
                        'acoustic_index': idx,
                        'correlation': r,
                        'abs_correlation': abs(r)
                    })
            
            pd.DataFrame(signature_data).to_csv(
                output_dir / f"phase7_acoustic_signatures_{station}.csv", index=False
            )
    
    print(f"\n💾 RESULTS SAVED:")
    print(f"   📊 Correlation matrices: phase7_correlation_matrix_[station].csv")
    print(f"   🎵 Acoustic signatures: phase7_acoustic_signatures_[station].csv")
    
    print("\n🎉 PHASE 7 COMPLETE!")
    print("=" * 30)
    print("✅ Temporal synchrony analysis completed")
    print("✅ Dimension reduction performed")
    print("✅ Multi-species signatures identified")
    print("✅ Predictive modeling recommendations generated")
    
    return all_results

if __name__ == "__main__":
    main()