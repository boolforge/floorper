"""
Pytest configuration for browser compatibility testing.
Defines fixtures used across test files.
"""

import os
import sys
import pytest
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the test data generator
from tests.test_data_generator import TestDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tests')

# List of supported browsers
BROWSERS = ["chrome", "firefox", "edge", "opera", "brave", "vivaldi"]

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture(scope="session")
def test_profiles(temp_dir):
    """Generate test profiles for each browser."""
    profiles = {}
    generator = TestDataGenerator(temp_dir)
    
    # Generate profiles for each browser
    for browser in BROWSERS:
        try:
            profile_path = generator.generate_profile(browser)
            profiles[browser] = str(profile_path)
        except Exception as e:
            logger.error(f"Failed to generate profile for {browser}: {e}")
    
    yield profiles

@pytest.fixture
def test_data():
    """Generate test data for browser tests."""
    return {
        "urls": [
            "https://www.example.com",
            "https://www.github.com",
            "https://www.python.org"
        ],
        "bookmarks": [
            {"title": "Example", "url": "https://www.example.com"},
            {"title": "GitHub", "url": "https://www.github.com"},
            {"title": "Python", "url": "https://www.python.org"}
        ],
        "cookies": [
            {"name": "session", "value": "test_value", "domain": "example.com"},
            {"name": "user_id", "value": "12345", "domain": "github.com"}
        ],
        "preferences": {
            "enable_cookies": True,
            "download_path": "/tmp/downloads",
            "enable_javascript": True
        }
    }

# For marking tests that require real browsers to be installed
def is_browser_installed(browser_name):
    """Check if a browser is installed."""
    if browser_name == "chrome":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/usr/bin/google-chrome",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    elif browser_name == "firefox":
        paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            "/usr/bin/firefox",
            "/Applications/Firefox.app/Contents/MacOS/firefox"
        ]
    # Add other browsers as needed
    
    return any(os.path.exists(path) for path in paths)

# Custom markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "chrome: mark tests that require Chrome browser")
    config.addinivalue_line("markers", "firefox: mark tests that require Firefox browser")
    config.addinivalue_line("markers", "edge: mark tests that require Edge browser")
    config.addinivalue_line("markers", "opera: mark tests that require Opera browser")
    config.addinivalue_line("markers", "brave: mark tests that require Brave browser")
    config.addinivalue_line("markers", "vivaldi: mark tests that require Vivaldi browser")
    config.addinivalue_line("markers", "real_browser: mark tests that require actual browsers to be installed") 