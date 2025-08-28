"""
CDN manifest generation utilities.

Generates and manages manifest files for CDN deployments,
tracking file versions, hashes, and metadata.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ManifestEntry:
    """Single file entry in a CDN manifest."""
    filename: str
    size: int
    hash: str
    modified_at: str
    content_type: str = "application/json"


def generate_manifest(views_dir: Path, include_metadata: bool = True) -> Dict[str, Any]:
    """
    Generate a CDN manifest from a views directory.
    
    Args:
        views_dir: Path to directory containing view files
        include_metadata: Whether to include generation metadata
        
    Returns:
        Dictionary containing manifest data
    """
    files = []
    total_size = 0
    
    # Process all JSON files in the directory
    for file_path in sorted(views_dir.glob('*.json')):
        file_stat = file_path.stat()
        
        entry = ManifestEntry(
            filename=file_path.name,
            size=file_stat.st_size,
            hash=_calculate_file_hash(file_path),
            modified_at=datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat(),
            content_type="application/json"
        )
        
        files.append(entry.__dict__)
        total_size += entry.size
    
    manifest = {
        'files': files,
        'total_files': len(files),
        'total_size_bytes': total_size
    }
    
    if include_metadata:
        manifest.update({
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'generator': 'mbon_analysis.deployment.manifest_generator',
            'version': '1.0.0'
        })
    
    return manifest


def save_manifest(manifest: Dict[str, Any], output_path: Path) -> None:
    """
    Save manifest to a JSON file.
    
    Args:
        manifest: Manifest data dictionary
        output_path: Path to save the manifest file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Load manifest from a JSON file.
    
    Args:
        manifest_path: Path to the manifest file
        
    Returns:
        Manifest data dictionary
        
    Raises:
        FileNotFoundError: If manifest file doesn't exist
        json.JSONDecodeError: If manifest file is not valid JSON
    """
    with open(manifest_path, 'r') as f:
        return json.load(f)


def compare_manifests(local_manifest: Dict[str, Any], remote_manifest: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Compare two manifests and return differences.
    
    Args:
        local_manifest: Local manifest data
        remote_manifest: Remote manifest data
        
    Returns:
        Dictionary with lists of added, modified, and deleted files
    """
    local_files = {f['filename']: f for f in local_manifest.get('files', [])}
    remote_files = {f['filename']: f for f in remote_manifest.get('files', [])}
    
    added = []
    modified = []
    deleted = []
    
    # Find added and modified files
    for filename, local_file in local_files.items():
        if filename not in remote_files:
            added.append(filename)
        elif remote_files[filename]['hash'] != local_file['hash']:
            modified.append(filename)
    
    # Find deleted files
    for filename in remote_files:
        if filename not in local_files:
            deleted.append(filename)
    
    return {
        'added': added,
        'modified': modified,
        'deleted': deleted
    }


def _calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    import hashlib
    
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()