"""
Retro browser handler.
This module provides handlers for historical browsers like Netscape Navigator, Mosaic, etc.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import logging
from datetime import datetime
import os
import configparser
import html
import re
import base64
import binascii

from . import BrowserHandler
from ..core.constants import RETRO_BROWSERS, RETRO_PROFILES

logger = logging.getLogger(__name__)

class RetroBrowserHandler(BrowserHandler):
    """Handler for retro browsers."""
    
    def __init__(self, browser_name: str = "netscape"):
        super().__init__()
        self.name = browser_name
        self.profiles_dir = None
        self.version = ""
        self.config = {}
    
    def detect_browser(self) -> bool:
        """Detect if a retro browser is installed."""
        for browser in RETRO_BROWSERS:
            if self.name.lower() in browser.lower():
                # Check for profiles directory
                for profile_dir in RETRO_PROFILES:
                    if profile_dir.exists():
                        self.profiles_dir = profile_dir
                        return True
        return False
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """Get list of available retro browser profiles."""
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
        """Get the path to a specific retro browser profile."""
        if not self.profiles_dir:
            return None
        
        profile_path = self.profiles_dir / profile_name
        return profile_path if profile_path.exists() else None
    
    def get_profile_data(self, profile_path: Path) -> Dict[str, Any]:
        """Get retro browser profile data including bookmarks, history, etc."""
        if not profile_path.exists():
            return {}
        
        data = {
            'bookmarks': self._get_bookmarks(profile_path),
            'history': self._get_history(profile_path),
            'cookies': self._get_cookies(profile_path),
            'extensions': self._get_extensions(profile_path),
            'preferences': self._get_preferences(profile_path)
        }
        return data
    
    def migrate_profile(self, source_path: Path, target_path: Path) -> bool:
        """Migrate retro browser profile data from source to target."""
        try:
            # Create target directory if it doesn't exist
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy essential files based on browser type
            if self.name.lower() == 'netscape':
                essential_files = [
                    'bookmark.htm',  # Bookmarks
                    'history.dat',  # History
                    'cookies.txt',  # Cookies
                    'prefs.js',  # Preferences
                    'plugins',  # Plugins directory
                    'cert7.db',  # Certificates
                    'key3.db'  # Key database
                ]
            elif self.name.lower() == 'mosaic':
                essential_files = [
                    'bookmarks.html',  # Bookmarks
                    'history',  # History
                    'cookies',  # Cookies
                    'mosaic.ini',  # Configuration
                    'plugins'  # Plugins directory
                ]
            else:
                essential_files = []  # Unknown browser type
            
            for file in essential_files:
                src_file = source_path / file
                if src_file.exists():
                    if src_file.is_dir():
                        shutil.copytree(src_file, target_path / file, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_file, target_path / file)
            
            return True
        except Exception as e:
            logger.error(f"Error migrating retro browser profile: {e}")
            return False
    
    def _get_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks based on browser type."""
        bookmarks = []
        
        try:
            if self.name.lower() == 'netscape':
                bookmarks = self._get_netscape_bookmarks(profile_path)
            elif self.name.lower() == 'mosaic':
                bookmarks = self._get_mosaic_bookmarks(profile_path)
        except Exception as e:
            logger.error(f"Error reading bookmarks: {e}")
        
        return bookmarks
    
    def _get_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history based on browser type."""
        history = []
        
        try:
            if self.name.lower() == 'netscape':
                history = self._get_netscape_history(profile_path)
            elif self.name.lower() == 'mosaic':
                history = self._get_mosaic_history(profile_path)
        except Exception as e:
            logger.error(f"Error reading history: {e}")
        
        return history
    
    def _get_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies based on browser type."""
        cookies = []
        
        try:
            if self.name.lower() == 'netscape':
                cookies = self._get_netscape_cookies(profile_path)
            elif self.name.lower() == 'mosaic':
                cookies = self._get_mosaic_cookies(profile_path)
        except Exception as e:
            logger.error(f"Error reading cookies: {e}")
        
        return cookies
    
    def _get_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed extensions based on browser type."""
        extensions = []
        
        try:
            if self.name.lower() == 'netscape':
                extensions = self._get_netscape_extensions(profile_path)
            elif self.name.lower() == 'mosaic':
                extensions = self._get_mosaic_extensions(profile_path)
        except Exception as e:
            logger.error(f"Error reading extensions: {e}")
        
        return extensions
    
    def _get_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract preferences based on browser type."""
        preferences = {}
        
        try:
            if self.name.lower() == 'netscape':
                preferences = self._get_netscape_preferences(profile_path)
            elif self.name.lower() == 'mosaic':
                preferences = self._get_mosaic_preferences(profile_path)
        except Exception as e:
            logger.error(f"Error reading preferences: {e}")
        
        return preferences
    
    # Netscape-specific methods
    def _get_netscape_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks from Netscape Navigator."""
        bookmarks = []
        bookmarks_file = profile_path / 'bookmark.htm'
        
        if not bookmarks_file.exists():
            return bookmarks
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse Netscape bookmarks format
                bookmark_pattern = r'<A HREF="([^"]+)">([^<]+)</A>'
                for match in re.finditer(bookmark_pattern, content):
                    bookmarks.append({
                        'url': html.unescape(match.group(1)),
                        'title': html.unescape(match.group(2))
                    })
        except Exception as e:
            logger.error(f"Error reading Netscape bookmarks: {e}")
        
        return bookmarks
    
    def _get_netscape_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history from Netscape Navigator."""
        history = []
        history_file = profile_path / 'history.dat'
        
        if not history_file.exists():
            return history
        
        try:
            with open(history_file, 'rb') as f:
                while True:
                    # Read record header
                    header = f.read(4)
                    if not header:
                        break
                    
                    # Parse record
                    record_size = int.from_bytes(header, 'big')
                    record_data = f.read(record_size)
                    
                    # Extract URL and timestamp
                    url_end = record_data.find(b'\x00')
                    if url_end != -1:
                        url = record_data[:url_end].decode('utf-8')
                        timestamp = int.from_bytes(record_data[url_end + 1:url_end + 5], 'big')
                        
                        history.append({
                            'url': url,
                            'timestamp': datetime.fromtimestamp(timestamp).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading Netscape history: {e}")
        
        return history
    
    def _get_netscape_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies from Netscape Navigator."""
        cookies = []
        cookies_file = profile_path / 'cookies.txt'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        # Netscape cookie format: domain\tTRUE\tpath\tsecure\texpiry\tname\tvalue
                        parts = line.strip().split('\t')
                        if len(parts) >= 7:
                            cookies.append({
                                'domain': parts[0],
                                'path': parts[2],
                                'secure': parts[3] == 'TRUE',
                                'expiry': datetime.fromtimestamp(int(parts[4])).isoformat(),
                                'name': parts[5],
                                'value': parts[6]
                            })
        except Exception as e:
            logger.error(f"Error reading Netscape cookies: {e}")
        
        return cookies
    
    def _get_netscape_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed Netscape extensions."""
        extensions = []
        plugins_dir = profile_path / 'plugins'
        
        if not plugins_dir.exists():
            return extensions
        
        try:
            for ext_file in plugins_dir.glob('*.dll'):
                extensions.append({
                    'name': ext_file.stem,
                    'path': str(ext_file),
                    'type': 'plugin'
                })
        except Exception as e:
            logger.error(f"Error reading Netscape extensions: {e}")
        
        return extensions
    
    def _get_netscape_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract preferences from Netscape Navigator."""
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
            logger.error(f"Error reading Netscape preferences: {e}")
        
        return preferences
    
    # Mosaic-specific methods
    def _get_mosaic_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks from Mosaic."""
        bookmarks = []
        bookmarks_file = profile_path / 'bookmarks.html'
        
        if not bookmarks_file.exists():
            return bookmarks
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse Mosaic bookmarks format
                bookmark_pattern = r'<A HREF="([^"]+)">([^<]+)</A>'
                for match in re.finditer(bookmark_pattern, content):
                    bookmarks.append({
                        'url': html.unescape(match.group(1)),
                        'title': html.unescape(match.group(2))
                    })
        except Exception as e:
            logger.error(f"Error reading Mosaic bookmarks: {e}")
        
        return bookmarks
    
    def _get_mosaic_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history from Mosaic."""
        history = []
        history_file = profile_path / 'history'
        
        if not history_file.exists():
            return history
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        # Mosaic history format: URL|Title|Timestamp
                        url, title, timestamp = line.strip().split('|')
                        history.append({
                            'url': url,
                            'title': title,
                            'timestamp': datetime.fromtimestamp(int(timestamp)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading Mosaic history: {e}")
        
        return history
    
    def _get_mosaic_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies from Mosaic."""
        cookies = []
        cookies_file = profile_path / 'cookies'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        # Mosaic cookie format: Domain|Name|Value|Path|Expiry
                        domain, name, value, path, expiry = line.strip().split('|')
                        cookies.append({
                            'domain': domain,
                            'name': name,
                            'value': value,
                            'path': path,
                            'expiry': datetime.fromtimestamp(int(expiry)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading Mosaic cookies: {e}")
        
        return cookies
    
    def _get_mosaic_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed Mosaic extensions."""
        extensions = []
        plugins_dir = profile_path / 'plugins'
        
        if not plugins_dir.exists():
            return extensions
        
        try:
            for ext_file in plugins_dir.glob('*.dll'):
                extensions.append({
                    'name': ext_file.stem,
                    'path': str(ext_file),
                    'type': 'plugin'
                })
        except Exception as e:
            logger.error(f"Error reading Mosaic extensions: {e}")
        
        return extensions
    
    def _get_mosaic_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract preferences from Mosaic."""
        preferences = {}
        config_file = profile_path / 'mosaic.ini'
        
        if not config_file.exists():
            return preferences
        
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            
            for section in config.sections():
                preferences[section] = dict(config.items(section))
        except Exception as e:
            logger.error(f"Error reading Mosaic preferences: {e}")
        
        return preferences 