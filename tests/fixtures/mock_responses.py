"""Mock responses for CDN and API calls."""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_cdn_response():
    """Mock successful CDN response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": "File uploaded successfully",
        "url": "https://pub-test.r2.dev/views/station_overview.json"
    }
    return mock_response


@pytest.fixture  
def mock_cdn_error_response():
    """Mock CDN error response."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {
        "error": "Upload failed"
    }
    return mock_response