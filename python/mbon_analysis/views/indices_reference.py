"""Indices reference view generator."""

from typing import Dict, Any, List
import pandas as pd
from .base import BaseViewGenerator
from ..data.loaders import create_loader


class IndicesReferenceViewGenerator(BaseViewGenerator):
    """Generate indices_reference.json with acoustic indices descriptions and categories."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate indices reference view data.
        
        Returns:
            Dictionary with indices reference information
        """
        loader = create_loader(self.data_root)
        
        # Load indices reference data
        indices_df = loader.load_indices_reference()
        
        # Process indices into structured format
        indices = []
        categories = {}
        
        for _, row in indices_df.iterrows():
            index_data = {
                "prefix": row.get('Prefix', ''),
                "category": row.get('Category', 'Uncategorized'),
                "subcategory": row.get('Subcategory', ''),
                "description": row.get('Description', ''),
                "full_name": self._expand_prefix(row.get('Prefix', '')),
                "computational_type": self._determine_comp_type(row.get('Category', ''))
            }
            indices.append(index_data)
            
            # Track categories
            category = row.get('Category', 'Uncategorized')
            if category not in categories:
                categories[category] = {
                    "name": category,
                    "count": 0,
                    "subcategories": set()
                }
            categories[category]["count"] += 1
            if row.get('Subcategory'):
                categories[category]["subcategories"].add(row.get('Subcategory'))
        
        # Convert sets to lists for JSON serialization
        for cat in categories.values():
            cat["subcategories"] = sorted(list(cat["subcategories"]))
        
        # Group indices by category for easier navigation
        grouped_indices = {}
        for index in indices:
            cat = index["category"]
            if cat not in grouped_indices:
                grouped_indices[cat] = []
            grouped_indices[cat].append(index)
        
        # Generate summary statistics
        summary = {
            "total_indices": len(indices),
            "categories": {
                "count": len(categories),
                "list": list(categories.keys())
            },
            "computational_types": {
                "temporal": len([i for i in indices if i["computational_type"] == "temporal"]),
                "spectral": len([i for i in indices if i["computational_type"] == "spectral"]),
                "complexity": len([i for i in indices if i["computational_type"] == "complexity"]),
                "diversity": len([i for i in indices if i["computational_type"] == "diversity"])
            }
        }
        
        return {
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "version": "1.0.0",
                "description": "Acoustic indices reference catalog for MBON dashboard"
            },
            "summary": summary,
            "categories": categories,
            "indices": indices,
            "grouped_indices": grouped_indices
        }
    
    def _expand_prefix(self, prefix: str) -> str:
        """Expand common acoustic index prefixes to full names.
        
        Args:
            prefix: Index prefix/abbreviation
            
        Returns:
            Full name of the index
        """
        expansions = {
            "ACI": "Acoustic Complexity Index",
            "ADI": "Acoustic Diversity Index",
            "AEI": "Acoustic Evenness Index",
            "BI": "Bioacoustic Index",
            "NDSI": "Normalized Difference Soundscape Index",
            "H": "Entropy",
            "LEQ": "Equivalent Continuous Sound Level",
            "ZCR": "Zero Crossing Rate",
            "MEAN": "Mean",
            "VAR": "Variance",
            "SKEW": "Skewness",
            "KURT": "Kurtosis",
            "NBPEAKS": "Number of Peaks",
            "LFC": "Low Frequency Cover",
            "MFC": "Mid Frequency Cover",
            "HFC": "High Frequency Cover",
            "RAOQ": "Rao's Quadratic Entropy",
            "rBA": "relative Bioacoustic Activity"
        }
        
        # Check for exact match
        if prefix in expansions:
            return expansions[prefix]
        
        # Check for prefix with suffix (e.g., MEANt, MEANf)
        base = prefix.rstrip('tf')
        if base in expansions:
            suffix = prefix[len(base):]
            if suffix == 't':
                return f"{expansions[base]} (Temporal)"
            elif suffix == 'f':
                return f"{expansions[base]} (Frequency)"
        
        # Check for entropy variants
        if prefix.startswith('H_'):
            entropy_type = prefix[2:].replace('_', ' ').title()
            return f"Entropy ({entropy_type})"
        
        return prefix
    
    def _determine_comp_type(self, category: str) -> str:
        """Determine computational type from category.
        
        Args:
            category: Index category
            
        Returns:
            Computational type classification
        """
        category_lower = category.lower() if category else ""
        
        if any(word in category_lower for word in ['temporal', 'time', 'duration']):
            return "temporal"
        elif any(word in category_lower for word in ['frequency', 'spectral', 'spectrum']):
            return "spectral"
        elif any(word in category_lower for word in ['complexity', 'aci', 'ndsi']):
            return "complexity"
        elif any(word in category_lower for word in ['diversity', 'entropy', 'evenness', 'richness']):
            return "diversity"
        else:
            return "other"