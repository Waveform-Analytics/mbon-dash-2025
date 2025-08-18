#!/usr/bin/env python3
"""
Exploratory Analysis of Acoustic Indices Data

This script provides comprehensive exploration of acoustic indices data to inform
research questions about biodiversity prediction and dimensionality reduction.

Key Research Questions:
1. Can we reduce 56+ acoustic indices to 3-5 "super indices" via PCA?
2. Which indices best predict species detection patterns?
3. How do different index categories (diversity, complexity, spectral) perform?
4. What are the temporal patterns and correlations between indices?

Run with: uv run scripts/exploratory/explore_acoustic_indices.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# Create output directory
FIGURES_DIR = Path("scripts/exploratory/figures")
FIGURES_DIR.mkdir(exist_ok=True)

def load_acoustic_indices():
    """Load and preprocess acoustic indices data."""
    print("📊 Loading acoustic indices data...")
    
    # Load the raw indices files
    data_dir = Path("data/cdn/raw-data/indices")
    
    # Check what files we have
    indices_files = list(data_dir.glob("*.csv"))
    print(f"Found {len(indices_files)} indices files:")
    for file in indices_files:
        print(f"  - {file.name}")
    
    if not indices_files:
        print("❌ No indices files found!")
        return None, None
    
    # Load the main indices file (Full BW version)
    main_file = data_dir / "Acoustic_Indices_9M_2021_FullBW_v2_Final.csv"
    if not main_file.exists():
        main_file = indices_files[0]  # Fallback to first available file
    
    print(f"📂 Loading primary indices file: {main_file.name}")
    
    # Read the data
    df = pd.read_csv(main_file)
    print(f"✅ Loaded {len(df)} records with {len(df.columns)} columns")
    
    # Parse the date column
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.month
        df['Day'] = df['Date'].dt.day
        df['Hour'] = df['Date'].dt.hour
    
    # Load index categories for better understanding
    categories_file = Path("data/cdn/raw-data/Updated_Index_Categories_v2.csv")
    categories = None
    if categories_file.exists():
        categories = pd.read_csv(categories_file)
        print(f"📋 Loaded {len(categories)} index category definitions")
    
    return df, categories

def basic_data_exploration(df, categories=None):
    """Perform basic exploration of the indices dataset."""
    print("\n" + "="*60)
    print("🔍 BASIC DATA EXPLORATION")
    print("="*60)
    
    # Basic info
    print(f"Dataset shape: {df.shape}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Time span: {(df['Date'].max() - df['Date'].min()).days} days")
    
    # Identify numeric columns (these are our indices)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    index_cols = [col for col in numeric_cols if col not in ['Month', 'Day', 'Hour']]
    
    print(f"\n📈 Found {len(index_cols)} acoustic indices:")
    
    # Group by category if we have category data
    if categories is not None:
        print("\n📊 Indices by Category:")
        category_counts = categories['Category'].value_counts()
        for cat, count in category_counts.items():
            print(f"  {cat}: {count} indices")
            
        # Show some examples from each category
        print("\n🔍 Sample indices by category:")
        for cat in category_counts.index[:5]:  # Show top 5 categories
            indices_in_cat = categories[categories['Category'] == cat]['Prefix'].tolist()
            available_in_cat = [idx for idx in indices_in_cat if idx in index_cols]
            if available_in_cat:
                print(f"  {cat}: {', '.join(available_in_cat[:5])}")
    else:
        # Just show first 20 indices
        print("First 20 indices:", ', '.join(index_cols[:20]))
    
    # Missing data analysis
    missing_data = df[index_cols].isnull().sum()
    if missing_data.sum() > 0:
        print(f"\n⚠️  Missing data found in {(missing_data > 0).sum()} indices")
        worst_missing = missing_data[missing_data > 0].head()
        for idx, count in worst_missing.items():
            print(f"  {idx}: {count} missing ({count/len(df)*100:.1f}%)")
    else:
        print("\n✅ No missing data in acoustic indices")
    
    return index_cols

def summary_statistics(df, index_cols):
    """Generate summary statistics for acoustic indices."""
    print("\n" + "="*60)
    print("📊 SUMMARY STATISTICS")
    print("="*60)
    
    # Basic stats
    stats = df[index_cols].describe()
    print("Summary statistics computed for all indices")
    
    # Look for extreme values or potential outliers
    print("\n🔍 Outlier Detection (IQR method):")
    outlier_counts = {}
    
    for col in index_cols[:10]:  # Check first 10 indices as examples
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        outlier_counts[col] = outliers
        
        if outliers > 0:
            print(f"  {col}: {outliers} outliers ({outliers/len(df)*100:.1f}%)")
    
    # Show indices with highest variability (CV)
    print("\n📈 Most Variable Indices (Coefficient of Variation):")
    cv_data = []
    for col in index_cols:
        if df[col].std() > 0:  # Avoid division by zero
            cv = df[col].std() / abs(df[col].mean()) if df[col].mean() != 0 else np.inf
            cv_data.append((col, cv))
    
    cv_data.sort(key=lambda x: x[1], reverse=True)
    for idx, cv in cv_data[:10]:
        print(f"  {idx}: CV = {cv:.2f}")
    
    return stats, outlier_counts

def temporal_patterns(df, index_cols):
    """Analyze temporal patterns in acoustic indices."""
    print("\n" + "="*60)
    print("⏰ TEMPORAL PATTERNS ANALYSIS")
    print("="*60)
    
    # Monthly patterns for key indices
    key_indices = index_cols[:8]  # Focus on first 8 indices
    
    monthly_stats = df.groupby('Month')[key_indices].agg(['mean', 'std']).round(3)
    print("Monthly patterns computed for key indices")
    
    # Hourly patterns (if we have hour data)
    if 'Hour' in df.columns and df['Hour'].nunique() > 1:
        hourly_stats = df.groupby('Hour')[key_indices].agg(['mean', 'std']).round(3)
        print("Hourly patterns computed for key indices")
    
    # Create temporal visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Temporal Patterns in Acoustic Indices', fontsize=16, fontweight='bold')
    
    # Plot 1: Time series of a representative index
    representative_idx = key_indices[0]
    axes[0, 0].plot(df['Date'], df[representative_idx], alpha=0.7, linewidth=0.8)
    axes[0, 0].set_title(f'Time Series: {representative_idx}')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Index Value')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Plot 2: Monthly boxplot
    monthly_data = df.melt(
        id_vars=['Month'], 
        value_vars=key_indices[:4], 
        var_name='Index', 
        value_name='Value'
    )
    sns.boxplot(data=monthly_data, x='Month', y='Value', hue='Index', ax=axes[0, 1])
    axes[0, 1].set_title('Monthly Variation (Top 4 Indices)')
    axes[0, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Plot 3: Hourly patterns (if available)
    if 'Hour' in df.columns and df['Hour'].nunique() > 1:
        hourly_means = df.groupby('Hour')[key_indices[:4]].mean()
        for idx in key_indices[:4]:
            axes[1, 0].plot(hourly_means.index, hourly_means[idx], marker='o', label=idx)
        axes[1, 0].set_title('Hourly Patterns (Top 4 Indices)')
        axes[1, 0].set_xlabel('Hour of Day')
        axes[1, 0].set_ylabel('Mean Index Value')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    else:
        axes[1, 0].text(0.5, 0.5, 'No hourly data available', 
                       ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Hourly Patterns (Not Available)')
    
    # Plot 4: Distribution of a key index
    axes[1, 1].hist(df[representative_idx], bins=30, alpha=0.7, edgecolor='black')
    axes[1, 1].set_title(f'Distribution: {representative_idx}')
    axes[1, 1].set_xlabel('Index Value')
    axes[1, 1].set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'temporal_patterns.png', dpi=300, bbox_inches='tight')
    print(f"📊 Temporal patterns plot saved to {FIGURES_DIR / 'temporal_patterns.png'}")
    
    return monthly_stats

def correlation_analysis(df, index_cols, categories=None):
    """Analyze correlations between acoustic indices."""
    print("\n" + "="*60)
    print("🔗 CORRELATION ANALYSIS")
    print("="*60)
    
    # Compute correlation matrix for a subset of indices (to keep it manageable)
    if len(index_cols) > 30:
        print(f"📊 Computing correlations for first 30 indices (out of {len(index_cols)})")
        analysis_cols = index_cols[:30]
    else:
        analysis_cols = index_cols
    
    corr_matrix = df[analysis_cols].corr()
    
    # Find highly correlated pairs
    high_corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > 0.8:  # High correlation threshold
                high_corr_pairs.append((
                    corr_matrix.columns[i], 
                    corr_matrix.columns[j], 
                    corr_val
                ))
    
    print(f"\n🔍 Found {len(high_corr_pairs)} highly correlated pairs (|r| > 0.8):")
    for idx1, idx2, corr in sorted(high_corr_pairs, key=lambda x: abs(x[2]), reverse=True)[:10]:
        print(f"  {idx1} ↔ {idx2}: r = {corr:.3f}")
    
    # Create correlation heatmap
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # Mask upper triangle
    sns.heatmap(
        corr_matrix, 
        mask=mask,
        annot=False, 
        cmap='RdBu_r', 
        center=0,
        square=True,
        fmt='.2f',
        cbar_kws={"shrink": .8}
    )
    plt.title('Acoustic Indices Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
    print(f"📊 Correlation matrix saved to {FIGURES_DIR / 'correlation_matrix.png'}")
    
    # If we have categories, analyze correlations within and between categories
    if categories is not None:
        print("\n📊 Correlation Analysis by Category:")
        
        # Create mapping of indices to categories
        idx_to_category = {}
        for _, row in categories.iterrows():
            if row['Prefix'] in analysis_cols:
                idx_to_category[row['Prefix']] = row['Category']
        
        # Analyze within-category correlations
        category_groups = {}
        for idx, cat in idx_to_category.items():
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append(idx)
        
        for cat, indices in category_groups.items():
            if len(indices) > 1:
                cat_corr = df[indices].corr()
                mean_corr = cat_corr.values[np.triu_indices_from(cat_corr.values, k=1)].mean()
                print(f"  {cat}: {len(indices)} indices, mean correlation = {mean_corr:.3f}")
    
    return corr_matrix, high_corr_pairs

def preliminary_pca_analysis(df, index_cols):
    """Perform preliminary PCA to understand dimensionality reduction potential."""
    print("\n" + "="*60)
    print("🎯 PRELIMINARY PCA ANALYSIS")
    print("="*60)
    
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    
    # Prepare data for PCA
    # Remove any columns with missing values or zero variance
    clean_indices = []
    for col in index_cols:
        if df[col].notna().all() and df[col].std() > 0:
            clean_indices.append(col)
    
    print(f"📊 Using {len(clean_indices)} indices for PCA (out of {len(index_cols)})")
    
    if len(clean_indices) < 3:
        print("❌ Not enough clean indices for meaningful PCA")
        return None
    
    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[clean_indices])
    
    # Fit PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)
    
    # Analyze explained variance
    explained_var = pca.explained_variance_ratio_
    cumulative_var = np.cumsum(explained_var)
    
    print(f"\n📈 PCA Results:")
    print(f"  PC1 explains {explained_var[0]:.1%} of variance")
    print(f"  PC2 explains {explained_var[1]:.1%} of variance")
    print(f"  PC3 explains {explained_var[2]:.1%} of variance")
    print(f"  First 3 PCs explain {cumulative_var[2]:.1%} of total variance")
    
    # Find how many components needed for 90% variance
    n_components_90 = np.argmax(cumulative_var >= 0.9) + 1
    print(f"  {n_components_90} components needed for 90% variance")
    
    # Create PCA visualization
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Plot 1: Scree plot
    axes[0].plot(range(1, min(21, len(explained_var)+1)), explained_var[:20], 'bo-')
    axes[0].set_xlabel('Principal Component')
    axes[0].set_ylabel('Explained Variance Ratio')
    axes[0].set_title('Scree Plot (First 20 Components)')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Cumulative variance
    axes[1].plot(range(1, min(21, len(cumulative_var)+1)), cumulative_var[:20], 'ro-')
    axes[1].axhline(y=0.9, color='gray', linestyle='--', label='90% threshold')
    axes[1].axvline(x=n_components_90, color='gray', linestyle='--', 
                   label=f'{n_components_90} components')
    axes[1].set_xlabel('Number of Components')
    axes[1].set_ylabel('Cumulative Explained Variance')
    axes[1].set_title('Cumulative Variance Explained')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: PC1 vs PC2 scatter
    axes[2].scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.6, s=30)
    axes[2].set_xlabel(f'PC1 ({explained_var[0]:.1%} variance)')
    axes[2].set_ylabel(f'PC2 ({explained_var[1]:.1%} variance)')
    axes[2].set_title('First Two Principal Components')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'pca_analysis.png', dpi=300, bbox_inches='tight')
    print(f"📊 PCA analysis plot saved to {FIGURES_DIR / 'pca_analysis.png'}")
    
    # Show top contributing indices for first 3 PCs
    print(f"\n🔍 Top Contributing Indices:")
    for pc in range(3):
        loadings = pca.components_[pc]
        top_indices = np.argsort(np.abs(loadings))[-5:][::-1]  # Top 5 by absolute loading
        print(f"  PC{pc+1}:")
        for idx in top_indices:
            print(f"    {clean_indices[idx]}: {loadings[idx]:.3f}")
    
    return {
        'pca': pca,
        'explained_variance': explained_var,
        'cumulative_variance': cumulative_var,
        'n_components_90': n_components_90,
        'clean_indices': clean_indices,
        'scaled_data': X_scaled
    }

def generate_research_insights(df, index_cols, categories, pca_results):
    """Generate insights relevant to the research questions."""
    print("\n" + "="*60)
    print("💡 RESEARCH INSIGHTS & RECOMMENDATIONS")
    print("="*60)
    
    insights = []
    
    # Dimensionality reduction potential
    if pca_results:
        n_comp_90 = pca_results['n_components_90']
        total_indices = len(index_cols)
        reduction_ratio = n_comp_90 / total_indices
        
        insights.append(f"🎯 Dimensionality Reduction: {n_comp_90} components capture 90% of variance from {total_indices} indices ({reduction_ratio:.1%} retention)")
        
        if n_comp_90 <= 5:
            insights.append("✅ Excellent potential for 'super indices' - less than 5 components needed")
        elif n_comp_90 <= 10:
            insights.append("👍 Good potential for index reduction - 10 or fewer components needed")
        else:
            insights.append("⚠️  High dimensionality - may need >10 components for adequate representation")
    
    # Data quality assessment
    total_records = len(df)
    date_span = (df['Date'].max() - df['Date'].min()).days
    insights.append(f"📊 Data Coverage: {total_records} records over {date_span} days (Station 9M, 2021)")
    
    # Temporal patterns
    if 'Month' in df.columns:
        months_covered = df['Month'].nunique()
        insights.append(f"📅 Temporal Coverage: {months_covered} months of data available")
    
    # Index categories (if available)
    if categories is not None:
        category_counts = categories['Category'].value_counts()
        insights.append(f"📋 Index Categories: {len(category_counts)} categories available")
        dominant_category = category_counts.index[0]
        insights.append(f"   Most represented: {dominant_category} ({category_counts.iloc[0]} indices)")
    
    # Missing data assessment
    missing_counts = df[index_cols].isnull().sum()
    clean_indices = (missing_counts == 0).sum()
    insights.append(f"✅ Data Quality: {clean_indices}/{len(index_cols)} indices have no missing data")
    
    print("\n📝 Key Insights:")
    for i, insight in enumerate(insights, 1):
        print(f"{i:2d}. {insight}")
    
    # Research recommendations
    print(f"\n🔬 Research Recommendations:")
    recommendations = [
        "Focus PCA analysis on the clean indices for reliable dimensionality reduction",
        "Compare Full BW vs 8kHz versions to understand frequency range impacts",
        "Expand analysis to other stations (14M, 37M) for spatial comparison",
        "Correlate indices with species detection data to identify biodiversity predictors",
        "Investigate temporal patterns to understand environmental vs biological drivers"
    ]
    
    if pca_results and pca_results['n_components_90'] <= 5:
        recommendations.append("Excellent candidate for 'super indices' approach - proceed with PC analysis")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i:2d}. {rec}")
    
    return insights

def main():
    """Main execution function."""
    print("🎵 MBON Acoustic Indices Exploratory Analysis")
    print("=" * 60)
    print("Research Focus: Biodiversity prediction via acoustic indices")
    print("Questions: PCA reduction, species correlation, temporal patterns")
    print("=" * 60)
    
    # Load data
    df, categories = load_acoustic_indices()
    if df is None:
        print("❌ Failed to load data. Exiting.")
        return
    
    # Basic exploration
    index_cols = basic_data_exploration(df, categories)
    
    # Summary statistics
    stats, outliers = summary_statistics(df, index_cols)
    
    # Temporal analysis
    temporal_stats = temporal_patterns(df, index_cols)
    
    # Correlation analysis
    corr_matrix, high_corr = correlation_analysis(df, index_cols, categories)
    
    # PCA analysis
    pca_results = preliminary_pca_analysis(df, index_cols)
    
    # Research insights
    insights = generate_research_insights(df, index_cols, categories, pca_results)
    
    print(f"\n🎯 Analysis complete! Check {FIGURES_DIR} for visualizations.")
    print("📚 Next steps: Use insights to inform mbon_analysis package development")

if __name__ == "__main__":
    main()