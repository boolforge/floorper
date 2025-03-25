"""
Firefox Handler Module

This module provides specialized functionality for handling Firefox browser profiles.
"""

import os
import sys
import platform
import logging
import json
import sqlite3
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Setup logging
logger = logging.getLogger('floorper.browsers.handlers.firefox_handler')

class FirefoxHandler:
    """Handler for Firefox browser."""
    
    def __init__(self):
        """Initialize the Firefox browser handler."""
        self.name = "firefox"
        self.profiles_dir = None
        self.version = ""
        self._detect_profiles_dir()
        self._detect_version()
    
    def _detect_profiles_dir(self) -> None:
        """Detect the profiles directory for Firefox."""
        system = platform.system()
        home_dir = Path.home()
        
        if system == "Windows":
            appdata = Path(os.environ.get("APPDATA", ""))
            possible_dirs = [
                appdata / "Mozilla" / "Firefox" / "Profiles"
            ]
        elif system == "Darwin":  # macOS
            possible_dirs = [
                home_dir / "Library" / "Application Support" / "Firefox" / "Profiles"
            ]
        else:  # Linux and others
            possible_dirs = [
                home_dir / ".mozilla" / "firefox",
                home_dir / ".firefox"
            ]
        
        # Check if any of the possible directories exist
        for dir_path in possible_dirs:
            if dir_path.exists() and dir_path.is_dir():
                self.profiles_dir = dir_path
                logger.debug(f"Found Firefox profiles directory: {dir_path}")
                break
    
    def _detect_version(self) -> None:
        """Detect the Firefox version."""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Try to get version from registry
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Mozilla\Mozilla Firefox") as key:
                    self.version = winreg.QueryValueEx(key, "CurrentVersion")[0]
            elif system == "Darwin":  # macOS
                # Try to get version from plist
                import plistlib
                plist_path = Path("/Applications/Firefox.app/Contents/Info.plist")
                if plist_path.exists():
                    with open(plist_path, 'rb') as f:
                        plist = plistlib.load(f)
                        self.version = plist.get("CFBundleShortVersionString", "")
            else:  # Linux and others
                # Try to get version from command line
                import subprocess
                result = subprocess.run(
                    ["firefox", "--version"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    version_str = result.stdout.strip()
                    # Extract version number from string like "Mozilla Firefox 98.0.2"
                    parts = version_str.split()
                    if len(parts) >= 3:
                        self.version = parts[2]
        except Exception as e:
            logger.error(f"Error detecting Firefox version: {e}")
    
    def detect_browser(self) -> bool:
        """
        Detect if Firefox is installed.
        
        Returns:
            True if Firefox is installed, False otherwise
        """
        return self.profiles_dir is not None
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """
        Get list of available Firefox profiles.
        
        Returns:
            List of profiles with their information
        """
        if not self.profiles_dir:
            return []
        
        profiles = []
        
        # Try to read profiles.ini if it exists
        profiles_ini = self.profiles_dir.parent / "profiles.ini"
        if profiles_ini.exists():
            try:
                profiles = self._parse_profiles_ini(profiles_ini)
                if profiles:
                    return profiles
            except Exception as e:
                logger.error(f"Error parsing profiles.ini: {e}")
        
        # Fallback: scan directories
        for profile_dir in self.profiles_dir.iterdir():
            if profile_dir.is_dir() and not profile_dir.name.startswith('.'):
                profile_data = self._get_profile_info(profile_dir)
                profiles.append({
                    'name': profile_dir.name,
                    'path': str(profile_dir),
                    'data': profile_data
                })
        
        return profiles
    
    def _parse_profiles_ini(self, profiles_ini: Path) -> List[Dict[str, Any]]:
        """
        Parse profiles.ini file to get profile information.
        
        Args:
            profiles_ini: Path to profiles.ini file
            
        Returns:
            List of profiles with their information
        """
        profiles = []
        current_profile = {}
        current_section = ""
        
        with open(profiles_ini, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith(';') or line.startswith('#'):
                    continue
                
                # Section header
                if line.startswith('[') and line.endswith(']'):
                    # Save previous profile if it exists
                    if current_section.startswith('Profile') and current_profile:
                        if 'Path' in current_profile:
                            # Determine profile path
                            if current_profile.get('IsRelative', '1') == '1':
                                profile_path = self.profiles_dir.parent / current_profile['Path']
                            else:
                                profile_path = Path(current_profile['Path'])
                            
                            # Add profile to list
                            if profile_path.exists():
                                profile_data = self._get_profile_info(profile_path)
                                profiles.append({
                                    'name': current_profile.get('Name', profile_path.name),
                                    'path': str(profile_path),
                                    'data': profile_data
                                })
                    
                    # Start new profile
                    current_section = line[1:-1]
                    current_profile = {}
                    continue
                
                # Key-value pair
                if '=' in line:
                    key, value = line.split('=', 1)
                    current_profile[key.strip()] = value.strip()
        
        # Add last profile if it exists
        if current_section.startswith('Profile') and current_profile:
            if 'Path' in current_profile:
                # Determine profile path
                if current_profile.get('IsRelative', '1') == '1':
                    profile_path = self.profiles_dir.parent / current_profile['Path']
                else:
                    profile_path = Path(current_profile['Path'])
                
                # Add profile to list
                if profile_path.exists():
                    profile_data = self._get_profile_info(profile_path)
                    profiles.append({
                        'name': current_profile.get('Name', profile_path.name),
                        'path': str(profile_path),
                        'data': profile_data
                    })
        
        return profiles
    
    def _get_profile_info(self, profile_path: Path) -> Dict[str, Any]:
        """
        Get basic information about a profile.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dictionary with profile information
        """
        info = {
            'size': 0,
            'last_modified': None,
            'has_bookmarks': False,
            'has_history': False,
            'has_passwords': False,
            'has_cookies': False,
            'has_extensions': False
        }
        
        try:
            # Get profile size
            info['size'] = sum(f.stat().st_size for f in profile_path.glob('**/*') if f.is_file())
            
            # Get last modified time
            info['last_modified'] = profile_path.stat().st_mtime
            
            # Check for specific files
            info['has_bookmarks'] = (profile_path / 'places.sqlite').exists()
            info['has_history'] = (profile_path / 'places.sqlite').exists()
            info['has_passwords'] = (profile_path / 'logins.json').exists() or (profile_path / 'key4.db').exists()
            info['has_cookies'] = (profile_path / 'cookies.sqlite').exists()
            info['has_extensions'] = (profile_path / 'extensions').exists() and (profile_path / 'extensions').is_dir()
        except Exception as e:
            logger.error(f"Error getting profile info: {e}")
        
        return info
    
    def get_profile_data(self, profile_path: Path) -> Dict[str, Any]:
        """
        Get detailed data from a profile.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dictionary with profile data
        """
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile path does not exist: {profile_path}")
        
        data = {
            'bookmarks': self._get_bookmarks(profile_path),
            'history': self._get_history(profile_path),
            'cookies': self._get_cookies(profile_path),
            'passwords': self._get_passwords(profile_path),
            'extensions': self._get_extensions(profile_path),
            'preferences': self._get_preferences(profile_path)
        }
        
        return data
    
    def _get_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """
        Extract bookmarks from places.sqlite.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            List of bookmarks
        """
        bookmarks = []
        places_file = profile_path / 'places.sqlite'
        
        if not places_file.exists():
            return bookmarks
        
        try:
            # Create a copy of the database to avoid locking issues
            temp_db = profile_path / 'places_temp.sqlite'
            shutil.copy2(places_file, temp_db)
            
            conn = sqlite3.connect(temp_db)
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
            
            # Remove temporary database
            temp_db.unlink()
        except Exception as e:
            logger.error(f"Error reading bookmarks: {e}")
        
        return bookmarks
    
    def _get_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """
        Extract history from places.sqlite.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            List of history entries
        """
        history = []
        places_file = profile_path / 'places.sqlite'
        
        if not places_file.exists():
            return history
        
        try:
            # Create a copy of the database to avoid locking issues
            temp_db = profile_path / 'places_temp.sqlite'
            shutil.copy2(places_file, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Get history from moz_places and moz_historyvisits tables
            cursor.execute("""
                SELECT p.url, p.title, h.visit_date, h.visit_type
                FROM moz_places p
                JOIN moz_historyvisits h ON p.id = h.place_id
                ORDER BY h.visit_date DESC
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                history.append({
                    'url': row[0],
                    'title': row[1],
                    'visit_date': datetime.fromtimestamp(row[2] / 1000000).isoformat(),
                    'visit_type': row[3]
                })
            
            conn.close()
            
            # Remove temporary database
            temp_db.unlink()
        except Exception as e:
            logger.error(f"Error reading history: {e}")
        
        return history
    
    def _get_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """
        Extract cookies from cookies.sqlite.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            List of cookies
        """
        cookies = []
        cookies_file = profile_path / 'cookies.sqlite'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            # Create a copy of the database to avoid locking issues
            temp_db = profile_path / 'cookies_temp.sqlite'
            shutil.copy2(cookies_file, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Get cookies from moz_cookies table
            cursor.execute("""
                SELECT host, name, value, path, expiry, lastAccessed, creationTime
                FROM moz_cookies
                LIMIT 1000
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
            
            # Remove temporary database
            temp_db.unlink()
        except Exception as e:
            logger.error(f"Error reading cookies: {e}")
        
        return cookies
    
    def _get_passwords(self, profile_path: Path) -> List[Dict[str, Any]]:
        """
        Extract passwords from logins.json.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            List of passwords (encrypted)
        """
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
        """
        Get list of installed extensions.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            List of extensions
        """
        extensions = []
        extensions_dir = profile_path / 'extensions'
        
        if not extensions_dir.exists():
            return extensions
        
        try:
            for ext_file in extensions_dir.iterdir():
                if ext_file.is_dir():
                    # Directory-based extension
                    manifest_file = ext_file / 'manifest.json'
                    if manifest_file.exists():
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                            extensions.append({
                                'id': ext_file.name,
                                'name': manifest.get('name'),
                                'version': manifest.get('version'),
                                'description': manifest.get('description')
                            })
                elif ext_file.suffix == '.xpi':
                    # XPI-based extension
                    extensions.append({
                        'id': ext_file.stem,
                        'name': ext_file.stem,
                        'version': 'Unknown',
                        'description': 'XPI extension'
                    })
        except Exception as e:
            logger.error(f"Error reading extensions: {e}")
        
        return extensions
    
    def _get_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """
        Extract user preferences from prefs.js.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dictionary with preferences
        """
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
