#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# The issue is likely that the heatmap data is missing some hours
# Let's create a simple visualization showing the problem and solution

def demonstrate_hour_axis_issue():
    """Create a demo showing the hour axis issue and fix."""
    
    # Create example heatmap data with missing hours (common data issue)
    weeks = np.arange(1, 53)  # 52 weeks
    hours_incomplete = np.arange(0, 12)  # Only first 12 hours (common in datasets)
    hours_complete = np.arange(0, 24)   # All 24 hours
    
    # Generate fake data
    np.random.seed(42)
    
    # Incomplete data (only 12 hours)
    incomplete_data = np.random.rand(len(weeks), len(hours_incomplete))
    # Add some pattern (evening activity)
    for i, week in enumerate(weeks):
        if 20 <= week <= 40:  # Active weeks
            for j, hour in enumerate(hours_incomplete):
                if 8 <= hour <= 11:  # "Evening" in this truncated view
                    incomplete_data[i, j] += 1.5
    
    # Complete data (24 hours) 
    complete_data = np.random.rand(len(weeks), len(hours_complete))
    # Add realistic pattern
    for i, week in enumerate(weeks):
        if 20 <= week <= 40:  # Active weeks
            for j, hour in enumerate(hours_complete):
                if 18 <= hour <= 22:  # Real evening
                    complete_data[i, j] += 1.5
    
    # Create comparison figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # Problem: Incomplete data with wrong hour labels
    ax1 = axes[0, 0]
    im1 = ax1.imshow(incomplete_data.T, cmap='YlOrRd', aspect='auto', origin='upper')
    ax1.set_title('PROBLEM: Incomplete Hour Data\n(Only 0-11h available but labeled 0-23h)', fontsize=11)
    ax1.set_xlabel('Week of Year', fontsize=10)
    ax1.set_ylabel('Hour of Day', fontsize=10)
    # This is the WRONG approach - labeling more hours than exist
    ax1.set_yticks(range(0, 24, 4))  # Labels 0,4,8,12,16,20 
    ax1.set_yticklabels(range(0, 24, 4))  # But data only goes 0-11!
    ax1.axhline(y=6, color='yellow', linestyle='--', alpha=0.7, label='6am')
    ax1.axhline(y=18, color='navy', linestyle='--', alpha=0.7, label='6pm')
    plt.colorbar(im1, ax=ax1, shrink=0.6)
    
    # Fix: Incomplete data with correct hour labels  
    ax2 = axes[0, 1]
    im2 = ax2.imshow(incomplete_data.T, cmap='YlOrRd', aspect='auto', origin='upper')
    ax2.set_title('FIXED: Incomplete Hour Data\n(Correctly labeled for available hours)', fontsize=11)
    ax2.set_xlabel('Week of Year', fontsize=10)
    ax2.set_ylabel('Hour of Day', fontsize=10)
    # This is the RIGHT approach - only label hours that exist
    n_hours = incomplete_data.T.shape[0]
    ax2.set_ylim(-0.5, n_hours - 0.5)
    ax2.set_yticks(range(0, n_hours, 2))
    ax2.set_yticklabels(range(0, n_hours, 2))
    # Only add lines if hours exist
    if n_hours >= 7:
        ax2.axhline(y=6, color='yellow', linestyle='--', alpha=0.7)
    plt.colorbar(im2, ax=ax2, shrink=0.6)
    
    # Ideal: Complete 24-hour data
    ax3 = axes[1, 0]
    im3 = ax3.imshow(complete_data.T, cmap='YlOrRd', aspect='auto', origin='upper')
    ax3.set_title('IDEAL: Complete 24-Hour Data\n(All hours available)', fontsize=11)
    ax3.set_xlabel('Week of Year', fontsize=10)
    ax3.set_ylabel('Hour of Day', fontsize=10)
    ax3.set_yticks(range(0, 24, 4))
    ax3.set_yticklabels(range(0, 24, 4))
    ax3.axhline(y=6, color='yellow', linestyle='--', alpha=0.7, label='6am')
    ax3.axhline(y=18, color='navy', linestyle='--', alpha=0.7, label='6pm')
    plt.colorbar(im3, ax=ax3, shrink=0.6)
    
    # Show data shapes
    ax4 = axes[1, 1]
    ax4.text(0.1, 0.8, f'Incomplete Data Shape: {incomplete_data.T.shape}', fontsize=12, transform=ax4.transAxes)
    ax4.text(0.1, 0.7, f'Hours available: 0-{len(hours_incomplete)-1}', fontsize=12, transform=ax4.transAxes)
    ax4.text(0.1, 0.6, f'Complete Data Shape: {complete_data.T.shape}', fontsize=12, transform=ax4.transAxes)
    ax4.text(0.1, 0.5, f'Hours available: 0-{len(hours_complete)-1}', fontsize=12, transform=ax4.transAxes)
    
    ax4.text(0.1, 0.3, 'The Fix:', fontsize=14, weight='bold', transform=ax4.transAxes)
    ax4.text(0.1, 0.2, '• Check actual data shape', fontsize=12, transform=ax4.transAxes)
    ax4.text(0.1, 0.15, '• Set ylim based on data dimensions', fontsize=12, transform=ax4.transAxes)
    ax4.text(0.1, 0.1, '• Only label existing hour indices', fontsize=12, transform=ax4.transAxes)
    ax4.text(0.1, 0.05, '• Conditional day/night lines', fontsize=12, transform=ax4.transAxes)
    
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.suptitle('Hour Axis Issue: Problem vs Solution', fontsize=16, y=0.98)
    plt.tight_layout()
    
    # Save
    output_path = Path.cwd() / "analysis_results" / "pattern_similarity" / "hour_axis_demonstration.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved demonstration: {output_path}")
    
    return fig

if __name__ == "__main__":
    demonstrate_hour_axis_issue()