"""
Floorper - Firefox Profile Handling Module

This module provides specialized functionality for handling Firefox and Firefox-based
browser profiles, including Floorp, Waterfox, LibreWolf, and other derivatives.
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
logger = logging.getLogger('floorper.browsers.firefox_based')

class FirefoxBasedHandler:
    """Handler for Firefox-based browsers."""
    
    def __init__(self, browser_name: str = "firefox"):
        """
        Initialize the Firefox-based browser handler.
        
        Args:
            browser_name: Name of the browser (firefox, floorp, waterfox, etc.)
        """
        self.name = browser_name
        self.profiles_dir = None
        self.version = ""
        self._detect_profiles_dir()
    
    def _detect_profiles_dir(self) -> None:
        """Detect the profiles directory for the browser."""
        system = platform.system()
        home_dir = Path.home()
        
        # Define possible profile directories based on OS and browser
        possible_dirs = []
        
        if system == "Windows":
            appdata = Path(os.environ.get("APPDATA", ""))
            localappdata = Path(os.environ.get("LOCALAPPDATA", ""))
            
            if self.name == "firefox":
                possible_dirs = [
                    appdata / "Mozilla" / "Firefox" / "Profiles",
                    localappdata / "Mozilla" / "Firefox" / "Profiles"
                ]
            elif self.name == "floorp":
                possible_dirs = [
                    appdata / "Floorp" / "Profiles",
                    localappdata / "Floorp" / "Profiles"
                ]
            elif self.name == "waterfox":
                possible_dirs = [
                    appdata / "Waterfox" / "Profiles",
                    localappdata / "Waterfox" / "Profiles"
                ]
            elif self.name == "librewolf":
                possible_dirs = [
                    appdata / "LibreWolf" / "Profiles",
                    localappdata / "LibreWolf" / "Profiles"
                ]
            elif self.name == "pale_moon":
                possible_dirs = [
                    appdata / "Moonchild Productions" / "Pale Moon" / "Profiles",
                    localappdata / "Moonchild Productions" / "Pale Moon" / "Profiles"
                ]
            elif self.name == "basilisk":
                possible_dirs = [
                    appdata / "Moonchild Productions" / "Basilisk" / "Profiles",
                    localappdata / "Moonchild Productions" / "Basilisk" / "Profiles"
                ]
        elif system == "Darwin":  # macOS
            if self.name == "firefox":
                possible_dirs = [
                    home_dir / "Library" / "Application Support" / "Firefox" / "Profiles"
                ]
            elif self.name == "floorp":
                possible_dirs = [
                    home_dir / "Library" / "Application Support" / "Floorp" / "Profiles"
                ]
            elif self.name == "waterfox":
                possible_dirs = [
                    home_dir / "Library" / "Application Support" / "Waterfox" / "Profiles"
                ]
            elif self.name == "librewolf":
                possible_dirs = [
                    home_dir / "Library" / "Application Support" / "LibreWolf" / "Profiles"
                ]
            elif self.name == "pale_moon":
                possible_dirs = [
                    home_dir / "Library" / "Application Support" / "Pale Moon" / "Profiles"
                ]
            elif self.name == "basilisk":
                possible_dirs = [
                    home_dir / "Library" / "Application Support" / "Basilisk" / "Profiles"
                ]
        else:  # Linux and others
            if self.name == "firefox":
                possible_dirs = [
                    home_dir / ".mozilla" / "firefox",
                    home_dir / ".firefox"
                ]
            elif self.name == "floorp":
                possible_dirs = [
                    home_dir / ".floorp",
                    home_dir / ".mozilla" / "floorp"
                ]
            elif self.name == "waterfox":
                possible_dirs = [
                    home_dir / ".waterfox",
                    home_dir / ".mozilla" / "waterfox"
                ]
            elif self.name == "librewolf":
                possible_dirs = [
                    home_dir / ".librewolf",
                    home_dir / ".mozilla" / "librewolf"
                ]
            elif self.name == "pale_moon":
                possible_dirs = [
                    home_dir / ".moonchild productions" / "pale moon",
                    home_dir / ".palemoon"
                ]
            elif self.name == "basilisk":
                possible_dirs = [
                    home_dir / ".moonchild productions" / "basilisk",
                    home_dir / ".basilisk"
                ]
        
        # Check if any of the possible directories exist
        for dir_path in possible_dirs:
            if dir_path.exists() and dir_path.is_dir():
                self.profiles_dir = dir_path
                logger.debug(f"Found profiles directory for {self.name}: {dir_path}")
                break
    
    def detect_browser(self) -> bool:
        """
        Detect if the browser is installed.
        
        Returns:
            True if the browser is installed, False otherwise
        """
        return self.profiles_dir is not None
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """
        Get list of available profiles.
        
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
    
    def migrate_profile(self, source_path: Path, target_path: Path) -> bool:
        """
        Migrate profile data from source to target.
        
        Args:
            source_path: Path to source profile
            target_path: Path to target profile
            
        Returns:
            True if migration was successful, False otherwise
        """
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
            logger.error(f"Error migrating profile: {e}")
            return False
    
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
