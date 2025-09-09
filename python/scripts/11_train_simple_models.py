#!/usr/bin/env python3
"""
Train simple predictive models (Logistic Regression and Random Forest) with temporal stratification.

This script implements temporal stratification to handle non-stationary marine soundscape signals,
where fish calling activity varies seasonally and different species have distinct temporal niches.

Outputs model performance metrics and feature importance rankings.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Machine learning imports
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report
)
# import shap  # Skip SHAP due to Python 3.12 compatibility issues


def load_modeling_data() -> pd.DataFrame:
    """Load the prepared modeling dataset."""
    data_file = Path(__file__).parent.parent.parent / "data" / "processed" / "modeling_dataset.json"
    
    if not data_file.exists():
        raise FileNotFoundError(f"Modeling dataset not found. Run 10_prepare_modeling_data.py first.")
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Convert to DataFrame
    df = pd.DataFrame(data['data'])
    
    print(f"✅ Loaded modeling dataset with {len(df):,} records")
    print(f"   Date range: {df['Date_x'].min()} to {df['Date_x'].max()}")
    print(f"   Stations: {', '.join(df['station'].unique())}")
    
    return df


def temporal_stratified_split(df: pd.DataFrame, test_size: float = 0.3, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform temporal stratification to handle non-stationary soundscape signals.
    
    Marine soundscapes have strong seasonal patterns:
    - Fish calling peaks during spawning season (spring)
    - Different species active at different times of year
    - Vessel activity may vary seasonally
    
    This stratification ensures both train/test sets contain representative samples 
    from each month, preserving temporal patterns while enabling generalization.
    """
    print(f"\n🕒 Performing temporal stratified split (test_size={test_size})...")
    
    # Extract month from date for stratification
    df['month'] = pd.to_datetime(df['Date_x']).dt.strftime('%Y-%m')
    months = sorted(df['month'].unique())
    
    print(f"   Available months: {', '.join(months)}")
    
    train_data_list = []
    test_data_list = []
    
    # Sample from each month proportionally
    for month in months:
        month_data = df[df['month'] == month].copy()
        n_month_records = len(month_data)
        n_test = max(1, int(n_month_records * test_size))  # Ensure at least 1 test record per month
        
        # Random sample within month
        test_indices = month_data.sample(n=n_test, random_state=random_state).index
        train_indices = month_data.drop(test_indices).index
        
        train_data_list.append(df.loc[train_indices])
        test_data_list.append(df.loc[test_indices])
        
        print(f"   {month}: {len(train_indices):,} train, {len(test_indices):,} test")
    
    train_df = pd.concat(train_data_list, ignore_index=True)
    test_df = pd.concat(test_data_list, ignore_index=True)
    
    print(f"✅ Split complete: {len(train_df):,} train ({len(train_df)/len(df):.1%}), {len(test_df):,} test ({len(test_df)/len(df):.1%})")
    
    # Verify temporal distribution preservation
    train_months = train_df['month'].value_counts().sort_index()
    test_months = test_df['month'].value_counts().sort_index()
    
    print(f"   Temporal balance preserved:")
    for month in months:
        train_pct = train_months.get(month, 0) / len(train_df) * 100
        test_pct = test_months.get(month, 0) / len(test_df) * 100
        print(f"     {month}: {train_pct:.1f}% train, {test_pct:.1f}% test")
    
    return train_df.drop('month', axis=1), test_df.drop('month', axis=1)


def prepare_features_and_targets(df: pd.DataFrame) -> Tuple[np.ndarray, Dict[str, np.ndarray], List[str]]:
    """Extract PCA features and target variables from the dataset."""
    
    # Feature columns (PCA components)
    feature_columns = [f'PC{i+1}' for i in range(5)]  # PC1-PC5
    X = df[feature_columns].values
    
    # Target variables
    targets = {
        'fish_presence': (df['fish_intensity'] > 0).astype(int).values,  # Binary: any fish activity
        'high_fish_activity': (df['fish_intensity'] > df['fish_intensity'].quantile(0.75)).astype(int).values,  # Binary: high activity
        'fish_intensity': df['fish_intensity'].values,  # Continuous: for regression
        'total_biodiversity': df['total_biodiversity'].values  # Ordinal: 0, 1, 2, 3 categories active
    }
    
    print(f"✅ Prepared features and targets:")
    print(f"   Features: {len(feature_columns)} PCA components")
    print(f"   Targets: {len(targets)} variables")
    
    # Print class balance for binary targets
    for target_name, target_values in targets.items():
        if target_name in ['fish_presence', 'high_fish_activity']:
            positive_pct = np.mean(target_values) * 100
            print(f"     {target_name}: {positive_pct:.1f}% positive class")
    
    return X, targets, feature_columns


def train_logistic_regression(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, 
                            target_name: str, feature_names: List[str]) -> Dict[str, Any]:
    """Train and evaluate a logistic regression model."""
    
    print(f"\n🔬 Training Logistic Regression for {target_name}...")
    
    # Standardize features (important for logistic regression)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model with L1 regularization for feature selection
    model = LogisticRegression(
        penalty='l1', 
        solver='liblinear', 
        C=1.0,  # Regularization strength
        random_state=42,
        max_iter=1000
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.0
    }
    
    # Feature coefficients (interpretable!)
    coefficients = pd.DataFrame({
        'feature': feature_names,
        'coefficient': model.coef_[0],
        'abs_coefficient': np.abs(model.coef_[0])
    }).sort_values('abs_coefficient', ascending=False)
    
    print(f"   Performance: F1={metrics['f1']:.3f}, Precision={metrics['precision']:.3f}, Recall={metrics['recall']:.3f}")
    print(f"   Top features: {', '.join(coefficients.head(3)['feature'].values)}")
    
    return {
        'model_type': 'logistic_regression',
        'target': target_name,
        'metrics': metrics,
        'feature_importance': coefficients.to_dict('records'),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'model_params': model.get_params(),
        'scaler_mean': scaler.mean_.tolist(),
        'scaler_std': scaler.scale_.tolist()
    }


def train_random_forest(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray,
                       target_name: str, feature_names: List[str]) -> Dict[str, Any]:
    """Train and evaluate a random forest model."""
    
    print(f"\n🌲 Training Random Forest for {target_name}...")
    
    # Train model (no scaling needed for tree-based models)
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,  # Shallow for interpretability
        min_samples_split=20,  # Prevent overfitting
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1  # Use all CPU cores
    )
    
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0.0
    }
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"   Performance: F1={metrics['f1']:.3f}, Precision={metrics['precision']:.3f}, Recall={metrics['recall']:.3f}")
    print(f"   Top features: {', '.join(importance.head(3)['feature'].values)}")
    
    # SHAP analysis for interpretability (skip for now due to Python 3.12 compatibility)
    print(f"   Skipping SHAP analysis (Python 3.12 compatibility)")
    shap_importance = pd.DataFrame({
        'feature': feature_names,
        'mean_abs_shap': [0.0] * len(feature_names)  # Placeholder
    })
    
    return {
        'model_type': 'random_forest',
        'target': target_name,
        'metrics': metrics,
        'feature_importance': importance.to_dict('records'),
        'shap_importance': shap_importance.to_dict('records'),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'model_params': model.get_params()
    }


def evaluate_model_variations(df: pd.DataFrame) -> Dict[str, Any]:
    """Test different model variations as outlined in the plan."""
    
    print(f"\n🔄 Testing model variations...")
    
    # Temporal stratified split
    train_df, test_df = temporal_stratified_split(df, test_size=0.3, random_state=42)
    
    # Prepare features and targets
    X_train, targets_train, feature_names = prepare_features_and_targets(train_df)
    X_test, targets_test, _ = prepare_features_and_targets(test_df)
    
    results = {
        'dataset_info': {
            'total_records': len(df),
            'train_records': len(train_df),
            'test_records': len(test_df),
            'features': len(feature_names),
            'split_strategy': 'temporal_stratified'
        },
        'models': []
    }
    
    # Test different target types
    target_types = ['fish_presence', 'high_fish_activity']  # Focus on binary classification
    model_types = ['logistic_regression', 'random_forest']
    
    for target_name in target_types:
        if np.sum(targets_test[target_name]) == 0:  # Skip if no positive examples in test
            print(f"⚠️  Skipping {target_name} - no positive examples in test set")
            continue
            
        y_train = targets_train[target_name] 
        y_test = targets_test[target_name]
        
        for model_type in model_types:
            try:
                if model_type == 'logistic_regression':
                    result = train_logistic_regression(X_train, y_train, X_test, y_test, target_name, feature_names)
                elif model_type == 'random_forest':
                    result = train_random_forest(X_train, y_train, X_test, y_test, target_name, feature_names)
                
                results['models'].append(result)
                
            except Exception as e:
                print(f"❌ Error training {model_type} for {target_name}: {e}")
    
    return results


def generate_model_summary(results: Dict[str, Any]) -> None:
    """Print a summary of model performance."""
    
    print(f"\n" + "=" * 80)
    print("📊 MODEL PERFORMANCE SUMMARY")
    print("=" * 80)
    
    print(f"Dataset: {results['dataset_info']['total_records']:,} records")
    print(f"Split: {results['dataset_info']['train_records']:,} train / {results['dataset_info']['test_records']:,} test")
    print(f"Strategy: {results['dataset_info']['split_strategy']}")
    
    # Performance table
    print(f"\nModel Performance:")
    print(f"{'Target':<20} {'Model':<18} {'F1':<6} {'Prec':<6} {'Rec':<6} {'AUC':<6}")
    print("-" * 70)
    
    for model in results['models']:
        metrics = model['metrics']
        print(f"{model['target']:<20} {model['model_type']:<18} "
              f"{metrics['f1']:.3f}  {metrics['precision']:.3f}  "
              f"{metrics['recall']:.3f}  {metrics['roc_auc']:.3f}")
    
    # Feature importance summary
    print(f"\nTop Predictive Features:")
    for model in results['models']:
        if model['model_type'] == 'random_forest':  # Use RF importance
            print(f"\n{model['target']} ({model['model_type']}):")
            for i, feat in enumerate(model['feature_importance'][:3]):
                print(f"  {i+1}. {feat['feature']}: {feat['importance']:.3f}")


def main():
    """Main execution function."""
    print("🚀 Starting simple model training with temporal stratification...")
    print("=" * 80)
    
    # Load modeling dataset
    print("\n1. Loading modeling dataset...")
    df = load_modeling_data()
    
    # Train and evaluate models
    print("\n2. Training models with temporal stratification...")
    results = evaluate_model_variations(df)
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    output_dir.mkdir(exist_ok=True)
    
    results_file = output_dir / "simple_models_results.json"
    results['metadata'] = {
        'generated_at': datetime.now().isoformat(),
        'version': '1.0.0',
        'description': 'Simple model results with temporal stratification for non-stationary marine soundscape data',
        'script': 'scripts/11_train_simple_models.py'
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Saved results to: {results_file}")
    
    # Generate summary
    generate_model_summary(results)
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Analyze feature importance patterns")
    print(f"   2. Test station-based cross-validation")
    print(f"   3. Investigate temporal patterns in predictions")
    print(f"   4. Create dashboard visualizations")


if __name__ == "__main__":
    main()