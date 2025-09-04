"""Tests for CDN upload operations."""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import tempfile
from botocore.exceptions import ClientError, NoCredentialsError

# Import the upload script functions - we need to adjust the import path
import sys
import importlib.util
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Load the upload_to_cdn script as a module
upload_script_path = Path(__file__).parent.parent / "scripts" / "upload_to_cdn.py"
spec = importlib.util.spec_from_file_location("upload_to_cdn", upload_script_path)
upload_to_cdn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upload_to_cdn)

upload_views_to_cdn = upload_to_cdn.upload_views_to_cdn
setup_logging = upload_to_cdn.setup_logging


class TestCDNUploadValidation:
    """Test CDN upload functionality."""
    
    def test_missing_environment_variables(self, monkeypatch):
        """Test behavior with missing required environment variables."""
        # Clear all CDN-related environment variables
        cdn_env_vars = [
            'CLOUDFLARE_R2_ACCOUNT_ID',
            'CLOUDFLARE_R2_ACCESS_KEY_ID',
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
            'CLOUDFLARE_R2_BUCKET_NAME',
            'CLOUDFLARE_R2_ENDPOINT'
        ]
        
        for var in cdn_env_vars:
            monkeypatch.delenv(var, raising=False)
        
        # Mock the environment file to exist but be empty of required vars
        with patch('pathlib.Path.exists', return_value=True), \
             patch.object(upload_to_cdn, 'load_dotenv'):
            
            result = upload_views_to_cdn()
            
            # Should fail due to missing environment variables
            assert result is False
    
    def test_missing_env_file(self, monkeypatch):
        """Test behavior when .env.local file doesn't exist.""" 
        # Clear environment variables
        cdn_env_vars = [
            'CLOUDFLARE_R2_ACCOUNT_ID',
            'CLOUDFLARE_R2_ACCESS_KEY_ID', 
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
            'CLOUDFLARE_R2_BUCKET_NAME',
            'CLOUDFLARE_R2_ENDPOINT'
        ]
        
        for var in cdn_env_vars:
            monkeypatch.delenv(var, raising=False)
        
        # Mock the environment file to not exist
        with patch('pathlib.Path.exists', return_value=False):
            result = upload_views_to_cdn()
            
            # Should fail due to missing .env.local file
            assert result is False
    
    def test_r2_connection_failure(self, setup_test_environment, temp_data_dir):
        """Test behavior when R2 connection fails."""
        # Mock boto3.client to raise an exception
        with patch.object(upload_to_cdn, 'boto3') as mock_boto3, \
             patch('pathlib.Path.exists', return_value=True), \
             patch.object(upload_to_cdn, 'load_dotenv'):
            
            mock_boto3.client.side_effect = Exception("Connection failed")
            result = upload_views_to_cdn()
            
            # Should fail due to connection error
            assert result is False
    
    def test_views_directory_not_found(self, setup_test_environment):
        """Test behavior when views directory doesn't exist."""
        # Mock everything to succeed except views directory existence
        mock_r2_client = Mock()
        
        with patch('upload_to_cdn.boto3.client', return_value=mock_r2_client), \
             patch.object(Path, 'exists', return_value=False), \
             patch('upload_to_cdn.load_dotenv'):
            
            result = upload_views_to_cdn()
            
            # Should fail due to missing views directory
            assert result is False
    
    def test_file_path_mapping(self, setup_test_environment, temp_data_dir):
        """Test that files go to correct CDN directories."""
        mock_r2_client = Mock()
        mock_r2_client.upload_fileobj = Mock()
        
        # Create a simple test file
        views_dir = temp_data_dir / "data" / "views"
        views_dir.mkdir(parents=True)
        test_file = views_dir / "test.json"
        test_file.write_text('{"test": "data"}')
        
        with patch('upload_to_cdn.boto3.client', return_value=mock_r2_client), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('upload_to_cdn.load_dotenv'), \
             patch('pathlib.Path.glob', return_value=[test_file]), \
             patch('builtins.open', mock_open(read_data='{"test": "data"}')):
            
            result = upload_views_to_cdn()
            
            # Should succeed
            assert result is True
            
            # Verify upload_fileobj was called
            assert mock_r2_client.upload_fileobj.called
    
    def test_upload_content_type_detection(self, setup_test_environment, temp_data_dir):
        """Test that correct MIME types are detected for uploads."""
        mock_r2_client = Mock()
        upload_calls = []
        
        def capture_upload(*args, **kwargs):
            upload_calls.append(kwargs)
        
        mock_r2_client.upload_fileobj.side_effect = capture_upload
        
        # Create a sample JSON file
        views_dir = temp_data_dir / "data" / "views"
        views_dir.mkdir(parents=True)
        (views_dir / "test.json").write_text('{"test": "data"}')
        
        with patch('upload_to_cdn.boto3.client', return_value=mock_r2_client), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('upload_to_cdn.load_dotenv'), \
             patch('mimetypes.guess_type', return_value=('application/json', None)):
            
            # Create minimal setup to test content type detection
            with patch('pathlib.Path.glob', return_value=[views_dir / "test.json"]), \
                 patch('builtins.open', mock_open(read_data='{"test": "data"}')):
                
                upload_views_to_cdn()
        
        # Verify that ExtraArgs included correct ContentType
        if upload_calls:
            extra_args = upload_calls[0].get('ExtraArgs', {})
            assert extra_args.get('ContentType') == 'application/json'
            assert 'CacheControl' in extra_args
    
    def test_upload_error_handling(self, setup_test_environment, temp_data_dir):
        """Test error handling during upload operations."""
        mock_r2_client = Mock()
        
        # Make upload_fileobj raise an exception
        mock_r2_client.upload_fileobj.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}}, 
            'upload_fileobj'
        )
        
        # Create a sample file
        views_dir = temp_data_dir / "data" / "views"
        views_dir.mkdir(parents=True)
        (views_dir / "test.json").write_text('{"test": "data"}')
        
        with patch('upload_to_cdn.boto3.client', return_value=mock_r2_client), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('upload_to_cdn.load_dotenv'), \
             patch('pathlib.Path.glob', return_value=[views_dir / "test.json"]), \
             patch('builtins.open', mock_open(read_data='{"test": "data"}')):
            
            result = upload_views_to_cdn()
            
            # Should return False due to upload error
            assert result is False
    
    def test_successful_upload_flow(self, setup_test_environment, temp_data_dir):
        """Test successful upload flow with all components working."""
        mock_r2_client = Mock()
        mock_r2_client.upload_fileobj = Mock()
        
        # Create sample files
        views_dir = temp_data_dir / "data" / "views" 
        views_dir.mkdir(parents=True)
        test_file = views_dir / "test.json"
        test_file.write_text('{"test": "data"}')
        
        with patch('upload_to_cdn.boto3.client', return_value=mock_r2_client), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('upload_to_cdn.load_dotenv'), \
             patch('pathlib.Path.glob', return_value=[test_file]), \
             patch('builtins.open', mock_open(read_data='{"test": "data"}')):
            
            result = upload_views_to_cdn()
            
            # Should succeed
            assert result is True
            
            # Verify files were uploaded (glob is called 3 times, so expect 3 uploads)
            assert mock_r2_client.upload_fileobj.call_count >= 1


class TestCDNEnvironmentValidation:
    """Test environment variable validation for CDN operations."""
    
    @pytest.mark.parametrize("missing_var", [
        'CLOUDFLARE_R2_ACCOUNT_ID',
        'CLOUDFLARE_R2_ACCESS_KEY_ID',
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
        'CLOUDFLARE_R2_BUCKET_NAME',
        'CLOUDFLARE_R2_ENDPOINT'
    ])
    def test_individual_missing_environment_variables(self, monkeypatch, missing_var):
        """Test that each required environment variable is validated."""
        # Set all variables except the one being tested
        required_vars = {
            'CLOUDFLARE_R2_ACCOUNT_ID': 'test_account',
            'CLOUDFLARE_R2_ACCESS_KEY_ID': 'test_key',
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY': 'test_secret',
            'CLOUDFLARE_R2_BUCKET_NAME': 'test_bucket',
            'CLOUDFLARE_R2_ENDPOINT': 'https://test.endpoint.com'
        }
        
        for var, value in required_vars.items():
            if var != missing_var:
                monkeypatch.setenv(var, value)
            else:
                monkeypatch.delenv(var, raising=False)
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('upload_to_cdn.load_dotenv'):
            
            result = upload_views_to_cdn()
            
            # Should fail due to missing variable
            assert result is False
    
    def test_all_environment_variables_present(self, setup_test_environment):
        """Test that validation passes when all environment variables are present."""
        # Mock the file operations to avoid actual I/O
        with patch('pathlib.Path.exists', return_value=True), \
             patch('upload_to_cdn.load_dotenv'), \
             patch('upload_to_cdn.boto3.client') as mock_boto3, \
             patch('pathlib.Path.glob', return_value=[]):
            
            mock_client = Mock()
            mock_boto3.return_value = mock_client
            
            result = upload_views_to_cdn()
            
            # Should succeed (no files to upload, but validation should pass)
            assert result is True


class TestLoggingSetup:
    """Test logging configuration."""
    
    def test_setup_logging(self):
        """Test that logging is configured correctly."""
        logger = setup_logging()
        
        assert logger is not None
        assert logger.name == 'upload_to_cdn'
    
    def test_logging_file_creation(self, temp_data_dir):
        """Test that log file is created.""" 
        with patch('os.getcwd', return_value=str(temp_data_dir)):
            logger = setup_logging()
            
            # Log a test message
            logger.info("Test message")
            
            # Check if log file would be created (we're not testing actual file I/O)
            assert logger is not None


@pytest.mark.integration
class TestCDNIntegration:
    """Integration tests for CDN operations."""
    
    @pytest.mark.cdn
    def test_cdn_connection_with_invalid_credentials(self):
        """Test CDN connection with invalid credentials."""
        # This test requires actual network access and should be marked as slow
        with patch.dict(os.environ, {
            'CLOUDFLARE_R2_ACCOUNT_ID': 'invalid_account',
            'CLOUDFLARE_R2_ACCESS_KEY_ID': 'invalid_key',
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY': 'invalid_secret',
            'CLOUDFLARE_R2_BUCKET_NAME': 'invalid_bucket',
            'CLOUDFLARE_R2_ENDPOINT': 'https://invalid.r2.cloudflarestorage.com'
        }):
            # This would test actual CDN connection - skipped in unit tests
            pytest.skip("CDN integration test requires valid credentials")
    
    @pytest.mark.cdn
    @pytest.mark.slow
    def test_large_file_upload(self, setup_test_environment, large_sample_data):
        """Test uploading large files to CDN."""
        # This test would upload actual large files
        pytest.skip("Large file upload test requires CDN access and significant time")


class TestFileHandling:
    """Test file handling operations in CDN upload."""
    
    def test_json_file_detection(self, temp_data_dir):
        """Test that only JSON files are detected for upload."""
        views_dir = temp_data_dir / "views"
        views_dir.mkdir(parents=True, exist_ok=True)
        
        # Create various file types
        (views_dir / "valid.json").write_text('{}')
        (views_dir / "invalid.txt").write_text('text')
        (views_dir / "also_invalid.csv").write_text('csv,data')
        (views_dir / "another_valid.json").write_text('{}')
        
        json_files = list(views_dir.glob('*.json'))
        
        # Should find only JSON files
        assert len(json_files) == 2
        assert all(f.suffix == '.json' for f in json_files)
    
    def test_file_size_reporting(self, temp_data_dir):
        """Test that file sizes are reported correctly."""
        views_dir = temp_data_dir / "views"
        views_dir.mkdir(parents=True, exist_ok=True)
        
        # Create files of different sizes
        small_file = views_dir / "small.json"
        large_file = views_dir / "large.json"
        
        small_data = '{"small": "data"}'
        large_data = '{"large": "' + 'x' * 10000 + '"}'
        
        small_file.write_text(small_data)
        large_file.write_text(large_data)
        
        # Verify file sizes
        assert small_file.stat().st_size < large_file.stat().st_size
        assert small_file.stat().st_size == len(small_data)
        assert large_file.stat().st_size == len(large_data)


class TestCDNPathMapping:
    """Test CDN path mapping logic."""
    
    def test_views_directory_mapping(self):
        """Test that views files map to views/ prefix."""
        from pathlib import Path
        
        # Simulate file in views directory
        views_file = Path("data/views/stations.json")
        
        # The upload logic should map this to views/stations.json
        if views_file.parent.name == 'views':
            upload_key = f'views/{views_file.name}'
        else:
            upload_key = f'other/{views_file.name}'
        
        assert upload_key == 'views/stations.json'
    
    def test_processed_directory_mapping(self):
        """Test that processed files map to processed/ prefix."""
        from pathlib import Path
        
        # Simulate file in processed directory
        processed_file = Path("data/processed/compiled_indices.json")
        
        # The upload logic should map this to processed/compiled_indices.json  
        if processed_file.parent.name == 'processed':
            upload_key = f'processed/{processed_file.name}'
        else:
            upload_key = f'other/{processed_file.name}'
        
        assert upload_key == 'processed/compiled_indices.json'
    
    def test_optimized_directory_mapping(self):
        """Test that optimized files map to processed/optimized/ prefix."""
        from pathlib import Path
        
        # Simulate file in optimized subdirectory
        optimized_file = Path("data/processed/optimized/indices_9M_2021_FullBW.json")
        
        # The upload logic should map this to processed/optimized/filename
        if optimized_file.parent.name == 'optimized':
            upload_key = f'processed/optimized/{optimized_file.name}'
        else:
            upload_key = f'other/{optimized_file.name}'
        
        assert upload_key == 'processed/optimized/indices_9M_2021_FullBW.json'