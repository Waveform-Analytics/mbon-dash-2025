#!/usr/bin/env python3
"""
Data statistics script for MBON Dashboard
Generates comprehensive statistics about the processed data
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd

class DataStatistics:
    def __init__(self, data_dir: str = "data/cdn/processed"):
        self.data_dir = Path(data_dir)
        self.stats = {}
        
    def load_json(self, filename: str) -> Any:
        """Load JSON file safely"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            return None
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None
    
    def analyze_detections(self) -> Dict:
        """Analyze detection data statistics"""
        data = self.load_json("detections.json")
        if not data:
            return {"error": "No detection data found"}
            
        df = pd.DataFrame(data)
        
        stats = {
            "total_records": len(df),
            "stations": df['station'].unique().tolist() if 'station' in df else [],
            "years": sorted(df['year'].unique().tolist()) if 'year' in df else [],
            "date_range": {
                "start": df['date_time'].min() if 'date_time' in df else None,
                "end": df['date_time'].max() if 'date_time' in df else None
            }
        }
        
        # Species detection counts
        species_cols = [col for col in df.columns if col not in ['station', 'year', 'date_time']]
        species_detections = {}
        
        for col in species_cols[:20]:  # Top 20 species
            if df[col].dtype in ['int64', 'float64']:
                species_detections[col] = {
                    "total_detections": int(df[col].sum()),
                    "records_with_detections": int((df[col] > 0).sum()),
                    "max_in_single_record": int(df[col].max())
                }
        
        stats["top_species"] = species_detections
        stats["total_species"] = len(species_cols)
        
        # Station-wise breakdown
        if 'station' in df:
            station_stats = {}
            for station in df['station'].unique():
                station_df = df[df['station'] == station]
                station_stats[station] = {
                    "records": len(station_df),
                    "years": sorted(station_df['year'].unique().tolist()) if 'year' in station_df else []
                }
            stats["by_station"] = station_stats
            
        return stats
    
    def analyze_environmental(self) -> Dict:
        """Analyze environmental data statistics"""
        data = self.load_json("environmental.json")
        if not data:
            return {"error": "No environmental data found"}
            
        df = pd.DataFrame(data)
        
        stats = {
            "total_records": len(df),
            "has_temperature": 'temperature' in df.columns,
            "has_depth": 'depth' in df.columns
        }
        
        if 'temperature' in df and df['temperature'].notna().any():
            stats["temperature"] = {
                "min": float(df['temperature'].min()),
                "max": float(df['temperature'].max()),
                "mean": float(df['temperature'].mean()),
                "missing_values": int(df['temperature'].isna().sum())
            }
            
        if 'depth' in df and df['depth'].notna().any():
            stats["depth"] = {
                "min": float(df['depth'].min()),
                "max": float(df['depth'].max()),
                "mean": float(df['depth'].mean()),
                "missing_values": int(df['depth'].isna().sum())
            }
            
        return stats
    
    def analyze_acoustic(self) -> Dict:
        """Analyze acoustic data statistics"""
        data = self.load_json("acoustic.json")
        if not data:
            return {"error": "No acoustic data found"}
            
        if len(data) == 0:
            return {"total_records": 0, "note": "Acoustic data file is empty"}
            
        df = pd.DataFrame(data)
        
        stats = {
            "total_records": len(df),
            "columns": df.columns.tolist()
        }
        
        # Look for rmsSPL or other acoustic indices
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            if col not in ['year', 'station']:
                stats[col] = {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean())
                }
                
        return stats
    
    def analyze_file_sizes(self) -> Dict:
        """Analyze file sizes"""
        sizes = {}
        for filepath in self.data_dir.glob("*.json"):
            size_bytes = filepath.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            sizes[filepath.name] = {
                "bytes": size_bytes,
                "mb": round(size_mb, 2)
            }
        return sizes
    
    def generate_report(self) -> None:
        """Generate comprehensive statistics report"""
        print("\n" + "="*60)
        print("MBON Dashboard Data Statistics Report")
        print("="*60 + "\n")
        
        # File sizes
        print("📁 File Sizes:")
        print("-" * 40)
        file_sizes = self.analyze_file_sizes()
        total_size = sum(f["mb"] for f in file_sizes.values())
        for filename, size in sorted(file_sizes.items()):
            status = "⚠️" if size["bytes"] < 100 else "✓"
            print(f"  {status} {filename:<25} {size['mb']:>8.2f} MB")
        print(f"  {'Total:':<27} {total_size:>8.2f} MB\n")
        
        # Detection statistics
        print("🐟 Detection Data Statistics:")
        print("-" * 40)
        detection_stats = self.analyze_detections()
        if "error" not in detection_stats:
            print(f"  • Total records: {detection_stats['total_records']:,}")
            print(f"  • Stations: {', '.join(detection_stats['stations'])}")
            print(f"  • Years: {', '.join(map(str, detection_stats['years']))}")
            print(f"  • Total species: {detection_stats['total_species']}")
            
            if "by_station" in detection_stats:
                print("\n  Station Breakdown:")
                for station, info in detection_stats['by_station'].items():
                    print(f"    - {station}: {info['records']:,} records, years {info['years']}")
                    
            if "top_species" in detection_stats and detection_stats["top_species"]:
                print("\n  Top 5 Species by Detections:")
                top_5 = sorted(detection_stats["top_species"].items(), 
                             key=lambda x: x[1]["total_detections"], 
                             reverse=True)[:5]
                for species, info in top_5:
                    print(f"    - {species}: {info['total_detections']:,} total detections")
        else:
            print(f"  ❌ {detection_stats['error']}")
        
        # Environmental statistics
        print("\n🌡️ Environmental Data Statistics:")
        print("-" * 40)
        env_stats = self.analyze_environmental()
        if "error" not in env_stats:
            print(f"  • Total records: {env_stats['total_records']:,}")
            if "temperature" in env_stats:
                temp = env_stats["temperature"]
                print(f"  • Temperature range: {temp['min']:.1f}°C - {temp['max']:.1f}°C (mean: {temp['mean']:.1f}°C)")
                print(f"    Missing values: {temp['missing_values']}")
            if "depth" in env_stats:
                depth = env_stats["depth"]
                print(f"  • Depth range: {depth['min']:.1f}m - {depth['max']:.1f}m (mean: {depth['mean']:.1f}m)")
                print(f"    Missing values: {depth['missing_values']}")
        else:
            print(f"  ❌ {env_stats['error']}")
        
        # Acoustic statistics
        print("\n🔊 Acoustic Data Statistics:")
        print("-" * 40)
        acoustic_stats = self.analyze_acoustic()
        if "error" not in acoustic_stats:
            print(f"  • Total records: {acoustic_stats['total_records']:,}")
            if acoustic_stats['total_records'] == 0:
                print("  ⚠️  Acoustic data file is empty - rmsSPL data may need to be processed")
            else:
                # Print any acoustic indices found
                for key, value in acoustic_stats.items():
                    if isinstance(value, dict) and 'mean' in value:
                        print(f"  • {key}: {value['min']:.2f} - {value['max']:.2f} (mean: {value['mean']:.2f})")
        else:
            print(f"  ❌ {acoustic_stats['error']}")
        
        # Metadata check
        print("\n📋 Metadata Status:")
        print("-" * 40)
        metadata = self.load_json("metadata.json")
        if metadata:
            print(f"  ✓ Last updated: {metadata.get('lastUpdated', 'Unknown')}")
            if 'dataStats' in metadata:
                stats = metadata['dataStats']
                print(f"  • Total records: {stats.get('totalRecords', 0):,}")
                print(f"  • Station count: {stats.get('stationCount', 0)}")
                print(f"  • Species count: {stats.get('speciesCount', 0)}")
        else:
            print("  ❌ No metadata file found")
            
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    stats = DataStatistics()
    stats.generate_report()