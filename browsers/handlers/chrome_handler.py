"""
Chrome browser handler.
Provides functionality to interact with Chrome browser profiles.
"""

import os
import json
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_handler import BaseBrowserHandler


class ChromeHandler(BaseBrowserHandler):
    """Handler for Chrome browser."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the Chrome handler.
        
        Args:
            data_dir: Directory where Chrome data is stored.
                     If None, the default location will be used.
        """
        super().__init__(data_dir)
        
        if self.data_dir is None:
            self.data_dir = self._get_default_data_dir()
    
    def _get_default_data_dir(self) -> Path:
        """
        Get the default data directory for Chrome.
        
        Returns:
            Path to the default data directory
        """
        system = platform.system()
        
        if system == "Windows":
            return Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
        elif system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        else:  # Linux and others
            return Path.home() / ".config" / "google-chrome"
    
    def is_installed(self) -> bool:
        """
        Check if Chrome is installed.
        
        Returns:
            True if Chrome is installed, False otherwise
        """
        # Check common installation paths
        system = platform.system()
        
        if system == "Windows":
            paths = [
                Path(os.environ["PROGRAMFILES"]) / "Google" / "Chrome" / "Application" / "chrome.exe",
                Path(os.environ["PROGRAMFILES(X86)"]) / "Google" / "Chrome" / "Application" / "chrome.exe",
            ]
        elif system == "Darwin":  # macOS
            paths = [
                Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            ]
        else:  # Linux and others
            paths = [
                Path("/usr/bin/google-chrome"),
                Path("/usr/bin/google-chrome-stable"),
            ]
        
        return any(path.exists() for path in paths) or self.data_dir.exists()
    
    def get_profiles(self) -> List[str]:
        """
        Get all available Chrome profiles.
        
        Returns:
            List of profile names
        """
        profiles = []
        
        # Chrome stores profiles in the User Data directory
        if not self.data_dir.exists():
            return profiles
        
        # The default profile is named "Default"
        if (self.data_dir / "Default").exists():
            profiles.append("Default")
        
        # Other profiles are named "Profile X"
        for item in self.data_dir.iterdir():
            if item.is_dir() and item.name.startswith("Profile "):
                profiles.append(item.name)
        
        return profiles
    
    def get_profile_data(self, profile_name: str) -> Dict[str, Any]:
        """
        Get data from a Chrome profile.
        
        Args:
            profile_name: Name of the profile to get data from
            
        Returns:
            Dictionary containing profile data (bookmarks, history, cookies, etc.)
        """
        profile_dir = self.data_dir / profile_name
        
        if not profile_dir.exists():
            raise FileNotFoundError(f"Profile '{profile_name}' not found")
        
        result = {
            "bookmarks": self._get_bookmarks(profile_dir),
            "history": self._get_history(profile_dir),
            "cookies": self._get_cookies(profile_dir),
            "preferences": self._get_preferences(profile_dir),
            "extensions": self._get_extensions(profile_dir),
        }
        
        return result
    
    def _get_bookmarks(self, profile_dir: Path) -> List[Dict[str, Any]]:
        """
        Get bookmarks from a Chrome profile.
        
        Args:
            profile_dir: Path to the profile directory
            
        Returns:
            List of bookmarks
        """
        bookmarks_file = profile_dir / "Bookmarks"
        
        if not bookmarks_file.exists():
            return []
        
        try:
            with open(bookmarks_file, encoding="utf-8") as f:
                data = json.load(f)
            
            bookmarks = []
            
            # Process bookmark bar
            if "roots" in data and "bookmark_bar" in data["roots"]:
                self._extract_bookmarks(data["roots"]["bookmark_bar"], bookmarks)
            
            # Process other bookmarks
            if "roots" in data and "other" in data["roots"]:
                self._extract_bookmarks(data["roots"]["other"], bookmarks)
            
            return bookmarks
        except Exception as e:
            print(f"Error reading bookmarks: {e}")
            return []
    
    def _extract_bookmarks(self, node: Dict[str, Any], bookmarks: List[Dict[str, Any]]) -> None:
        """
        Extract bookmarks from a bookmark node.
        
        Args:
            node: Bookmark node
            bookmarks: List to add bookmarks to
        """
        if "type" in node and node["type"] == "url":
            bookmarks.append({
                "title": node.get("name", ""),
                "url": node.get("url", ""),
                "added": node.get("date_added", ""),
            })
        
        if "children" in node:
            for child in node["children"]:
                self._extract_bookmarks(child, bookmarks)
    
    def _get_history(self, profile_dir: Path) -> List[Dict[str, Any]]:
        """
        Get history from a Chrome profile.
        
        Args:
            profile_dir: Path to the profile directory
            
        Returns:
            List of history entries
        """
        # In a real implementation, this would use SQLite to read the History database
        # For now, return a placeholder
        return []
    
    def _get_cookies(self, profile_dir: Path) -> List[Dict[str, Any]]:
        """
        Get cookies from a Chrome profile.
        
        Args:
            profile_dir: Path to the profile directory
            
        Returns:
            List of cookies
        """
        # In a real implementation, this would use SQLite to read the Cookies database
        # For now, return a placeholder
        return []
    
    def _get_preferences(self, profile_dir: Path) -> Dict[str, Any]:
        """
        Get preferences from a Chrome profile.
        
        Args:
            profile_dir: Path to the profile directory
            
        Returns:
            Dictionary of preferences
        """
        preferences_file = profile_dir / "Preferences"
        
        if not preferences_file.exists():
            return {}
        
        try:
            with open(preferences_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading preferences: {e}")
            return {}
    
    def _get_extensions(self, profile_dir: Path) -> List[Dict[str, Any]]:
        """
        Get extensions from a Chrome profile.
        
        Args:
            profile_dir: Path to the profile directory
            
        Returns:
            List of extensions
        """
        extensions_dir = profile_dir / "Extensions"
        
        if not extensions_dir.exists():
            return []
        
        extensions = []
        
        for ext_id in extensions_dir.iterdir():
            if not ext_id.is_dir():
                continue
            
            versions = [v for v in ext_id.iterdir() if v.is_dir()]
            
            if not versions:
                continue
            
            # Use the latest version
            latest_version = sorted(versions)[-1]
            manifest_file = latest_version / "manifest.json"
            
            if not manifest_file.exists():
                continue
            
            try:
                with open(manifest_file, encoding="utf-8") as f:
                    manifest = json.load(f)
                
                extensions.append({
                    "id": ext_id.name,
                    "name": manifest.get("name", "Unknown"),
                    "version": manifest.get("version", "Unknown"),
                    "description": manifest.get("description", ""),
                })
            except Exception as e:
                print(f"Error reading extension manifest: {e}")
        
        return extensions
    
    def migrate_profile(self, profile_name: str, target_dir: str) -> bool:
        """
        Migrate a Chrome profile to a different directory.
        
        Args:
            profile_name: Name of the profile to migrate
            target_dir: Target directory to migrate to
            
        Returns:
            True if migration was successful, False otherwise
        """
        profile_dir = self.data_dir / profile_name
        target_path = Path(target_dir)
        
        if not profile_dir.exists():
            raise FileNotFoundError(f"Profile '{profile_name}' not found")
        
        try:
            # Create target directory
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Get profile data
            profile_data = self.get_profile_data(profile_name)
            
            # Store profile data as JSON
            with open(target_path / "profile_data.json", "w") as f:
                json.dump(profile_data, f, indent=2, default=str)
            
            # Copy important files
            for file_name in ["Bookmarks", "Preferences"]:
                source_file = profile_dir / file_name
                target_file = target_path / file_name
                
                if source_file.exists():
                    shutil.copy2(source_file, target_file)
            
            return True
        except Exception as e:
            print(f"Error migrating profile: {e}")
            return False 