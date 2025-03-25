"""
Exotic browser handler.
This module provides handlers for less common browsers like qutebrowser, Dillo, NetSurf, etc.
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

from . import BrowserHandler
from ..core.constants import EXOTIC_BROWSERS, EXOTIC_PROFILES

logger = logging.getLogger(__name__)

class ExoticBrowserHandler(BrowserHandler):
    """Handler for exotic browsers."""
    
    def __init__(self, browser_name: str = "qutebrowser"):
        super().__init__()
        self.name = browser_name
        self.profiles_dir = None
        self.version = ""
        self.config = {}
    
    def detect_browser(self) -> bool:
        """Detect if an exotic browser is installed."""
        for browser in EXOTIC_BROWSERS:
            if self.name.lower() in browser.lower():
                # Check for profiles directory
                for profile_dir in EXOTIC_PROFILES:
                    if profile_dir.exists():
                        self.profiles_dir = profile_dir
                        return True
        return False
    
    def get_profiles(self) -> List[Dict[str, Any]]:
        """Get list of available exotic browser profiles."""
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
        """Get the path to a specific exotic browser profile."""
        if not self.profiles_dir:
            return None
        
        profile_path = self.profiles_dir / profile_name
        return profile_path if profile_path.exists() else None
    
    def get_profile_data(self, profile_path: Path) -> Dict[str, Any]:
        """Get exotic browser profile data including bookmarks, history, etc."""
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
        """Migrate exotic browser profile data from source to target."""
        try:
            # Create target directory if it doesn't exist
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy essential files based on browser type
            if self.name.lower() == 'qutebrowser':
                essential_files = [
                    'bookmarks/urls',  # Bookmarks
                    'history',  # History
                    'cookies',  # Cookies
                    'config.py',  # Configuration
                    'quickmarks',  # Quickmarks
                    'greasemonkey',  # User scripts
                    'userscripts'  # User scripts
                ]
            elif self.name.lower() == 'dillo':
                essential_files = [
                    'bookmarks.html',  # Bookmarks
                    'history',  # History
                    'cookies',  # Cookies
                    'dillorc'  # Configuration
                ]
            elif self.name.lower() == 'netsurf':
                essential_files = [
                    'bookmarks',  # Bookmarks
                    'history',  # History
                    'cookies',  # Cookies
                    'Choices'  # Configuration
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
            logger.error(f"Error migrating exotic browser profile: {e}")
            return False
    
    def _get_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks based on browser type."""
        bookmarks = []
        
        try:
            if self.name.lower() == 'qutebrowser':
                bookmarks = self._get_qutebrowser_bookmarks(profile_path)
            elif self.name.lower() == 'dillo':
                bookmarks = self._get_dillo_bookmarks(profile_path)
            elif self.name.lower() == 'netsurf':
                bookmarks = self._get_netsurf_bookmarks(profile_path)
        except Exception as e:
            logger.error(f"Error reading bookmarks: {e}")
        
        return bookmarks
    
    def _get_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history based on browser type."""
        history = []
        
        try:
            if self.name.lower() == 'qutebrowser':
                history = self._get_qutebrowser_history(profile_path)
            elif self.name.lower() == 'dillo':
                history = self._get_dillo_history(profile_path)
            elif self.name.lower() == 'netsurf':
                history = self._get_netsurf_history(profile_path)
        except Exception as e:
            logger.error(f"Error reading history: {e}")
        
        return history
    
    def _get_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies based on browser type."""
        cookies = []
        
        try:
            if self.name.lower() == 'qutebrowser':
                cookies = self._get_qutebrowser_cookies(profile_path)
            elif self.name.lower() == 'dillo':
                cookies = self._get_dillo_cookies(profile_path)
            elif self.name.lower() == 'netsurf':
                cookies = self._get_netsurf_cookies(profile_path)
        except Exception as e:
            logger.error(f"Error reading cookies: {e}")
        
        return cookies
    
    def _get_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed extensions based on browser type."""
        extensions = []
        
        try:
            if self.name.lower() == 'qutebrowser':
                extensions = self._get_qutebrowser_extensions(profile_path)
            elif self.name.lower() == 'dillo':
                extensions = self._get_dillo_extensions(profile_path)
            elif self.name.lower() == 'netsurf':
                extensions = self._get_netsurf_extensions(profile_path)
        except Exception as e:
            logger.error(f"Error reading extensions: {e}")
        
        return extensions
    
    def _get_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract preferences based on browser type."""
        preferences = {}
        
        try:
            if self.name.lower() == 'qutebrowser':
                preferences = self._get_qutebrowser_preferences(profile_path)
            elif self.name.lower() == 'dillo':
                preferences = self._get_dillo_preferences(profile_path)
            elif self.name.lower() == 'netsurf':
                preferences = self._get_netsurf_preferences(profile_path)
        except Exception as e:
            logger.error(f"Error reading preferences: {e}")
        
        return preferences
    
    # Qutebrowser-specific methods
    def _get_qutebrowser_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks from qutebrowser."""
        bookmarks = []
        bookmarks_file = profile_path / 'bookmarks' / 'urls'
        
        if not bookmarks_file.exists():
            return bookmarks
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        url, title = line.strip().split(' ', 1)
                        bookmarks.append({
                            'url': url,
                            'title': title
                        })
        except Exception as e:
            logger.error(f"Error reading qutebrowser bookmarks: {e}")
        
        return bookmarks
    
    def _get_qutebrowser_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history from qutebrowser."""
        history = []
        history_file = profile_path / 'history'
        
        if not history_file.exists():
            return history
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        url, title, timestamp = line.strip().split(' ', 2)
                        history.append({
                            'url': url,
                            'title': title,
                            'timestamp': datetime.fromtimestamp(int(timestamp)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading qutebrowser history: {e}")
        
        return history
    
    def _get_qutebrowser_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies from qutebrowser."""
        cookies = []
        cookies_file = profile_path / 'cookies'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        domain, name, value, path, expiry = line.strip().split(' ', 4)
                        cookies.append({
                            'domain': domain,
                            'name': name,
                            'value': value,
                            'path': path,
                            'expiry': datetime.fromtimestamp(int(expiry)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading qutebrowser cookies: {e}")
        
        return cookies
    
    def _get_qutebrowser_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed qutebrowser extensions."""
        extensions = []
        extensions_dir = profile_path / 'userscripts'
        
        if not extensions_dir.exists():
            return extensions
        
        try:
            for ext_file in extensions_dir.glob('*.js'):
                with open(ext_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract metadata from userscript header
                    name_match = re.search(r'@name\s+(.+)', content)
                    version_match = re.search(r'@version\s+(.+)', content)
                    description_match = re.search(r'@description\s+(.+)', content)
                    
                    extensions.append({
                        'name': name_match.group(1) if name_match else ext_file.stem,
                        'version': version_match.group(1) if version_match else '1.0',
                        'description': description_match.group(1) if description_match else '',
                        'path': str(ext_file)
                    })
        except Exception as e:
            logger.error(f"Error reading qutebrowser extensions: {e}")
        
        return extensions
    
    def _get_qutebrowser_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract preferences from qutebrowser."""
        preferences = {}
        config_file = profile_path / 'config.py'
        
        if not config_file.exists():
            return preferences
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract settings from config.py
                settings_match = re.search(r'config\.set\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)', content)
                if settings_match:
                    preferences[settings_match.group(1)] = settings_match.group(2)
        except Exception as e:
            logger.error(f"Error reading qutebrowser preferences: {e}")
        
        return preferences
    
    # Dillo-specific methods
    def _get_dillo_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks from Dillo."""
        bookmarks = []
        bookmarks_file = profile_path / 'bookmarks.html'
        
        if not bookmarks_file.exists():
            return bookmarks
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse HTML bookmarks
                bookmark_pattern = r'<A HREF="([^"]+)">([^<]+)</A>'
                for match in re.finditer(bookmark_pattern, content):
                    bookmarks.append({
                        'url': html.unescape(match.group(1)),
                        'title': html.unescape(match.group(2))
                    })
        except Exception as e:
            logger.error(f"Error reading Dillo bookmarks: {e}")
        
        return bookmarks
    
    def _get_dillo_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history from Dillo."""
        history = []
        history_file = profile_path / 'history'
        
        if not history_file.exists():
            return history
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        url, title, timestamp = line.strip().split('|')
                        history.append({
                            'url': url,
                            'title': title,
                            'timestamp': datetime.fromtimestamp(int(timestamp)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading Dillo history: {e}")
        
        return history
    
    def _get_dillo_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies from Dillo."""
        cookies = []
        cookies_file = profile_path / 'cookies'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        domain, name, value, path, expiry = line.strip().split('|')
                        cookies.append({
                            'domain': domain,
                            'name': name,
                            'value': value,
                            'path': path,
                            'expiry': datetime.fromtimestamp(int(expiry)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading Dillo cookies: {e}")
        
        return cookies
    
    def _get_dillo_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed Dillo extensions."""
        extensions = []
        extensions_dir = profile_path / 'plugins'
        
        if not extensions_dir.exists():
            return extensions
        
        try:
            for ext_file in extensions_dir.glob('*.so'):
                extensions.append({
                    'name': ext_file.stem,
                    'path': str(ext_file),
                    'type': 'plugin'
                })
        except Exception as e:
            logger.error(f"Error reading Dillo extensions: {e}")
        
        return extensions
    
    def _get_dillo_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract preferences from Dillo."""
        preferences = {}
        config_file = profile_path / 'dillorc'
        
        if not config_file.exists():
            return preferences
        
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            
            for section in config.sections():
                preferences[section] = dict(config.items(section))
        except Exception as e:
            logger.error(f"Error reading Dillo preferences: {e}")
        
        return preferences
    
    # NetSurf-specific methods
    def _get_netsurf_bookmarks(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract bookmarks from NetSurf."""
        bookmarks = []
        bookmarks_file = profile_path / 'bookmarks'
        
        if not bookmarks_file.exists():
            return bookmarks
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        url, title = line.strip().split(' ', 1)
                        bookmarks.append({
                            'url': url,
                            'title': title
                        })
        except Exception as e:
            logger.error(f"Error reading NetSurf bookmarks: {e}")
        
        return bookmarks
    
    def _get_netsurf_history(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract history from NetSurf."""
        history = []
        history_file = profile_path / 'history'
        
        if not history_file.exists():
            return history
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        url, title, timestamp = line.strip().split(' ', 2)
                        history.append({
                            'url': url,
                            'title': title,
                            'timestamp': datetime.fromtimestamp(int(timestamp)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading NetSurf history: {e}")
        
        return history
    
    def _get_netsurf_cookies(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Extract cookies from NetSurf."""
        cookies = []
        cookies_file = profile_path / 'cookies'
        
        if not cookies_file.exists():
            return cookies
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        domain, name, value, path, expiry = line.strip().split(' ', 4)
                        cookies.append({
                            'domain': domain,
                            'name': name,
                            'value': value,
                            'path': path,
                            'expiry': datetime.fromtimestamp(int(expiry)).isoformat()
                        })
        except Exception as e:
            logger.error(f"Error reading NetSurf cookies: {e}")
        
        return cookies
    
    def _get_netsurf_extensions(self, profile_path: Path) -> List[Dict[str, Any]]:
        """Get list of installed NetSurf extensions."""
        extensions = []
        extensions_dir = profile_path / 'plugins'
        
        if not extensions_dir.exists():
            return extensions
        
        try:
            for ext_file in extensions_dir.glob('*.so'):
                extensions.append({
                    'name': ext_file.stem,
                    'path': str(ext_file),
                    'type': 'plugin'
                })
        except Exception as e:
            logger.error(f"Error reading NetSurf extensions: {e}")
        
        return extensions
    
    def _get_netsurf_preferences(self, profile_path: Path) -> Dict[str, Any]:
        """Extract preferences from NetSurf."""
        preferences = {}
        choices_file = profile_path / 'Choices'
        
        if not choices_file.exists():
            return preferences
        
        try:
            with open(choices_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        preferences[key] = value
        except Exception as e:
            logger.error(f"Error reading NetSurf preferences: {e}")
        
        return preferences 