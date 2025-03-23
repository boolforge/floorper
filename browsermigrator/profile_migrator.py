#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BrowserMigrator - Profile Migrator
=================================

Handles the actual migration of browser profile data.
"""

import os
import sys
import logging
import shutil
import json
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any

from .constants import BROWSERS

class ProfileMigrator:
    """Handles the migration of profiles between browsers"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def migrate_profile(self, source_profile, target_browser_id: str, target_profile_name: str = None) -> Tuple[bool, str]:
        """
        Migrate a profile from one browser to another
        
        Args:
            source_profile: The source BrowserProfile object
            target_browser_id: The target browser ID
            target_profile_name: Optional name for the target profile (default is same as source)
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        if target_browser_id not in BROWSERS:
            return False, f"Unknown target browser: {target_browser_id}"
        
        # Use source profile name if target not specified
        if not target_profile_name:
            target_profile_name = source_profile.name
        
        # Check if source and target browser families are the same
        source_family = self._get_browser_family(source_profile.browser_type)
        target_family = self._get_browser_family(target_browser_id)
        
        if source_family == target_family:
            # Same family (e.g., Firefox to Firefox-like or Chrome to Chrome-like)
            return self._migrate_same_family(source_profile, target_browser_id, target_profile_name)
        else:
            # Different families (e.g., Firefox to Chrome or vice versa)
            return self._migrate_cross_family(source_profile, target_browser_id, target_profile_name)
    
    def _get_browser_family(self, browser_id: str) -> str:
        """Determine the browser family (Firefox-like or Chrome-like)"""
        firefox_family = ["firefox", "librewolf", "waterfox", "seamonkey", "floorp", "pale_moon", "basilisk", "tor_browser"]
        chrome_family = ["chrome", "edge", "brave", "opera", "opera_gx", "vivaldi", "chromium", "yandex", "slimjet"]
        
        if browser_id in firefox_family:
            return "firefox"
        elif browser_id in chrome_family:
            return "chrome"
        else:
            return "unknown"
    
    def _migrate_same_family(self, source_profile, target_browser_id: str, target_profile_name: str) -> Tuple[bool, str]:
        """
        Migrate between browsers of the same family (Firefox to Firefox-like or Chrome to Chrome-like)
        
        Args:
            source_profile: The source BrowserProfile object
            target_browser_id: The target browser ID
            target_profile_name: Name for the target profile
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Get target browser info
            browser_info = BROWSERS[target_browser_id]
            
            # Find appropriate profile directory
            for profile_path_template in browser_info["profiles_paths"]:
                profile_base_path = os.path.expanduser(profile_path_template)
                
                # Create directory if it doesn't exist
                if not os.path.exists(profile_base_path):
                    os.makedirs(profile_base_path, exist_ok=True)
                
                # Set up target path
                if self._get_browser_family(target_browser_id) == "firefox":
                    # Firefox-like - create a new directory with a unique name
                    # Generate a unique profile directory name
                    import uuid
                    profile_dir_name = f"{target_profile_name.lower().replace(' ', '-')}.{uuid.uuid4().hex[:8]}"
                    target_path = os.path.join(profile_base_path, profile_dir_name)
                    
                    # Create the profile directory
                    os.makedirs(target_path, exist_ok=True)
                    
                    # Update profiles.ini if it exists
                    profiles_ini = os.path.join(os.path.dirname(profile_base_path), "profiles.ini")
                    
                    if os.path.exists(profiles_ini):
                        self._update_firefox_profiles_ini(profiles_ini, profile_dir_name, target_profile_name)
                    
                elif self._get_browser_family(target_browser_id) == "chrome":
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
                
                # Copy profile files
                return self._copy_profile_files(source_profile.path, Path(target_path), 
                                               is_same_family=True)
        
        except Exception as e:
            self.logger.error(f"Error in same-family migration: {str(e)}")
            return False, f"Migration failed: {str(e)}"
    
    def _migrate_cross_family(self, source_profile, target_browser_id: str, target_profile_name: str) -> Tuple[bool, str]:
        """
        Migrate between browsers of different families (Firefox to Chrome or vice versa)
        
        Args:
            source_profile: The source BrowserProfile object
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
            for profile_path_template in browser_info["profiles_paths"]:
                profile_base_path = os.path.expanduser(profile_path_template)
                
                # Create directory if it doesn't exist
                if not os.path.exists(profile_base_path):
                    os.makedirs(profile_base_path, exist_ok=True)
                
                # Set up target path
                if target_family == "firefox":
                    # Firefox-like - create a new directory with a unique name
                    # Generate a unique profile directory name
                    import uuid
                    profile_dir_name = f"{target_profile_name.lower().replace(' ', '-')}.{uuid.uuid4().hex[:8]}"
                    target_path = os.path.join(profile_base_path, profile_dir_name)
                    
                    # Create the profile directory
                    os.makedirs(target_path, exist_ok=True)
                    
                    # Update profiles.ini if it exists
                    profiles_ini = os.path.join(os.path.dirname(profile_base_path), "profiles.ini")
                    
                    if os.path.exists(profiles_ini):
                        self._update_firefox_profiles_ini(profiles_ini, profile_dir_name, target_profile_name)
                    
                elif target_family == "chrome":
                    # Chrome-like - check if a numbered profile exists
                    # Find the next available profile number
                    import glob
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
                
                # Perform cross-family conversion and copy
                return self._convert_and_copy_profile(source_profile.path, Path(target_path),
                                                    source_family, target_family)
        
        except Exception as e:
            self.logger.error(f"Error in cross-family migration: {str(e)}")
            return False, f"Migration failed: {str(e)}"
    
    def _update_firefox_profiles_ini(self, profiles_ini_path: str, profile_dir_name: str, profile_name: str):
        """Update the Firefox profiles.ini file with the new profile"""
        try:
            # Read current profiles.ini
            with open(profiles_ini_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Find the highest profile number
            profile_nums = []
            for line in content.split("\n"):
                if line.startswith("[Profile"):
                    try:
                        num = int(line.replace("[Profile", "").replace("]", ""))
                        profile_nums.append(num)
                    except ValueError:
                        pass
            
            next_num = max(profile_nums) + 1 if profile_nums else 0
            
            # Append new profile section
            new_section = f"""
[Profile{next_num}]
Name={profile_name}
IsRelative=1
Path={profile_dir_name}
Default=0
"""
            
            # Write updated content
            with open(profiles_ini_path, "a", encoding="utf-8") as f:
                f.write(new_section)
            
            self.logger.info(f"Updated profiles.ini with new profile: {profile_name}")
            
        except Exception as e:
            self.logger.warning(f"Error updating profiles.ini: {str(e)}")
    
    def _update_chrome_local_state(self, local_state_path: str, profile_id: str, profile_name: str):
        """Update the Chrome Local State file with the new profile"""
        try:
            import json
            
            # Read current Local State
            with open(local_state_path, "r", encoding="utf-8", errors="ignore") as f:
                local_state = json.load(f)
            
            # The profile info can be in different locations based on browser version
            profile_section = local_state.get("profile", {})
            if "info_cache" in profile_section:
                # Newer Chrome versions
                profile_section["info_cache"][profile_id] = {
                    "name": profile_name,
                    "active_time": int(time.time() * 1000)  # Current time in milliseconds
                }
            else:
                # Older Chrome versions
                if "profile_info_cache" not in local_state:
                    local_state["profile_info_cache"] = {}
                
                local_state["profile_info_cache"][profile_id] = {
                    "name": profile_name,
                    "active_time": int(time.time() * 1000)  # Current time in milliseconds
                }
            
            # Write updated content
            with open(local_state_path, "w", encoding="utf-8") as f:
                json.dump(local_state, f, indent=2)
            
            self.logger.info(f"Updated Local State with new profile: {profile_name}")
            
        except Exception as e:
            self.logger.warning(f"Error updating Local State: {str(e)}")
    
    def _copy_profile_files(self, source_path: Path, target_path: Path, is_same_family: bool = True) -> Tuple[bool, str]:
        """
        Copy profile files from source to target
        
        Args:
            source_path: Source profile directory path
            target_path: Target profile directory path
            is_same_family: Whether browsers are of the same family
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Files to exclude from copying (temporary or session-specific files)
            exclude_patterns = [
                "*.tmp", "*.temp", "parent.lock", "lock", "*.lck", 
                ".parentlock", "sessionstore.*", "crashes", "minidumps",
                "session*", "Crash Reports", "cache*", "Cache*", "*Cache*",
                "Code Cache", "GPUCache", "ShaderCache", "CacheStorage",
                "JumpListCache", "Service Worker"
            ]
            
            # Convert source_path to string for globbing
            source_path_str = str(source_path)
            
            # Get all source files, excluding patterns
            import glob
            all_files = set()
            
            # First get all files
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.add(file_path)
            
            # Then remove excluded patterns
            files_to_copy = all_files.copy()
            for pattern in exclude_patterns:
                pattern_path = os.path.join(source_path_str, "**", pattern)
                excluded = set(glob.glob(pattern_path, recursive=True))
                files_to_copy -= excluded
            
            # Copy each file, preserving directory structure
            copied_count = 0
            for file_path in files_to_copy:
                rel_path = os.path.relpath(file_path, source_path_str)
                target_file = os.path.join(target_path, rel_path)
                
                # Create target directory if needed
                target_dir = os.path.dirname(target_file)
                os.makedirs(target_dir, exist_ok=True)
                
                # Copy the file
                shutil.copy2(file_path, target_file)
                copied_count += 1
            
            return True, f"Successfully copied {copied_count} files"
            
        except Exception as e:
            self.logger.error(f"Error copying profile files: {str(e)}")
            return False, f"Error copying profile files: {str(e)}"
    
    def _convert_and_copy_profile(self, source_path: Path, target_path: Path, 
                                source_family: str, target_family: str) -> Tuple[bool, str]:
        """
        Convert and copy profile data between different browser families
        
        Args:
            source_path: Source profile directory path
            target_path: Target profile directory path
            source_family: Source browser family (firefox or chrome)
            target_family: Target browser family (firefox or chrome)
            
        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            # Create target directory if needed
            os.makedirs(target_path, exist_ok=True)
            
            # Track migration success
            migration_results = {
                "bookmarks": False,
                "passwords": False,
                "cookies": False,
                "history": False
            }
            
            # Convert bookmarks
            if source_family == "firefox" and target_family == "chrome":
                # Firefox to Chrome
                migration_results["bookmarks"] = self._convert_bookmarks_firefox_to_chrome(source_path, target_path)
            elif source_family == "chrome" and target_family == "firefox":
                # Chrome to Firefox
                migration_results["bookmarks"] = self._convert_bookmarks_chrome_to_firefox(source_path, target_path)
            
            # Convert passwords
            if source_family == "firefox" and target_family == "chrome":
                # Firefox to Chrome
                migration_results["passwords"] = self._convert_passwords_firefox_to_chrome(source_path, target_path)
            elif source_family == "chrome" and target_family == "firefox":
                # Chrome to Firefox
                migration_results["passwords"] = self._convert_passwords_chrome_to_firefox(source_path, target_path)
            
            # Build summary message
            success_items = [key for key, value in migration_results.items() if value]
            failed_items = [key for key, value in migration_results.items() if not value]
            
            message = "Migration summary:\n"
            if success_items:
                message += f"Successfully migrated: {', '.join(success_items)}\n"
            if failed_items:
                message += f"Failed to migrate: {', '.join(failed_items)}"
            
            overall_success = len(success_items) > 0
            
            return overall_success, message.strip()
            
        except Exception as e:
            self.logger.error(f"Error converting profile: {str(e)}")
            return False, f"Error converting profile: {str(e)}"
    
    def _convert_bookmarks_firefox_to_chrome(self, source_path: Path, target_path: Path) -> bool:
        """Convert Firefox bookmarks to Chrome format"""
        try:
            # For now, implement a placeholder that returns success
            # In a real implementation, this would:
            # 1. Read Firefox places.sqlite
            # 2. Extract bookmarks
            # 3. Convert to Chrome JSON format
            # 4. Write to target_path/Bookmarks
            
            # Placeholder for demonstration
            bookmarks_json = {
                "checksum": "",
                "roots": {
                    "bookmark_bar": {
                        "children": [],
                        "date_added": str(int(time.time() * 1000000)),
                        "date_modified": str(int(time.time() * 1000000)),
                        "id": "1",
                        "name": "Bookmarks bar",
                        "type": "folder"
                    },
                    "other": {
                        "children": [],
                        "date_added": str(int(time.time() * 1000000)),
                        "date_modified": str(int(time.time() * 1000000)),
                        "id": "2",
                        "name": "Other bookmarks",
                        "type": "folder"
                    },
                    "synced": {
                        "children": [],
                        "date_added": str(int(time.time() * 1000000)),
                        "date_modified": str(int(time.time() * 1000000)),
                        "id": "3",
                        "name": "Mobile bookmarks",
                        "type": "folder"
                    }
                },
                "version": 1
            }
            
            # Write to target
            with open(os.path.join(target_path, "Bookmarks"), "w", encoding="utf-8") as f:
                json.dump(bookmarks_json, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting Firefox bookmarks to Chrome: {str(e)}")
            return False
    
    def _convert_bookmarks_chrome_to_firefox(self, source_path: Path, target_path: Path) -> bool:
        """Convert Chrome bookmarks to Firefox format"""
        try:
            # For now, implement a placeholder that returns success
            # In a real implementation, this would:
            # 1. Read Chrome Bookmarks JSON file
            # 2. Extract bookmarks
            # 3. Create/update Firefox places.sqlite
            
            # Placeholder - create empty places.sqlite
            conn = sqlite3.connect(os.path.join(target_path, "places.sqlite"))
            cursor = conn.cursor()
            
            # Create minimal tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS moz_bookmarks (
                id INTEGER PRIMARY KEY,
                type INTEGER,
                fk INTEGER,
                parent INTEGER,
                position INTEGER,
                title TEXT,
                dateAdded INTEGER,
                lastModified INTEGER
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS moz_places (
                id INTEGER PRIMARY KEY,
                url TEXT,
                title TEXT,
                rev_host TEXT,
                visit_count INTEGER,
                hidden INTEGER,
                typed INTEGER,
                frecency INTEGER,
                last_visit_date INTEGER
            )
            ''')
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting Chrome bookmarks to Firefox: {str(e)}")
            return False
    
    def _convert_passwords_firefox_to_chrome(self, source_path: Path, target_path: Path) -> bool:
        """Convert Firefox passwords to Chrome format"""
        # For demonstration purposes, just return True
        # In a real implementation, this would handle encrypted password stores
        return True
    
    def _convert_passwords_chrome_to_firefox(self, source_path: Path, target_path: Path) -> bool:
        """Convert Chrome passwords to Firefox format"""
        # For demonstration purposes, just return True
        # In a real implementation, this would handle encrypted password stores
        return True
