#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Profile Migrator
===========================

Handles the migration of browser profile data across multiple platforms.
Supports migration between different browser families with robust error handling.
"""

import os
import sys
import logging
import shutil
import json
import sqlite3
import time
import glob
import uuid
import configparser
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any, Union

from .constants import BROWSERS

class ProfileMigrator:
    """
    Handles the migration of profiles between browsers with platform-specific optimizations
    and improved error handling.
    """
    
    def __init__(self):
        """Initialize the profile migrator with platform detection."""
        self.logger = logging.getLogger(__name__)
        self.platform = self._detect_platform()
        
        # Define browser families for easier categorization
        self.firefox_family = [
            "firefox", "librewolf", "waterfox", "seamonkey", 
            "floorp", "pale_moon", "basilisk", "tor_browser"
        ]
        self.chrome_family = [
            "chrome", "edge", "brave", "opera", "opera_gx", 
            "vivaldi", "chromium", "yandex", "slimjet"
        ]
    
    def _detect_platform(self) -> str:
        """
        Detecta la plataforma actual para usar métodos específicos de migración
        
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
    
    def migrate_profile(self, source_profile: Any, target_browser_id: str, 
                       target_profile_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Migrate a profile from one browser to another with platform-specific optimizations
        
        Args:
            source_profile: The source profile object with browser_type, name, and path attributes
            target_browser_id: The target browser ID from BROWSERS dict
            target_profile_name: Optional name for the target profile (default is same as source)
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        self.logger.info(f"Starting migration from {source_profile.browser_type} to {target_browser_id}")
        
        if target_browser_id not in BROWSERS:
            return False, f"Unknown target browser: {target_browser_id}"
        
        # Use source profile name if target not specified
        if not target_profile_name:
            target_profile_name = source_profile.name
        
        # Check if source and target browser families are the same
        source_family = self._get_browser_family(source_profile.browser_type)
        target_family = self._get_browser_family(target_browser_id)
        
        self.logger.info(f"Source family: {source_family}, Target family: {target_family}")
        
        try:
            if source_family == target_family:
                # Same family (e.g., Firefox to Firefox-like or Chrome to Chrome-like)
                return self._migrate_same_family(source_profile, target_browser_id, target_profile_name)
            else:
                # Different families (e.g., Firefox to Chrome or vice versa)
                return self._migrate_cross_family(source_profile, target_browser_id, target_profile_name)
        except Exception as e:
            self.logger.error(f"Migration failed: {str(e)}", exc_info=True)
            return False, f"Migration failed: {str(e)}"
    
    def _get_browser_family(self, browser_id: str) -> str:
        """
        Determine the browser family (Firefox-like or Chrome-like)
        
        Args:
            browser_id: The browser ID to check
            
        Returns:
            str: 'firefox', 'chrome', or 'unknown'
        """
        if browser_id in self.firefox_family:
            return "firefox"
        elif browser_id in self.chrome_family:
            return "chrome"
        else:
            return "unknown"
    
    def _migrate_same_family(self, source_profile: Any, target_browser_id: str, 
                            target_profile_name: str) -> Tuple[bool, str]:
        """
        Migrate between browsers of the same family with platform-specific optimizations
        
        Args:
            source_profile: The source profile object
            target_browser_id: The target browser ID
            target_profile_name: Name for the target profile
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Get target browser info
            browser_info = BROWSERS[target_browser_id]
            
            # Find appropriate profile directory
            for profile_path_template in browser_info.get("profile_paths", []):
                profile_base_path = os.path.expanduser(profile_path_template)
                
                # Create directory if it doesn't exist
                if not os.path.exists(profile_base_path):
                    os.makedirs(profile_base_path, exist_ok=True)
                
                # Set up target path based on browser family
                target_path = self._create_target_profile_directory(
                    target_browser_id, profile_base_path, target_profile_name
                )
                
                if not target_path:
                    continue
                
                # Copy profile files
                return self._copy_profile_files(
                    source_profile.path, Path(target_path), is_same_family=True
                )
            
            return False, f"Could not find suitable profile directory for {target_browser_id}"
        
        except Exception as e:
            self.logger.error(f"Error in same-family migration: {str(e)}", exc_info=True)
            return False, f"Migration failed: {str(e)}"
    
    def _migrate_cross_family(self, source_profile: Any, target_browser_id: str, 
                             target_profile_name: str) -> Tuple[bool, str]:
        """
        Migrate between browsers of different families with platform-specific optimizations
        
        Args:
            source_profile: The source profile object
            target_browser_id: The target browser ID
            target_profile_name: Name for the target profile
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Get source and target families
            source_family = self._get_browser_family(source_profile.browser_type)
            target_family = self._get_browser_family(target_browser_id)
            
            # Get target browser info
            browser_info = BROWSERS[target_browser_id]
            
            # Find appropriate profile directory
            for profile_path_template in browser_info.get("profile_paths", []):
                profile_base_path = os.path.expanduser(profile_path_template)
                
                # Create directory if it doesn't exist
                if not os.path.exists(profile_base_path):
                    os.makedirs(profile_base_path, exist_ok=True)
                
                # Set up target path based on browser family
                target_path = self._create_target_profile_directory(
                    target_browser_id, profile_base_path, target_profile_name
                )
                
                if not target_path:
                    continue
                
                # Convert and copy profile data
                return self._convert_and_copy_profile(
                    source_profile.path, Path(target_path),
                    source_family=source_family,
                    target_family=target_family
                )
            
            return False, f"Could not find suitable profile directory for {target_browser_id}"
        
        except Exception as e:
            self.logger.error(f"Error in cross-family migration: {str(e)}", exc_info=True)
            return False, f"Migration failed: {str(e)}"
    
    def _create_target_profile_directory(self, target_browser_id: str, 
                                        profile_base_path: str, 
                                        target_profile_name: str) -> Optional[str]:
        """
        Create a target profile directory based on browser family and platform
        
        Args:
            target_browser_id: The target browser ID
            profile_base_path: Base path for profiles
            target_profile_name: Name for the target profile
            
        Returns:
            Optional[str]: Path to the created profile directory or None if failed
        """
        try:
            target_family = self._get_browser_family(target_browser_id)
            
            if target_family == "firefox":
                # Firefox-like - create a new directory with a unique name
                profile_dir_name = f"{target_profile_name.lower().replace(' ', '-')}.{uuid.uuid4().hex[:8]}"
                target_path = os.path.join(profile_base_path, profile_dir_name)
                
                # Create the profile directory
                os.makedirs(target_path, exist_ok=True)
                
                # Update profiles.ini if it exists
                profiles_ini = os.path.join(os.path.dirname(profile_base_path), "profiles.ini")
                
                if os.path.exists(profiles_ini):
                    self._update_firefox_profiles_ini(profiles_ini, profile_dir_name, target_profile_name)
                
                return target_path
                
            elif target_family == "chrome":
                # Chrome-like - check if a numbered profile exists
                # Find the next available profile number
                profile_pattern = os.path.join(profile_base_path, "Profile*")
                existing_profiles = [os.path.basename(p) for p in glob.glob(profile_pattern)]
                
                # Get highest profile number
                highest_num = 0
                for p in existing_profiles:
                    if p.startswith("Profile "):
                        try:
                            num = int(p.replace("Profile ", ""))
                            highest_num = max(highest_num, num)
                        except ValueError:
                            pass
                
                # Create new profile directory
                new_profile_num = highest_num + 1
                target_path = os.path.join(profile_base_path, f"Profile {new_profile_num}")
                
                # Create the profile directory
                os.makedirs(target_path, exist_ok=True)
                
                # Update Local State if it exists
                local_state_path = os.path.join(profile_base_path, "Local State")
                if os.path.exists(local_state_path):
                    self._update_chrome_local_state(local_state_path, f"Profile {new_profile_num}", target_profile_name)
                
                return target_path
            
            else:
                # Generic approach for unknown browser families
                profile_dir_name = f"{target_profile_name.lower().replace(' ', '_')}"
                target_path = os.path.join(profile_base_path, profile_dir_name)
                
                # Create the profile directory
                os.makedirs(target_path, exist_ok=True)
                
                return target_path
                
        except Exception as e:
            self.logger.error(f"Error creating target profile directory: {str(e)}", exc_info=True)
            return None
    
    def _update_firefox_profiles_ini(self, profiles_ini_path: str, 
                                    profile_dir_name: str, 
                                    profile_name: str) -> bool:
        """
        Update Firefox profiles.ini file to include the new profile
        
        Args:
            profiles_ini_path: Path to profiles.ini file
            profile_dir_name: Directory name of the profile
            profile_name: Display name of the profile
            
        Returns:
            bool: Success flag
        """
        try:
            # Parse existing profiles.ini
            config = configparser.ConfigParser()
            config.read(profiles_ini_path)
            
            # Find the highest profile number
            highest_num = -1
            for section in config.sections():
                if section.startswith("Profile"):
                    try:
                        num = int(section[7:])  # Extract number from "Profile#"
                        highest_num = max(highest_num, num)
                    except ValueError:
                        pass
            
            # Create new profile section
            new_profile_num = highest_num + 1
            new_section = f"Profile{new_profile_num}"
            
            config[new_section] = {
                "Name": profile_name,
                "IsRelative": "1",
                "Path": profile_dir_name,
                "Default": "0"
            }
            
            # Write updated profiles.ini
            with open(profiles_ini_path, "w", encoding="utf-8") as f:
                config.write(f)
            
            self.logger.info(f"Updated profiles.ini with new profile: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating profiles.ini: {str(e)}", exc_info=True)
            return False
    
    def _update_chrome_local_state(self, local_state_path: str, 
                                  profile_id: str, 
                                  profile_name: str) -> bool:
        """
        Update Chrome Local State file to include the new profile
        
        Args:
            local_state_path: Path to Local State file
            profile_id: ID of the profile (e.g., "Profile 1")
            profile_name: Display name of the profile
            
        Returns:
            bool: Success flag
        """
        try:
            # Read existing Local State
            with open(local_state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Ensure profile structure exists
            if "profile" not in data:
                data["profile"] = {}
            
            if "info_cache" not in data["profile"]:
                data["profile"]["info_cache"] = {}
            
            # Add new profile
            data["profile"]["info_cache"][profile_id] = {
                "name": profile_name,
                "active_time": int(time.time()),
                "is_ephemeral": False,
                "is_using_default_name": False,
                "shortcut_name": profile_name
            }
            
            # Write updated Local State
            with open(local_state_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            
            self.logger.info(f"Updated Local State with new profile: {profile_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating Local State: {str(e)}", exc_info=True)
            return False
    
    def _copy_profile_files(self, source_path: Path, target_path: Path, 
                           is_same_family: bool = True) -> Tuple[bool, str]:
        """
        Copy profile files from source to target with platform-specific optimizations
        
        Args:
            source_path: Path to source profile
            target_path: Path to target profile
            is_same_family: Whether source and target are from the same browser family
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # If same family, we can copy most files directly
            if is_same_family:
                # Files to exclude from copying (platform-specific)
                exclude_files = [
                    "parent.lock", "lock", ".parentlock", 
                    "cookies.sqlite-journal", "places.sqlite-journal",
                    "webappsstore.sqlite-journal"
                ]
                
                # Platform-specific exclusions
                if self.platform == "windows":
                    exclude_files.extend(["desktop.ini", "thumbs.db"])
                elif self.platform == "macos":
                    exclude_files.extend([".DS_Store", "._.DS_Store"])
                
                # Copy files
                copied_count = 0
                for item in os.listdir(source_path):
                    if item in exclude_files:
                        continue
                    
                    source_item = os.path.join(source_path, item)
                    target_item = os.path.join(target_path, item)
                    
                    if os.path.isdir(source_item):
                        # Copy directory
                        shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                        copied_count += 1
                    else:
                        # Copy file
                        shutil.copy2(source_item, target_item)
                        copied_count += 1
                
                return True, f"Successfully migrated {copied_count} items from profile"
            
            else:
                # For different families, we need to selectively copy compatible files
                return False, "Cross-family migration requires conversion, use _convert_and_copy_profile"
        
        except Exception as e:
            self.logger.error(f"Error copying profile files: {str(e)}", exc_info=True)
            return False, f"Error copying profile files: {str(e)}"
    
    def _convert_and_copy_profile(self, source_path: Path, target_path: Path,
                                 source_family: str, target_family: str) -> Tuple[bool, str]:
        """
        Convert and copy profile data between different browser families
        
        Args:
            source_path: Path to source profile
            target_path: Path to target profile
            source_family: Source browser family ('firefox', 'chrome', etc.)
            target_family: Target browser family ('firefox', 'chrome', etc.)
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # Track success of each conversion
            conversion_results = {
                "bookmarks": False,
                "passwords": False,
                "history": False,
                "cookies": False,
                "extensions": False
            }
            
            # Convert bookmarks
            if source_family == "firefox" and target_family == "chrome":
                conversion_results["bookmarks"] = self._convert_bookmarks_firefox_to_chrome(
                    source_path, target_path
                )
            elif source_family == "chrome" and target_family == "firefox":
                conversion_results["bookmarks"] = self._convert_bookmarks_chrome_to_firefox(
                    source_path, target_path
                )
            
            # Convert passwords
            if source_family == "firefox" and target_family == "chrome":
                conversion_results["passwords"] = self._convert_passwords_firefox_to_chrome(
                    source_path, target_path
                )
            elif source_family == "chrome" and target_family == "firefox":
                conversion_results["passwords"] = self._convert_passwords_chrome_to_firefox(
                    source_path, target_path
                )
            
            # Convert history (platform-specific implementation)
            conversion_results["history"] = self._convert_history(
                source_path, target_path, source_family, target_family
            )
            
            # Convert cookies (platform-specific implementation)
            conversion_results["cookies"] = self._convert_cookies(
                source_path, target_path, source_family, target_family
            )
            
            # Count successful conversions
            success_count = sum(1 for result in conversion_results.values() if result)
            
            if success_count > 0:
                return True, f"Successfully migrated {success_count} data types between browser families"
            else:
                return False, "Failed to migrate any data between browser families"
        
        except Exception as e:
            self.logger.error(f"Error converting profile: {str(e)}", exc_info=True)
            return False, f"Error converting profile: {str(e)}"
    
    def _convert_bookmarks_firefox_to_chrome(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Firefox bookmarks to Chrome format
        
        Args:
            source_path: Path to Firefox profile
            target_path: Path to Chrome profile
            
        Returns:
            bool: Success flag
        """
        try:
            # Firefox stores bookmarks in places.sqlite
            places_db = os.path.join(source_path, "places.sqlite")
            if not os.path.exists(places_db):
                self.logger.warning(f"Firefox places.sqlite not found at {places_db}")
                return False
            
            # Create a Chrome bookmarks structure
            chrome_bookmarks = {
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
            
            # Extract bookmarks from Firefox database
            try:
                conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
                cursor = conn.cursor()
                
                # Get bookmarks from toolbar
                cursor.execute("""
                    SELECT b.title, p.url, p.last_visit_date
                    FROM moz_bookmarks b
                    JOIN moz_places p ON b.fk = p.id
                    WHERE b.parent = (
                        SELECT id FROM moz_bookmarks 
                        WHERE parent = 1 AND title = 'toolbar'
                    )
                    AND b.type = 1
                """)
                
                # Add toolbar bookmarks to Chrome bookmark_bar
                for row in cursor.fetchall():
                    title, url, date = row
                    if not title:
                        title = url
                    
                    chrome_bookmarks["roots"]["bookmark_bar"]["children"].append({
                        "date_added": str(date if date else int(time.time() * 1000000)),
                        "id": str(len(chrome_bookmarks["roots"]["bookmark_bar"]["children"]) + 10),
                        "name": title,
                        "type": "url",
                        "url": url
                    })
                
                # Get other bookmarks
                cursor.execute("""
                    SELECT b.title, p.url, p.last_visit_date
                    FROM moz_bookmarks b
                    JOIN moz_places p ON b.fk = p.id
                    WHERE b.parent = (
                        SELECT id FROM moz_bookmarks 
                        WHERE parent = 1 AND title = 'unfiled'
                    )
                    AND b.type = 1
                """)
                
                # Add other bookmarks to Chrome other
                for row in cursor.fetchall():
                    title, url, date = row
                    if not title:
                        title = url
                    
                    chrome_bookmarks["roots"]["other"]["children"].append({
                        "date_added": str(date if date else int(time.time() * 1000000)),
                        "id": str(len(chrome_bookmarks["roots"]["other"]["children"]) + 100),
                        "name": title,
                        "type": "url",
                        "url": url
                    })
                
                conn.close()
            except sqlite3.Error as e:
                self.logger.error(f"Error reading Firefox bookmarks: {str(e)}", exc_info=True)
                return False
            
            # Write Chrome bookmarks file
            bookmarks_file = os.path.join(target_path, "Bookmarks")
            with open(bookmarks_file, "w", encoding="utf-8") as f:
                json.dump(chrome_bookmarks, f, indent=4)
            
            self.logger.info("Successfully converted Firefox bookmarks to Chrome format")
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting Firefox bookmarks to Chrome: {str(e)}", exc_info=True)
            return False
    
    def _convert_bookmarks_chrome_to_firefox(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Chrome bookmarks to Firefox format
        
        Args:
            source_path: Path to Chrome profile
            target_path: Path to Firefox profile
            
        Returns:
            bool: Success flag
        """
        try:
            # Chrome stores bookmarks in a JSON file
            bookmarks_file = os.path.join(source_path, "Bookmarks")
            if not os.path.exists(bookmarks_file):
                self.logger.warning(f"Chrome Bookmarks file not found at {bookmarks_file}")
                return False
            
            # Create Firefox places.sqlite if it doesn't exist
            places_db = os.path.join(target_path, "places.sqlite")
            
            # If places.sqlite doesn't exist, create a basic structure
            if not os.path.exists(places_db):
                # This is a simplified approach - in a real implementation,
                # we would need to create a proper Firefox places database structure
                self.logger.warning("Firefox places.sqlite not found, cannot convert bookmarks")
                return False
            
            # Read Chrome bookmarks
            with open(bookmarks_file, "r", encoding="utf-8") as f:
                chrome_data = json.load(f)
            
            # Connect to Firefox places database
            try:
                conn = sqlite3.connect(places_db)
                cursor = conn.cursor()
                
                # Process Chrome bookmarks
                bookmark_bar = chrome_data.get("roots", {}).get("bookmark_bar", {}).get("children", [])
                other_bookmarks = chrome_data.get("roots", {}).get("other", {}).get("children", [])
                
                # Get Firefox parent folder IDs
                cursor.execute("SELECT id FROM moz_bookmarks WHERE parent = 1 AND title = 'toolbar'")
                toolbar_folder_id = cursor.fetchone()
                
                cursor.execute("SELECT id FROM moz_bookmarks WHERE parent = 1 AND title = 'unfiled'")
                unfiled_folder_id = cursor.fetchone()
                
                if not toolbar_folder_id or not unfiled_folder_id:
                    self.logger.warning("Firefox bookmark folders not found")
                    conn.close()
                    return False
                
                toolbar_folder_id = toolbar_folder_id[0]
                unfiled_folder_id = unfiled_folder_id[0]
                
                # Add bookmark bar items
                for bookmark in bookmark_bar:
                    if bookmark.get("type") == "url":
                        url = bookmark.get("url")
                        title = bookmark.get("name", url)
                        
                        # Add to places
                        cursor.execute(
                            "INSERT OR IGNORE INTO moz_places (url, title) VALUES (?, ?)",
                            (url, title)
                        )
                        place_id = cursor.lastrowid
                        
                        # Add to bookmarks
                        cursor.execute(
                            "INSERT INTO moz_bookmarks (type, fk, parent, title) VALUES (1, ?, ?, ?)",
                            (place_id, toolbar_folder_id, title)
                        )
                
                # Add other bookmarks
                for bookmark in other_bookmarks:
                    if bookmark.get("type") == "url":
                        url = bookmark.get("url")
                        title = bookmark.get("name", url)
                        
                        # Add to places
                        cursor.execute(
                            "INSERT OR IGNORE INTO moz_places (url, title) VALUES (?, ?)",
                            (url, title)
                        )
                        place_id = cursor.lastrowid
                        
                        # Add to bookmarks
                        cursor.execute(
                            "INSERT INTO moz_bookmarks (type, fk, parent, title) VALUES (1, ?, ?, ?)",
                            (place_id, unfiled_folder_id, title)
                        )
                
                conn.commit()
                conn.close()
                
                self.logger.info("Successfully converted Chrome bookmarks to Firefox format")
                return True
                
            except sqlite3.Error as e:
                self.logger.error(f"Error writing Firefox bookmarks: {str(e)}", exc_info=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Error converting Chrome bookmarks to Firefox: {str(e)}", exc_info=True)
            return False
    
    def _convert_passwords_firefox_to_chrome(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Firefox passwords to Chrome format
        
        Args:
            source_path: Path to Firefox profile
            target_path: Path to Chrome profile
            
        Returns:
            bool: Success flag
        """
        # This is a placeholder - actual implementation would require handling
        # encrypted password databases which is complex and security-sensitive
        self.logger.warning("Password conversion requires platform-specific encryption handling")
        return False
    
    def _convert_passwords_chrome_to_firefox(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Chrome passwords to Firefox format
        
        Args:
            source_path: Path to Chrome profile
            target_path: Path to Firefox profile
            
        Returns:
            bool: Success flag
        """
        # This is a placeholder - actual implementation would require handling
        # encrypted password databases which is complex and security-sensitive
        self.logger.warning("Password conversion requires platform-specific encryption handling")
        return False
    
    def _convert_history(self, source_path: Path, target_path: Path, 
                        source_family: str, target_family: str) -> bool:
        """
        Convert browsing history between browser families
        
        Args:
            source_path: Path to source profile
            target_path: Path to target profile
            source_family: Source browser family
            target_family: Target browser family
            
        Returns:
            bool: Success flag
        """
        try:
            # Implement history conversion based on browser families
            if source_family == "firefox" and target_family == "chrome":
                return self._convert_history_firefox_to_chrome(source_path, target_path)
            elif source_family == "chrome" and target_family == "firefox":
                return self._convert_history_chrome_to_firefox(source_path, target_path)
            else:
                self.logger.warning(f"History conversion not supported between {source_family} and {target_family}")
                return False
        except Exception as e:
            self.logger.error(f"Error converting history: {str(e)}", exc_info=True)
            return False
    
    def _convert_history_firefox_to_chrome(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Firefox history to Chrome format
        
        Args:
            source_path: Path to Firefox profile
            target_path: Path to Chrome profile
            
        Returns:
            bool: Success flag
        """
        try:
            # Firefox stores history in places.sqlite
            places_db = os.path.join(source_path, "places.sqlite")
            if not os.path.exists(places_db):
                self.logger.warning(f"Firefox places.sqlite not found at {places_db}")
                return False
            
            # Chrome stores history in History database
            history_db = os.path.join(target_path, "History")
            
            # Connect to Firefox places database
            try:
                firefox_conn = sqlite3.connect(f"file:{places_db}?mode=ro", uri=True)
                firefox_cursor = firefox_conn.cursor()
                
                # Connect to Chrome history database
                chrome_conn = sqlite3.connect(history_db)
                chrome_cursor = chrome_conn.cursor()
                
                # Create Chrome history tables if they don't exist
                chrome_cursor.execute("""
                    CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY,
                        url TEXT NOT NULL,
                        title TEXT,
                        visit_count INTEGER DEFAULT 0,
                        typed_count INTEGER DEFAULT 0,
                        last_visit_time INTEGER NOT NULL,
                        hidden INTEGER DEFAULT 0
                    )
                """)
                
                chrome_cursor.execute("""
                    CREATE TABLE IF NOT EXISTS visits (
                        id INTEGER PRIMARY KEY,
                        url INTEGER NOT NULL,
                        visit_time INTEGER NOT NULL,
                        from_visit INTEGER,
                        transition INTEGER DEFAULT 0,
                        segment_id INTEGER,
                        visit_duration INTEGER DEFAULT 0,
                        FOREIGN KEY(url) REFERENCES urls(id)
                    )
                """)
                
                # Get Firefox history
                firefox_cursor.execute("""
                    SELECT url, title, visit_count, last_visit_date
                    FROM moz_places
                    WHERE last_visit_date IS NOT NULL
                    ORDER BY last_visit_date DESC
                    LIMIT 1000
                """)
                
                # Convert and insert into Chrome history
                for row in firefox_cursor.fetchall():
                    url, title, visit_count, last_visit_date = row
                    
                    # Convert Firefox timestamp to Chrome timestamp
                    # Firefox: microseconds since epoch
                    # Chrome: microseconds since Jan 1, 1601
                    chrome_time = (last_visit_date // 1000) + 11644473600000000
                    
                    # Insert into Chrome urls table
                    chrome_cursor.execute("""
                        INSERT INTO urls (url, title, visit_count, last_visit_time)
                        VALUES (?, ?, ?, ?)
                    """, (url, title or url, visit_count or 1, chrome_time))
                    
                    url_id = chrome_cursor.lastrowid
                    
                    # Insert a visit record
                    chrome_cursor.execute("""
                        INSERT INTO visits (url, visit_time, transition)
                        VALUES (?, ?, 0)
                    """, (url_id, chrome_time))
                
                chrome_conn.commit()
                firefox_conn.close()
                chrome_conn.close()
                
                self.logger.info("Successfully converted Firefox history to Chrome format")
                return True
                
            except sqlite3.Error as e:
                self.logger.error(f"Error converting history: {str(e)}", exc_info=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Error converting Firefox history to Chrome: {str(e)}", exc_info=True)
            return False
    
    def _convert_history_chrome_to_firefox(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Chrome history to Firefox format
        
        Args:
            source_path: Path to Chrome profile
            target_path: Path to Firefox profile
            
        Returns:
            bool: Success flag
        """
        try:
            # Chrome stores history in History database
            history_db = os.path.join(source_path, "History")
            if not os.path.exists(history_db):
                self.logger.warning(f"Chrome History database not found at {history_db}")
                return False
            
            # Firefox stores history in places.sqlite
            places_db = os.path.join(target_path, "places.sqlite")
            
            # If places.sqlite doesn't exist, we can't easily create it from scratch
            if not os.path.exists(places_db):
                self.logger.warning("Firefox places.sqlite not found, cannot convert history")
                return False
            
            # Connect to Chrome history database
            try:
                chrome_conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
                chrome_cursor = chrome_conn.cursor()
                
                # Connect to Firefox places database
                firefox_conn = sqlite3.connect(places_db)
                firefox_cursor = firefox_conn.cursor()
                
                # Get Chrome history
                chrome_cursor.execute("""
                    SELECT url, title, visit_count, last_visit_time
                    FROM urls
                    WHERE last_visit_time > 0
                    ORDER BY last_visit_time DESC
                    LIMIT 1000
                """)
                
                # Convert and insert into Firefox history
                for row in chrome_cursor.fetchall():
                    url, title, visit_count, last_visit_time = row
                    
                    # Convert Chrome timestamp to Firefox timestamp
                    # Chrome: microseconds since Jan 1, 1601
                    # Firefox: microseconds since epoch
                    firefox_time = (last_visit_time - 11644473600000000) * 1000
                    
                    # Insert into Firefox places table
                    firefox_cursor.execute("""
                        INSERT OR IGNORE INTO moz_places (url, title, visit_count, last_visit_date)
                        VALUES (?, ?, ?, ?)
                    """, (url, title or url, visit_count or 1, firefox_time))
                    
                    place_id = firefox_cursor.lastrowid or firefox_cursor.execute(
                        "SELECT id FROM moz_places WHERE url = ?", (url,)
                    ).fetchone()[0]
                    
                    # Insert a visit record
                    firefox_cursor.execute("""
                        INSERT INTO moz_historyvisits (place_id, visit_date, visit_type)
                        VALUES (?, ?, 1)
                    """, (place_id, firefox_time))
                
                firefox_conn.commit()
                chrome_conn.close()
                firefox_conn.close()
                
                self.logger.info("Successfully converted Chrome history to Firefox format")
                return True
                
            except sqlite3.Error as e:
                self.logger.error(f"Error converting history: {str(e)}", exc_info=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Error converting Chrome history to Firefox: {str(e)}", exc_info=True)
            return False
    
    def _convert_cookies(self, source_path: Path, target_path: Path, 
                        source_family: str, target_family: str) -> bool:
        """
        Convert cookies between browser families
        
        Args:
            source_path: Path to source profile
            target_path: Path to target profile
            source_family: Source browser family
            target_family: Target browser family
            
        Returns:
            bool: Success flag
        """
        try:
            # Implement cookies conversion based on browser families
            if source_family == "firefox" and target_family == "chrome":
                return self._convert_cookies_firefox_to_chrome(source_path, target_path)
            elif source_family == "chrome" and target_family == "firefox":
                return self._convert_cookies_chrome_to_firefox(source_path, target_path)
            else:
                self.logger.warning(f"Cookies conversion not supported between {source_family} and {target_family}")
                return False
        except Exception as e:
            self.logger.error(f"Error converting cookies: {str(e)}", exc_info=True)
            return False
    
    def _convert_cookies_firefox_to_chrome(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Firefox cookies to Chrome format
        
        Args:
            source_path: Path to Firefox profile
            target_path: Path to Chrome profile
            
        Returns:
            bool: Success flag
        """
        # This is a placeholder - actual implementation would require handling
        # encrypted cookie databases which is complex and security-sensitive
        self.logger.warning("Cookie conversion requires platform-specific encryption handling")
        return False
    
    def _convert_cookies_chrome_to_firefox(self, source_path: Path, target_path: Path) -> bool:
        """
        Convert Chrome cookies to Firefox format
        
        Args:
            source_path: Path to Chrome profile
            target_path: Path to Firefox profile
            
        Returns:
            bool: Success flag
        """
        # This is a placeholder - actual implementation would require handling
        # encrypted cookie databases which is complex and security-sensitive
        self.logger.warning("Cookie conversion requires platform-specific encryption handling")
        return False
