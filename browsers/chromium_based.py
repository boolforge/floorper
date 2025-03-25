"""
Chromium-based browser handler.
This module provides handlers for Chromium and its derivatives (Chrome, Edge, Brave, Opera, etc.).
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import logging
from datetime import datetime
import base64
import os

from . import BrowserHandler
from ..core.constants import CHROMIUM_PROFILES, CHROMIUM_BROWSERS

logger = logging.getLogger(__name__)

class ChromiumBasedHandler(BrowserHandler):
    """Handler for Chromium-based browsers."""
    
    def __init__(self, browser_name: str = "chrome"):
        super().__init__()
        self.name = browser_name
        self.profiles_dir = None
        self.version = ""
    
    def detect_browser(self) -> bool:
        """Detect if Chromium or its derivatives are installed."""
        for browser in CHROMIUM_BROWSERS:
            if self.name.lower() in browser.lower():
                # Check for profiles directory
                for profile_dir in CHROMIUM_PROFILES:
                    if profile_dir.exists():
                        self.profiles_dir = profile_dir
                        return True
        return False
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """Get list of available Chromium profiles."""
        if not self.profiles_dir:
            return []
        
        profiles = []
        for profile_dir in self.profiles_dir.iterdir():
            if profile_dir.is_dir() and not profile_dir.name.startswith('.'):
                profile_data = self.get_profile_data(profile_dir)
                if profile_data:
                    profiles.append({
                        'name': profile_dir.name,
                        'path': str(profile_dir),
                        'data': profile_data
                    })
        return profiles
    
    def get_profile_path(self, profile_name: str) -> Optional[Path]:
        """Get the path to a specific Chromium profile."""
        if not self.profiles_dir:
            return None
        
        profile_path = self.profiles_dir / profile_name
        return profile_path if profile_path.exists() else None
    
    def get_profile_data(self, profile_path: Path) -> Dict[str, Any]:
        """Get Chromium profile data including bookmarks, history, etc."""
        if not profile_path.exists():
            return {}
        
        data = {
            'bookmarks': self._get_bookmarks(profile_path),
            'history': self._get_history(profile_path),
            'cookies': self._get_cookies(profile_path),
            'passwords': self._get_passwords(profile_path),
            'extensions': self._get_extensions(profile_path),
            'preferences': self._get_preferences(profile_path)
        }
        return data
    
    def migrate_profile(self, source_path: Path, target_path: Path) -> bool:
        """Migrate Chromium profile data from source to target."""
        try:
            # Create target directory if it doesn't exist
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy essential files
            essential_files = [
                'Bookmarks',  # Bookmarks file
                'History',  # History database
                'Cookies',  # Cookies database
                'Login Data',  # Passwords database
                'Preferences',  # Preferences file
                'Extensions',  # Extensions directory
                'Sessions',  # Session data
                'Web Data',  # Form data and other web data
                'Favicons',  # Favicon cache
                'Network',  # Network-related data
                'QuotaManager-journal',  # Storage quota data
                'QuotaManager'  # Storage quota data
            ]
            
            for file in essential_files:
                src_file = source_path / file
                if src_file.exists():
                    if src_file.is_dir():
                        shutil.copytree(src_file, target_path / file, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_file, target_path / file)
            
            return True
        except Exception as e:
            logger.error(f"Error migrating Chromium profile: {e}")
            return False
    
    def _get_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks from Bookmarks file."""
        bookmarks = []
        bookmarks_file = profile_path / 'Bookmarks'
        
        if not bookmarks_file.exists():
            return bookmarks
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                bookmarks_data = json.load(f)
                
                def process_node(node: Dict[str, Any], parent: Optional[Dict[str, Any]] = None) -> None:
                    if node.get('type') == 'url':
                        bookmark = {
                            'title': node.get('name', ''),
                            'url': node.get('url', ''),
                            'date_added': datetime.fromtimestamp(node.get('date_added', 0) / 1000000).isoformat(),
                            'last_modified': datetime.fromtimestamp(node.get('date_modified', 0) / 1000000).isoformat()
                        }
                        if parent:
                            bookmark['folder'] = parent.get('name', '')
                        bookmarks.append(bookmark)
                    elif node.get('type') == 'folder':
                        for child in node.get('children', []):
                            process_node(child, node)
                
                for root in bookmarks_data.get('roots', {}).values():
                    process_node(root)
        except Exception as e:
            logger.error(f"Error reading bookmarks: {e}")
        
        return bookmarks
    
    def _get_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history from History database."""
        history = []
        history_file = profile_path / 'History'
        
        if not history_file.exists():
            return history
        
        try:
            conn = sqlite3.connect(history_file)
            cursor = conn.cursor()
            
            # Get history from urls and visits tables
            cursor.execute("""
                SELECT u.url, u.title, v.visit_time, v.visit_duration, v.visit_type
                FROM urls u
                JOIN visits v ON u.id = v.url
                ORDER BY v.visit_time DESC
            """)
            
            for row in cursor.fetchall():
                history.append({
                    'url': row[0],
                    'title': row[1],
                    'visit_time': datetime.fromtimestamp(row[2] / 1000000).isoformat(),
                    'visit_duration': row[3],
                    'visit_type': row[4]
                })
            
            conn.close()
        except Exception as e:
            logger.error(f"Error reading history: {e}")
        
        return history
    
    def _get_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies from Cookies database."""
        cookies = []
        cookies_file = profile_path / 'Cookies'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            conn = sqlite3.connect(cookies_file)
            cursor = conn.cursor()
            
            # Get cookies from cookies table
            cursor.execute("""
                SELECT host_key, name, encrypted_value, path, expires_utc, last_access_utc, creation_utc
                FROM cookies
            """)
            
            for row in cursor.fetchall():
                cookies.append({
                    'host': row[0],
                    'name': row[1],
                    'value': self._decrypt_value(row[2]),
                    'path': row[3],
                    'expiry': datetime.fromtimestamp(row[4] / 1000000).isoformat(),
                    'last_accessed': datetime.fromtimestamp(row[5] / 1000000).isoformat(),
                    'creation_time': datetime.fromtimestamp(row[6] / 1000000).isoformat()
                })
            
            conn.close()
        except Exception as e:
            logger.error(f"Error reading cookies: {e}")
        
        return cookies
    
    def _get_passwords(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract passwords from Login Data database."""
        passwords = []
        login_data_file = profile_path / 'Login Data'
        
        if not login_data_file.exists():
            return passwords
        
        try:
            conn = sqlite3.connect(login_data_file)
            cursor = conn.cursor()
            
            # Get passwords from logins table
            cursor.execute("""
                SELECT origin_url, username_value, password_value, date_created, date_last_used
                FROM logins
            """)
            
            for row in cursor.fetchall():
                passwords.append({
                    'url': row[0],
                    'username': row[1],
                    'password': self._decrypt_value(row[2]),
                    'date_created': datetime.fromtimestamp(row[3] / 1000000).isoformat(),
                    'date_last_used': datetime.fromtimestamp(row[4] / 1000000).isoformat()
                })
            
            conn.close()
        except Exception as e:
            logger.error(f"Error reading passwords: {e}")
        
        return passwords
    
    def _get_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed extensions."""
        extensions = []
        extensions_dir = profile_path / 'Extensions'
        
        if not extensions_dir.exists():
            return extensions
        
        try:
            for ext_dir in extensions_dir.iterdir():
                if ext_dir.is_dir():
                    manifest_file = ext_dir / 'manifest.json'
                    if manifest_file.exists():
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                            extensions.append({
                                'id': ext_dir.name,
                                'name': manifest.get('name'),
                                'version': manifest.get('version'),
                                'description': manifest.get('description')
                            })
        except Exception as e:
            logger.error(f"Error reading extensions: {e}")
        
        return extensions
    
    def _get_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract user preferences from Preferences file."""
        preferences = {}
        prefs_file = profile_path / 'Preferences'
        
        if not prefs_file.exists():
            return preferences
        
        try:
            with open(prefs_file, 'r', encoding='utf-8') as f:
                preferences = json.load(f)
        except Exception as e:
            logger.error(f"Error reading preferences: {e}")
        
        return preferences
    
    def _decrypt_value(self, encrypted_value: bytes) -> str:
        """Decrypt encrypted values from Chromium databases."""
        # This is a placeholder for the actual decryption logic
        # The actual implementation would depend on the OS and Chromium version
        # For now, we'll just return the base64 encoded value
        try:
            return base64.b64encode(encrypted_value).decode('utf-8')
        except Exception as e:
            logger.error(f"Error decrypting value: {e}")
            return "" 