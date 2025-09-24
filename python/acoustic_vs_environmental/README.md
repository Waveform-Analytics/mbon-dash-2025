# Marine Acoustic Discovery Analysis - Reproducible Pipeline

This repository contains the complete analysis pipeline for the Marine Biodiversity Observation Network (MBON) acoustic monitoring study, which demonstrates how to transform marine acoustic monitoring from a manual bottleneck into a scalable research tool.

## 🎯 Quick Start (5 minutes)

### Prerequisites
- Python 3.8+ 
- Required data file: `data_01_aligned_2021.csv`

### One-Command Pipeline
```bash
# Install dependencies
pip install pandas numpy matplotlib seaborn scipy scikit-learn pathlib

# Run complete analysis
python run_full_pipeline.py
```

### Generate Final Report
```bash
# Render the Quarto document (requires Quarto installed)
quarto render Marine_Acoustic_Discovery_Report_v2.qmd

# OR use the existing HTML file
open Marine_Acoustic_Discovery_Report_v2.html
```

## 📁 Repository Structure

```
acoustic_vs_environmental/
├── run_full_pipeline.py          # 🚀 MAIN PIPELINE RUNNER
├── README.md                     # This file
│
├── data_01_aligned_2021.csv       # 📊 Main dataset (13,100 time periods)
│
├── 01_data_loading.py             # Phase 1: Data verification
├── 02_baseline_comparison.py      # Phase 2: Traditional ML analysis  
├── 06_temporal_correlation_analysis.py  # Phase 6: Pattern discovery
├── 09_detection_guidance.py       # Phase 9: Guidance system
│
├── utils/
│   └── data_utils.py              # Shared data loading utilities
│
├── Marine_Acoustic_Discovery_Report_v2.qmd  # 📝 Report source
├── Marine_Acoustic_Discovery_Report_v2.html # 📄 Generated report
│
├── output/                        # 📊 Generated analysis outputs
│   ├── phase2_baseline/
│   ├── phase6_temporal_correlation/
│   └── phase9_detection_guidance/
│
└── netlify_deploy/               # 🌐 Web deployment ready folder
```

## 🔬 Analysis Pipeline Overview

Our analysis proceeds through these key phases:

### Phase 1: Data Loading & Verification
- **Input**: `data_01_aligned_2021.csv` 
- **Output**: Data quality report, basic statistics
- **Purpose**: Verify data integrity and generate baseline metrics

### Phase 2: Traditional Machine Learning Analysis  
- **Input**: Aligned dataset with acoustic indices + fish detections
- **Output**: ML model performance, feature importance plots
- **Key Finding**: Traditional ML hits seasonal data obstacles

### Phase 6: Temporal Correlation Analysis
- **Input**: Temporal features, acoustic indices, manual detections  
- **Output**: **Figure 4** - Acoustic vs Manual Detection Comparison
- **Key Finding**: Visual similarity between acoustic indices and fish detection patterns

### Phase 9: Detection Guidance System
- **Input**: Historical detection patterns, environmental data
- **Output**: **Figure 5** - Species-Specific 2D Probability Surfaces
- **Key Achievement**: 80% reduction in manual effort, 70-85% detection efficiency

## 📊 Key Figures Generated

| Figure | Description | Location |
|--------|-------------|----------|
| **Figure 4** | Acoustic Index vs Manual Detection Comparison | `output/phase6_temporal_correlation/figures/` |
| **Figure 5** | Species-Specific 2D Probability Surfaces | `output/phase9_detection_guidance/figures/` |
| **Figure 10** | Time Savings Analysis | `output/phase9_detection_guidance/figures/` |

## 🎯 Research Questions Addressed

1. **Can acoustic indices predict fish vocal activity beyond environmental data?**
   - Answer: Yes, but with important caveats about seasonal boundaries

2. **What causes traditional ML to fail on seasonal biological data?** 
   - Answer: Models trained on summer data incorrectly predict winter activity

3. **How can we transform pattern recognition into actionable guidance?**
   - Answer: 2D probability surfaces mapping likelihood across day-of-year × time-of-day

## 💻 Running Individual Phases

If you need to run specific phases separately:

```bash
# Phase 1: Data verification
python 01_data_loading.py

# Phase 2: Traditional ML baseline
python 02_baseline_comparison.py  

# Phase 6: Pattern discovery (creates Figure 4)
python 06_temporal_correlation_analysis.py

# Phase 9: Guidance system (creates Figure 5)
python 09_detection_guidance.py
```

## 🔧 Troubleshooting

### Common Issues

**"FileNotFoundError: data_01_aligned_2021.csv"**
- Ensure the aligned dataset is in the root directory
- This file should be ~16MB and contain 13,100+ rows

**"ModuleNotFoundError: No module named 'sklearn'"**
- Install missing packages: `pip install scikit-learn`
- See requirements in `run_full_pipeline.py`

**"Empty output directories"**
- Scripts may have failed silently
- Check individual phase outputs with verbose logging
- Ensure write permissions on output/ directory

### Data Requirements

The analysis expects the aligned dataset with these columns:
- `datetime`: Timestamp for each 2-hour period  
- `station`: Monitoring station ID (9M, 14M, 37M)
- `Spotted seatrout`, `Silver perch`, etc.: Fish detection scores
- `Water temp (°C)`: Environmental data
- Acoustic indices: `ADI`, `ACI`, `NDSI`, `BGNf`, etc.

## 🌐 Web Deployment (Netlify)

After running the pipeline:

1. **Prepare deployment folder**:
   ```bash
   # The pipeline automatically creates netlify_deploy/ with all assets
   ls netlify_deploy/  # Should contain HTML + all images
   ```

2. **Deploy to Netlify**:
   - Go to [netlify.com/drop](https://app.netlify.com/drop)
   - Drag the entire `netlify_deploy/` folder to the drop zone
   - Get your live URL instantly

## 📈 Expected Results

When the pipeline completes successfully, you should see:

- **Detection efficiency**: 70-85% of fish detections found in top 20% of time periods
- **Time savings**: 80% reduction in manual analysis effort  
- **Cross-validation**: Consistent performance across monitoring stations
- **Biological alignment**: Patterns match known fish spawning seasons

## 🧬 Scientific Impact

This work demonstrates how data science can address a fundamental bottleneck in marine conservation: the gap between data collection and actionable insights. The 80% reduction in manual workload makes large-scale acoustic monitoring feasible while maintaining scientific accuracy.

**Key Innovation**: Instead of predicting "Will fish call tomorrow?" we ask "Given it's May 15 at 6 AM, how likely are fish calling right now?" This reframing unlocked temporal patterns that traditional ML couldn't capture.

## 📚 Citation

If you use this pipeline in your research, please cite:

```bibtex
@article{mbon_acoustic_discovery_2025,
  title={Finding Fish in Ocean Sounds: A Data-Driven Approach to Marine Acoustic Monitoring},
  author={Marine Biodiversity Observation Network (MBON)},
  year={2025},
  publisher={MBON-USC}
}
```

## 📞 Support

For questions about reproduction or methodology:
- Check the generated report: `Marine_Acoustic_Discovery_Report_v2.html`
- Review phase-specific outputs in `output/` directories
- Examine the pipeline logs from `run_full_pipeline.py`

---

🐟 *"The ocean generates acoustic data faster than we can analyze it, but with the right approach to guide our listening, we can finally process what the ocean has been telling us."*