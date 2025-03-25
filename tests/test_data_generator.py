"""
Test data generator for browser profiles.
Creates realistic browser profiles with sample data for testing.
"""

import os
import json
import sqlite3
import random
import string
import datetime
from pathlib import Path
import shutil
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_data_generator')

class TestDataGenerator:
    """Generates test data for browser profiles."""
    
    def __init__(self, base_dir):
        """
        Initialize the test data generator.
        
        Args:
            base_dir: Base directory to create test profiles in
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.sample_urls = [
            "https://www.example.com",
            "https://www.github.com",
            "https://www.python.org",
            "https://www.mozilla.org",
            "https://www.google.com",
            "https://www.microsoft.com",
            "https://www.apple.com",
            "https://www.amazon.com",
            "https://www.wikipedia.org",
            "https://www.reddit.com"
        ]
        
    def _random_string(self, length=10):
        """Generate a random string of fixed length."""
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    def _random_date(self, start_date=None, end_date=None):
        """Generate a random date between start_date and end_date."""
        if not start_date:
            start_date = datetime.datetime(2020, 1, 1)
        if not end_date:
            end_date = datetime.datetime.now()
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_days = random.randrange(days_between_dates)
        return start_date + datetime.timedelta(days=random_days)
    
    def generate_chrome_profile(self, profile_name="Default"):
        """
        Generate a Chrome browser profile with test data.
        
        Args:
            profile_name: Name of the profile to create
            
        Returns:
            Path to the generated profile
        """
        profile_dir = self.base_dir / "Chrome" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate bookmarks
        bookmarks_data = self._generate_chrome_bookmarks()
        with open(profile_dir / "Bookmarks", 'w') as f:
            json.dump(bookmarks_data, f, indent=2)
        
        # Generate history
        # In a real implementation, we'd create an SQLite database
        # For testing, we'll create a placeholder file
        with open(profile_dir / "History", 'w') as f:
            f.write("Chrome History Placeholder")
        
        # Generate cookies
        with open(profile_dir / "Cookies", 'w') as f:
            f.write("Chrome Cookies Placeholder")
        
        # Generate preferences
        preferences_data = self._generate_chrome_preferences()
        with open(profile_dir / "Preferences", 'w') as f:
            json.dump(preferences_data, f, indent=2)
        
        # Generate extensions
        extensions_dir = profile_dir / "Extensions"
        extensions_dir.mkdir(exist_ok=True)
        for i in range(3):
            ext_id = self._random_string(32)
            ext_dir = extensions_dir / ext_id / "1.0"
            ext_dir.mkdir(parents=True, exist_ok=True)
            with open(ext_dir / "manifest.json", 'w') as f:
                json.dump({
                    "name": f"Test Extension {i}",
                    "version": "1.0",
                    "manifest_version": 2,
                    "description": "A test extension"
                }, f, indent=2)
        
        logger.info(f"Generated Chrome profile at {profile_dir}")
        return profile_dir
    
    def generate_firefox_profile(self, profile_name="default"):
        """
        Generate a Firefox browser profile with test data.
        
        Args:
            profile_name: Name of the profile to create
            
        Returns:
            Path to the generated profile
        """
        profile_dir = self.base_dir / "Firefox" / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate places.sqlite (bookmarks and history)
        # In a real implementation, we'd create a proper SQLite database
        # For testing, we'll create a placeholder file
        with open(profile_dir / "places.sqlite", 'wb') as f:
            f.write(b'SQLite format 3\0')
        
        # Generate cookies.sqlite
        with open(profile_dir / "cookies.sqlite", 'wb') as f:
            f.write(b'SQLite format 3\0')
        
        # Generate prefs.js
        prefs_data = self._generate_firefox_preferences()
        with open(profile_dir / "prefs.js", 'w') as f:
            f.write(prefs_data)
        
        # Generate extensions
        extensions_dir = profile_dir / "extensions"
        extensions_dir.mkdir(exist_ok=True)
        for i in range(3):
            ext_id = f"test-extension-{i}@example.com"
            with open(extensions_dir / f"{ext_id}.xpi", 'w') as f:
                f.write(f"Firefox Extension {i} placeholder")
        
        logger.info(f"Generated Firefox profile at {profile_dir}")
        return profile_dir
    
    def _generate_chrome_bookmarks(self):
        """Generate Chrome bookmarks in JSON format."""
        now = int(datetime.datetime.now().timestamp())
        
        bookmarks = {
            "checksum": "",
            "roots": {
                "bookmark_bar": {
                    "children": [],
                    "date_added": str(now),
                    "date_modified": str(now),
                    "id": "1",
                    "name": "Bookmarks Bar",
                    "type": "folder"
                },
                "other": {
                    "children": [],
                    "date_added": str(now),
                    "date_modified": str(now),
                    "id": "2",
                    "name": "Other Bookmarks",
                    "type": "folder"
                },
                "synced": {
                    "children": [],
                    "date_added": str(now),
                    "date_modified": str(now),
                    "id": "3",
                    "name": "Mobile Bookmarks",
                    "type": "folder"
                }
            },
            "version": 1
        }
        
        # Add some random bookmarks
        for i, url in enumerate(self.sample_urls[:5]):
            bookmarks["roots"]["bookmark_bar"]["children"].append({
                "date_added": str(now - random.randint(1, 10000)),
                "id": str(10 + i),
                "name": f"Bookmark {i}",
                "type": "url",
                "url": url
            })
        
        for i, url in enumerate(self.sample_urls[5:]):
            bookmarks["roots"]["other"]["children"].append({
                "date_added": str(now - random.randint(1, 10000)),
                "id": str(20 + i),
                "name": f"Other Bookmark {i}",
                "type": "url",
                "url": url
            })
        
        return bookmarks
    
    def _generate_chrome_preferences(self):
        """Generate Chrome preferences in JSON format."""
        return {
            "browser": {
                "enabled_labs_experiments": [],
                "has_seen_welcome_page": True,
                "window_placement": {
                    "bottom": 1000,
                    "left": 0,
                    "maximized": False,
                    "right": 1000,
                    "top": 0,
                    "work_area_bottom": 1080,
                    "work_area_left": 0,
                    "work_area_right": 1920,
                    "work_area_top": 0
                }
            },
            "download": {
                "default_directory": "/tmp/downloads",
                "prompt_for_download": False
            },
            "profile": {
                "content_settings": {
                    "cookies": 1,  # Allow cookies
                    "images": 1,  # Allow images
                    "javascript": 1,  # Allow JavaScript
                    "plugins": 1  # Allow plugins
                },
                "default_content_setting_values": {
                    "notifications": 2  # Block notifications
                },
                "password_manager_enabled": True
            },
            "translate": {
                "enabled": True
            }
        }
    
    def _generate_firefox_preferences(self):
        """Generate Firefox preferences in prefs.js format."""
        prefs = [
            'user_pref("browser.startup.homepage", "https://www.mozilla.org/en-US/firefox/");',
            'user_pref("browser.download.dir", "/tmp/downloads");',
            'user_pref("browser.download.folderList", 2);',
            'user_pref("browser.search.defaultenginename", "Google");',
            'user_pref("browser.search.selectedEngine", "Google");',
            'user_pref("network.cookie.cookieBehavior", 0);',
            'user_pref("privacy.donottrackheader.enabled", true);',
            'user_pref("browser.urlbar.maxRichResults", 10);',
            'user_pref("browser.contentblocking.category", "standard");',
            'user_pref("browser.privatebrowsing.autostart", false);'
        ]
        return '\n'.join(prefs)
    
    def generate_profile(self, browser_type, profile_name=None):
        """
        Generate a browser profile for the specified browser type.
        
        Args:
            browser_type: Type of browser (chrome, firefox, edge, etc.)
            profile_name: Name of the profile to create (optional)
            
        Returns:
            Path to the generated profile
        """
        browser_type = browser_type.lower()
        
        if browser_type == "chrome":
            return self.generate_chrome_profile(profile_name or "Default")
        elif browser_type == "firefox":
            return self.generate_firefox_profile(profile_name or "default")
        elif browser_type in ["edge", "brave", "vivaldi"]:
            # These browsers use Chrome's format
            profile_dir = self.base_dir / browser_type.capitalize() / (profile_name or "Default")
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy Chrome profile structure
            chrome_profile = self.generate_chrome_profile("temp_profile")
            for item in chrome_profile.iterdir():
                if item.is_dir():
                    shutil.copytree(item, profile_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, profile_dir / item.name)
            
            logger.info(f"Generated {browser_type} profile at {profile_dir}")
            return profile_dir
        elif browser_type == "opera":
            # Opera uses Chrome's format with slight variations
            profile_dir = self.base_dir / "Opera" / (profile_name or "Default")
            profile_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy Chrome profile structure
            chrome_profile = self.generate_chrome_profile("temp_profile")
            for item in chrome_profile.iterdir():
                if item.is_dir():
                    shutil.copytree(item, profile_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, profile_dir / item.name)
                    
            # Add Opera-specific files
            with open(profile_dir / "Speeddial", 'w') as f:
                f.write("Opera Speeddial Placeholder")
                
            logger.info(f"Generated Opera profile at {profile_dir}")
            return profile_dir
        else:
            logger.error(f"Unsupported browser type: {browser_type}")
            raise ValueError(f"Unsupported browser type: {browser_type}")


# Example usage
if __name__ == "__main__":
    generator = TestDataGenerator("/tmp/test_profiles")
    chrome_profile = generator.generate_profile("chrome")
    firefox_profile = generator.generate_profile("firefox")
    edge_profile = generator.generate_profile("edge")
    print(f"Generated profiles at: {generator.base_dir}") 