#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Exotic Browser Support Module
========================================

This module provides specialized detection and migration support for exotic browsers,
including text-based browsers and those with special features.
"""

import os
import sys
import logging
import platform
import shutil
import json
import configparser
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .constants import BROWSERS, get_platform, expand_path

class ExoticBrowserHandler:
    """
    Specialized handler for exotic and text-based browsers.
    Provides detection and migration support for browsers like elinks, w3m, lynx, etc.
    """
    
    def __init__(self):
        """Initialize the exotic browser handler."""
        self.logger = logging.getLogger(__name__)
        self.platform = get_platform()
        
        # Text-based browsers
        self.text_browsers = [
            "elinks", "links", "lynx", "w3m"
        ]
        
        # Browsers with special features
        self.special_browsers = [
            "qutebrowser", "dillo", "netsurf", "konqueror", "falkon", "otter"
        ]
    
    def detect_text_browser_profiles(self, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect profiles for text-based browsers.
        
        Args:
            browser_id: ID of the text-based browser
            
        Returns:
            List of detected profiles
        """
        profiles = []
        
        if browser_id not in self.text_browsers:
            return profiles
        
        try:
            # Get browser info
            browser_info = BROWSERS.get(browser_id, {})
            
            # Check each possible profile path
            for path_template in browser_info.get("profile_paths", []):
                profile_path = expand_path(path_template)
                
                if os.path.exists(profile_path):
                    # Text browsers typically have a single profile
                    profile = {
                        "name": f"{browser_info.get('name', browser_id)} Default",
                        "path": profile_path,
                        "browser_type": browser_id,
                        "stats": self._get_text_browser_stats(browser_id, profile_path)
                    }
                    profiles.append(profile)
                    self.logger.info(f"Detected {browser_id} profile at {profile_path}")
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error detecting {browser_id} profiles: {str(e)}", exc_info=True)
            return []
    
    def _get_text_browser_stats(self, browser_id: str, profile_path: str) -> Dict[str, int]:
        """
        Get statistics for a text-based browser profile.
        
        Args:
            browser_id: ID of the text-based browser
            profile_path: Path to the profile
            
        Returns:
            Dictionary of profile statistics
        """
        stats = {
            "bookmarks": 0,
            "history": 0,
            "cookies": 0,
            "passwords": 0,
            "tabs": 0,
            "windows": 0,
            "extensions": 0,
            "certificates": 0,
            "forms": 0,
            "permissions": 0
        }
        
        try:
            # ELinks
            if browser_id == "elinks":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "bookmarks")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] = content.count("\n")
                
                # History file
                history_file = os.path.join(profile_path, "globhist")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["history"] = content.count("\n")
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "cookies")
                if os.path.exists(cookies_file):
                    with open(cookies_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["cookies"] = content.count("\n")
            
            # Links
            elif browser_id == "links":
                # Links stores history in a single file
                history_file = os.path.join(profile_path, "links.his")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["history"] = content.count("\n")
            
            # Lynx
            elif browser_id == "lynx":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "lynx_bookmarks.html")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] = content.count("<a href=")
                
                # History file
                history_file = os.path.join(profile_path, "lynx_history")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["history"] = content.count("\n")
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "lynx_cookies")
                if os.path.exists(cookies_file):
                    with open(cookies_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["cookies"] = content.count("\n")
            
            # w3m
            elif browser_id == "w3m":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "bookmark.html")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] = content.count("<a href=")
                
                # History file
                history_file = os.path.join(profile_path, "history")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["history"] = content.count("\n")
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "cookie")
                if os.path.exists(cookies_file):
                    with open(cookies_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["cookies"] = content.count("\n")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting stats for {browser_id}: {str(e)}", exc_info=True)
            return stats
    
    def detect_special_browser_profiles(self, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect profiles for browsers with special features.
        
        Args:
            browser_id: ID of the special browser
            
        Returns:
            List of detected profiles
        """
        profiles = []
        
        if browser_id not in self.special_browsers:
            return profiles
        
        try:
            # Get browser info
            browser_info = BROWSERS.get(browser_id, {})
            
            # Check each possible profile path
            for path_template in browser_info.get("profile_paths", []):
                profile_path = expand_path(path_template)
                
                if os.path.exists(profile_path):
                    # Handle different profile structures based on browser
                    if browser_id == "qutebrowser":
                        profiles.extend(self._detect_qutebrowser_profiles(profile_path, browser_id))
                    elif browser_id in ["dillo", "netsurf"]:
                        profiles.extend(self._detect_simple_browser_profiles(profile_path, browser_id, browser_info))
                    elif browser_id in ["konqueror", "falkon", "otter"]:
                        profiles.extend(self._detect_kde_browser_profiles(profile_path, browser_id, browser_info))
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error detecting {browser_id} profiles: {str(e)}", exc_info=True)
            return []
    
    def _detect_qutebrowser_profiles(self, profile_path: str, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect qutebrowser profiles.
        
        Args:
            profile_path: Path to the qutebrowser config directory
            browser_id: Browser ID
            
        Returns:
            List of detected profiles
        """
        profiles = []
        
        try:
            # qutebrowser has a single profile by default
            # Check if the config.py file exists
            config_file = os.path.join(profile_path, "config.py")
            autoconfig_file = os.path.join(profile_path, "autoconfig.yml")
            
            if os.path.exists(config_file) or os.path.exists(autoconfig_file):
                # Get browser info
                browser_info = BROWSERS.get(browser_id, {})
                
                profile = {
                    "name": f"{browser_info.get('name', browser_id)} Default",
                    "path": profile_path,
                    "browser_type": browser_id,
                    "stats": self._get_special_browser_stats(browser_id, profile_path)
                }
                profiles.append(profile)
                self.logger.info(f"Detected {browser_id} profile at {profile_path}")
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error detecting qutebrowser profiles: {str(e)}", exc_info=True)
            return []
    
    def _detect_simple_browser_profiles(self, profile_path: str, browser_id: str, browser_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect profiles for simple browsers like Dillo and NetSurf.
        
        Args:
            profile_path: Path to the browser config directory
            browser_id: Browser ID
            browser_info: Browser information dictionary
            
        Returns:
            List of detected profiles
        """
        profiles = []
        
        try:
            # Simple browsers typically have a single profile
            if os.path.exists(profile_path):
                profile = {
                    "name": f"{browser_info.get('name', browser_id)} Default",
                    "path": profile_path,
                    "browser_type": browser_id,
                    "stats": self._get_special_browser_stats(browser_id, profile_path)
                }
                profiles.append(profile)
                self.logger.info(f"Detected {browser_id} profile at {profile_path}")
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error detecting simple browser profiles: {str(e)}", exc_info=True)
            return []
    
    def _detect_kde_browser_profiles(self, profile_path: str, browser_id: str, browser_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect profiles for KDE-based browsers like Konqueror, Falkon, and Otter.
        
        Args:
            profile_path: Path to the browser config directory
            browser_id: Browser ID
            browser_info: Browser information dictionary
            
        Returns:
            List of detected profiles
        """
        profiles = []
        
        try:
            # KDE browsers may have multiple profiles
            if os.path.exists(profile_path):
                # Check for profile directories
                if browser_id == "konqueror":
                    # Konqueror typically has a single profile
                    profile = {
                        "name": f"{browser_info.get('name', browser_id)} Default",
                        "path": profile_path,
                        "browser_type": browser_id,
                        "stats": self._get_special_browser_stats(browser_id, profile_path)
                    }
                    profiles.append(profile)
                    self.logger.info(f"Detected {browser_id} profile at {profile_path}")
                
                elif browser_id == "falkon":
                    # Falkon stores profiles in profiles.ini
                    profiles_ini = os.path.join(profile_path, "profiles.ini")
                    if os.path.exists(profiles_ini):
                        config = configparser.ConfigParser()
                        config.read(profiles_ini)
                        
                        for section in config.sections():
                            if section.startswith("Profile"):
                                profile_name = config.get(section, "Name", fallback=f"Profile {section[7:]}")
                                profile_path_rel = config.get(section, "Path", fallback="")
                                
                                if profile_path_rel:
                                    full_path = os.path.join(profile_path, profile_path_rel)
                                    if os.path.exists(full_path):
                                        profile = {
                                            "name": profile_name,
                                            "path": full_path,
                                            "browser_type": browser_id,
                                            "stats": self._get_special_browser_stats(browser_id, full_path)
                                        }
                                        profiles.append(profile)
                                        self.logger.info(f"Detected {browser_id} profile: {profile_name} at {full_path}")
                    
                    # If no profiles found, check for default profile
                    if not profiles:
                        default_path = os.path.join(profile_path, "default")
                        if os.path.exists(default_path):
                            profile = {
                                "name": f"{browser_info.get('name', browser_id)} Default",
                                "path": default_path,
                                "browser_type": browser_id,
                                "stats": self._get_special_browser_stats(browser_id, default_path)
                            }
                            profiles.append(profile)
                            self.logger.info(f"Detected {browser_id} default profile at {default_path}")
                
                elif browser_id == "otter":
                    # Otter Browser stores profiles in a profiles directory
                    profiles_dir = os.path.join(profile_path, "profiles")
                    if os.path.exists(profiles_dir):
                        for item in os.listdir(profiles_dir):
                            profile_dir = os.path.join(profiles_dir, item)
                            if os.path.isdir(profile_dir):
                                # Check if it's a valid profile
                                if os.path.exists(os.path.join(profile_dir, "options.ini")):
                                    profile = {
                                        "name": item,
                                        "path": profile_dir,
                                        "browser_type": browser_id,
                                        "stats": self._get_special_browser_stats(browser_id, profile_dir)
                                    }
                                    profiles.append(profile)
                                    self.logger.info(f"Detected {browser_id} profile: {item} at {profile_dir}")
                    
                    # If no profiles found, check for default profile
                    if not profiles:
                        profile = {
                            "name": f"{browser_info.get('name', browser_id)} Default",
                            "path": profile_path,
                            "browser_type": browser_id,
                            "stats": self._get_special_browser_stats(browser_id, profile_path)
                        }
                        profiles.append(profile)
                        self.logger.info(f"Detected {browser_id} default profile at {profile_path}")
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error detecting KDE browser profiles: {str(e)}", exc_info=True)
            return []
    
    def _get_special_browser_stats(self, browser_id: str, profile_path: str) -> Dict[str, int]:
        """
        Get statistics for a browser with special features.
        
        Args:
            browser_id: ID of the special browser
            profile_path: Path to the profile
            
        Returns:
            Dictionary of profile statistics
        """
        stats = {
            "bookmarks": 0,
            "history": 0,
            "cookies": 0,
            "passwords": 0,
            "tabs": 0,
            "windows": 0,
            "extensions": 0,
            "certificates": 0,
            "forms": 0,
            "permissions": 0
        }
        
        try:
            # qutebrowser
            if browser_id == "qutebrowser":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "bookmarks", "urls")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] = content.count("\n")
                
                # History file
                history_file = os.path.join(profile_path, "history", "urls")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["history"] = content.count("\n")
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "cookies")
                if os.path.exists(cookies_file):
                    stats["cookies"] = 1  # Just indicate presence
                
                # Quickmarks file
                quickmarks_file = os.path.join(profile_path, "quickmarks")
                if os.path.exists(quickmarks_file):
                    with open(quickmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] += content.count("\n")
            
            # Dillo
            elif browser_id == "dillo":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "bm.txt")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] = content.count("\n")
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "cookies.txt")
                if os.path.exists(cookies_file):
                    with open(cookies_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["cookies"] = content.count("\n")
            
            # NetSurf
            elif browser_id == "netsurf":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "Bookmarks")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] = content.count("<bookmark")
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "Cookies")
                if os.path.exists(cookies_file):
                    stats["cookies"] = 1  # Just indicate presence
                
                # History file
                history_file = os.path.join(profile_path, "URLs")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["history"] = content.count("\n")
            
            # Konqueror
            elif browser_id == "konqueror":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "bookmarks.xml")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        stats["bookmarks"] = content.count("<bookmark")
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "cookies")
                if os.path.exists(cookies_file):
                    stats["cookies"] = 1  # Just indicate presence
                
                # History file
                history_file = os.path.join(profile_path, "history")
                if os.path.exists(history_file):
                    stats["history"] = 1  # Just indicate presence
            
            # Falkon
            elif browser_id == "falkon":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "bookmarks.json")
                if os.path.exists(bookmarks_file):
                    try:
                        with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                            data = json.load(f)
                            stats["bookmarks"] = self._count_falkon_bookmarks(data)
                    except json.JSONDecodeError:
                        pass
                
                # History database
                history_db = os.path.join(profile_path, "browsedata.db")
                if os.path.exists(history_db):
                    try:
                        conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                        cursor = conn.cursor()
                        
                        # Count history entries
                        cursor.execute("SELECT COUNT(*) FROM history")
                        stats["history"] = cursor.fetchone()[0]
                        
                        # Count cookies
                        cursor.execute("SELECT COUNT(*) FROM autofill")
                        stats["forms"] = cursor.fetchone()[0]
                        
                        conn.close()
                    except sqlite3.Error:
                        pass
            
            # Otter Browser
            elif browser_id == "otter":
                # Bookmarks file
                bookmarks_file = os.path.join(profile_path, "bookmarks.json")
                if os.path.exists(bookmarks_file):
                    try:
                        with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                stats["bookmarks"] = len(data)
                    except json.JSONDecodeError:
                        pass
                
                # History database
                history_db = os.path.join(profile_path, "browsingHistory.sqlite")
                if os.path.exists(history_db):
                    try:
                        conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                        cursor = conn.cursor()
                        
                        # Count history entries
                        cursor.execute("SELECT COUNT(*) FROM visits")
                        stats["history"] = cursor.fetchone()[0]
                        
                        conn.close()
                    except sqlite3.Error:
                        pass
                
                # Cookies file
                cookies_file = os.path.join(profile_path, "cookies.dat")
                if os.path.exists(cookies_file):
                    stats["cookies"] = 1  # Just indicate presence
                
                # Passwords file
                passwords_file = os.path.join(profile_path, "passwords.json")
                if os.path.exists(passwords_file):
                    stats["passwords"] = 1  # Just indicate presence
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting stats for {browser_id}: {str(e)}", exc_info=True)
            return stats
    
    def _count_falkon_bookmarks(self, data: Dict[str, Any]) -> int:
        """
        Count bookmarks in Falkon bookmarks data.
        
        Args:
            data: Bookmarks data
            
        Returns:
            Number of bookmarks
        """
        count = 0
        
        if not isinstance(data, dict):
            return count
        
        # Check if it's a bookmark
        if "type" in data and data["type"] == "url":
            return 1
        
        # Check if it has children
        if "children" in data and isinstance(data["children"], list):
            for child in data["children"]:
                count += self._count_falkon_bookmarks(child)
        
        return count
    
    def migrate_text_browser_data(self, source_profile: Dict[str, Any], target_path: Path) -> Tuple[bool, str]:
        """
        Migrate data from a text-based browser to the target browser.
        
        Args:
            source_profile: Source profile information
            target_path: Path to the target profile
            
        Returns:
            Tuple of success flag and message
        """
        browser_id = source_profile.get("browser_type")
        
        if browser_id not in self.text_browsers:
            return False, f"Unsupported browser type: {browser_id}"
        
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # Migrate bookmarks
            bookmarks_migrated = self._migrate_text_browser_bookmarks(browser_id, source_profile["path"], target_path)
            
            # Migrate history (if supported)
            history_migrated = self._migrate_text_browser_history(browser_id, source_profile["path"], target_path)
            
            # Return result
            if bookmarks_migrated or history_migrated:
                return True, f"Successfully migrated data from {browser_id}"
            else:
                return False, f"No data migrated from {browser_id}"
            
        except Exception as e:
            self.logger.error(f"Error migrating {browser_id} data: {str(e)}", exc_info=True)
            return False, f"Error migrating {browser_id} data: {str(e)}"
    
    def _migrate_text_browser_bookmarks(self, browser_id: str, source_path: str, target_path: Path) -> bool:
        """
        Migrate bookmarks from a text-based browser to the target browser.
        
        Args:
            browser_id: ID of the text-based browser
            source_path: Path to the source profile
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Get bookmarks from source browser
            bookmarks = []
            
            # ELinks
            if browser_id == "elinks":
                bookmarks_file = os.path.join(source_path, "bookmarks")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip() and not line.startswith("#"):
                                parts = line.strip().split(" ")
                                if len(parts) >= 2:
                                    url = parts[0]
                                    title = " ".join(parts[1:])
                                    bookmarks.append({"url": url, "title": title})
            
            # Lynx
            elif browser_id == "lynx":
                bookmarks_file = os.path.join(source_path, "lynx_bookmarks.html")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        import re
                        # Extract links from HTML
                        links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', content)
                        for url, title in links:
                            bookmarks.append({"url": url, "title": title})
            
            # w3m
            elif browser_id == "w3m":
                bookmarks_file = os.path.join(source_path, "bookmark.html")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        import re
                        # Extract links from HTML
                        links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', content)
                        for url, title in links:
                            bookmarks.append({"url": url, "title": title})
            
            # If no bookmarks found, return False
            if not bookmarks:
                return False
            
            # Determine target browser family from target path
            target_browser_family = self._detect_target_browser_family(target_path)
            
            # Convert bookmarks to target format
            if target_browser_family == "firefox":
                return self._convert_bookmarks_to_firefox(bookmarks, target_path)
            elif target_browser_family == "chrome":
                return self._convert_bookmarks_to_chrome(bookmarks, target_path)
            else:
                return False
            
        except Exception as e:
            self.logger.error(f"Error migrating {browser_id} bookmarks: {str(e)}", exc_info=True)
            return False
    
    def _migrate_text_browser_history(self, browser_id: str, source_path: str, target_path: Path) -> bool:
        """
        Migrate history from a text-based browser to the target browser.
        
        Args:
            browser_id: ID of the text-based browser
            source_path: Path to the source profile
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Get history from source browser
            history_entries = []
            
            # ELinks
            if browser_id == "elinks":
                history_file = os.path.join(source_path, "globhist")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip() and not line.startswith("#"):
                                parts = line.strip().split(" ")
                                if len(parts) >= 3:
                                    url = parts[0]
                                    title = " ".join(parts[1:-1])
                                    timestamp = parts[-1]
                                    try:
                                        timestamp = int(timestamp)
                                    except ValueError:
                                        timestamp = 0
                                    history_entries.append({
                                        "url": url,
                                        "title": title,
                                        "timestamp": timestamp
                                    })
            
            # Lynx
            elif browser_id == "lynx":
                history_file = os.path.join(source_path, "lynx_history")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip():
                                # Lynx history format is simple URLs
                                url = line.strip()
                                history_entries.append({
                                    "url": url,
                                    "title": url,
                                    "timestamp": 0  # No timestamp in Lynx history
                                })
            
            # w3m
            elif browser_id == "w3m":
                history_file = os.path.join(source_path, "history")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip():
                                # w3m history format is simple URLs
                                url = line.strip()
                                history_entries.append({
                                    "url": url,
                                    "title": url,
                                    "timestamp": 0  # No timestamp in w3m history
                                })
            
            # If no history found, return False
            if not history_entries:
                return False
            
            # Determine target browser family from target path
            target_browser_family = self._detect_target_browser_family(target_path)
            
            # Convert history to target format
            if target_browser_family == "firefox":
                return self._convert_history_to_firefox(history_entries, target_path)
            elif target_browser_family == "chrome":
                return self._convert_history_to_chrome(history_entries, target_path)
            else:
                return False
            
        except Exception as e:
            self.logger.error(f"Error migrating {browser_id} history: {str(e)}", exc_info=True)
            return False
    
    def _detect_target_browser_family(self, target_path: Path) -> str:
        """
        Detect the browser family of the target profile.
        
        Args:
            target_path: Path to the target profile
            
        Returns:
            Browser family ('firefox', 'chrome', or 'unknown')
        """
        # Check for Firefox-specific files
        if os.path.exists(os.path.join(target_path, "places.sqlite")) or \
           os.path.exists(os.path.join(target_path, "cookies.sqlite")) or \
           os.path.exists(os.path.join(target_path, "prefs.js")):
            return "firefox"
        
        # Check for Chrome-specific files
        if os.path.exists(os.path.join(target_path, "Preferences")) or \
           os.path.exists(os.path.join(target_path, "History")) or \
           os.path.exists(os.path.join(target_path, "Cookies")):
            return "chrome"
        
        # Unknown browser family
        return "unknown"
    
    def _convert_bookmarks_to_firefox(self, bookmarks: List[Dict[str, str]], target_path: Path) -> bool:
        """
        Convert bookmarks to Firefox format and add to target profile.
        
        Args:
            bookmarks: List of bookmarks (url, title)
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Firefox stores bookmarks in places.sqlite
            places_db = os.path.join(target_path, "places.sqlite")
            
            if not os.path.exists(places_db):
                self.logger.warning(f"Firefox places.sqlite not found at {places_db}")
                return False
            
            # Connect to the database
            conn = sqlite3.connect(places_db)
            cursor = conn.cursor()
            
            # Get the ID of the "Other Bookmarks" folder
            cursor.execute("""
                SELECT id FROM moz_bookmarks 
                WHERE parent = 1 AND title = 'unfiled'
            """)
            result = cursor.fetchone()
            
            if not result:
                self.logger.warning("Firefox 'Other Bookmarks' folder not found")
                conn.close()
                return False
            
            unfiled_folder_id = result[0]
            
            # Add bookmarks to the "Other Bookmarks" folder
            for bookmark in bookmarks:
                url = bookmark["url"]
                title = bookmark["title"]
                
                # Add URL to moz_places
                cursor.execute("""
                    INSERT OR IGNORE INTO moz_places (url, title, frecency)
                    VALUES (?, ?, 10)
                """, (url, title))
                
                # Get the ID of the inserted URL
                cursor.execute("SELECT id FROM moz_places WHERE url = ?", (url,))
                place_id = cursor.fetchone()[0]
                
                # Add bookmark to moz_bookmarks
                cursor.execute("""
                    INSERT INTO moz_bookmarks (type, fk, parent, title, dateAdded, lastModified)
                    VALUES (1, ?, ?, ?, strftime('%s', 'now') * 1000000, strftime('%s', 'now') * 1000000)
                """, (place_id, unfiled_folder_id, title))
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully added {len(bookmarks)} bookmarks to Firefox profile")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting bookmarks to Firefox: {str(e)}", exc_info=True)
            return False
    
    def _convert_bookmarks_to_chrome(self, bookmarks: List[Dict[str, str]], target_path: Path) -> bool:
        """
        Convert bookmarks to Chrome format and add to target profile.
        
        Args:
            bookmarks: List of bookmarks (url, title)
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Chrome stores bookmarks in a JSON file
            bookmarks_file = os.path.join(target_path, "Bookmarks")
            
            # Read existing bookmarks file
            if os.path.exists(bookmarks_file):
                with open(bookmarks_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                # Create a new bookmarks file
                data = {
                    "checksum": "",
                    "roots": {
                        "bookmark_bar": {
                            "children": [],
                            "date_added": str(int(time.time() * 1000000)),
                            "date_modified": str(int(time.time() * 1000000)),
                            "id": "1",
                            "name": "Bookmarks Bar",
                            "type": "folder"
                        },
                        "other": {
                            "children": [],
                            "date_added": str(int(time.time() * 1000000)),
                            "date_modified": str(int(time.time() * 1000000)),
                            "id": "2",
                            "name": "Other Bookmarks",
                            "type": "folder"
                        },
                        "synced": {
                            "children": [],
                            "date_added": str(int(time.time() * 1000000)),
                            "date_modified": str(int(time.time() * 1000000)),
                            "id": "3",
                            "name": "Mobile Bookmarks",
                            "type": "folder"
                        }
                    },
                    "version": 1
                }
            
            # Add bookmarks to "Other Bookmarks" folder
            other_folder = data["roots"]["other"]
            
            # Get the highest ID
            highest_id = 10
            for child in other_folder["children"]:
                if "id" in child:
                    try:
                        child_id = int(child["id"])
                        highest_id = max(highest_id, child_id)
                    except ValueError:
                        pass
            
            # Add bookmarks
            for bookmark in bookmarks:
                highest_id += 1
                other_folder["children"].append({
                    "date_added": str(int(time.time() * 1000000)),
                    "id": str(highest_id),
                    "name": bookmark["title"],
                    "type": "url",
                    "url": bookmark["url"]
                })
            
            # Update modification time
            other_folder["date_modified"] = str(int(time.time() * 1000000))
            
            # Write updated bookmarks file
            with open(bookmarks_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            
            self.logger.info(f"Successfully added {len(bookmarks)} bookmarks to Chrome profile")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting bookmarks to Chrome: {str(e)}", exc_info=True)
            return False
    
    def _convert_history_to_firefox(self, history_entries: List[Dict[str, Any]], target_path: Path) -> bool:
        """
        Convert history entries to Firefox format and add to target profile.
        
        Args:
            history_entries: List of history entries (url, title, timestamp)
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Firefox stores history in places.sqlite
            places_db = os.path.join(target_path, "places.sqlite")
            
            if not os.path.exists(places_db):
                self.logger.warning(f"Firefox places.sqlite not found at {places_db}")
                return False
            
            # Connect to the database
            conn = sqlite3.connect(places_db)
            cursor = conn.cursor()
            
            # Add history entries
            for entry in history_entries:
                url = entry["url"]
                title = entry["title"]
                timestamp = entry["timestamp"]
                
                # If timestamp is 0, use current time
                if timestamp == 0:
                    timestamp = int(time.time() * 1000000)
                else:
                    # Convert to microseconds if needed
                    if timestamp < 1000000000000:
                        timestamp *= 1000000
                
                # Add URL to moz_places
                cursor.execute("""
                    INSERT OR IGNORE INTO moz_places (url, title, frecency, last_visit_date)
                    VALUES (?, ?, 10, ?)
                """, (url, title, timestamp))
                
                # Get the ID of the inserted URL
                cursor.execute("SELECT id FROM moz_places WHERE url = ?", (url,))
                place_id = cursor.fetchone()[0]
                
                # Add visit to moz_historyvisits
                cursor.execute("""
                    INSERT INTO moz_historyvisits (place_id, visit_date, visit_type)
                    VALUES (?, ?, 1)
                """, (place_id, timestamp))
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully added {len(history_entries)} history entries to Firefox profile")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting history to Firefox: {str(e)}", exc_info=True)
            return False
    
    def _convert_history_to_chrome(self, history_entries: List[Dict[str, Any]], target_path: Path) -> bool:
        """
        Convert history entries to Chrome format and add to target profile.
        
        Args:
            history_entries: List of history entries (url, title, timestamp)
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Chrome stores history in a SQLite database
            history_db = os.path.join(target_path, "History")
            
            # If History file doesn't exist, we can't add history
            if not os.path.exists(history_db):
                self.logger.warning(f"Chrome History database not found at {history_db}")
                return False
            
            # Connect to the database
            conn = sqlite3.connect(history_db)
            cursor = conn.cursor()
            
            # Add history entries
            for entry in history_entries:
                url = entry["url"]
                title = entry["title"]
                timestamp = entry["timestamp"]
                
                # If timestamp is 0, use current time
                if timestamp == 0:
                    chrome_time = int(time.time() * 1000000) + 11644473600000000
                else:
                    # Convert to Chrome time format (microseconds since Jan 1, 1601)
                    chrome_time = timestamp + 11644473600000000
                
                # Add URL to urls table
                cursor.execute("""
                    INSERT OR IGNORE INTO urls (url, title, visit_count, typed_count, last_visit_time, hidden)
                    VALUES (?, ?, 1, 0, ?, 0)
                """, (url, title, chrome_time))
                
                # Get the ID of the inserted URL
                cursor.execute("SELECT id FROM urls WHERE url = ?", (url,))
                url_id = cursor.fetchone()[0]
                
                # Add visit to visits table
                cursor.execute("""
                    INSERT INTO visits (url, visit_time, transition, visit_duration)
                    VALUES (?, ?, 0, 0)
                """, (url_id, chrome_time))
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            self.logger.info(f"Successfully added {len(history_entries)} history entries to Chrome profile")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting history to Chrome: {str(e)}", exc_info=True)
            return False
    
    def migrate_special_browser_data(self, source_profile: Dict[str, Any], target_path: Path) -> Tuple[bool, str]:
        """
        Migrate data from a browser with special features to the target browser.
        
        Args:
            source_profile: Source profile information
            target_path: Path to the target profile
            
        Returns:
            Tuple of success flag and message
        """
        browser_id = source_profile.get("browser_type")
        
        if browser_id not in self.special_browsers:
            return False, f"Unsupported browser type: {browser_id}"
        
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # Migrate bookmarks
            bookmarks_migrated = self._migrate_special_browser_bookmarks(browser_id, source_profile["path"], target_path)
            
            # Migrate history (if supported)
            history_migrated = self._migrate_special_browser_history(browser_id, source_profile["path"], target_path)
            
            # Return result
            if bookmarks_migrated or history_migrated:
                return True, f"Successfully migrated data from {browser_id}"
            else:
                return False, f"No data migrated from {browser_id}"
            
        except Exception as e:
            self.logger.error(f"Error migrating {browser_id} data: {str(e)}", exc_info=True)
            return False, f"Error migrating {browser_id} data: {str(e)}"
    
    def _migrate_special_browser_bookmarks(self, browser_id: str, source_path: str, target_path: Path) -> bool:
        """
        Migrate bookmarks from a browser with special features to the target browser.
        
        Args:
            browser_id: ID of the special browser
            source_path: Path to the source profile
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Get bookmarks from source browser
            bookmarks = []
            
            # qutebrowser
            if browser_id == "qutebrowser":
                bookmarks_file = os.path.join(source_path, "bookmarks", "urls")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip():
                                parts = line.strip().split(" ", 1)
                                if len(parts) == 2:
                                    url, title = parts
                                    bookmarks.append({"url": url, "title": title})
                
                # Also check quickmarks
                quickmarks_file = os.path.join(source_path, "quickmarks")
                if os.path.exists(quickmarks_file):
                    with open(quickmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip():
                                parts = line.strip().split(" ", 1)
                                if len(parts) == 2:
                                    name, url = parts
                                    bookmarks.append({"url": url, "title": name})
            
            # Dillo
            elif browser_id == "dillo":
                bookmarks_file = os.path.join(source_path, "bm.txt")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip() and not line.startswith("#"):
                                parts = line.strip().split(" ", 1)
                                if len(parts) == 2:
                                    url, title = parts
                                    bookmarks.append({"url": url, "title": title})
            
            # NetSurf
            elif browser_id == "netsurf":
                bookmarks_file = os.path.join(source_path, "Bookmarks")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        import re
                        # Extract links from NetSurf bookmarks format
                        links = re.findall(r'<bookmark url="([^"]+)"[^>]*>([^<]+)</bookmark>', content)
                        for url, title in links:
                            bookmarks.append({"url": url, "title": title})
            
            # Konqueror
            elif browser_id == "konqueror":
                bookmarks_file = os.path.join(source_path, "bookmarks.xml")
                if os.path.exists(bookmarks_file):
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        import re
                        # Extract links from Konqueror bookmarks format
                        links = re.findall(r'<bookmark href="([^"]+)"[^>]*>\s*<title>([^<]+)</title>', content)
                        for url, title in links:
                            bookmarks.append({"url": url, "title": title})
            
            # Falkon
            elif browser_id == "falkon":
                bookmarks_file = os.path.join(source_path, "bookmarks.json")
                if os.path.exists(bookmarks_file):
                    try:
                        with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                            data = json.load(f)
                            self._extract_falkon_bookmarks(data, bookmarks)
                    except json.JSONDecodeError:
                        pass
            
            # Otter Browser
            elif browser_id == "otter":
                bookmarks_file = os.path.join(source_path, "bookmarks.json")
                if os.path.exists(bookmarks_file):
                    try:
                        with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict) and "url" in item and "title" in item:
                                        bookmarks.append({
                                            "url": item["url"],
                                            "title": item["title"]
                                        })
                    except json.JSONDecodeError:
                        pass
            
            # If no bookmarks found, return False
            if not bookmarks:
                return False
            
            # Determine target browser family from target path
            target_browser_family = self._detect_target_browser_family(target_path)
            
            # Convert bookmarks to target format
            if target_browser_family == "firefox":
                return self._convert_bookmarks_to_firefox(bookmarks, target_path)
            elif target_browser_family == "chrome":
                return self._convert_bookmarks_to_chrome(bookmarks, target_path)
            else:
                return False
            
        except Exception as e:
            self.logger.error(f"Error migrating {browser_id} bookmarks: {str(e)}", exc_info=True)
            return False
    
    def _extract_falkon_bookmarks(self, data: Dict[str, Any], bookmarks: List[Dict[str, str]]) -> None:
        """
        Extract bookmarks from Falkon bookmarks data.
        
        Args:
            data: Bookmarks data
            bookmarks: List to append extracted bookmarks to
        """
        if not isinstance(data, dict):
            return
        
        # Check if it's a bookmark
        if "type" in data and data["type"] == "url" and "url" in data and "name" in data:
            bookmarks.append({
                "url": data["url"],
                "title": data["name"]
            })
        
        # Check if it has children
        if "children" in data and isinstance(data["children"], list):
            for child in data["children"]:
                self._extract_falkon_bookmarks(child, bookmarks)
    
    def _migrate_special_browser_history(self, browser_id: str, source_path: str, target_path: Path) -> bool:
        """
        Migrate history from a browser with special features to the target browser.
        
        Args:
            browser_id: ID of the special browser
            source_path: Path to the source profile
            target_path: Path to the target profile
            
        Returns:
            Success flag
        """
        try:
            # Get history from source browser
            history_entries = []
            
            # qutebrowser
            if browser_id == "qutebrowser":
                history_file = os.path.join(source_path, "history", "urls")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip():
                                parts = line.strip().split(" ", 1)
                                if len(parts) >= 1:
                                    url = parts[0]
                                    title = parts[1] if len(parts) > 1 else url
                                    history_entries.append({
                                        "url": url,
                                        "title": title,
                                        "timestamp": 0  # No timestamp in qutebrowser history
                                    })
            
            # NetSurf
            elif browser_id == "netsurf":
                history_file = os.path.join(source_path, "URLs")
                if os.path.exists(history_file):
                    with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.strip():
                                url = line.strip()
                                history_entries.append({
                                    "url": url,
                                    "title": url,
                                    "timestamp": 0  # No timestamp in NetSurf history
                                })
            
            # Falkon
            elif browser_id == "falkon":
                history_db = os.path.join(source_path, "browsedata.db")
                if os.path.exists(history_db):
                    try:
                        conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                        cursor = conn.cursor()
                        
                        # Get history entries
                        cursor.execute("SELECT url, title, date FROM history")
                        for row in cursor.fetchall():
                            url, title, timestamp = row
                            history_entries.append({
                                "url": url,
                                "title": title or url,
                                "timestamp": timestamp
                            })
                        
                        conn.close()
                    except sqlite3.Error:
                        pass
            
            # Otter Browser
            elif browser_id == "otter":
                history_db = os.path.join(source_path, "browsingHistory.sqlite")
                if os.path.exists(history_db):
                    try:
                        conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                        cursor = conn.cursor()
                        
                        # Get history entries
                        cursor.execute("""
                            SELECT urls.url, urls.title, visits.date
                            FROM visits
                            JOIN urls ON visits.url = urls.id
                        """)
                        for row in cursor.fetchall():
                            url, title, timestamp = row
                            history_entries.append({
                                "url": url,
                                "title": title or url,
                                "timestamp": timestamp
                            })
                        
                        conn.close()
                    except sqlite3.Error:
                        pass
            
            # If no history found, return False
            if not history_entries:
                return False
            
            # Determine target browser family from target path
            target_browser_family = self._detect_target_browser_family(target_path)
            
            # Convert history to target format
            if target_browser_family == "firefox":
                return self._convert_history_to_firefox(history_entries, target_path)
            elif target_browser_family == "chrome":
                return self._convert_history_to_chrome(history_entries, target_path)
            else:
                return False
            
        except Exception as e:
            self.logger.error(f"Error migrating {browser_id} history: {str(e)}", exc_info=True)
            return False
