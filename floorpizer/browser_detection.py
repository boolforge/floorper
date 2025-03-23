"""
Browser detection functionality for Floorpizer.
Handles the detection of installed browsers and their profiles.
"""

import os
import sys
import json
import logging
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
import configparser
import sqlite3
import hashlib
import re
from datetime import datetime
import traceback
from dataclasses import dataclass

try:
    import winreg
except ImportError:
    # winreg is only available on Windows
    pass

try:
    import lz4.block
except ImportError:
    print("Warning: lz4 not found. Some features may be limited.")
    lz4 = None

from .config import (
    BROWSERS,
    FLOORP,
    PROFILE_ITEMS
)

from .utils import (
    get_system_info,
    get_registry_value,
    get_file_info,
    run_command,
    safe_file_operation,
    verify_json_file,
    verify_sqlite_db,
    decompress_lz4,
    safe_db_connection
)

logger = logging.getLogger(__name__)

@dataclass
class Profile:
    """Represents a browser profile."""
    name: str
    path: str
    browser_type: str
    version: str
    is_default: bool
    stats: Dict[str, int]

class BrowserDetector:
    """Handles detection of browsers and their profiles."""
    
    def __init__(self):
        self.system_info = get_system_info()
        self.is_windows = self.system_info["system"] == "Windows"
        self.detected_browsers: Dict[str, List[Profile]] = {}
    
    def detect_browser_version(self, browser_type: str) -> Optional[str]:
        """Detect installed version of a browser."""
        browser = BROWSERS.get(browser_type)
        if not browser:
            return None
        
        try:
            if self.is_windows:
                # Try registry first
                version = get_registry_value(browser.registry_path, "CurrentVersion")
                if version:
                    return version
                
                # Try executable locations
                paths = [
                    r"C:\Program Files",
                    r"C:\Program Files (x86)",
                    os.path.expanduser("~\\AppData\\Local")
                ]
                
                for base_path in paths:
                    browser_path = Path(base_path) / browser.name / browser.executable
                    if browser_path.exists():
                        output = run_command([str(browser_path), "--version"])
                        if version := self._extract_version(output):
                            return version
            else:
                # Linux/macOS paths
                paths = [
                    "/usr/bin",
                    "/usr/local/bin",
                    "/Applications" if self.system_info["system"] == "Darwin" else None
                ]
                
                for base_path in paths:
                    if not base_path:
                        continue
                    
                    browser_path = Path(base_path) / browser.executable
                    if browser_path.exists():
                        output = run_command([str(browser_path), "--version"])
                        if version := self._extract_version(output):
                            return version
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting {browser_type} version: {e}")
            return None
    
    def _extract_version(self, output: str) -> Optional[str]:
        """Extract version number from command output."""
        match = re.search(r'(\d+\.\d+(\.\d+)?)', output)
        return match.group(1) if match else None
    
    def detect_profiles(self, browser_type: str) -> List[Profile]:
        """Detect profiles for a specific browser type."""
        profiles = []
        
        try:
            browser = BROWSERS.get(browser_type)
            if not browser:
                logger.error(f"Unknown browser type: {browser_type}")
                return []
                
            # For Firefox-based browsers, check profiles.ini
            if browser.profiles_ini:
                # Check both AppData\Roaming and AppData\Local
                roaming_profiles_dir = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / browser.profiles_dir
                local_profiles_dir = Path(os.path.expanduser("~")) / "AppData" / "Local" / browser.profiles_dir
                
                # Check profiles.ini in Roaming
                roaming_profiles_ini = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / browser.profiles_ini
                if roaming_profiles_ini.exists():
                    profiles.extend(self._read_profiles_ini(roaming_profiles_ini, browser_type, roaming_profiles_dir))
                
                # Check profiles.ini in Local
                local_profiles_ini = Path(os.path.expanduser("~")) / "AppData" / "Local" / browser.profiles_ini
                if local_profiles_ini.exists():
                    profiles.extend(self._read_profiles_ini(local_profiles_ini, browser_type, local_profiles_dir))
                    
            # For Chrome-based browsers, check User Data directory
            else:
                roaming_profiles_dir = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / browser.profiles_dir
                local_profiles_dir = Path(os.path.expanduser("~")) / "AppData" / "Local" / browser.profiles_dir
                
                # Check for profiles in AppData\Roaming
                if roaming_profiles_dir.exists():
                    profiles.extend(self._find_chrome_profiles(roaming_profiles_dir, browser_type))
                
                # Check for profiles in AppData\Local (more common for Chrome)
                if local_profiles_dir.exists():
                    profiles.extend(self._find_chrome_profiles(local_profiles_dir, browser_type))
            
            # Log profile detection results
            if profiles:
                logger.info(f"Found {len(profiles)} profiles for {browser.name}")
                for profile in profiles:
                    logger.info(f" - {profile.name} ({profile.path})")
            else:
                logger.info(f"No profiles found for {browser.name}")
                
            return profiles
            
        except Exception as e:
            logger.error(f"Error detecting profiles for {browser_type}: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    def _read_profiles_ini(self, profiles_ini: Path, browser_type: str, profiles_dir: Path) -> List[Profile]:
        """Read profiles from profiles.ini file."""
        profiles = []
        try:
            config = configparser.ConfigParser()
            with safe_file_operation(profiles_ini) as f:
                config.read_file(f)
            
            for section in config.sections():
                if section.startswith("Profile"):
                    try:
                        name = config[section].get("Name", "")
                        is_relative = config[section].getboolean("IsRelative", True)
                        path_value = config[section].get("Path", "")
                        default = config[section].getboolean("Default", False)
                        
                        if is_relative:
                            full_path = profiles_ini.parent / path_value
                        else:
                            full_path = Path(path_value)
                        
                        if profile := self._create_profile(full_path, browser_type):
                            profile.is_default = default
                            profiles.append(profile)
                            
                    except Exception as e:
                        logger.warning(f"Error processing profile {section}: {e}")
        
        except Exception as e:
            logger.error(f"Error reading profiles.ini: {e}")
        
        return profiles
    
    def _find_chrome_profiles(self, profiles_dir: Path, browser_type: str) -> List[Profile]:
        """Find Chrome profiles in a directory."""
        profiles = []
        try:
            for item in profiles_dir.iterdir():
                if item.is_dir() and item.name.startswith("Profile"):
                    profile = self._create_profile(item, browser_type)
                    if profile:
                        profiles.append(profile)
        
        except Exception as e:
            logger.error(f"Error finding Chrome profiles: {e}")
        
        return profiles
    
    def _create_profile(self, profile_path: Path, browser_type: str) -> Optional[Profile]:
        """Create a Profile object from a directory path."""
        try:
            if not profile_path.is_dir():
                return None
            
            # Get profile name
            name = profile_path.name
            
            # Get browser version
            version = self.detect_browser_version(browser_type)
            
            # Analyze profile
            stats = self._analyze_profile(profile_path)
            
            return Profile(
                name=name,
                path=str(profile_path),
                browser_type=browser_type,
                version=version or "unknown",
                is_default=False,
                stats=stats
            )
            
        except Exception as e:
            logger.error(f"Error creating profile from {profile_path}: {e}")
            return None
    
    def _analyze_profile(self, profile_path: Path) -> Dict[str, int]:
        """Analyze profile contents and return statistics."""
        stats = {
            "passwords": 0,
            "tabs": 0,
            "windows": 0,
            "bookmarks": 0,
            "cookies": 0,
            "certificates": 0,
            "extensions": 0,
            "history": 0,
            "forms": 0,
            "permissions": 0
        }
        
        try:
            # Analyze passwords
            logins_file = profile_path / "logins.json"
            if logins_file.exists() and verify_json_file(logins_file):
                with safe_file_operation(logins_file) as f:
                    data = json.load(f)
                    stats["passwords"] = len(data.get("logins", []))
            
            # Analyze tabs and windows
            session_file = profile_path / "sessionstore.jsonlz4"
            if session_file.exists():
                try:
                    with safe_file_operation(session_file, 'rb') as f:
                        data = json.loads(decompress_lz4(f.read()))
                        stats["windows"] = len(data.get("windows", []))
                        stats["tabs"] = sum(len(window.get("tabs", [])) 
                                         for window in data.get("windows", []))
                except Exception as e:
                    logger.warning(f"Error analyzing session file: {e}")
            
            # Analyze bookmarks and history
            places_file = profile_path / "places.sqlite"
            if places_file.exists() and verify_sqlite_db(places_file):
                with safe_db_connection(places_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_bookmarks WHERE type = 1")
                    stats["bookmarks"] = cursor.fetchone()[0]
                    cursor.execute("SELECT COUNT(*) FROM moz_places")
                    stats["history"] = cursor.fetchone()[0]
            
            # Analyze cookies
            cookies_file = profile_path / "cookies.sqlite"
            if cookies_file.exists() and verify_sqlite_db(cookies_file):
                with safe_db_connection(cookies_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_cookies")
                    stats["cookies"] = cursor.fetchone()[0]
            
            # Analyze certificates
            cert_file = profile_path / "cert9.db"
            if cert_file.exists() and verify_sqlite_db(cert_file):
                with safe_db_connection(cert_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_certs")
                    stats["certificates"] = cursor.fetchone()[0]
            
            # Analyze extensions
            extensions_file = profile_path / "extensions.json"
            if extensions_file.exists() and verify_json_file(extensions_file):
                with safe_file_operation(extensions_file) as f:
                    data = json.load(f)
                    stats["extensions"] = len(data.get("addons", []))
            
            # Analyze forms
            forms_file = profile_path / "formhistory.sqlite"
            if forms_file.exists() and verify_sqlite_db(forms_file):
                with safe_db_connection(forms_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_formhistory")
                    stats["forms"] = cursor.fetchone()[0]
            
            # Analyze permissions
            permissions_file = profile_path / "permissions.sqlite"
            if permissions_file.exists() and verify_sqlite_db(permissions_file):
                with safe_db_connection(permissions_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_perms")
                    stats["permissions"] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing profile: {e}")
            return stats
    
    def detect_all_browsers(self) -> Dict[str, List[Profile]]:
        """Detect all supported browsers and their profiles."""
        for browser_type in BROWSERS:
            profiles = self.detect_profiles(browser_type)
            if profiles:
                self.detected_browsers[browser_type] = profiles
        
        return self.detected_browsers
    
    def get_installed_browsers(self) -> List[str]:
        """
        Detect installed browsers on the system.
        Returns a list of browser_ids that are installed.
        """
        installed_browsers = []
        
        # Create a list of all browsers to check
        browser_ids = list(BROWSERS.keys())
        
        # Log the detection process
        logging.info(f"Detecting installed browsers from list: {', '.join(browser_ids)}")
        
        # Check each browser for existence
        for browser_id in browser_ids:
            browser = BROWSERS.get(browser_id)
            if not browser:
                continue
                
            # Flag to track if we found the browser
            browser_found = False
            found_by_method = None
            
            # 1. Check executable paths
            for exec_path in browser.get_possible_paths():
                if os.path.exists(exec_path):
                    logging.info(f"Found {browser.name} executable at {exec_path}")
                    browser_found = True
                    found_by_method = "executable"
                    break
            
            # 2. Check profile directories
            if not browser_found and browser.profiles_dir:
                # Get user's home directory
                home = os.path.expanduser("~")
                
                # Check AppData\Roaming
                roaming_path = os.path.join(home, "AppData", "Roaming", browser.profiles_dir)
                if os.path.exists(roaming_path) and os.path.isdir(roaming_path):
                    logging.info(f"Found {browser.name} profile directory at {roaming_path}")
                    browser_found = True
                    found_by_method = "profile_dir_roaming"
                
                # Check AppData\Local
                if not browser_found:
                    local_path = os.path.join(home, "AppData", "Local", browser.profiles_dir)
                    if os.path.exists(local_path) and os.path.isdir(local_path):
                        logging.info(f"Found {browser.name} profile directory at {local_path}")
                        browser_found = True
                        found_by_method = "profile_dir_local"
            
            # 3. Check for desktop shortcuts
            if not browser_found:
                # Common shortcut locations
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                start_menu_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", 
                                              "Microsoft", "Windows", "Start Menu", "Programs")
                
                # Possible shortcut names (case insensitive)
                shortcut_names = [
                    f"{browser.name}.lnk",
                    f"{browser.name.lower()}.lnk",
                    f"{browser_id}.lnk"
                ]
                
                # Check desktop shortcuts
                for shortcut_name in shortcut_names:
                    desktop_shortcut = os.path.join(desktop_path, shortcut_name)
                    if os.path.exists(desktop_shortcut):
                        logging.info(f"Found {browser.name} desktop shortcut at {desktop_shortcut}")
                        browser_found = True
                        found_by_method = "desktop_shortcut"
                        break
                
                # Check Start Menu shortcuts
                if not browser_found:
                    for shortcut_name in shortcut_names:
                        start_menu_shortcut = os.path.join(start_menu_path, shortcut_name)
                        if os.path.exists(start_menu_shortcut):
                            logging.info(f"Found {browser.name} Start Menu shortcut at {start_menu_shortcut}")
                            browser_found = True
                            found_by_method = "start_menu_shortcut"
                            break
            
            # 4. Check registry for installation
            if not browser_found and browser.registry_key:
                # Try to read the registry value
                try:
                    registry_value = get_registry_value(browser.registry_key, browser.registry_name)
                    if registry_value:
                        logging.info(f"Found {browser.name} in registry at {browser.registry_key}")
                        browser_found = True
                        found_by_method = "registry"
                except Exception as e:
                    logging.debug(f"Registry check failed for {browser.name}: {str(e)}")
            
            # If browser is found, add it to the list
            if browser_found:
                installed_browsers.append(browser_id)
                logging.info(f"Detected {browser.name} as installed via {found_by_method}")
            else:
                logging.info(f"{browser.name} not detected")
        
        # Return the actual detected browsers without any fallbacks
        logging.info(f"Final detected browser list: {', '.join(installed_browsers) if installed_browsers else 'None'}")
        return installed_browsers
    
    def print_profile_summary(self, profile: Profile) -> None:
        """Print a summary of profile contents."""
        print(f"\nProfile: {profile.name}")
        print(f"Browser: {BROWSERS[profile.browser_type].name}")
        print(f"Version: {profile.version}")
        print(f"Default: {'Yes' if profile.is_default else 'No'}")
        print("\nContents:")
        for key, value in profile.stats.items():
            print(f"  {key.title()}: {value}")
        print(f"\nTotal items: {sum(profile.stats.values())}") 