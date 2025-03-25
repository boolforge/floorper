#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Browser Detector
===========================

Reliable browser detection with multiple detection methods and fallbacks.
Supports multiple platforms including Windows, Linux, macOS, and other systems.
"""

import os
import sys
import logging
import glob
import shutil
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple

# Conditional import of platform-specific modules
if sys.platform == "win32":
    import winreg
elif sys.platform == "darwin":
    # macOS specific modules if needed
    pass
elif sys.platform.startswith("linux"):
    # Linux specific modules if needed
    import subprocess
    import configparser

from .constants import BROWSERS, PLATFORM

class BrowserDetector:
    """Detects installed browsers and their profiles across multiple platforms"""
    
    def __init__(self):
        """Initialize the browser detector with platform-specific settings"""
        self.logger = logging.getLogger(__name__)
        self.platform = PLATFORM
        self.logger.info(f"Browser detector initialized for platform: {self.platform}")
    
    def detect_browsers(self) -> List[Dict[str, Any]]:
        """
        Detect installed browsers using multiple methods for reliability
        
        Returns:
            List[Dict[str, Any]]: List of detected browsers with their information
        """
        installed_browser_ids = set()
        
        # Method 1: Check executables (cross-platform)
        self._detect_browsers_by_executables(installed_browser_ids)
        
        # Method 2: Check profile directories (cross-platform)
        self._detect_browsers_by_profile_dirs(installed_browser_ids)
        
        # Platform-specific detection methods
        if self.platform == "windows":
            self._detect_browsers_windows(installed_browser_ids)
        elif self.platform == "macos":
            self._detect_browsers_macos(installed_browser_ids)
        elif self.platform == "linux":
            self._detect_browsers_linux(installed_browser_ids)
        elif self.platform == "haiku":
            self._detect_browsers_haiku(installed_browser_ids)
        elif self.platform == "os2":
            self._detect_browsers_os2(installed_browser_ids)
        
        # Always include Firefox and Chrome as critical browsers
        for critical_browser in ["firefox", "chrome"]:
            if critical_browser not in installed_browser_ids:
                installed_browser_ids.add(critical_browser)
                self.logger.info(f"Added critical browser: {critical_browser}")
        
        # Convert browser IDs to full browser information
        installed_browsers = []
        for browser_id in installed_browser_ids:
            if browser_id in BROWSERS:
                browser_info = BROWSERS[browser_id].copy()
                browser_info["id"] = browser_id
                browser_info["version"] = self._detect_browser_version(browser_id)
                browser_info["profiles"] = self._detect_browser_profiles(browser_id)
                installed_browsers.append(browser_info)
        
        self.logger.info(f"Detected {len(installed_browsers)} browsers")
        return installed_browsers
    
    def _detect_browsers_by_executables(self, installed_browsers: Set[str]) -> None:
        """
        Detect browsers by checking for their executables in PATH
        
        Args:
            installed_browsers: Set to store detected browser IDs
        """
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for exe_name in browser_info.get("executable_names", []):
                try:
                    if shutil.which(exe_name):
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser by executable: {browser_id} ({exe_name})")
                        break
                except Exception as e:
                    self.logger.debug(f"Error checking executable {exe_name}: {str(e)}")
    
    def _detect_browsers_by_profile_dirs(self, installed_browsers: Set[str]) -> None:
        """
        Detect browsers by checking for their profile directories
        
        Args:
            installed_browsers: Set to store detected browser IDs
        """
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for profile_path in browser_info.get("profile_paths", []):
                expanded_path = os.path.expanduser(profile_path)
                if os.path.exists(expanded_path):
                    installed_browsers.add(browser_id)
                    self.logger.info(f"Found browser by profile dir: {browser_id} at {expanded_path}")
                    break
    
    def _detect_browsers_windows(self, installed_browsers: Set[str]) -> None:
        """
        Windows-specific methods to detect browsers
        
        Args:
            installed_browsers: Set to store detected browser IDs
        """
        # Method: Check registry keys
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for reg_key in browser_info.get("registry_paths", []):
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
        
        # Method: Check for shortcuts in common locations
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
    
    def _detect_browsers_macos(self, installed_browsers: Set[str]) -> None:
        """
        macOS-specific methods to detect browsers
        
        Args:
            installed_browsers: Set to store detected browser IDs
        """
        # Check Applications folder
        applications_dir = "/Applications"
        if os.path.exists(applications_dir):
            for browser_id, browser_info in BROWSERS.items():
                # Skip Floorp as it's our target browser
                if browser_id == "floorp":
                    continue
                    
                browser_name = browser_info.get("name", "")
                if browser_name:
                    app_pattern = f"{applications_dir}/{browser_name}.app"
                    if os.path.exists(app_pattern):
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser in Applications: {browser_id}")
    
    def _detect_browsers_linux(self, installed_browsers: Set[str]) -> None:
        """
        Linux-specific methods to detect browsers
        
        Args:
            installed_browsers: Set to store detected browser IDs
        """
        # Method: Check for .desktop files
        xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
        xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        
        desktop_file_locations = [
            f"{xdg_data_home}/applications",
            *[f"{data_dir}/applications" for data_dir in xdg_data_dirs.split(":")]
        ]
        
        for location in desktop_file_locations:
            if os.path.exists(location):
                for browser_id, browser_info in BROWSERS.items():
                    # Skip Floorp as it's our target browser
                    if browser_id == "floorp":
                        continue
                        
                    for package_name in browser_info.get("package_names", []):
                        desktop_file = f"{location}/{package_name}.desktop"
                        if os.path.exists(desktop_file):
                            installed_browsers.add(browser_id)
                            self.logger.info(f"Found browser by desktop file: {browser_id}")
                            break
        
        # Method: Check installed packages
        try:
            # Try apt (Debian/Ubuntu)
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Package}\n"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                installed_packages = result.stdout.splitlines()
                
                for browser_id, browser_info in BROWSERS.items():
                    # Skip Floorp as it's our target browser
                    if browser_id == "floorp":
                        continue
                        
                    for package_name in browser_info.get("package_names", []):
                        if package_name in installed_packages:
                            installed_browsers.add(browser_id)
                            self.logger.info(f"Found browser by apt package: {browser_id}")
                            break
        except Exception as e:
            self.logger.debug(f"Error checking apt packages: {str(e)}")
        
        try:
            # Try rpm (Fedora/RHEL/openSUSE)
            result = subprocess.run(
                ["rpm", "-qa"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                installed_packages = result.stdout.splitlines()
                
                for browser_id, browser_info in BROWSERS.items():
                    # Skip Floorp as it's our target browser
                    if browser_id == "floorp":
                        continue
                        
                    for package_name in browser_info.get("package_names", []):
                        if any(package_name in pkg for pkg in installed_packages):
                            installed_browsers.add(browser_id)
                            self.logger.info(f"Found browser by rpm package: {browser_id}")
                            break
        except Exception as e:
            self.logger.debug(f"Error checking rpm packages: {str(e)}")
    
    def _detect_browsers_haiku(self, installed_browsers: Set[str]) -> None:
        """
        Haiku-specific methods to detect browsers
        
        Args:
            installed_browsers: Set to store detected browser IDs
        """
        # Check common Haiku package locations
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for exe_name in browser_info.get("executable_names", []):
                common_paths = [
                    f"/boot/system/apps/{exe_name}",
                    f"/boot/system/non-packaged/apps/{exe_name}",
                    f"/boot/home/config/non-packaged/apps/{exe_name}"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser in Haiku: {browser_id}")
                        break
    
    def _detect_browsers_os2(self, installed_browsers: Set[str]) -> None:
        """
        OS/2-specific methods to detect browsers
        
        Args:
            installed_browsers: Set to store detected browser IDs
        """
        # Check common OS/2 locations
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for exe_name in browser_info.get("executable_names", []):
                if exe_name.endswith(".exe"):
                    exe_base = exe_name
                else:
                    exe_base = f"{exe_name}.exe"
                    
                common_paths = [
                    f"C:\\APPS\\{exe_base}",
                    f"C:\\PROGRAMS\\{exe_base}",
                    f"C:\\{exe_base}"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser in OS/2: {browser_id}")
                        break
    
    def _detect_browser_version(self, browser_id: str) -> str:
        """
        Detect the version of a specific browser
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            str: Browser version or "Unknown"
        """
        # Implementation depends on the browser
        # This is a simplified version
        try:
            if self.platform == "windows" and browser_id in BROWSERS:
                for reg_key in BROWSERS[browser_id].get("registry_paths", []):
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key) as key:
                            version, _ = winreg.QueryValueEx(key, "Version")
                            return version
                    except (FileNotFoundError, OSError):
                        try:
                            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key) as key:
                                version, _ = winreg.QueryValueEx(key, "Version")
                                return version
                        except (FileNotFoundError, OSError):
                            continue
            
            # Try to get version from executable
            if browser_id in BROWSERS:
                for exe_name in BROWSERS[browser_id].get("executable_names", []):
                    exe_path = shutil.which(exe_name)
                    if exe_path:
                        try:
                            result = subprocess.run(
                                [exe_path, "--version"],
                                capture_output=True,
                                text=True,
                                check=False,
                                timeout=2
                            )
                            if result.returncode == 0:
                                # Extract version from output
                                output = result.stdout.strip()
                                # Simple extraction, can be improved
                                import re
                                version_match = re.search(r'(\d+\.\d+(\.\d+)?)', output)
                                if version_match:
                                    return version_match.group(1)
                        except Exception:
                            pass
        except Exception as e:
            self.logger.debug(f"Error detecting version for {browser_id}: {str(e)}")
        
        return "Unknown"
    
    def _detect_browser_profiles(self, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect profiles for a specific browser
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        profiles = []
        
        if browser_id not in BROWSERS:
            return profiles
        
        browser_info = BROWSERS[browser_id]
        
        # Check each potential profile path
        for profile_path in browser_info.get("profile_paths", []):
            expanded_path = os.path.expanduser(profile_path)
            if not os.path.exists(expanded_path):
                continue
            
            # Handle different browser families
            if browser_info.get("family") == "firefox":
                profiles.extend(self._detect_firefox_profiles(expanded_path, browser_id))
            elif browser_info.get("family") == "chrome":
                profiles.extend(self._detect_chrome_profiles(expanded_path, browser_id))
            elif browser_info.get("family") == "safari":
                profiles.extend(self._detect_safari_profiles(expanded_path, browser_id))
            elif browser_info.get("family") == "webkit":
                profiles.extend(self._detect_webkit_profiles(expanded_path, browser_id))
            elif browser_info.get("family") == "text":
                profiles.extend(self._detect_text_browser_profiles(expanded_path, browser_id))
            else:
                # Generic profile detection
                profiles.extend(self._detect_generic_profiles(expanded_path, browser_id))
        
        return profiles
    
    def _detect_firefox_profiles(self, base_path: str, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect Firefox-based browser profiles
        
        Args:
            base_path: Base profile directory
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        profiles = []
        
        # Check for profiles.ini
        profiles_ini_path = os.path.join(base_path, "profiles.ini")
        if os.path.exists(profiles_ini_path):
            try:
                config = configparser.ConfigParser()
                config.read(profiles_ini_path)
                
                for section in config.sections():
                    if section.startswith("Profile"):
                        try:
                            profile_path = config.get(section, "Path")
                            is_relative = config.getboolean(section, "IsRelative", fallback=True)
                            
                            if is_relative:
                                full_path = os.path.join(base_path, profile_path)
                            else:
                                full_path = profile_path
                            
                            name = config.get(section, "Name", fallback=f"Profile {len(profiles) + 1}")
                            is_default = config.getboolean(section, "Default", fallback=False)
                            
                            # Check if profile exists
                            if os.path.exists(full_path):
                                profile_info = {
                                    "id": f"{browser_id}_{len(profiles)}",
                                    "name": name,
                                    "path": full_path,
                                    "browser_id": browser_id,
                                    "is_default": is_default,
                                    "stats": self._get_firefox_profile_stats(full_path)
                                }
                                profiles.append(profile_info)
                        except Exception as e:
                            self.logger.debug(f"Error processing Firefox profile: {str(e)}")
            except Exception as e:
                self.logger.debug(f"Error reading profiles.ini: {str(e)}")
        
        # If no profiles found, check for direct profile directories
        if not profiles:
            try:
                for item in os.listdir(base_path):
                    full_path = os.path.join(base_path, item)
                    if os.path.isdir(full_path) and item.endswith(".default"):
                        profile_info = {
                            "id": f"{browser_id}_default",
                            "name": "Default Profile",
                            "path": full_path,
                            "browser_id": browser_id,
                            "is_default": True,
                            "stats": self._get_firefox_profile_stats(full_path)
                        }
                        profiles.append(profile_info)
            except Exception as e:
                self.logger.debug(f"Error detecting direct Firefox profiles: {str(e)}")
        
        return profiles
    
    def _get_firefox_profile_stats(self, profile_path: str) -> Dict[str, int]:
        """
        Get statistics for a Firefox profile
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dict[str, int]: Profile statistics
        """
        stats = {
            "bookmarks": 0,
            "history": 0,
            "passwords": 0,
            "cookies": 0,
            "extensions": 0
        }
        
        try:
            # Count bookmarks and history from places.sqlite
            places_db = os.path.join(profile_path, "places.sqlite")
            if os.path.exists(places_db):
                try:
                    conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    
                    # Count bookmarks
                    cursor.execute("SELECT COUNT(*) FROM moz_bookmarks")
                    stats["bookmarks"] = cursor.fetchone()[0]
                    
                    # Count history
                    cursor.execute("SELECT COUNT(*) FROM moz_places")
                    stats["history"] = cursor.fetchone()[0]
                    
                    conn.close()
                except Exception as e:
                    self.logger.debug(f"Error reading places.sqlite: {str(e)}")
            
            # Count passwords
            logins_json = os.path.join(profile_path, "logins.json")
            if os.path.exists(logins_json):
                try:
                    with open(logins_json, "r") as f:
                        logins_data = json.load(f)
                        stats["passwords"] = len(logins_data.get("logins", []))
                except Exception as e:
                    self.logger.debug(f"Error reading logins.json: {str(e)}")
            
            # Count cookies
            cookies_db = os.path.join(profile_path, "cookies.sqlite")
            if os.path.exists(cookies_db):
                try:
                    conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM moz_cookies")
                    stats["cookies"] = cursor.fetchone()[0]
                    
                    conn.close()
                except Exception as e:
                    self.logger.debug(f"Error reading cookies.sqlite: {str(e)}")
            
            # Count extensions
            extensions_dir = os.path.join(profile_path, "extensions")
            if os.path.exists(extensions_dir):
                try:
                    stats["extensions"] = len(os.listdir(extensions_dir))
                except Exception as e:
                    self.logger.debug(f"Error counting extensions: {str(e)}")
        except Exception as e:
            self.logger.debug(f"Error getting Firefox profile stats: {str(e)}")
        
        return stats
    
    def _detect_chrome_profiles(self, base_path: str, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect Chrome-based browser profiles
        
        Args:
            base_path: Base profile directory
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        profiles = []
        
        try:
            # Check for Local State file
            local_state_path = os.path.join(base_path, "Local State")
            profile_dirs = []
            
            if os.path.exists(local_state_path):
                try:
                    with open(local_state_path, "r") as f:
                        local_state = json.load(f)
                        
                    info_cache = local_state.get("profile", {}).get("info_cache", {})
                    last_active = local_state.get("profile", {}).get("last_active_profiles", [])
                    
                    for profile_name, profile_info in info_cache.items():
                        profile_path = os.path.join(base_path, profile_name)
                        
                        if os.path.exists(profile_path):
                            is_default = profile_name == "Default" or (last_active and profile_name == last_active[0])
                            name = profile_info.get("name", profile_name)
                            
                            profile_data = {
                                "id": f"{browser_id}_{profile_name}",
                                "name": name,
                                "path": profile_path,
                                "browser_id": browser_id,
                                "is_default": is_default,
                                "stats": self._get_chrome_profile_stats(profile_path)
                            }
                            profiles.append(profile_data)
                            profile_dirs.append(profile_name)
                except Exception as e:
                    self.logger.debug(f"Error reading Local State: {str(e)}")
            
            # Check for profile directories directly if Local State parsing failed
            if not profiles:
                for item in os.listdir(base_path):
                    full_path = os.path.join(base_path, item)
                    
                    if os.path.isdir(full_path) and (item == "Default" or item.startswith("Profile")):
                        is_default = item == "Default"
                        name = "Default" if is_default else f"Profile {item.split('Profile ')[-1]}"
                        
                        profile_data = {
                            "id": f"{browser_id}_{item}",
                            "name": name,
                            "path": full_path,
                            "browser_id": browser_id,
                            "is_default": is_default,
                            "stats": self._get_chrome_profile_stats(full_path)
                        }
                        profiles.append(profile_data)
        except Exception as e:
            self.logger.debug(f"Error detecting Chrome profiles: {str(e)}")
        
        return profiles
    
    def _get_chrome_profile_stats(self, profile_path: str) -> Dict[str, int]:
        """
        Get statistics for a Chrome profile
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dict[str, int]: Profile statistics
        """
        stats = {
            "bookmarks": 0,
            "history": 0,
            "passwords": 0,
            "cookies": 0,
            "extensions": 0
        }
        
        try:
            # Count bookmarks
            bookmarks_file = os.path.join(profile_path, "Bookmarks")
            if os.path.exists(bookmarks_file):
                try:
                    with open(bookmarks_file, "r") as f:
                        bookmarks_data = json.load(f)
                        
                    def count_bookmarks(node):
                        count = 0
                        if node.get("type") == "url":
                            count = 1
                        for child in node.get("children", []):
                            count += count_bookmarks(child)
                        return count
                    
                    roots = bookmarks_data.get("roots", {})
                    for root in roots.values():
                        stats["bookmarks"] += count_bookmarks(root)
                except Exception as e:
                    self.logger.debug(f"Error reading Bookmarks: {str(e)}")
            
            # Count history
            history_db = os.path.join(profile_path, "History")
            if os.path.exists(history_db):
                try:
                    conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM urls")
                    stats["history"] = cursor.fetchone()[0]
                    
                    conn.close()
                except Exception as e:
                    self.logger.debug(f"Error reading History: {str(e)}")
            
            # Count passwords
            login_data = os.path.join(profile_path, "Login Data")
            if os.path.exists(login_data):
                try:
                    conn = sqlite3.connect(f"file:{login_data}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM logins")
                    stats["passwords"] = cursor.fetchone()[0]
                    
                    conn.close()
                except Exception as e:
                    self.logger.debug(f"Error reading Login Data: {str(e)}")
            
            # Count cookies
            cookies_db = os.path.join(profile_path, "Cookies")
            if os.path.exists(cookies_db):
                try:
                    conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM cookies")
                    stats["cookies"] = cursor.fetchone()[0]
                    
                    conn.close()
                except Exception as e:
                    self.logger.debug(f"Error reading Cookies: {str(e)}")
            
            # Count extensions
            extensions_dir = os.path.join(profile_path, "Extensions")
            if os.path.exists(extensions_dir):
                try:
                    extension_count = 0
                    for ext_id in os.listdir(extensions_dir):
                        ext_path = os.path.join(extensions_dir, ext_id)
                        if os.path.isdir(ext_path):
                            extension_count += 1
                    stats["extensions"] = extension_count
                except Exception as e:
                    self.logger.debug(f"Error counting extensions: {str(e)}")
        except Exception as e:
            self.logger.debug(f"Error getting Chrome profile stats: {str(e)}")
        
        return stats
    
    def _detect_safari_profiles(self, base_path: str, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect Safari browser profiles
        
        Args:
            base_path: Base profile directory
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        # Safari typically has a single profile
        if os.path.exists(base_path):
            return [{
                "id": f"{browser_id}_default",
                "name": "Default Profile",
                "path": base_path,
                "browser_id": browser_id,
                "is_default": True,
                "stats": self._get_safari_profile_stats(base_path)
            }]
        return []
    
    def _get_safari_profile_stats(self, profile_path: str) -> Dict[str, int]:
        """
        Get statistics for a Safari profile
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dict[str, int]: Profile statistics
        """
        stats = {
            "bookmarks": 0,
            "history": 0,
            "passwords": 0,
            "cookies": 0,
            "extensions": 0
        }
        
        try:
            # Count bookmarks
            bookmarks_file = os.path.join(profile_path, "Bookmarks.plist")
            if os.path.exists(bookmarks_file):
                # Simplified count based on file size
                stats["bookmarks"] = os.path.getsize(bookmarks_file) // 500
            
            # Count history
            history_db = os.path.join(profile_path, "History.db")
            if os.path.exists(history_db):
                try:
                    conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT COUNT(*) FROM history_items")
                    stats["history"] = cursor.fetchone()[0]
                    
                    conn.close()
                except Exception as e:
                    self.logger.debug(f"Error reading History.db: {str(e)}")
            
            # Count cookies
            cookies_file = os.path.join(profile_path, "Cookies.binarycookies")
            if os.path.exists(cookies_file):
                # Simplified count based on file size
                stats["cookies"] = os.path.getsize(cookies_file) // 100
            
            # Count extensions
            extensions_dir = os.path.join(profile_path, "Extensions")
            if os.path.exists(extensions_dir):
                try:
                    stats["extensions"] = len(os.listdir(extensions_dir))
                except Exception as e:
                    self.logger.debug(f"Error counting extensions: {str(e)}")
        except Exception as e:
            self.logger.debug(f"Error getting Safari profile stats: {str(e)}")
        
        return stats
    
    def _detect_webkit_profiles(self, base_path: str, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect WebKit-based browser profiles
        
        Args:
            base_path: Base profile directory
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        # Most WebKit browsers have a single profile
        if os.path.exists(base_path):
            return [{
                "id": f"{browser_id}_default",
                "name": "Default Profile",
                "path": base_path,
                "browser_id": browser_id,
                "is_default": True,
                "stats": self._get_webkit_profile_stats(base_path)
            }]
        return []
    
    def _get_webkit_profile_stats(self, profile_path: str) -> Dict[str, int]:
        """
        Get statistics for a WebKit-based profile
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dict[str, int]: Profile statistics
        """
        stats = {
            "bookmarks": 0,
            "history": 0,
            "passwords": 0,
            "cookies": 0,
            "extensions": 0
        }
        
        try:
            # Look for common WebKit database files
            for db_file in ["bookmarks.db", "Bookmarks.db"]:
                bookmarks_db = os.path.join(profile_path, db_file)
                if os.path.exists(bookmarks_db):
                    try:
                        conn = sqlite3.connect(f"file:{bookmarks_db}?mode=ro", uri=True)
                        cursor = conn.cursor()
                        
                        # Try common table names
                        for table in ["bookmarks", "Bookmarks"]:
                            try:
                                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                                stats["bookmarks"] = cursor.fetchone()[0]
                                break
                            except sqlite3.OperationalError:
                                continue
                        
                        conn.close()
                    except Exception as e:
                        self.logger.debug(f"Error reading bookmarks database: {str(e)}")
            
            # Look for history databases
            for db_file in ["history.db", "History.db", "WebpageIcons.db"]:
                history_db = os.path.join(profile_path, db_file)
                if os.path.exists(history_db):
                    try:
                        conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                        cursor = conn.cursor()
                        
                        # Try common table names
                        for table in ["history", "History", "history_items"]:
                            try:
                                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                                stats["history"] = cursor.fetchone()[0]
                                break
                            except sqlite3.OperationalError:
                                continue
                        
                        conn.close()
                    except Exception as e:
                        self.logger.debug(f"Error reading history database: {str(e)}")
            
            # Look for cookies
            for db_file in ["cookies.db", "Cookies.db"]:
                cookies_db = os.path.join(profile_path, db_file)
                if os.path.exists(cookies_db):
                    try:
                        conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
                        cursor = conn.cursor()
                        
                        # Try common table names
                        for table in ["cookies", "Cookies"]:
                            try:
                                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                                stats["cookies"] = cursor.fetchone()[0]
                                break
                            except sqlite3.OperationalError:
                                continue
                        
                        conn.close()
                    except Exception as e:
                        self.logger.debug(f"Error reading cookies database: {str(e)}")
        except Exception as e:
            self.logger.debug(f"Error getting WebKit profile stats: {str(e)}")
        
        return stats
    
    def _detect_text_browser_profiles(self, base_path: str, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect text-based browser profiles
        
        Args:
            base_path: Base profile directory
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        # Text browsers typically have a single profile
        if os.path.exists(base_path):
            return [{
                "id": f"{browser_id}_default",
                "name": "Default Profile",
                "path": base_path,
                "browser_id": browser_id,
                "is_default": True,
                "stats": self._get_text_browser_profile_stats(base_path)
            }]
        return []
    
    def _get_text_browser_profile_stats(self, profile_path: str) -> Dict[str, int]:
        """
        Get statistics for a text-based browser profile
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Dict[str, int]: Profile statistics
        """
        stats = {
            "bookmarks": 0,
            "history": 0,
            "passwords": 0,
            "cookies": 0,
            "extensions": 0
        }
        
        try:
            # Look for bookmarks files
            for bookmarks_file in ["bookmarks", "bookmarks.html", "bookmark.html"]:
                full_path = os.path.join(profile_path, bookmarks_file)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, "r") as f:
                            content = f.read()
                            # Rough estimate based on line count
                            stats["bookmarks"] = content.count("\n")
                    except Exception as e:
                        self.logger.debug(f"Error reading bookmarks file: {str(e)}")
            
            # Look for history files
            for history_file in ["history", "historyt.txt", "visited.txt"]:
                full_path = os.path.join(profile_path, history_file)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, "r") as f:
                            content = f.read()
                            # Rough estimate based on line count
                            stats["history"] = content.count("\n")
                    except Exception as e:
                        self.logger.debug(f"Error reading history file: {str(e)}")
            
            # Look for cookies files
            for cookies_file in ["cookies", "cookies.txt"]:
                full_path = os.path.join(profile_path, cookies_file)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, "r") as f:
                            content = f.read()
                            # Rough estimate based on line count
                            stats["cookies"] = content.count("\n")
                    except Exception as e:
                        self.logger.debug(f"Error reading cookies file: {str(e)}")
        except Exception as e:
            self.logger.debug(f"Error getting text browser profile stats: {str(e)}")
        
        return stats
    
    def _detect_generic_profiles(self, base_path: str, browser_id: str) -> List[Dict[str, Any]]:
        """
        Generic profile detection for unknown browser types
        
        Args:
            base_path: Base profile directory
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        # For unknown browser types, assume a single profile
        if os.path.exists(base_path):
            return [{
                "id": f"{browser_id}_default",
                "name": "Default Profile",
                "path": base_path,
                "browser_id": browser_id,
                "is_default": True,
                "stats": {
                    "bookmarks": 0,
                    "history": 0,
                    "passwords": 0,
                    "cookies": 0,
                    "extensions": 0
                }
            }]
        return []
