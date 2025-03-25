"""
Firefox-based browser handler.
This module provides handlers for Firefox and its derivatives (LibreWolf, Waterfox, Pale Moon, etc.).
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import logging
from datetime import datetime

from . import BrowserHandler
from ..core.constants import FIREFOX_PROFILES, FIREFOX_BROWSERS

logger = logging.getLogger(__name__)

class FirefoxBasedHandler(BrowserHandler):
    """Handler for Firefox-based browsers."""
    
    def __init__(self, browser_name: str = "firefox"):
        super().__init__()
        self.name = browser_name
        self.profiles_dir = None
        self.version = ""
    
    def detect_browser(self) -> bool:
        """Detect if Firefox or its derivatives are installed."""
        for browser in FIREFOX_BROWSERS:
            if self.name.lower() in browser.lower():
                # Check for profiles directory
                for profile_dir in FIREFOX_PROFILES:
                    if profile_dir.exists():
                        self.profiles_dir = profile_dir
                        return True
        return False
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """Get list of available Firefox profiles."""
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
        """Get the path to a specific Firefox profile."""
        if not self.profiles_dir:
            return None
        
        profile_path = self.profiles_dir / profile_name
        return profile_path if profile_path.exists() else None
    
    def get_profile_data(self, profile_path: Path) -> Dict[str, Any]:
        """Get Firefox profile data including bookmarks, history, etc."""
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
        """Migrate Firefox profile data from source to target."""
        try:
            # Create target directory if it doesn't exist
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy essential files
            essential_files = [
                'places.sqlite',  # Bookmarks and history
                'cookies.sqlite',  # Cookies
                'key4.db',  # Passwords
                'logins.json',  # Additional login data
                'cert9.db',  # Certificates
                'permissions.sqlite',  # Site permissions
                'prefs.js',  # Preferences
                'extensions',  # Extensions directory
                'sessionstore.jsonlz4'  # Session data
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
            logger.error(f"Error migrating Firefox profile: {e}")
            return False
    
    def _get_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks from places.sqlite."""
        bookmarks = []
        places_file = profile_path / 'places.sqlite'
        
        if not places_file.exists():
            return bookmarks
        
        try:
            conn = sqlite3.connect(places_file)
            cursor = conn.cursor()
            
            # Get bookmarks from moz_bookmarks table
            cursor.execute("""
                SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified
                FROM moz_bookmarks b
                JOIN moz_places p ON b.fk = p.id
                WHERE b.type = 1
            """)
            
            for row in cursor.fetchall():
                bookmarks.append({
                    'id': row[0],
                    'title': row[1],
                    'url': row[2],
                    'date_added': datetime.fromtimestamp(row[3] / 1000000).isoformat(),
                    'last_modified': datetime.fromtimestamp(row[4] / 1000000).isoformat()
                })
            
            conn.close()
        except Exception as e:
            logger.error(f"Error reading bookmarks: {e}")
        
        return bookmarks
    
    def _get_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history from places.sqlite."""
        history = []
        places_file = profile_path / 'places.sqlite'
        
        if not places_file.exists():
            return history
        
        try:
            conn = sqlite3.connect(places_file)
            cursor = conn.cursor()
            
            # Get history from moz_places and moz_historyvisits tables
            cursor.execute("""
                SELECT p.url, p.title, h.visit_date, h.visit_type
                FROM moz_places p
                JOIN moz_historyvisits h ON p.id = h.place_id
                ORDER BY h.visit_date DESC
            """)
            
            for row in cursor.fetchall():
                history.append({
                    'url': row[0],
                    'title': row[1],
                    'visit_date': datetime.fromtimestamp(row[2] / 1000000).isoformat(),
                    'visit_type': row[3]
                })
            
            conn.close()
        except Exception as e:
            logger.error(f"Error reading history: {e}")
        
        return history
    
    def _get_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies from cookies.sqlite."""
        cookies = []
        cookies_file = profile_path / 'cookies.sqlite'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            conn = sqlite3.connect(cookies_file)
            cursor = conn.cursor()
            
            # Get cookies from moz_cookies table
            cursor.execute("""
                SELECT host, name, value, path, expiry, lastAccessed, creationTime
                FROM moz_cookies
            """)
            
            for row in cursor.fetchall():
                cookies.append({
                    'host': row[0],
                    'name': row[1],
                    'value': row[2],
                    'path': row[3],
                    'expiry': datetime.fromtimestamp(row[4]).isoformat(),
                    'last_accessed': datetime.fromtimestamp(row[5] / 1000000).isoformat(),
                    'creation_time': datetime.fromtimestamp(row[6] / 1000000).isoformat()
                })
            
            conn.close()
        except Exception as e:
            logger.error(f"Error reading cookies: {e}")
        
        return cookies
    
    def _get_passwords(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract passwords from logins.json."""
        passwords = []
        logins_file = profile_path / 'logins.json'
        
        if not logins_file.exists():
            return passwords
        
        try:
            with open(logins_file, 'r', encoding='utf-8') as f:
                logins_data = json.load(f)
                
                for login in logins_data.get('logins', []):
                    passwords.append({
                        'hostname': login.get('hostname'),
                        'encrypted_username': login.get('encryptedUsername'),
                        'encrypted_password': login.get('encryptedPassword'),
                        'form_submit_url': login.get('formSubmitURL'),
                        'http_realm': login.get('httpRealm'),
                        'guid': login.get('guid')
                    })
        except Exception as e:
            logger.error(f"Error reading passwords: {e}")
        
        return passwords
    
    def _get_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed extensions."""
        extensions = []
        extensions_dir = profile_path / 'extensions'
        
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
        """Extract user preferences from prefs.js."""
        preferences = {}
        prefs_file = profile_path / 'prefs.js'
        
        if not prefs_file.exists():
            return preferences
        
        try:
            with open(prefs_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('user_pref('):
                        # Parse preference line
                        line = line.strip()
                        if line.endswith(');'):
                            line = line[:-2]
                        if line.startswith('user_pref("'):
                            line = line[10:]
                        
                        # Split into key and value
                        parts = line.split('", ', 1)
                        if len(parts) == 2:
                            key = parts[0].strip('"')
                            value = parts[1].strip()
                            
                            # Convert string values to appropriate types
                            if value.lower() == 'true':
                                value = True
                            elif value.lower() == 'false':
                                value = False
                            elif value.isdigit():
                                value = int(value)
                            elif value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            
                            preferences[key] = value
        except Exception as e:
            logger.error(f"Error reading preferences: {e}")
        
        return preferences 