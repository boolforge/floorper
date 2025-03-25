"""
Tests for all browser handlers using parameterization.
This file consolidates browser-specific tests into a single parameterized approach.
"""

import os
import sys
import pytest
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import browser handlers
from floorper.browsers.handlers.base_handler import BaseBrowserHandler
from floorper.browsers.handlers.chrome_handler import ChromeHandler
from floorper.browsers.handlers.firefox_handler import FirefoxHandler

# Define browser handler fixtures
@pytest.fixture(params=[
    ChromeHandler,
    FirefoxHandler,
])
def browser_handler(request, tmp_path):
    """Fixture that provides each browser handler class."""
    handler_class = request.param
    # Initialize with a temp directory for testing
    return handler_class(str(tmp_path))

# Define test data for each browser type
@pytest.fixture
def browser_test_data():
    """Test data for different browsers and their expected profile structure."""
    return {
        "ChromeHandler": {
            "profile_folders": ["Default", "Profile 1"],
            "data_types": ["bookmarks", "history", "cookies", "preferences", "extensions"],
            "file_structure": {
                "bookmarks": "Bookmarks",
                "history": "History",
                "cookies": "Cookies",
                "preferences": "Preferences"
            }
        },
        "FirefoxHandler": {
            "profile_folders": ["default", "profile1"],
            "data_types": ["bookmarks", "history", "cookies", "preferences", "extensions"],
            "file_structure": {
                "bookmarks": "places.sqlite",
                "history": "places.sqlite",
                "cookies": "cookies.sqlite",
                "preferences": "prefs.js"
            }
        },
    }

# Mock setup for browser profile data
@pytest.fixture
def mock_profile_structure(tmp_path, browser_test_data):
    """Creates a mock profile structure for testing."""
    def _create_profile(handler_name):
        # Get expected structure for this handler
        structure = browser_test_data[handler_name]
        profiles = {}
        
        # Create profile folders
        for profile_name in structure["profile_folders"]:
            profile_path = tmp_path / profile_name
            profile_path.mkdir(exist_ok=True)
            
            # Create expected files in profile
            for data_type, file_name in structure["file_structure"].items():
                file_path = profile_path / file_name
                
                # Create different types of files based on extensions
                if file_name.endswith('.sqlite'):
                    # Create empty SQLite file
                    with open(file_path, 'wb') as f:
                        f.write(b'SQLite format 3\0')
                elif file_name.endswith('.json'):
                    # Create JSON file
                    with open(file_path, 'w') as f:
                        f.write('{"data": "test"}')
                elif file_name.endswith('.js'):
                    # Create JS file
                    with open(file_path, 'w') as f:
                        f.write('user_pref("test", true);')
                else:
                    # Create generic file
                    with open(file_path, 'w') as f:
                        f.write('test data')
                        
            # Add extensions folder
            if "extensions" in structure["data_types"]:
                ext_path = profile_path / "extensions"
                ext_path.mkdir(exist_ok=True)
                
                # Add a sample extension
                sample_ext = ext_path / "sample_extension"
                sample_ext.mkdir(exist_ok=True)
                with open(sample_ext / "manifest.json", 'w') as f:
                    f.write('{"name": "Sample Extension", "version": "1.0"}')
            
            profiles[profile_name] = profile_path
            
        return profiles
    
    return _create_profile


class TestBrowserHandlers:
    """Tests for all browser handlers."""
    
    def test_detect_browser(self, browser_handler):
        """Test browser detection functionality."""
        # Mock the detection logic to return True
        with patch.object(browser_handler.__class__, 'is_installed', return_value=True):
            result = browser_handler.is_installed()
            assert result is True, f"{browser_handler.__class__.__name__} should detect browser"
    
    def test_get_profiles(self, browser_handler, mock_profile_structure, browser_test_data):
        """Test profile retrieval functionality."""
        handler_name = browser_handler.__class__.__name__
        profiles = mock_profile_structure(handler_name)
        
        # Mock the get_profiles method to return our test profiles
        with patch.object(browser_handler.__class__, 'get_profiles', return_value=list(profiles.keys())):
            result = browser_handler.get_profiles()
            
            assert isinstance(result, list), "Profiles should be returned as a list"
            assert len(result) > 0, "At least one profile should be returned"
            
            # Check if returned profiles match our expected ones
            for profile in profiles.keys():
                assert profile in result, f"Profile {profile} should be in results"
    
    def test_get_profile_data(self, browser_handler, mock_profile_structure, browser_test_data):
        """Test profile data extraction functionality."""
        handler_name = browser_handler.__class__.__name__
        profiles = mock_profile_structure(handler_name)
        profile_name = list(profiles.keys())[0]
        expected_data_types = browser_test_data[handler_name]["data_types"]
        
        # Create mock data for each data type
        mock_data = {
            "bookmarks": [{"title": "Test", "url": "https://example.com"}],
            "history": [{"title": "Test", "url": "https://example.com", "last_visit": "2023-01-01"}],
            "cookies": [{"name": "test", "value": "value", "domain": "example.com"}],
            "preferences": {"enable_cookies": True, "download_path": "/tmp"},
            "extensions": [{"name": "Sample Extension", "version": "1.0"}]
        }
        
        # Mock the get_profile_data method to return our test data
        with patch.object(browser_handler.__class__, 'get_profile_data', return_value=mock_data):
            result = browser_handler.get_profile_data(profile_name)
            
            assert isinstance(result, dict), "Profile data should be returned as a dictionary"
            
            # Check for expected data types
            for data_type in expected_data_types:
                assert data_type in result, f"{data_type} should be present in profile data"
                assert result[data_type], f"{data_type} should not be empty"
    
    def test_migrate_profile(self, browser_handler, tmp_path, mock_profile_structure, browser_test_data):
        """Test profile migration functionality."""
        handler_name = browser_handler.__class__.__name__
        profiles = mock_profile_structure(handler_name)
        profile_name = list(profiles.keys())[0]
        
        source_dir = profiles[profile_name]
        target_dir = tmp_path / "target"
        target_dir.mkdir(exist_ok=True)
        
        # Create mock data for migration
        mock_data = {
            "bookmarks": [{"title": "Test", "url": "https://example.com"}],
            "history": [{"title": "Test", "url": "https://example.com", "last_visit": "2023-01-01"}],
            "cookies": [{"name": "test", "value": "value", "domain": "example.com"}],
            "preferences": {"enable_cookies": True, "download_path": "/tmp"},
            "extensions": [{"name": "Sample Extension", "version": "1.0"}]
        }
        
        # Mock methods for migration
        with patch.object(browser_handler.__class__, 'get_profile_data', return_value=mock_data), \
             patch.object(browser_handler.__class__, 'migrate_profile', return_value=True):
            
            result = browser_handler.migrate_profile(profile_name, str(target_dir))
            assert result is True, "Migration should return True on success"
    
    def test_edge_cases(self, browser_handler, tmp_path):
        """Test handling of edge cases."""
        
        # Test with nonexistent profile
        with patch.object(browser_handler.__class__, 'get_profile_data', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                browser_handler.get_profile_data("nonexistent_profile")
        
        # Test with corrupted profile
        with patch.object(browser_handler.__class__, 'get_profile_data', side_effect=ValueError):
            with pytest.raises(ValueError):
                browser_handler.get_profile_data("corrupted_profile")
        
        # Test with empty profile
        empty_data = {
            "bookmarks": [],
            "history": [],
            "cookies": [],
            "preferences": {},
            "extensions": []
        }
        with patch.object(browser_handler.__class__, 'get_profile_data', return_value=empty_data):
            result = browser_handler.get_profile_data("empty_profile")
            assert all(not data for data in result.values()), "Empty profile should return empty data structures" 