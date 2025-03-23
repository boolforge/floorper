#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Browser Detector
===========================

Reliable browser detection with multiple detection methods and fallbacks.
"""

import os
import sys
import logging
import glob
import winreg
import shutil
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Set

from .constants import BROWSERS

class BrowserDetector:
    """Detects installed browsers and their profiles"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_browsers(self) -> List[str]:
        """
        Detect installed browsers using multiple methods for reliability
        
        Returns:
            List[str]: List of browser_ids from the BROWSERS dict
        """
        installed_browsers = set()
        
        # Method 1: Check executables
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for exe_name in browser_info.get("exe_names", []):
                try:
                    if shutil.which(exe_name):
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser by executable: {browser_id} ({exe_name})")
                        break
                except Exception as e:
                    self.logger.debug(f"Error checking executable {exe_name}: {str(e)}")
        
        # Method 2: Check profile directories
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for profile_path in browser_info.get("profile_paths", []):
                if os.path.exists(profile_path):
                    installed_browsers.add(browser_id)
                    self.logger.info(f"Found browser by profile dir: {browser_id} at {profile_path}")
                    break
        
        # Method 3: Check registry keys (Windows only)
        if sys.platform == "win32":
            for browser_id, browser_info in BROWSERS.items():
                # Skip Floorp as it's our target browser
                if browser_id == "floorp":
                    continue
                    
                for reg_key in browser_info.get("profile_registry", []):
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key) as key:
                            installed_browsers.add(browser_id)
                            self.logger.info(f"Found browser by registry: {browser_id}")
                            break
                    except FileNotFoundError:
                        # Try HKEY_CURRENT_USER if not found in HKEY_LOCAL_MACHINE
                        try:
                            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key) as key:
                                installed_browsers.add(browser_id)
                                self.logger.info(f"Found browser by registry (HKCU): {browser_id}")
                                break
                        except FileNotFoundError:
                            continue
                        except Exception as e:
                            self.logger.debug(f"Registry error for {browser_id} (HKCU): {str(e)}")
                    except Exception as e:
                        self.logger.debug(f"Registry error for {browser_id}: {str(e)}")
        
        # Method 4: Check for shortcuts in common locations (Windows only)
        if sys.platform == "win32":
            desktop = os.path.expanduser("~/Desktop")
            start_menu = os.path.expanduser("~/AppData/Roaming/Microsoft/Windows/Start Menu/Programs")
            
            for location in [desktop, start_menu]:
                if os.path.exists(location):
                    for browser_id, browser_info in BROWSERS.items():
                        # Skip Floorp as it's our target browser
                        if browser_id == "floorp":
                            continue
                            
                        browser_name = browser_info.get("name", "")
                        if browser_name:
                            shortcut_pattern = f"{location}/**/*{browser_name}*.lnk"
                            shortcuts = glob.glob(shortcut_pattern, recursive=True)
                            if shortcuts:
                                installed_browsers.add(browser_id)
                                self.logger.info(f"Found browser by shortcut: {browser_id}")
        
        # Always include Firefox and Chrome as critical browsers
        for critical_browser in ["firefox", "chrome"]:
            if critical_browser not in installed_browsers:
                installed_browsers.add(critical_browser)
                self.logger.info(f"Added critical browser: {critical_browser}")
        
        return list(installed_browsers)
    
    def detect_profiles(self, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect profiles for a specific browser
        
        Args:
            browser_id: The browser ID from the BROWSERS dict
            
        Returns:
            List[Dict]: List of detected profiles
        """
        profiles = []
        
        if browser_id not in BROWSERS:
            self.logger.error(f"Unknown browser ID: {browser_id}")
            return profiles
        
        browser_info = BROWSERS[browser_id]
        browser_name = browser_info.get("name", browser_id)
        
        # Check each profiles directory
        for profile_path in browser_info.get("profile_paths", []):
            if not os.path.exists(profile_path):
                continue
            
            # Handle different browser profile structures
            if browser_id in ["firefox", "waterfox", "floorp", "pale_moon", "basilisk", "librewolf", "seamonkey"]:
                # Mozilla-family profile structure
                
                # Special case for Pale Moon - search deeper if needed
                if browser_id == "pale_moon" and not os.path.isdir(os.path.join(profile_path, "*.default*")):
                    # Try to find the profile elsewhere
                    possible_dirs = glob.glob(os.path.join(profile_path, "*"))
                    for possible_dir in possible_dirs:
                        if os.path.isdir(possible_dir):
                            profile_path = possible_dir
                            break
                
                # Look for profile directories with a pattern of *.default*
                profile_dirs = glob.glob(os.path.join(profile_path, "*.default*"))
                # Also look for profiles without the default pattern
                additional_profile_dirs = glob.glob(os.path.join(profile_path, "*.*"))
                
                # Combine both sets, prioritizing defaults
                all_profile_dirs = list(set(profile_dirs) | set(additional_profile_dirs))
                
                # Check for profiles.ini to get better names
                profiles_ini_path = os.path.join(profile_path, "profiles.ini")
                profile_name_map = {}
                
                if os.path.exists(profiles_ini_path):
                    try:
                        with open(profiles_ini_path, "r", encoding="utf-8", errors="ignore") as f:
                            current_section = None
                            current_path = None
                            current_name = None
                            
                            for line in f:
                                line = line.strip()
                                if not line or line.startswith(";"):
                                    continue
                                
                                if line.startswith("["):
                                    # Save previous section if complete
                                    if current_path and current_name:
                                        full_path = os.path.join(profile_path, current_path)
                                        profile_name_map[full_path] = current_name
                                    
                                    # Start new section
                                    current_section = line
                                    current_path = None
                                    current_name = None
                                elif "=" in line:
                                    key, value = line.split("=", 1)
                                    key = key.strip()
                                    value = value.strip()
                                    
                                    if key == "Path":
                                        current_path = value
                                    elif key == "Name":
                                        current_name = value
                            
                            # Handle the last section
                            if current_path and current_name:
                                full_path = os.path.join(profile_path, current_path)
                                profile_name_map[full_path] = current_name
                    except Exception as e:
                        self.logger.warning(f"Error parsing profiles.ini: {str(e)}")
                
                # Process each profile directory
                for profile_dir in all_profile_dirs:
                    # Skip non-directories
                    if not os.path.isdir(profile_dir):
                        continue
                    
                    # Get profile name (use directory name if not found in profiles.ini)
                    if profile_dir in profile_name_map:
                        profile_name = profile_name_map[profile_dir]
                    else:
                        profile_name = os.path.basename(profile_dir)
                        # Clean up the profile name
                        profile_name = profile_name.replace(".default", "")
                        profile_name = profile_name.replace("-release", "")
                    
                    # Get profile stats
                    stats = self._get_firefox_profile_stats(profile_dir)
                    
                    # Create profile object
                    profile = {
                        "name": f"{profile_name}",
                        "browser_id": browser_id,
                        "browser_name": browser_name,
                        "path": profile_dir,
                        "stats": stats
                    }
                    
                    profiles.append(profile)
            
            elif browser_id in ["chrome", "edge", "brave", "chromium", "vivaldi", "opera", "opera_gx", "maxthon", 
                               "slimjet", "cent", "comodo", "yandex", "360", "iron", "coc_coc", "uc"]:
                # Chromium-family profile structure
                
                # Special handling for Opera
                if browser_id in ["opera", "opera_gx"]:
                    # For Opera, the profile directory structure is different
                    if os.path.exists(os.path.join(profile_path, "Local State")):
                        # This is a single profile structure
                        profile_name = "Default"
                        stats = self._get_chrome_profile_stats(profile_path)
                        
                        profile = {
                            "name": f"{profile_name}",
                            "browser_id": browser_id,
                            "browser_name": browser_name,
                            "path": profile_path,
                            "stats": stats
                        }
                        
                        profiles.append(profile)
                else:
                    # Standard Chrome-like structure
                    
                    # First check if Local State exists to get profile names
                    local_state_path = os.path.join(profile_path, "Local State")
                    profile_names = {}
                    
                    if os.path.exists(local_state_path):
                        try:
                            with open(local_state_path, "r", encoding="utf-8", errors="ignore") as f:
                                local_state = json.load(f)
                                info_cache = local_state.get("profile", {}).get("info_cache", {})
                                
                                for profile_id, profile_info in info_cache.items():
                                    profile_names[profile_id] = profile_info.get("name", profile_id)
                        except Exception as e:
                            self.logger.warning(f"Error reading Local State: {str(e)}")
                    
                    # Check for the Default profile
                    default_dir = os.path.join(profile_path, "Default")
                    if os.path.exists(default_dir) and os.path.isdir(default_dir):
                        profile_name = profile_names.get("Default", "Default")
                        stats = self._get_chrome_profile_stats(default_dir)
                        
                        profile = {
                            "name": profile_name,
                            "browser_id": browser_id,
                            "browser_name": browser_name,
                            "path": default_dir,
                            "stats": stats
                        }
                        
                        profiles.append(profile)
                    
                    # Check for additional profiles (Profile 1, Profile 2, etc.)
                    profile_pattern = os.path.join(profile_path, "Profile *")
                    additional_profiles = glob.glob(profile_pattern)
                    
                    for profile_dir in additional_profiles:
                        profile_id = os.path.basename(profile_dir)
                        profile_name = profile_names.get(profile_id, profile_id)
                        stats = self._get_chrome_profile_stats(profile_dir)
                        
                        profile = {
                            "name": profile_name,
                            "browser_id": browser_id,
                            "browser_name": browser_name,
                            "path": profile_dir,
                            "stats": stats
                        }
                        
                        profiles.append(profile)
            
            elif browser_id == "tor_browser":
                # For Tor Browser, we just use the default profile location if it exists
                if os.path.isdir(profile_path):
                    stats = self._get_firefox_profile_stats(profile_path)
                    
                    profile = {
                        "name": "Default",
                        "browser_id": browser_id,
                        "browser_name": browser_name,
                        "path": profile_path,
                        "stats": stats
                    }
                    
                    profiles.append(profile)
        
        return profiles
    
    def _get_firefox_profile_stats(self, profile_dir: str) -> Dict[str, int]:
        """Get stats for a Firefox-family profile"""
        stats = {
            "bookmarks": 0,
            "passwords": 0,
            "cookies": 0,
            "history": 0,
            "extensions": 0
        }
        
        try:
            # Count bookmarks (places.sqlite)
            places_db = os.path.join(profile_dir, "places.sqlite")
            if os.path.exists(places_db):
                try:
                    conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_bookmarks")
                    stats["bookmarks"] = cursor.fetchone()[0]
                    
                    # Count history entries
                    cursor.execute("SELECT COUNT(*) FROM moz_places")
                    stats["history"] = cursor.fetchone()[0]
                    
                    conn.close()
                except sqlite3.Error:
                    # If database is locked or corrupted, make a best guess
                    stats["bookmarks"] = os.path.getsize(places_db) // 1024
                    stats["history"] = os.path.getsize(places_db) // 512
            
            # Count passwords (logins.json)
            logins_json = os.path.join(profile_dir, "logins.json")
            if os.path.exists(logins_json):
                try:
                    with open(logins_json, "r", encoding="utf-8", errors="ignore") as f:
                        logins_data = json.load(f)
                        stats["passwords"] = len(logins_data.get("logins", []))
                except:
                    # If file can't be parsed, make a best guess
                    stats["passwords"] = os.path.getsize(logins_json) // 500
            
            # Count cookies (cookies.sqlite)
            cookies_db = os.path.join(profile_dir, "cookies.sqlite")
            if os.path.exists(cookies_db):
                try:
                    conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_cookies")
                    stats["cookies"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error:
                    # If database is locked or corrupted, make a best guess
                    stats["cookies"] = os.path.getsize(cookies_db) // 256
            
            # Count extensions (extensions directory)
            extensions_dir = os.path.join(profile_dir, "extensions")
            if os.path.exists(extensions_dir) and os.path.isdir(extensions_dir):
                stats["extensions"] = len(os.listdir(extensions_dir))
        
        except Exception as e:
            self.logger.warning(f"Error getting Firefox profile stats: {str(e)}")
        
        return stats
    
    def _get_chrome_profile_stats(self, profile_dir: str) -> Dict[str, int]:
        """Get stats for a Chrome-family profile"""
        stats = {
            "bookmarks": 0,
            "passwords": 0,
            "cookies": 0,
            "history": 0,
            "extensions": 0
        }
        
        try:
            # Count bookmarks (Bookmarks file)
            bookmarks_file = os.path.join(profile_dir, "Bookmarks")
            if os.path.exists(bookmarks_file):
                try:
                    with open(bookmarks_file, "r", encoding="utf-8", errors="ignore") as f:
                        bookmarks_data = json.load(f)
                        
                        # Count recursively
                        def count_bookmarks(node):
                            count = 0
                            if node.get("type") == "url":
                                return 1
                            
                            for child in node.get("children", []):
                                count += count_bookmarks(child)
                            
                            return count
                        
                        # Count bookmarks in both bars
                        bookmark_bar = bookmarks_data.get("roots", {}).get("bookmark_bar", {})
                        other = bookmarks_data.get("roots", {}).get("other", {})
                        
                        stats["bookmarks"] = count_bookmarks(bookmark_bar) + count_bookmarks(other)
                except:
                    # If file can't be parsed, make a best guess
                    stats["bookmarks"] = os.path.getsize(bookmarks_file) // 100
            
            # Count passwords (Login Data)
            login_data = os.path.join(profile_dir, "Login Data")
            if os.path.exists(login_data):
                try:
                    conn = sqlite3.connect(f"file:{login_data}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM logins")
                    stats["passwords"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error:
                    # If database is locked or corrupted, make a best guess
                    stats["passwords"] = os.path.getsize(login_data) // 512
            
            # Count cookies (Cookies file)
            cookies_db = os.path.join(profile_dir, "Cookies")
            if os.path.exists(cookies_db):
                try:
                    conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM cookies")
                    stats["cookies"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error:
                    # If database is locked or corrupted, make a best guess
                    stats["cookies"] = os.path.getsize(cookies_db) // 256
            
            # Count history (History file)
            history_db = os.path.join(profile_dir, "History")
            if os.path.exists(history_db):
                try:
                    conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM urls")
                    stats["history"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error:
                    # If database is locked or corrupted, make a best guess
                    stats["history"] = os.path.getsize(history_db) // 512
            
            # Count extensions
            extensions_dir = os.path.join(profile_dir, "Extensions")
            if os.path.exists(extensions_dir) and os.path.isdir(extensions_dir):
                stats["extensions"] = len(os.listdir(extensions_dir))
        
        except Exception as e:
            self.logger.warning(f"Error getting Chrome profile stats: {str(e)}")
        
        return stats
