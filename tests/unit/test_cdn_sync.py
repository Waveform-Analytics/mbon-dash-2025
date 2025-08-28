"""
Tests for CDN synchronization module.

Testing the CDN deployer with focus on:
- Hash-based change detection
- Atomic deployments
- Manifest generation and management
- Deployment validation
- Local development vs production modes
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from mbon_analysis.deployment.cdn_sync import CDNDeployer, DeploymentResult


class TestCDNDeployer:
    """Test the CDN deployment system."""

    @pytest.fixture
    def mock_views_dir(self, tmp_path):
        """Create a temporary views directory with test files."""
        views_dir = tmp_path / "views"
        views_dir.mkdir()
        
        # Create test view files
        (views_dir / "station_overview.json").write_text('{"test": "station_data"}')
        (views_dir / "species_timeline.json").write_text('{"test": "species_data"}')
        
        return views_dir

    @pytest.fixture
    def cdn_deployer(self):
        """Create a CDN deployer instance for testing."""
        return CDNDeployer(
            provider='local_dev',
            base_url='http://localhost:3000'
        )

    def test_deployer_initialization(self):
        """Test CDN deployer initializes correctly."""
        deployer = CDNDeployer(
            provider='cloudflare_r2',
            base_url='https://cdn.example.com'
        )
        
        assert deployer.provider == 'cloudflare_r2'
        assert deployer.base_url == 'https://cdn.example.com'
        assert deployer.dry_run is False

    def test_deployer_dry_run_mode(self):
        """Test dry run mode doesn't actually deploy."""
        deployer = CDNDeployer(
            provider='cloudflare_r2',
            base_url='https://cdn.example.com',
            dry_run=True
        )
        
        assert deployer.dry_run is True

    def test_calculate_file_hash(self, cdn_deployer, mock_views_dir):
        """Test file hash calculation for change detection."""
        test_file = mock_views_dir / "station_overview.json"
        
        hash1 = cdn_deployer._calculate_file_hash(test_file)
        assert isinstance(hash1, str)
        assert len(hash1) == 64  # SHA-256 hex digest length
        
        # Same file should produce same hash
        hash2 = cdn_deployer._calculate_file_hash(test_file)
        assert hash1 == hash2
        
        # Different content should produce different hash
        test_file.write_text('{"different": "content"}')
        hash3 = cdn_deployer._calculate_file_hash(test_file)
        assert hash1 != hash3

    def test_generate_local_manifest(self, cdn_deployer, mock_views_dir):
        """Test local manifest generation from view files."""
        manifest = cdn_deployer._generate_local_manifest(mock_views_dir)
        
        assert isinstance(manifest, dict)
        assert 'files' in manifest
        assert 'generated_at' in manifest
        assert 'total_files' in manifest
        
        # Should include both test files
        assert len(manifest['files']) == 2
        
        station_file = next(f for f in manifest['files'] if f['filename'] == 'station_overview.json')
        assert station_file['size'] > 0
        assert len(station_file['hash']) == 64

    def test_compare_manifests(self, cdn_deployer):
        """Test manifest comparison for change detection."""
        local_manifest = {
            'files': [
                {'filename': 'file1.json', 'hash': 'hash1', 'size': 100},
                {'filename': 'file2.json', 'hash': 'hash2', 'size': 200}
            ]
        }
        
        remote_manifest = {
            'files': [
                {'filename': 'file1.json', 'hash': 'hash1', 'size': 100},  # Same
                {'filename': 'file2.json', 'hash': 'old_hash', 'size': 200}  # Different
            ]
        }
        
        changed_files = cdn_deployer._compare_manifests(local_manifest, remote_manifest)
        assert len(changed_files) == 1
        assert changed_files[0]['filename'] == 'file2.json'

    def test_local_development_sync(self, cdn_deployer, mock_views_dir):
        """Test sync in local development mode."""
        result = cdn_deployer.sync_views(mock_views_dir)
        
        assert isinstance(result, DeploymentResult)
        assert result.success is True
        assert result.provider == 'local_dev'
        assert result.files_processed >= 0
        assert 'Local development mode' in result.message

    def test_deployment_result_structure(self):
        """Test DeploymentResult data structure."""
        result = DeploymentResult(
            success=True,
            provider='cloudflare_r2',
            files_processed=5,
            files_uploaded=3,
            files_skipped=2,
            total_size_bytes=1024,
            duration_seconds=2.5,
            message='Deployment successful'
        )
        
        assert result.success is True
        assert result.provider == 'cloudflare_r2'
        assert result.files_processed == 5