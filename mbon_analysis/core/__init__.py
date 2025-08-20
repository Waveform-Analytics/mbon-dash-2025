"""
Core data processing utilities for MBON analysis.

Data loading hierarchy:
1. data_loader - Basic loading from local files
2. data_sync - CDN synchronization 
3. auto_loader - Combined sync + load with smart features
"""

from .data_loader import (
    load_processed_data,
    load_data,  # Alias for backward compatibility
    load_acoustic_indices,
    load_metadata,
    get_data_directory
)

from .data_sync import (
    check_data_freshness,
    sync_raw_data,
    ensure_data_available,
    sync_and_process
)

from .auto_loader import (
    load_with_auto_sync,
    load_acoustic_indices_with_sync,
    smart_load
)

from .data_prep import (
    prepare_detection_data,
    get_detection_columns,
    classify_detections,
    create_dashboard_aggregations
)

from .acoustic_indices_loader import (
    load_acoustic_indices_csv,
    load_all_acoustic_indices,
    prepare_temporal_heatmap_data,
    prepare_box_plot_data,
    get_available_indices,
    export_for_dashboard,
    create_temporal_heatmap_json,
    create_box_plot_json
)