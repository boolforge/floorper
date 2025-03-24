"""
Browser compatibility tests for Floorper.
Tests profile detection, extraction, and migration across different browsers.
"""

import os
import sys
import pytest
import shutil
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import logging
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from floorper.browsers.chrome import ChromeBrowserHandler
from floorper.browsers.firefox import FirefoxBrowserHandler
from floorper.browsers.edge import EdgeBrowserHandler
from floorper.browsers.opera import OperaBrowserHandler
from floorper.browsers.brave import BraveBrowserHandler
from floorper.browsers.vivaldi import VivaldiBrowserHandler
from floorper.browsers.floorp import FloorpBrowserHandler
from floorper.browsers.exotic import ExoticBrowserHandler
from floorper.browsers.retro import RetroBrowserHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("browser_compatibility_tests.log")
    ]
)

logger = logging.getLogger(__name__)

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
BROWSER_PROFILES = {
    "firefox": TEST_DATA_DIR / "firefox",
    "chrome": TEST_DATA_DIR / "chrome",
    "edge": TEST_DATA_DIR / "edge",
    "opera": TEST_DATA_DIR / "opera",
    "brave": TEST_DATA_DIR / "brave",
    "vivaldi": TEST_DATA_DIR / "vivaldi",
    "floorp": TEST_DATA_DIR / "floorp",
    "qutebrowser": TEST_DATA_DIR / "qutebrowser",
    "netscape": TEST_DATA_DIR / "netscape"
}

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture(scope="session")
def test_profiles():
    """Set up test profiles for each browser."""
    # Create test data directory if it doesn't exist
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create test profiles for each browser
    for browser, profile_dir in BROWSER_PROFILES.items():
        if not profile_dir.exists():
            profile_dir.mkdir(parents=True)
            # Create basic profile structure
            (profile_dir / "bookmarks.html").touch()
            (profile_dir / "history").touch()
            (profile_dir / "cookies.txt").touch()
            (profile_dir / "prefs.js").touch()
    
    yield BROWSER_PROFILES
    
    # Cleanup after tests
    for profile_dir in BROWSER_PROFILES.values():
        if profile_dir.exists():
            shutil.rmtree(profile_dir)

# Browser handler mapping
BROWSER_HANDLERS = {
    "chrome": ChromeBrowserHandler,
    "firefox": FirefoxBrowserHandler,
    "edge": EdgeBrowserHandler,
    "opera": OperaBrowserHandler,
    "brave": BraveBrowserHandler,
    "vivaldi": VivaldiBrowserHandler,
    "floorp": FloorpBrowserHandler,
    "qutebrowser": ExoticBrowserHandler,
    "netscape": RetroBrowserHandler
}

class TestBrowserDetection:
    """Test browser detection functionality."""
    
    @pytest.mark.parametrize("browser", BROWSER_HANDLERS.keys())
    def test_browser_detection(self, browser: str, test_profiles: Dict[str, Dict[str, Path]]) -> None:
        """Test detection of each browser.
        
        Args:
            browser: Browser name
            test_profiles: Test profile directories
        """
        handler = BROWSER_HANDLERS[browser]()
        assert handler.detect_browser() is True
        
    def test_unsupported_browser(self) -> None:
        """Test detection of unsupported browser."""
        class UnsupportedHandler:
            def detect_browser(self) -> bool:
                return False
                
        handler = UnsupportedHandler()
        assert handler.detect_browser() is False

class TestProfileExtraction:
    """Test profile data extraction."""
    
    @pytest.mark.parametrize("browser", BROWSER_HANDLERS.keys())
    def test_get_profiles(self, browser: str, test_profiles: Dict[str, Dict[str, Path]]) -> None:
        """Test getting available profiles.
        
        Args:
            browser: Browser name
            test_profiles: Test profile directories
        """
        handler = BROWSER_HANDLERS[browser]()
        profiles = handler.get_profiles()
        assert len(profiles) > 0
        assert all(isinstance(p, str) for p in profiles)
        
    @pytest.mark.parametrize("browser", BROWSER_HANDLERS.keys())
    def test_get_profile_data(self, browser: str, test_profiles: Dict[str, Dict[str, Path]], test_data: Dict[str, Any]) -> None:
        """Test extracting profile data.
        
        Args:
            browser: Browser name
            test_profiles: Test profile directories
            test_data: Test data for validation
        """
        handler = BROWSER_HANDLERS[browser]()
        profile_dir = test_profiles[browser]["Default"]
        
        data = handler.get_profile_data(profile_dir)
        assert "bookmarks" in data
        assert "history" in data
        assert "cookies" in data
        assert "preferences" in data
        assert "extensions" in data
        
        # Validate bookmarks
        assert len(data["bookmarks"]) > 0
        assert all("name" in b and "url" in b for b in data["bookmarks"])
        
        # Validate history
        assert len(data["history"]) > 0
        assert all("url" in h and "title" in h for h in data["history"])
        
        # Validate cookies
        assert len(data["cookies"]) > 0
        assert all("domain" in c and "name" in c for c in data["cookies"])
        
        # Validate preferences
        assert isinstance(data["preferences"], dict)
        assert len(data["preferences"]) > 0
        
        # Validate extensions
        assert isinstance(data["extensions"], list)
        assert all("id" in e and "name" in e for e in data["extensions"])

class TestProfileMigration:
    """Test profile migration functionality."""
    
    @pytest.mark.parametrize("browser", BROWSER_HANDLERS.keys())
    def test_migrate_profile(self, browser: str, test_profiles: Dict[str, Dict[str, Path]], temp_dir: Path) -> None:
        """Test migrating a profile.
        
        Args:
            browser: Browser name
            test_profiles: Test profile directories
            temp_dir: Temporary directory
        """
        handler = BROWSER_HANDLERS[browser]()
        source_dir = test_profiles[browser]["Default"]
        target_dir = temp_dir / f"migrated_{browser}"
        
        # Migrate profile
        handler.migrate_profile(source_dir, target_dir)
        
        # Verify migration
        assert target_dir.exists()
        assert (target_dir / "bookmarks").exists()
        assert (target_dir / "history").exists()
        assert (target_dir / "cookies").exists()
        assert (target_dir / "preferences").exists()
        assert (target_dir / "extensions").exists()
        
        # Clean up
        shutil.rmtree(target_dir)

class TestCrossBrowserMigration:
    """Test cross-browser profile migration."""
    
    @pytest.mark.parametrize("source_browser", BROWSER_HANDLERS.keys())
    @pytest.mark.parametrize("target_browser", BROWSER_HANDLERS.keys())
    def test_cross_browser_migration(
        self,
        source_browser: str,
        target_browser: str,
        test_profiles: Dict[str, Dict[str, Path]],
        temp_dir: Path
    ) -> None:
        """Test migrating profiles between different browsers.
        
        Args:
            source_browser: Source browser name
            target_browser: Target browser name
            test_profiles: Test profile directories
            temp_dir: Temporary directory
        """
        if source_browser == target_browser:
            pytest.skip("Skipping same-browser migration test")
            
        source_handler = BROWSER_HANDLERS[source_browser]()
        target_handler = BROWSER_HANDLERS[target_browser]()
        
        source_dir = test_profiles[source_browser]["Default"]
        target_dir = temp_dir / f"migrated_{source_browser}_to_{target_browser}"
        
        # Migrate profile
        source_handler.migrate_profile(source_dir, target_dir)
        
        # Verify migration
        assert target_dir.exists()
        
        # Extract and validate data
        data = target_handler.get_profile_data(target_dir)
        assert "bookmarks" in data
        assert "history" in data
        assert "cookies" in data
        assert "preferences" in data
        assert "extensions" in data
        
        # Clean up
        shutil.rmtree(target_dir)

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.parametrize("browser", BROWSER_HANDLERS.keys())
    def test_nonexistent_profile(self, browser: str) -> None:
        """Test handling of nonexistent profile.
        
        Args:
            browser: Browser name
        """
        handler = BROWSER_HANDLERS[browser]()
        with pytest.raises(FileNotFoundError):
            handler.get_profile_data(Path("/nonexistent/profile"))
            
    @pytest.mark.parametrize("browser", BROWSER_HANDLERS.keys())
    def test_corrupted_profile(self, browser: str, temp_dir: Path) -> None:
        """Test handling of corrupted profile.
        
        Args:
            browser: Browser name
            temp_dir: Temporary directory
        """
        handler = BROWSER_HANDLERS[browser]()
        corrupted_dir = temp_dir / "corrupted_profile"
        corrupted_dir.mkdir()
        
        # Create corrupted files
        (corrupted_dir / "bookmarks").write_text("invalid json")
        (corrupted_dir / "history").write_text("invalid json")
        (corrupted_dir / "cookies").write_text("invalid json")
        
        with pytest.raises(Exception):
            handler.get_profile_data(corrupted_dir)
            
    @pytest.mark.parametrize("browser", BROWSER_HANDLERS.keys())
    def test_empty_profile(self, browser: str, temp_dir: Path) -> None:
        """Test handling of empty profile.
        
        Args:
            browser: Browser name
            temp_dir: Temporary directory
        """
        handler = BROWSER_HANDLERS[browser]()
        empty_dir = temp_dir / "empty_profile"
        empty_dir.mkdir()
        
        data = handler.get_profile_data(empty_dir)
        assert data["bookmarks"] == []
        assert data["history"] == []
        assert data["cookies"] == []
        assert data["preferences"] == {}
        assert data["extensions"] == []

class TestPerformance:
    """Test performance metrics."""
    
    @pytest.mark.parametrize("browser,handler_class", [
        ("firefox", FirefoxBrowserHandler),
        ("chrome", ChromeBrowserHandler),
        ("edge", EdgeBrowserHandler)
    ])
    def test_extraction_performance(self, browser, handler_class, test_profiles):
        """Test performance of profile data extraction."""
        handler = handler_class()
        profile_path = test_profiles[browser]
        
        start_time = datetime.now()
        
        # Test bookmarks extraction
        handler._get_bookmarks(profile_path)
        bookmarks_time = (datetime.now() - start_time).total_seconds()
        assert bookmarks_time < 1.0, f"Bookmarks extraction too slow for {browser}"
        
        # Test history extraction
        handler._get_history(profile_path)
        history_time = (datetime.now() - start_time).total_seconds()
        assert history_time < 2.0, f"History extraction too slow for {browser}"
        
        # Test cookies extraction
        handler._get_cookies(profile_path)
        cookies_time = (datetime.now() - start_time).total_seconds()
        assert cookies_time < 1.0, f"Cookies extraction too slow for {browser}"
    
    @pytest.mark.parametrize("browser,handler_class", [
        ("firefox", FirefoxBrowserHandler),
        ("chrome", ChromeBrowserHandler),
        ("edge", EdgeBrowserHandler)
    ])
    def test_migration_performance(self, browser, handler_class, test_profiles, temp_dir):
        """Test performance of profile migration."""
        handler = handler_class()
        source_path = test_profiles[browser]
        target_path = temp_dir / f"{browser}_performance"
        
        start_time = datetime.now()
        success = handler.migrate_profile(source_path, target_path)
        migration_time = (datetime.now() - start_time).total_seconds()
        
        assert success is True, f"Migration failed for {browser}"
        assert migration_time < 5.0, f"Migration too slow for {browser}" 