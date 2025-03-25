"""Tests for Firefox browser handler."""

import os
import sys
import pytest
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from floorper.browsers.firefox import FirefoxBrowserHandler

class TestFirefoxHandler:
    """Test Firefox browser handler functionality."""
    
    @pytest.fixture
    def handler(self):
        """Create Firefox handler instance."""
        return FirefoxBrowserHandler()
        
    def test_detect_browser(self, handler):
        """Test Firefox browser detection."""
        assert handler.detect_browser() is True
        
    def test_get_profiles(self, handler):
        """Test getting Firefox profiles."""
        profiles = handler.get_profiles()
        assert len(profiles) > 0
        assert all(isinstance(p, str) for p in profiles)
        
    def test_get_profile_data(self, handler, test_profiles: Dict[str, Dict[str, Path]], test_data: Dict[str, Any]):
        """Test extracting Firefox profile data.
        
        Args:
            handler: Firefox handler instance
            test_profiles: Test profile directories
            test_data: Test data for validation
        """
        profile_dir = test_profiles["firefox"]["Default"]
        
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
        
    def test_migrate_profile(self, handler, test_profiles: Dict[str, Dict[str, Path]], temp_dir: Path):
        """Test migrating Firefox profile.
        
        Args:
            handler: Firefox handler instance
            test_profiles: Test profile directories
            temp_dir: Temporary directory
        """
        source_dir = test_profiles["firefox"]["Default"]
        target_dir = temp_dir / "migrated_firefox"
        
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
        
    def test_edge_cases(self, handler, temp_dir: Path):
        """Test Firefox handler edge cases.
        
        Args:
            handler: Firefox handler instance
            temp_dir: Temporary directory
        """
        # Test nonexistent profile
        with pytest.raises(FileNotFoundError):
            handler.get_profile_data(Path("/nonexistent/profile"))
            
        # Test corrupted profile
        corrupted_dir = temp_dir / "corrupted_profile"
        corrupted_dir.mkdir()
        
        # Create corrupted files
        (corrupted_dir / "bookmarks").write_text("invalid json")
        (corrupted_dir / "history").write_text("invalid json")
        (corrupted_dir / "cookies").write_text("invalid json")
        
        with pytest.raises(Exception):
            handler.get_profile_data(corrupted_dir)
            
        # Test empty profile
        empty_dir = temp_dir / "empty_profile"
        empty_dir.mkdir()
        
        data = handler.get_profile_data(empty_dir)
        assert data["bookmarks"] == []
        assert data["history"] == []
        assert data["cookies"] == []
        assert data["preferences"] == {}
        assert data["extensions"] == [] 