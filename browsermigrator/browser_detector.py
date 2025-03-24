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
from typing import List, Dict, Any, Set, Optional

# Importación condicional de módulos específicos de plataforma
if sys.platform == "win32":
    import winreg
elif sys.platform == "darwin":
    # Módulos específicos para macOS si son necesarios
    pass
elif sys.platform.startswith("linux"):
    # Módulos específicos para Linux si son necesarios
    import subprocess
    import configparser

from .constants import BROWSERS

class BrowserDetector:
    """Detects installed browsers and their profiles across multiple platforms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = self._detect_platform()
    
    def _detect_platform(self) -> str:
        """
        Detecta la plataforma actual para usar métodos específicos de detección
        
        Returns:
            str: Identificador de plataforma ('windows', 'macos', 'linux', 'haiku', 'os2', 'other')
        """
        if sys.platform == "win32":
            return "windows"
        elif sys.platform == "darwin":
            return "macos"
        elif sys.platform.startswith("linux"):
            return "linux"
        elif sys.platform == "haiku1":
            return "haiku"
        elif sys.platform == "os2emx":
            return "os2"
        else:
            return "other"
    
    def detect_browsers(self) -> List[str]:
        """
        Detect installed browsers using multiple methods for reliability
        
        Returns:
            List[str]: List of browser_ids from the BROWSERS dict
        """
        installed_browsers = set()
        
        # Method 1: Check executables (cross-platform)
        self._detect_browsers_by_executables(installed_browsers)
        
        # Method 2: Check profile directories (cross-platform)
        self._detect_browsers_by_profile_dirs(installed_browsers)
        
        # Platform-specific detection methods
        if self.platform == "windows":
            self._detect_browsers_windows(installed_browsers)
        elif self.platform == "macos":
            self._detect_browsers_macos(installed_browsers)
        elif self.platform == "linux":
            self._detect_browsers_linux(installed_browsers)
        elif self.platform == "haiku":
            self._detect_browsers_haiku(installed_browsers)
        elif self.platform == "os2":
            self._detect_browsers_os2(installed_browsers)
        
        # Always include Firefox and Chrome as critical browsers
        for critical_browser in ["firefox", "chrome"]:
            if critical_browser not in installed_browsers:
                installed_browsers.add(critical_browser)
                self.logger.info(f"Added critical browser: {critical_browser}")
        
        return list(installed_browsers)
    
    def _detect_browsers_by_executables(self, installed_browsers: Set[str]) -> None:
        """
        Detecta navegadores buscando sus ejecutables en el PATH
        
        Args:
            installed_browsers: Conjunto para almacenar los navegadores detectados
        """
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
    
    def _detect_browsers_by_profile_dirs(self, installed_browsers: Set[str]) -> None:
        """
        Detecta navegadores buscando sus directorios de perfil
        
        Args:
            installed_browsers: Conjunto para almacenar los navegadores detectados
        """
        for browser_id, browser_info in BROWSERS.items():
            # Skip Floorp as it's our target browser
            if browser_id == "floorp":
                continue
                
            for profile_path in browser_info.get("profile_paths", []):
                if os.path.exists(profile_path):
                    installed_browsers.add(browser_id)
                    self.logger.info(f"Found browser by profile dir: {browser_id} at {profile_path}")
                    break
    
    def _detect_browsers_windows(self, installed_browsers: Set[str]) -> None:
        """
        Métodos específicos de Windows para detectar navegadores
        
        Args:
            installed_browsers: Conjunto para almacenar los navegadores detectados
        """
        # Method: Check registry keys
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
        Métodos específicos de macOS para detectar navegadores
        
        Args:
            installed_browsers: Conjunto para almacenar los navegadores detectados
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
                    app_pattern = f"{applications_dir}/{browser_name}*.app"
                    apps = glob.glob(app_pattern)
                    if apps:
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser in Applications: {browser_id}")
        
        # Check user Applications folder
        user_applications_dir = os.path.expanduser("~/Applications")
        if os.path.exists(user_applications_dir):
            for browser_id, browser_info in BROWSERS.items():
                # Skip Floorp as it's our target browser
                if browser_id == "floorp":
                    continue
                
                browser_name = browser_info.get("name", "")
                if browser_name:
                    app_pattern = f"{user_applications_dir}/{browser_name}*.app"
                    apps = glob.glob(app_pattern)
                    if apps:
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser in user Applications: {browser_id}")
    
    def _detect_browsers_linux(self, installed_browsers: Set[str]) -> None:
        """
        Métodos específicos de Linux para detectar navegadores
        
        Args:
            installed_browsers: Conjunto para almacenar los navegadores detectados
        """
        # Check desktop entries
        xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share')
        xdg_data_home = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        
        desktop_dirs = [os.path.join(d, 'applications') for d in xdg_data_dirs.split(':')]
        desktop_dirs.append(os.path.join(xdg_data_home, 'applications'))
        
        for desktop_dir in desktop_dirs:
            if os.path.exists(desktop_dir):
                for browser_id, browser_info in BROWSERS.items():
                    # Skip Floorp as it's our target browser
                    if browser_id == "floorp":
                        continue
                    
                    browser_name = browser_info.get("name", "").lower()
                    if browser_name:
                        desktop_pattern = f"{desktop_dir}/*{browser_name}*.desktop"
                        desktop_files = glob.glob(desktop_pattern)
                        if desktop_files:
                            installed_browsers.add(browser_id)
                            self.logger.info(f"Found browser desktop entry: {browser_id}")
        
        # Check if browsers are installed using package manager (for Debian/Ubuntu based)
        try:
            for browser_id, browser_info in BROWSERS.items():
                # Skip Floorp as it's our target browser
                if browser_id == "floorp":
                    continue
                
                package_name = browser_info.get("linux_package", browser_id.lower())
                if package_name:
                    result = subprocess.run(
                        ["dpkg", "-l", package_name], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if "ii" in result.stdout:
                        installed_browsers.add(browser_id)
                        self.logger.info(f"Found browser by package manager: {browser_id}")
        except (FileNotFoundError, subprocess.SubprocessError) as e:
            self.logger.debug(f"Error checking package manager: {str(e)}")
    
    def _detect_browsers_haiku(self, installed_browsers: Set[str]) -> None:
        """
        Métodos específicos de Haiku para detectar navegadores
        
        Args:
            installed_browsers: Conjunto para almacenar los navegadores detectados
        """
        # Check common Haiku application directories
        app_dirs = [
            "/boot/system/apps",
            "/boot/home/config/apps",
            "/boot/system/non-packaged/apps"
        ]
        
        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                for browser_id, browser_info in BROWSERS.items():
                    # Skip Floorp as it's our target browser
                    if browser_id == "floorp":
                        continue
                    
                    browser_name = browser_info.get("name", "")
                    if browser_name:
                        app_pattern = f"{app_dir}/*{browser_name}*"
                        apps = glob.glob(app_pattern)
                        if apps:
                            installed_browsers.add(browser_id)
                            self.logger.info(f"Found browser in Haiku apps: {browser_id}")
    
    def _detect_browsers_os2(self, installed_browsers: Set[str]) -> None:
        """
        Métodos específicos de OS/2 para detectar navegadores
        
        Args:
            installed_browsers: Conjunto para almacenar los navegadores detectados
        """
        # Check common OS/2 application directories
        app_dirs = [
            "C:\\APPS",
            "C:\\PROGRAMS"
        ]
        
        for app_dir in app_dirs:
            if os.path.exists(app_dir):
                for browser_id, browser_info in BROWSERS.items():
                    # Skip Floorp as it's our target browser
                    if browser_id == "floorp":
                        continue
                    
                    browser_name = browser_info.get("name", "")
                    if browser_name:
                        app_pattern = f"{app_dir}\\*{browser_name}*"
                        apps = glob.glob(app_pattern)
                        if apps:
                            installed_browsers.add(browser_id)
                            self.logger.info(f"Found browser in OS/2 apps: {browser_id}")
    
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
                profiles.extend(self._detect_mozilla_profiles(browser_id, browser_name, profile_path))
            elif browser_id in ["chrome", "chromium", "edge", "brave", "opera", "opera_gx", "vivaldi"]:
                # Chromium-family profile structure
                profiles.extend(self._detect_chromium_profiles(browser_id, browser_name, profile_path))
            else:
                # Generic profile detection
                profiles.extend(self._detect_generic_profiles(browser_id, browser_name, profile_path))
        
        return profiles
    
    def _detect_mozilla_profiles(self, browser_id: str, browser_name: str, profile_path: str) -> List[Dict[str, Any]]:
        """
        Detecta perfiles para navegadores de la familia Mozilla
        
        Args:
            browser_id: ID del navegador
            browser_name: Nombre del navegador
            profile_path: Ruta base de los perfiles
            
        Returns:
            List[Dict]: Lista de perfiles detectados
        """
        profiles = []
        
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
        profile_name_map = self._parse_mozilla_profiles_ini(profiles_ini_path, profile_path)
        
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
            
            # Create profile object
            profile = {
                "browser_id": browser_id,
                "browser_name": browser_name,
                "name": profile_name,
                "path": profile_dir,
                "type": "mozilla"
            }
            
            # Get profile stats
            profile["stats"] = self._get_mozilla_profile_stats(profile_dir)
            
            profiles.append(profile)
        
        return profiles
    
    def _parse_mozilla_profiles_ini(self, profiles_ini_path: str, profile_base_path: str) -> Dict[str, str]:
        """
        Parsea el archivo profiles.ini de Mozilla para obtener nombres de perfiles
        
        Args:
            profiles_ini_path: Ruta al archivo profiles.ini
            profile_base_path: Ruta base de los perfiles
            
        Returns:
            Dict[str, str]: Mapeo de rutas de perfil a nombres
        """
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
                                full_path = os.path.join(profile_base_path, current_path)
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
                        full_path = os.path.join(profile_base_path, current_path)
                        profile_name_map[full_path] = current_name
            except Exception as e:
                self.logger.warning(f"Error parsing profiles.ini: {str(e)}")
        
        return profile_name_map
    
    def _get_mozilla_profile_stats(self, profile_dir: str) -> Dict[str, int]:
        """
        Obtiene estadísticas de un perfil de Mozilla
        
        Args:
            profile_dir: Ruta al directorio del perfil
            
        Returns:
            Dict[str, int]: Estadísticas del perfil
        """
        stats = {}
        
        try:
            # Count bookmarks
            places_db = os.path.join(profile_dir, "places.sqlite")
            if os.path.exists(places_db):
                try:
                    conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_bookmarks WHERE type = 1")
                    stats["bookmarks"] = cursor.fetchone()[0]
                    
                    # Count history entries
                    cursor.execute("SELECT COUNT(*) FROM moz_places")
                    stats["history"] = cursor.fetchone()[0]
                    
                    conn.close()
                except sqlite3.Error as e:
                    self.logger.debug(f"Error reading places database: {str(e)}")
            
            # Count passwords
            logins_json = os.path.join(profile_dir, "logins.json")
            if os.path.exists(logins_json):
                try:
                    with open(logins_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        stats["passwords"] = len(data.get("logins", []))
                except Exception as e:
                    self.logger.debug(f"Error reading logins.json: {str(e)}")
            
            # Count cookies
            cookies_db = os.path.join(profile_dir, "cookies.sqlite")
            if os.path.exists(cookies_db):
                try:
                    conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_cookies")
                    stats["cookies"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error as e:
                    self.logger.debug(f"Error reading cookies database: {str(e)}")
            
            # Count extensions
            extensions_dir = os.path.join(profile_dir, "extensions")
            if os.path.exists(extensions_dir):
                extensions = [f for f in os.listdir(extensions_dir) if os.path.isfile(os.path.join(extensions_dir, f))]
                stats["extensions"] = len(extensions)
        
        except Exception as e:
            self.logger.warning(f"Error getting Mozilla profile stats: {str(e)}")
        
        return stats
    
    def _detect_chromium_profiles(self, browser_id: str, browser_name: str, profile_path: str) -> List[Dict[str, Any]]:
        """
        Detecta perfiles para navegadores de la familia Chromium
        
        Args:
            browser_id: ID del navegador
            browser_name: Nombre del navegador
            profile_path: Ruta base de los perfiles
            
        Returns:
            List[Dict]: Lista de perfiles detectados
        """
        profiles = []
        
        # Check for Local State file to get profile names
        local_state_path = os.path.join(profile_path, "Local State")
        profile_name_map = self._parse_chromium_local_state(local_state_path)
        
        # Look for profile directories
        profile_dirs = []
        
        # Default profile
        default_profile = os.path.join(profile_path, "Default")
        if os.path.isdir(default_profile):
            profile_dirs.append(default_profile)
        
        # Numbered profiles
        profile_pattern = os.path.join(profile_path, "Profile*")
        profile_dirs.extend([p for p in glob.glob(profile_pattern) if os.path.isdir(p)])
        
        # Process each profile directory
        for profile_dir in profile_dirs:
            # Get profile name
            profile_folder = os.path.basename(profile_dir)
            if profile_folder in profile_name_map:
                profile_name = profile_name_map[profile_folder]
            else:
                profile_name = profile_folder
            
            # Create profile object
            profile = {
                "browser_id": browser_id,
                "browser_name": browser_name,
                "name": profile_name,
                "path": profile_dir,
                "type": "chromium"
            }
            
            # Get profile stats
            profile["stats"] = self._get_chromium_profile_stats(profile_dir)
            
            profiles.append(profile)
        
        return profiles
    
    def _parse_chromium_local_state(self, local_state_path: str) -> Dict[str, str]:
        """
        Parsea el archivo Local State de Chromium para obtener nombres de perfiles
        
        Args:
            local_state_path: Ruta al archivo Local State
            
        Returns:
            Dict[str, str]: Mapeo de carpetas de perfil a nombres
        """
        profile_name_map = {}
        
        if os.path.exists(local_state_path):
            try:
                with open(local_state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    profiles_info = data.get("profile", {}).get("info_cache", {})
                    
                    for profile_folder, profile_info in profiles_info.items():
                        profile_name = profile_info.get("name", profile_folder)
                        profile_name_map[profile_folder] = profile_name
            except Exception as e:
                self.logger.warning(f"Error parsing Local State: {str(e)}")
        
        return profile_name_map
    
    def _get_chromium_profile_stats(self, profile_dir: str) -> Dict[str, int]:
        """
        Obtiene estadísticas de un perfil de Chromium
        
        Args:
            profile_dir: Ruta al directorio del perfil
            
        Returns:
            Dict[str, int]: Estadísticas del perfil
        """
        stats = {}
        
        try:
            # Count bookmarks
            bookmarks_file = os.path.join(profile_dir, "Bookmarks")
            if os.path.exists(bookmarks_file):
                try:
                    with open(bookmarks_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        def count_bookmarks(node):
                            count = 0
                            if node.get("type") == "url":
                                count = 1
                            
                            for child in node.get("children", []):
                                count += count_bookmarks(child)
                            
                            return count
                        
                        bookmark_count = 0
                        for root in data.get("roots", {}).values():
                            if isinstance(root, dict):
                                bookmark_count += count_bookmarks(root)
                        
                        stats["bookmarks"] = bookmark_count
                except Exception as e:
                    self.logger.debug(f"Error reading bookmarks file: {str(e)}")
            
            # Count passwords
            login_data = os.path.join(profile_dir, "Login Data")
            if os.path.exists(login_data):
                try:
                    conn = sqlite3.connect(f"file:{login_data}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM logins")
                    stats["passwords"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error as e:
                    self.logger.debug(f"Error reading Login Data: {str(e)}")
            
            # Count cookies
            cookies_db = os.path.join(profile_dir, "Cookies")
            if os.path.exists(cookies_db):
                try:
                    conn = sqlite3.connect(f"file:{cookies_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM cookies")
                    stats["cookies"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error as e:
                    self.logger.debug(f"Error reading Cookies database: {str(e)}")
            
            # Count history entries
            history_db = os.path.join(profile_dir, "History")
            if os.path.exists(history_db):
                try:
                    conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM urls")
                    stats["history"] = cursor.fetchone()[0]
                    conn.close()
                except sqlite3.Error as e:
                    self.logger.debug(f"Error reading History database: {str(e)}")
            
            # Count extensions
            extensions_dir = os.path.join(profile_dir, "Extensions")
            if os.path.exists(extensions_dir):
                extension_count = 0
                for root, dirs, files in os.walk(extensions_dir):
                    for d in dirs:
                        if os.path.isdir(os.path.join(root, d)) and not d.startswith("."):
                            extension_count += 1
                
                stats["extensions"] = extension_count
        
        except Exception as e:
            self.logger.warning(f"Error getting Chromium profile stats: {str(e)}")
        
        return stats
    
    def _detect_generic_profiles(self, browser_id: str, browser_name: str, profile_path: str) -> List[Dict[str, Any]]:
        """
        Detecta perfiles para navegadores genéricos
        
        Args:
            browser_id: ID del navegador
            browser_name: Nombre del navegador
            profile_path: Ruta base de los perfiles
            
        Returns:
            List[Dict]: Lista de perfiles detectados
        """
        profiles = []
        
        # If the path exists and is a directory, treat it as a single profile
        if os.path.isdir(profile_path):
            profile_name = os.path.basename(profile_path)
            
            # Create profile object
            profile = {
                "browser_id": browser_id,
                "browser_name": browser_name,
                "name": profile_name,
                "path": profile_path,
                "type": "generic"
            }
            
            # Get basic stats
            profile["stats"] = self._get_generic_profile_stats(profile_path)
            
            profiles.append(profile)
        
        return profiles
    
    def _get_generic_profile_stats(self, profile_dir: str) -> Dict[str, int]:
        """
        Obtiene estadísticas básicas de un perfil genérico
        
        Args:
            profile_dir: Ruta al directorio del perfil
            
        Returns:
            Dict[str, int]: Estadísticas del perfil
        """
        stats = {}
        
        try:
            # Count files as a basic metric
            file_count = 0
            for root, dirs, files in os.walk(profile_dir):
                file_count += len(files)
            
            stats["files"] = file_count
        
        except Exception as e:
            self.logger.warning(f"Error getting generic profile stats: {str(e)}")
        
        return stats
