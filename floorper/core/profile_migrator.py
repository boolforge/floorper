#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Profile Migrator
==========================

Handles the migration of browser profiles between different browsers.
Supports various data types and migration strategies.
"""

import os
import sys
import logging
import shutil
import json
import sqlite3
import tempfile
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Set

from .constants import BROWSERS, DATA_TYPES, FLOORP
from .backup_manager import BackupManager

logger = logging.getLogger(__name__)

class ProfileMigrator:
    """
    Handles the migration of browser profiles between different browsers.
    
    This class provides functionality to migrate various types of data
    from source browser profiles to target browser profiles, with support
    for different migration strategies and data types.
    """
    
    def __init__(self, backup_manager: Optional[BackupManager] = None):
        """
        Initialize the profile migrator.
        
        Args:
            backup_manager: Optional backup manager instance
        """
        self.backup_manager = backup_manager or BackupManager()
        logger.info("Profile migrator initialized")
    
    def migrate_profile(
        self, 
        source_profile: Dict[str, Any], 
        target_profile: Dict[str, Any], 
        data_types: Optional[List[str]] = None, 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Migrate a source profile to a target profile.
        
        Args:
            source_profile: Source profile information
            target_profile: Target profile information
            data_types: Data types to migrate (default: all)
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration results
        """
        # Set default options
        if options is None:
            options = {}
        
        default_options = {
            "backup": True,
            "merge_strategy": "smart",  # smart, overwrite, append
            "deduplicate": True,
            "verify": True
        }
        
        # Merge with default options
        for key, value in default_options.items():
            if key not in options:
                options[key] = value
        
        # Set default data types (all)
        if data_types is None:
            data_types = list(DATA_TYPES.keys())
        
        # Validate profiles
        if not self._validate_profile(source_profile):
            logger.error("Invalid source profile")
            return {"success": False, "error": "Invalid source profile"}
        
        if not self._validate_profile(target_profile):
            logger.error("Invalid target profile")
            return {"success": False, "error": "Invalid target profile"}
        
        # Create backup if enabled
        if options["backup"]:
            logger.info("Creating backup of target profile")
            backup_path = self.backup_manager.create_backup(
                target_profile["path"],
                target_profile["browser_id"],
                target_profile["name"]
            )
            
            if not backup_path:
                logger.warning("Failed to create backup, continuing without backup")
        
        # Initialize results
        results = {
            "success": True,
            "source_profile": source_profile,
            "target_profile": target_profile,
            "data_types": data_types,
            "options": options,
            "migrated_data": {},
            "errors": []
        }
        
        # Migrate each data type
        for data_type in data_types:
            if data_type not in DATA_TYPES:
                logger.warning(f"Unknown data type: {data_type}, skipping")
                results["errors"].append(f"Unknown data type: {data_type}")
                continue
            
            logger.info(f"Migrating data type: {data_type}")
            
            try:
                # Determine migration method based on browser families
                source_family = BROWSERS.get(source_profile["browser_id"], {}).get("family", "")
                target_family = BROWSERS.get(target_profile["browser_id"], {}).get("family", "")
                
                migration_result = self._migrate_data_type(
                    data_type,
                    source_profile,
                    target_profile,
                    source_family,
                    target_family,
                    options
                )
                
                results["migrated_data"][data_type] = migration_result
                
                if not migration_result["success"]:
                    results["errors"].append(f"Failed to migrate {data_type}: {migration_result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"Error migrating {data_type}: {str(e)}")
                results["errors"].append(f"Error migrating {data_type}: {str(e)}")
                results["migrated_data"][data_type] = {"success": False, "error": str(e)}
        
        # Update overall success status
        if results["errors"]:
            results["success"] = False
        
        return results
    
    def _validate_profile(self, profile: Dict[str, Any]) -> bool:
        """
        Validate a profile dictionary.
        
        Args:
            profile: Profile information dictionary
            
        Returns:
            bool: True if profile is valid, False otherwise
        """
        required_keys = ["path", "browser_id", "name"]
        
        for key in required_keys:
            if key not in profile:
                logger.error(f"Missing required key in profile: {key}")
                return False
        
        if not os.path.exists(profile["path"]):
            logger.error(f"Profile path does not exist: {profile['path']}")
            return False
        
        return True
    
    def _migrate_data_type(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        source_family: str,
        target_family: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate a specific data type between profiles.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            source_family: Source browser family
            target_family: Target browser family
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # Determine migration method based on browser families
        if source_family == "firefox" and target_family == "firefox":
            return self._migrate_firefox_to_firefox(data_type, source_profile, target_profile, options)
        elif source_family == "chrome" and target_family == "firefox":
            return self._migrate_chrome_to_firefox(data_type, source_profile, target_profile, options)
        elif source_family == "firefox" and target_family == "chrome":
            return self._migrate_firefox_to_chrome(data_type, source_profile, target_profile, options)
        elif source_family == "chrome" and target_family == "chrome":
            return self._migrate_chrome_to_chrome(data_type, source_profile, target_profile, options)
        elif source_family == "safari" and target_family == "firefox":
            return self._migrate_safari_to_firefox(data_type, source_profile, target_profile, options)
        elif source_family == "webkit" and target_family == "firefox":
            return self._migrate_webkit_to_firefox(data_type, source_profile, target_profile, options)
        elif source_family == "text" and target_family == "firefox":
            return self._migrate_text_to_firefox(data_type, source_profile, target_profile, options)
        else:
            logger.warning(f"Unsupported migration path: {source_family} to {target_family}")
            return {"success": False, "error": f"Unsupported migration path: {source_family} to {target_family}"}
    
    def _migrate_firefox_to_firefox(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate data from Firefox-based browser to Firefox-based browser.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        source_path = source_profile["path"]
        target_path = target_profile["path"]
        
        # Get relevant files for the data type
        relevant_files = DATA_TYPES[data_type].get("firefox_files", [])
        
        if not relevant_files:
            return {"success": False, "error": f"No relevant files defined for {data_type}"}
        
        # Initialize result
        result = {
            "success": True,
            "migrated_items": 0,
            "details": []
        }
        
        # Process each relevant file
        for file_pattern in relevant_files:
            # Handle directory patterns
            if not file_pattern.endswith((".sqlite", ".json", ".js", ".jsonlz4")):
                # Likely a directory
                source_dir = os.path.join(source_path, file_pattern)
                target_dir = os.path.join(target_path, file_pattern)
                
                if os.path.isdir(source_dir):
                    try:
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir, exist_ok=True)
                        
                        # Copy directory contents
                        for item in os.listdir(source_dir):
                            source_item = os.path.join(source_dir, item)
                            target_item = os.path.join(target_dir, item)
                            
                            if os.path.isfile(source_item):
                                if os.path.exists(target_item) and options["merge_strategy"] != "overwrite":
                                    # Skip existing files unless overwrite is specified
                                    continue
                                
                                shutil.copy2(source_item, target_item)
                                result["migrated_items"] += 1
                                result["details"].append(f"Copied {item}")
                        
                        logger.info(f"Migrated directory: {file_pattern}")
                    except Exception as e:
                        logger.error(f"Error migrating directory {file_pattern}: {str(e)}")
                        result["success"] = False
                        result["error"] = f"Error migrating directory {file_pattern}: {str(e)}"
                        return result
                
                continue
            
            # Handle file patterns
            source_file = os.path.join(source_path, file_pattern)
            target_file = os.path.join(target_path, file_pattern)
            
            if not os.path.exists(source_file):
                logger.warning(f"Source file does not exist: {source_file}")
                continue
            
            try:
                # Handle different file types
                if file_pattern.endswith(".sqlite"):
                    # SQLite database
                    if data_type == "bookmarks" or data_type == "history":
                        migrated = self._migrate_places_database(source_file, target_file, options)
                        if migrated["success"]:
                            result["migrated_items"] += migrated["count"]
                            result["details"].append(f"Migrated {migrated['count']} items from {file_pattern}")
                        else:
                            result["success"] = False
                            result["error"] = migrated["error"]
                            return result
                    elif data_type == "cookies":
                        migrated = self._migrate_cookies_database(source_file, target_file, options)
                        if migrated["success"]:
                            result["migrated_items"] += migrated["count"]
                            result["details"].append(f"Migrated {migrated['count']} cookies from {file_pattern}")
                        else:
                            result["success"] = False
                            result["error"] = migrated["error"]
                            return result
                    else:
                        # Generic SQLite file copy
                        if os.path.exists(target_file) and options["merge_strategy"] != "overwrite":
                            logger.warning(f"Target file exists and overwrite not specified: {target_file}")
                            continue
                        
                        shutil.copy2(source_file, target_file)
                        result["migrated_items"] += 1
                        result["details"].append(f"Copied {file_pattern}")
                elif file_pattern.endswith(".json"):
                    # JSON file
                    if data_type == "passwords" and file_pattern == "logins.json":
                        migrated = self._migrate_logins_json(source_file, target_file, options)
                        if migrated["success"]:
                            result["migrated_items"] += migrated["count"]
                            result["details"].append(f"Migrated {migrated['count']} passwords from {file_pattern}")
                        else:
                            result["success"] = False
                            result["error"] = migrated["error"]
                            return result
                    else:
                        # Generic JSON file copy
                        if os.path.exists(target_file) and options["merge_strategy"] != "overwrite":
                            logger.warning(f"Target file exists and overwrite not specified: {target_file}")
                            continue
                        
                        shutil.copy2(source_file, target_file)
                        result["migrated_items"] += 1
                        result["details"].append(f"Copied {file_pattern}")
                elif file_pattern.endswith(".js"):
                    # JavaScript preference file
                    if data_type == "preferences":
                        migrated = self._migrate_preferences_js(source_file, target_file, options)
                        if migrated["success"]:
                            result["migrated_items"] += migrated["count"]
                            result["details"].append(f"Migrated {migrated['count']} preferences from {file_pattern}")
                        else:
                            result["success"] = False
                            result["error"] = migrated["error"]
                            return result
                    else:
                        # Generic JS file copy
                        if os.path.exists(target_file) and options["merge_strategy"] != "overwrite":
                            logger.warning(f"Target file exists and overwrite not specified: {target_file}")
                            continue
                        
                        shutil.copy2(source_file, target_file)
                        result["migrated_items"] += 1
                        result["details"].append(f"Copied {file_pattern}")
                elif file_pattern.endswith(".jsonlz4"):
                    # Compressed JSON file (sessions)
                    if data_type == "sessions":
                        migrated = self._migrate_sessions_jsonlz4(source_file, target_file, options)
                        if migrated["success"]:
                            result["migrated_items"] += migrated["count"]
                            result["details"].append(f"Migrated {migrated['count']} session items from {file_pattern}")
                        else:
                            result["success"] = False
                            result["error"] = migrated["error"]
                            return result
                    else:
                        # Generic compressed file copy
                        if os.path.exists(target_file) and options["merge_strategy"] != "overwrite":
                            logger.warning(f"Target file exists and overwrite not specified: {target_file}")
                            continue
                        
                        shutil.copy2(source_file, target_file)
                        result["migrated_items"] += 1
                        result["details"].append(f"Copied {file_pattern}")
                else:
                    # Generic file copy
                    if os.path.exists(target_file) and options["merge_strategy"] != "overwrite":
                        logger.warning(f"Target file exists and overwrite not specified: {target_file}")
                        continue
                    
                    shutil.copy2(source_file, target_file)
                    result["migrated_items"] += 1
                    result["details"].append(f"Copied {file_pattern}")
                
                logger.info(f"Migrated file: {file_pattern}")
            except Exception as e:
                logger.error(f"Error migrating file {file_pattern}: {str(e)}")
                result["success"] = False
                result["error"] = f"Error migrating file {file_pattern}: {str(e)}"
                return result
        
        return result
    
    def _migrate_places_database(self, source_file: str, target_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Firefox places database (bookmarks and history).
        
        Args:
            source_file: Source database file path
            target_file: Target database file path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        result = {
            "success": True,
            "count": 0,
            "details": []
        }
        
        try:
            # Check if target file exists
            if not os.path.exists(target_file):
                # If target doesn't exist, just copy the file
                shutil.copy2(source_file, target_file)
                
                # Count items in the copied database
                with sqlite3.connect(f"file:{target_file}?mode=ro", uri=True) as conn:
                    cursor = conn.cursor()
                    
                    # Count bookmarks
                    cursor.execute("SELECT COUNT(*) FROM moz_bookmarks")
                    bookmark_count = cursor.fetchone()[0]
                    
                    # Count history
                    cursor.execute("SELECT COUNT(*) FROM moz_places")
                    history_count = cursor.fetchone()[0]
                    
                    result["count"] = bookmark_count + history_count
                    result["details"].append(f"Copied places database with {bookmark_count} bookmarks and {history_count} history items")
                
                return result
            
            # If target exists, we need to merge the databases
            if options["merge_strategy"] == "overwrite":
                # Overwrite the target file
                shutil.copy2(source_file, target_file)
                
                # Count items in the copied database
                with sqlite3.connect(f"file:{target_file}?mode=ro", uri=True) as conn:
                    cursor = conn.cursor()
                    
                    # Count bookmarks
                    cursor.execute("SELECT COUNT(*) FROM moz_bookmarks")
                    bookmark_count = cursor.fetchone()[0]
                    
                    # Count history
                    cursor.execute("SELECT COUNT(*) FROM moz_places")
                    history_count = cursor.fetchone()[0]
                    
                    result["count"] = bookmark_count + history_count
                    result["details"].append(f"Overwrote places database with {bookmark_count} bookmarks and {history_count} history items")
                
                return result
            
            # For smart or append strategy, we need to merge the databases
            # This is a complex operation that requires careful handling of foreign keys
            # For simplicity, we'll implement a basic version here
            
            # Create a temporary copy of the target database
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            shutil.copy2(target_file, temp_path)
            
            try:
                # Open both databases
                with sqlite3.connect(source_file) as source_conn, sqlite3.connect(temp_path) as target_conn:
                    source_cursor = source_conn.cursor()
                    target_cursor = target_conn.cursor()
                    
                    # Get max IDs from target to avoid conflicts
                    target_cursor.execute("SELECT MAX(id) FROM moz_places")
                    max_place_id = target_cursor.fetchone()[0] or 0
                    
                    target_cursor.execute("SELECT MAX(id) FROM moz_bookmarks")
                    max_bookmark_id = target_cursor.fetchone()[0] or 0
                    
                    # Get source bookmarks
                    source_cursor.execute("""
                        SELECT b.id, b.type, b.parent, b.position, b.title, b.fk, b.dateAdded, b.lastModified, p.url
                        FROM moz_bookmarks b
                        LEFT JOIN moz_places p ON b.fk = p.id
                        WHERE b.type = 1 AND p.url IS NOT NULL
                    """)
                    
                    source_bookmarks = source_cursor.fetchall()
                    
                    # Get existing URLs in target to avoid duplicates
                    target_cursor.execute("SELECT url FROM moz_places")
                    existing_urls = {row[0] for row in target_cursor.fetchall()}
                    
                    # Insert new places and bookmarks
                    for bookmark in source_bookmarks:
                        _, b_type, parent, position, title, fk, date_added, last_modified, url = bookmark
                        
                        if url in existing_urls and options["deduplicate"]:
                            # Skip duplicate URLs if deduplication is enabled
                            continue
                        
                        # Insert place
                        target_cursor.execute("""
                            INSERT INTO moz_places (url, title, rev_host, visit_count, hidden, typed, frecency, last_visit_date)
                            VALUES (?, ?, ?, 0, 0, 0, 0, NULL)
                        """, (url, title, ''.join(reversed(url.split('/')[2])) + '.'))
                        
                        new_place_id = target_cursor.lastrowid
                        existing_urls.add(url)
                        
                        # Insert bookmark
                        target_cursor.execute("""
                            INSERT INTO moz_bookmarks (type, parent, position, title, fk, dateAdded, lastModified)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (b_type, 3, position, title, new_place_id, date_added or int(datetime.datetime.now().timestamp() * 1000000), last_modified or int(datetime.datetime.now().timestamp() * 1000000)))
                        
                        result["count"] += 1
                    
                    # Get source history if not deduplicating
                    if not options["deduplicate"]:
                        source_cursor.execute("""
                            SELECT url, title, rev_host, visit_count, hidden, typed, frecency, last_visit_date
                            FROM moz_places
                            WHERE id NOT IN (SELECT fk FROM moz_bookmarks WHERE fk IS NOT NULL)
                        """)
                        
                        source_history = source_cursor.fetchall()
                        
                        # Insert history
                        for history_item in source_history:
                            url, title, rev_host, visit_count, hidden, typed, frecency, last_visit_date = history_item
                            
                            if url in existing_urls:
                                # Skip duplicate URLs
                                continue
                            
                            target_cursor.execute("""
                                INSERT INTO moz_places (url, title, rev_host, visit_count, hidden, typed, frecency, last_visit_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (url, title, rev_host, visit_count, hidden, typed, frecency, last_visit_date))
                            
                            existing_urls.add(url)
                            result["count"] += 1
                    
                    # Commit changes
                    target_conn.commit()
                
                # Replace the target file with our merged version
                shutil.copy2(temp_path, target_file)
                
                result["details"].append(f"Merged {result['count']} items into places database")
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        except Exception as e:
            logger.error(f"Error migrating places database: {str(e)}")
            result["success"] = False
            result["error"] = f"Error migrating places database: {str(e)}"
        
        return result
    
    def _migrate_cookies_database(self, source_file: str, target_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Firefox cookies database.
        
        Args:
            source_file: Source database file path
            target_file: Target database file path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        result = {
            "success": True,
            "count": 0,
            "details": []
        }
        
        try:
            # Check if target file exists
            if not os.path.exists(target_file):
                # If target doesn't exist, just copy the file
                shutil.copy2(source_file, target_file)
                
                # Count cookies in the copied database
                with sqlite3.connect(f"file:{target_file}?mode=ro", uri=True) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_cookies")
                    cookie_count = cursor.fetchone()[0]
                    
                    result["count"] = cookie_count
                    result["details"].append(f"Copied cookies database with {cookie_count} cookies")
                
                return result
            
            # If target exists, we need to merge the databases
            if options["merge_strategy"] == "overwrite":
                # Overwrite the target file
                shutil.copy2(source_file, target_file)
                
                # Count cookies in the copied database
                with sqlite3.connect(f"file:{target_file}?mode=ro", uri=True) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM moz_cookies")
                    cookie_count = cursor.fetchone()[0]
                    
                    result["count"] = cookie_count
                    result["details"].append(f"Overwrote cookies database with {cookie_count} cookies")
                
                return result
            
            # For smart or append strategy, we need to merge the databases
            # Create a temporary copy of the target database
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            shutil.copy2(target_file, temp_path)
            
            try:
                # Open both databases
                with sqlite3.connect(source_file) as source_conn, sqlite3.connect(temp_path) as target_conn:
                    source_cursor = source_conn.cursor()
                    target_cursor = target_conn.cursor()
                    
                    # Get existing cookies in target to avoid duplicates
                    target_cursor.execute("SELECT host, name, path FROM moz_cookies")
                    existing_cookies = {(row[0], row[1], row[2]) for row in target_cursor.fetchall()}
                    
                    # Get source cookies
                    source_cursor.execute("SELECT * FROM moz_cookies")
                    columns = [description[0] for description in source_cursor.description]
                    source_cookies = source_cursor.fetchall()
                    
                    # Insert new cookies
                    for cookie in source_cookies:
                        cookie_dict = dict(zip(columns, cookie))
                        
                        # Check for duplicates
                        cookie_key = (cookie_dict["host"], cookie_dict["name"], cookie_dict["path"])
                        if cookie_key in existing_cookies and options["deduplicate"]:
                            # Skip duplicate cookies if deduplication is enabled
                            continue
                        
                        # Insert cookie
                        placeholders = ", ".join(["?"] * len(cookie))
                        target_cursor.execute(f"INSERT INTO moz_cookies VALUES ({placeholders})", cookie)
                        
                        existing_cookies.add(cookie_key)
                        result["count"] += 1
                    
                    # Commit changes
                    target_conn.commit()
                
                # Replace the target file with our merged version
                shutil.copy2(temp_path, target_file)
                
                result["details"].append(f"Merged {result['count']} cookies into database")
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        except Exception as e:
            logger.error(f"Error migrating cookies database: {str(e)}")
            result["success"] = False
            result["error"] = f"Error migrating cookies database: {str(e)}"
        
        return result
    
    def _migrate_logins_json(self, source_file: str, target_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Firefox logins.json file (passwords).
        
        Args:
            source_file: Source file path
            target_file: Target file path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        result = {
            "success": True,
            "count": 0,
            "details": []
        }
        
        try:
            # Read source logins
            with open(source_file, "r") as f:
                source_data = json.load(f)
            
            source_logins = source_data.get("logins", [])
            
            # Check if target file exists
            if not os.path.exists(target_file):
                # If target doesn't exist, just copy the file
                shutil.copy2(source_file, target_file)
                
                result["count"] = len(source_logins)
                result["details"].append(f"Copied logins.json with {result['count']} passwords")
                
                return result
            
            # If target exists, we need to merge the files
            if options["merge_strategy"] == "overwrite":
                # Overwrite the target file
                shutil.copy2(source_file, target_file)
                
                result["count"] = len(source_logins)
                result["details"].append(f"Overwrote logins.json with {result['count']} passwords")
                
                return result
            
            # For smart or append strategy, we need to merge the files
            with open(target_file, "r") as f:
                target_data = json.load(f)
            
            target_logins = target_data.get("logins", [])
            
            # Create a set of existing login URLs and usernames to avoid duplicates
            existing_logins = set()
            for login in target_logins:
                login_key = (login.get("hostname", ""), login.get("username", ""))
                existing_logins.add(login_key)
            
            # Add new logins
            for login in source_logins:
                login_key = (login.get("hostname", ""), login.get("username", ""))
                
                if login_key in existing_logins and options["deduplicate"]:
                    # Skip duplicate logins if deduplication is enabled
                    continue
                
                target_logins.append(login)
                existing_logins.add(login_key)
                result["count"] += 1
            
            # Update target data
            target_data["logins"] = target_logins
            
            # Write merged data back to target file
            with open(target_file, "w") as f:
                json.dump(target_data, f, indent=2)
            
            result["details"].append(f"Merged {result['count']} passwords into logins.json")
        except Exception as e:
            logger.error(f"Error migrating logins.json: {str(e)}")
            result["success"] = False
            result["error"] = f"Error migrating logins.json: {str(e)}"
        
        return result
    
    def _migrate_preferences_js(self, source_file: str, target_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Firefox preferences file.
        
        Args:
            source_file: Source file path
            target_file: Target file path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        result = {
            "success": True,
            "count": 0,
            "details": []
        }
        
        try:
            # Read source preferences
            with open(source_file, "r") as f:
                source_lines = f.readlines()
            
            # Parse source preferences
            source_prefs = {}
            for line in source_lines:
                line = line.strip()
                if line.startswith("user_pref(") and line.endswith(");"):
                    # Extract preference name and value
                    pref_content = line[len("user_pref("):-len(");")]
                    parts = pref_content.split(",", 1)
                    if len(parts) == 2:
                        name = parts[0].strip().strip('"\'')
                        value = parts[1].strip()
                        source_prefs[name] = value
            
            # Check if target file exists
            if not os.path.exists(target_file):
                # If target doesn't exist, just copy the file
                shutil.copy2(source_file, target_file)
                
                result["count"] = len(source_prefs)
                result["details"].append(f"Copied preferences file with {result['count']} preferences")
                
                return result
            
            # If target exists, we need to merge the files
            if options["merge_strategy"] == "overwrite":
                # Overwrite the target file
                shutil.copy2(source_file, target_file)
                
                result["count"] = len(source_prefs)
                result["details"].append(f"Overwrote preferences file with {result['count']} preferences")
                
                return result
            
            # For smart or append strategy, we need to merge the files
            with open(target_file, "r") as f:
                target_lines = f.readlines()
            
            # Parse target preferences
            target_prefs = {}
            for line in target_lines:
                line = line.strip()
                if line.startswith("user_pref(") and line.endswith(");"):
                    # Extract preference name and value
                    pref_content = line[len("user_pref("):-len(");")]
                    parts = pref_content.split(",", 1)
                    if len(parts) == 2:
                        name = parts[0].strip().strip('"\'')
                        value = parts[1].strip()
                        target_prefs[name] = value
            
            # Merge preferences
            for name, value in source_prefs.items():
                if name not in target_prefs or options["merge_strategy"] == "overwrite":
                    target_prefs[name] = value
                    result["count"] += 1
            
            # Write merged preferences back to target file
            with open(target_file, "w") as f:
                for name, value in target_prefs.items():
                    f.write(f'user_pref("{name}", {value});\n')
            
            result["details"].append(f"Merged {result['count']} preferences into file")
        except Exception as e:
            logger.error(f"Error migrating preferences file: {str(e)}")
            result["success"] = False
            result["error"] = f"Error migrating preferences file: {str(e)}"
        
        return result
    
    def _migrate_sessions_jsonlz4(self, source_file: str, target_file: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Firefox session file.
        
        Args:
            source_file: Source file path
            target_file: Target file path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        result = {
            "success": True,
            "count": 0,
            "details": []
        }
        
        try:
            # For sessions, we typically just copy the file
            # More sophisticated merging would require decompressing and parsing the LZ4 format
            
            # Check if target file exists
            if not os.path.exists(target_file) or options["merge_strategy"] == "overwrite":
                # If target doesn't exist or overwrite is specified, just copy the file
                shutil.copy2(source_file, target_file)
                
                result["count"] = 1
                result["details"].append("Copied session file")
            else:
                # For now, skip if target exists and we're not overwriting
                result["count"] = 0
                result["details"].append("Skipped existing session file")
        except Exception as e:
            logger.error(f"Error migrating session file: {str(e)}")
            result["success"] = False
            result["error"] = f"Error migrating session file: {str(e)}"
        
        return result
    
    def _migrate_chrome_to_firefox(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate data from Chrome-based browser to Firefox-based browser.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        source_path = source_profile["path"]
        target_path = target_profile["path"]
        
        # Get relevant files for the data type
        chrome_files = DATA_TYPES[data_type].get("chrome_files", [])
        firefox_files = DATA_TYPES[data_type].get("firefox_files", [])
        
        if not chrome_files or not firefox_files:
            return {"success": False, "error": f"No relevant files defined for {data_type}"}
        
        # Initialize result
        result = {
            "success": True,
            "migrated_items": 0,
            "details": []
        }
        
        # Implement specific migration logic for each data type
        if data_type == "bookmarks":
            return self._migrate_chrome_bookmarks_to_firefox(source_path, target_path, options)
        elif data_type == "history":
            return self._migrate_chrome_history_to_firefox(source_path, target_path, options)
        elif data_type == "passwords":
            return self._migrate_chrome_passwords_to_firefox(source_path, target_path, options)
        elif data_type == "cookies":
            return self._migrate_chrome_cookies_to_firefox(source_path, target_path, options)
        else:
            # For other data types, return not implemented
            return {"success": False, "error": f"Migration of {data_type} from Chrome to Firefox not implemented"}
    
    def _migrate_chrome_bookmarks_to_firefox(self, source_path: str, target_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Chrome bookmarks to Firefox.
        
        Args:
            source_path: Source profile path
            target_path: Target profile path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        result = {
            "success": True,
            "migrated_items": 0,
            "details": []
        }
        
        try:
            # Chrome bookmarks file
            chrome_bookmarks_file = os.path.join(source_path, "Bookmarks")
            
            if not os.path.exists(chrome_bookmarks_file):
                return {"success": False, "error": "Chrome bookmarks file not found"}
            
            # Firefox places database
            firefox_places_file = os.path.join(target_path, "places.sqlite")
            
            # Read Chrome bookmarks
            with open(chrome_bookmarks_file, "r") as f:
                bookmarks_data = json.load(f)
            
            # Extract bookmarks from Chrome format
            bookmarks = []
            
            def extract_bookmarks(node, parent_path=""):
                if "type" not in node:
                    return
                
                if node["type"] == "url":
                    bookmarks.append({
                        "title": node.get("name", ""),
                        "url": node.get("url", ""),
                        "added_date": node.get("date_added", ""),
                        "path": parent_path
                    })
                elif node["type"] == "folder":
                    folder_name = node.get("name", "")
                    new_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
                    
                    for child in node.get("children", []):
                        extract_bookmarks(child, new_path)
            
            # Process bookmark roots
            for root_name, root in bookmarks_data.get("roots", {}).items():
                if root_name in ["bookmark_bar", "other", "synced"]:
                    extract_bookmarks(root, root_name)
            
            # Check if Firefox places database exists
            if not os.path.exists(firefox_places_file):
                # Create a new places database (simplified)
                result["success"] = False
                result["error"] = "Firefox places database not found and creation not implemented"
                return result
            
            # Import bookmarks into Firefox places database
            with sqlite3.connect(firefox_places_file) as conn:
                cursor = conn.cursor()
                
                # Get existing URLs to avoid duplicates
                cursor.execute("SELECT url FROM moz_places")
                existing_urls = {row[0] for row in cursor.fetchall()}
                
                # Get max IDs to avoid conflicts
                cursor.execute("SELECT MAX(id) FROM moz_places")
                max_place_id = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT MAX(id) FROM moz_bookmarks")
                max_bookmark_id = cursor.fetchone()[0] or 0
                
                # Get bookmark folders
                cursor.execute("SELECT id, title FROM moz_bookmarks WHERE type = 2")
                folders = {row[1]: row[0] for row in cursor.fetchall()}
                
                # Create necessary folders
                for bookmark in bookmarks:
                    path_parts = bookmark["path"].split("/")
                    current_parent = 3  # Firefox's "Other Bookmarks" folder
                    
                    # Map Chrome root folders to Firefox folders
                    if path_parts[0] == "bookmark_bar":
                        current_parent = 2  # Firefox's "Bookmarks Toolbar" folder
                    elif path_parts[0] == "other":
                        current_parent = 3  # Firefox's "Other Bookmarks" folder
                    elif path_parts[0] == "synced":
                        current_parent = 5  # Firefox's "Mobile Bookmarks" folder
                    
                    # Create folder hierarchy
                    for i in range(1, len(path_parts)):
                        folder_path = "/".join(path_parts[:i+1])
                        if folder_path not in folders:
                            # Create folder
                            cursor.execute("""
                                INSERT INTO moz_bookmarks (type, parent, position, title, dateAdded, lastModified)
                                VALUES (2, ?, 0, ?, ?, ?)
                            """, (
                                current_parent,
                                path_parts[i],
                                int(datetime.datetime.now().timestamp() * 1000000),
                                int(datetime.datetime.now().timestamp() * 1000000)
                            ))
                            
                            folders[folder_path] = cursor.lastrowid
                        
                        current_parent = folders[folder_path]
                
                # Import bookmarks
                for bookmark in bookmarks:
                    url = bookmark["url"]
                    
                    if url in existing_urls and options["deduplicate"]:
                        # Skip duplicate URLs if deduplication is enabled
                        continue
                    
                    # Determine parent folder
                    parent_id = 3  # Default to "Other Bookmarks"
                    
                    path_parts = bookmark["path"].split("/")
                    if path_parts[0] == "bookmark_bar":
                        parent_id = 2  # "Bookmarks Toolbar"
                    elif path_parts[0] == "other":
                        parent_id = 3  # "Other Bookmarks"
                    elif path_parts[0] == "synced":
                        parent_id = 5  # "Mobile Bookmarks"
                    
                    # Use created folder if available
                    if bookmark["path"] in folders:
                        parent_id = folders[bookmark["path"]]
                    
                    # Insert place
                    cursor.execute("""
                        INSERT INTO moz_places (url, title, rev_host, visit_count, hidden, typed, frecency, last_visit_date)
                        VALUES (?, ?, ?, 0, 0, 0, 0, NULL)
                    """, (
                        url,
                        bookmark["title"],
                        ''.join(reversed(url.split('/')[2])) + '.' if '://' in url and len(url.split('/')) > 2 else ''
                    ))
                    
                    place_id = cursor.lastrowid
                    existing_urls.add(url)
                    
                    # Insert bookmark
                    cursor.execute("""
                        INSERT INTO moz_bookmarks (type, parent, position, title, fk, dateAdded, lastModified)
                        VALUES (1, ?, 0, ?, ?, ?, ?)
                    """, (
                        parent_id,
                        bookmark["title"],
                        place_id,
                        int(bookmark["added_date"]) if bookmark["added_date"] else int(datetime.datetime.now().timestamp() * 1000000),
                        int(datetime.datetime.now().timestamp() * 1000000)
                    ))
                    
                    result["migrated_items"] += 1
                
                # Commit changes
                conn.commit()
            
            result["details"].append(f"Migrated {result['migrated_items']} bookmarks from Chrome to Firefox")
        except Exception as e:
            logger.error(f"Error migrating Chrome bookmarks to Firefox: {str(e)}")
            result["success"] = False
            result["error"] = f"Error migrating Chrome bookmarks to Firefox: {str(e)}"
        
        return result
    
    def _migrate_chrome_history_to_firefox(self, source_path: str, target_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Chrome history to Firefox.
        
        Args:
            source_path: Source profile path
            target_path: Target profile path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # Implementation would be similar to bookmarks migration but for history
        # This is a placeholder for the actual implementation
        return {"success": False, "error": "Migration of history from Chrome to Firefox not implemented"}
    
    def _migrate_chrome_passwords_to_firefox(self, source_path: str, target_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Chrome passwords to Firefox.
        
        Args:
            source_path: Source profile path
            target_path: Target profile path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # Implementation would handle Chrome's encrypted password database
        # This is a placeholder for the actual implementation
        return {"success": False, "error": "Migration of passwords from Chrome to Firefox not implemented"}
    
    def _migrate_chrome_cookies_to_firefox(self, source_path: str, target_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate Chrome cookies to Firefox.
        
        Args:
            source_path: Source profile path
            target_path: Target profile path
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # Implementation would handle Chrome's cookie database
        # This is a placeholder for the actual implementation
        return {"success": False, "error": "Migration of cookies from Chrome to Firefox not implemented"}
    
    def _migrate_firefox_to_chrome(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate data from Firefox-based browser to Chrome-based browser.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # This is a placeholder for the actual implementation
        return {"success": False, "error": f"Migration of {data_type} from Firefox to Chrome not implemented"}
    
    def _migrate_chrome_to_chrome(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate data from Chrome-based browser to Chrome-based browser.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # This is a placeholder for the actual implementation
        return {"success": False, "error": f"Migration of {data_type} between Chrome-based browsers not implemented"}
    
    def _migrate_safari_to_firefox(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate data from Safari to Firefox-based browser.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # This is a placeholder for the actual implementation
        return {"success": False, "error": f"Migration of {data_type} from Safari to Firefox not implemented"}
    
    def _migrate_webkit_to_firefox(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate data from WebKit-based browser to Firefox-based browser.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # This is a placeholder for the actual implementation
        return {"success": False, "error": f"Migration of {data_type} from WebKit-based browser to Firefox not implemented"}
    
    def _migrate_text_to_firefox(
        self,
        data_type: str,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Migrate data from text-based browser to Firefox-based browser.
        
        Args:
            data_type: Data type to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            
        Returns:
            Dict[str, Any]: Migration result
        """
        # This is a placeholder for the actual implementation
        return {"success": False, "error": f"Migration of {data_type} from text-based browser to Firefox not implemented"}
