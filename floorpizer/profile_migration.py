"""
Profile migration functionality for Floorpizer.
Handles the migration of browser profiles to Floorp.
"""

import os
import sys
import json
import shutil
import logging
import sqlite3
import tempfile
import platform
import configparser
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import lz4.block

from .config import (
    BROWSERS,
    FLOORP,
    PROFILE_ITEMS,
    MIGRATION_RULES,
    BACKUP_SUFFIX,
    EXCLUDE_PATTERNS,
    CRITICAL_FILES,
    MAX_WORKERS
)

from .utils import (
    safe_file_operation,
    safe_db_connection,
    decompress_lz4,
    compress_lz4,
    calculate_file_hash,
    get_file_info,
    verify_json_file,
    verify_sqlite_db,
    format_size
)

logger = logging.getLogger(__name__)

class MigrationError(Exception):
    """Base exception for migration errors."""
    pass

class ProfileMigrator:
    """Handles the migration of browser profiles to Floorp."""
    
    def __init__(self):
        self.migration_stats = {
            "files_copied": 0,
            "files_modified": 0,
            "files_skipped": 0,
            "files_cleaned": 0,
            "errors": 0
        }
        self.backup_path: Optional[Path] = None
        self.target_profile_path: Optional[Path] = None
    
    def migrate_profile(self, source_profile: Union[str, Path], 
                       target_profile: Union[str, Path], 
                       merge: bool = False) -> bool:
        """Migrate a profile from source to target location."""
        try:
            source_profile = Path(source_profile)
            target_profile = Path(target_profile)
            self.target_profile_path = target_profile
            
            # Validate profiles
            if not source_profile.exists():
                raise MigrationError(f"Source profile does not exist: {source_profile}")
            
            # Check disk space
            if not self._check_disk_space(source_profile, target_profile):
                raise MigrationError("Insufficient disk space")
            
            # Create backup if target exists
            if target_profile.exists():
                self.backup_path = self._create_backup(target_profile)
                if not self.backup_path:
                    raise MigrationError("Failed to create backup")
            
            # Create target directory
            target_profile.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            self._copy_files(source_profile, target_profile)
            
            # Handle Floorp-specific files
            self._handle_floorp_specific_files(target_profile)
            
            # Modify files for Floorp compatibility
            self._modify_compatibility_ini(target_profile)
            self._modify_prefs_js(target_profile)
            self._modify_extensions_json(target_profile)
            self._modify_addon_startup(target_profile)
            self._modify_session_store(target_profile)
            
            # Optimize profile
            self._optimize_profile(target_profile)
            
            # Clean target profile
            self._clean_profile(target_profile)
            
            # Verify migration
            if not self._verify_migration(target_profile):
                raise MigrationError("Migration verification failed")
            
            logger.info("Profile migration completed successfully")
            self._print_migration_stats()
            return True
            
        except Exception as e:
            logger.error(f"Error during profile migration: {e}")
            self._restore_backup()
            return False
    
    def _check_disk_space(self, source: Path, target: Path) -> bool:
        """Check if there's enough disk space for migration."""
        try:
            # Get free space in target directory
            target_free = shutil.disk_usage(target.parent).free
            
            # Calculate required space (source + backup + 20% buffer)
            source_size = sum(f.stat().st_size 
                            for f in source.rglob("*") 
                            if f.is_file())
            
            required_space = source_size * 2.2  # Source + backup + 20% buffer
            
            if target_free < required_space:
                logger.error(f"Not enough disk space. Required: {format_size(required_space)}, "
                           f"Available: {format_size(target_free)}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking disk space: {e}")
            return False
    
    def _create_backup(self, profile_path: Path) -> Optional[Path]:
        """Create a backup of the profile."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_name = f"{profile_path.name}_backup_{timestamp}"
            backup_path = profile_path.parent / backup_name
            
            logger.info(f"Creating backup in {backup_path}")
            shutil.copytree(profile_path, backup_path)
            logger.info("Backup created successfully")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def _copy_files(self, source: Path, target: Path) -> None:
        """Copy files from source to target using parallel processing."""
        def copy_file(src_file: Path, tgt_file: Path) -> bool:
            try:
                shutil.copy2(src_file, tgt_file)
                self.migration_stats["files_copied"] += 1
                return True
            except Exception as e:
                logger.error(f"Error copying file {src_file}: {e}")
                self.migration_stats["errors"] += 1
                return False
        
        # Create target directories
        for root, dirs, _ in os.walk(source):
            rel_path = Path(root).relative_to(source)
            target_dir = target / rel_path
            target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files in parallel
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for root, _, files in os.walk(source):
                for file in files:
                    src_file = Path(root) / file
                    if self._should_exclude(src_file) and file not in CRITICAL_FILES:
                        self.migration_stats["files_skipped"] += 1
                        continue
                    
                    rel_path = src_file.relative_to(source)
                    tgt_file = target / rel_path
                    futures.append(executor.submit(copy_file, src_file, tgt_file))
            
            # Wait for all copies to complete
            for future in as_completed(futures):
                future.result()
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded from migration."""
        path_str = str(path).lower()
        return any(pattern.lower() in path_str for pattern in EXCLUDE_PATTERNS)
    
    def _handle_floorp_specific_files(self, profile_path: Path) -> None:
        """Create Floorp-specific files and directories."""
        try:
            # Create directories
            for dir_name in FLOORP.dirs:
                dir_path = profile_path / dir_name
                dir_path.mkdir(exist_ok=True)
            
            # Create files
            for file_name in FLOORP.files:
                file_path = profile_path / file_name
                if not file_path.exists():
                    with safe_file_operation(file_path, 'w') as f:
                        if file_name.endswith('.json'):
                            json.dump({}, f)
                        elif file_name.endswith('.mozlz4'):
                            f.write(b"mozLz40\0")
            
            # Create default workspace
            workspaces_dir = profile_path / "Workspaces"
            if workspaces_dir.exists():
                default_workspace = {
                    "name": "Default Workspace",
                    "tabs": [],
                    "created": int(datetime.now().timestamp()),
                    "lastAccessed": int(datetime.now().timestamp())
                }
                with safe_file_operation(workspaces_dir / "default.json", 'w') as f:
                    json.dump(default_workspace, f)
        
        except Exception as e:
            logger.error(f"Error handling Floorp-specific files: {e}")
            raise MigrationError(f"Failed to create Floorp structure: {e}")
    
    def _modify_compatibility_ini(self, profile_path: Path) -> None:
        """Modify compatibility.ini for Floorp compatibility."""
        compat_file = profile_path / "compatibility.ini"
        try:
            config = configparser.ConfigParser()
            
            if compat_file.exists():
                with safe_file_operation(compat_file) as f:
                    config.read_file(f)
            else:
                config["Compatibility"] = {}
            
            # Update compatibility settings
            config["Compatibility"].update({
                "LastVersion": f"{FLOORP.version}/20230718150114",
                "LastOSABI": "WINNT_x86_64-msvc" if os.name == "nt" else "Linux_x86_64-gcc3",
                "LastPlatformDir": "C:\\Program Files\\Floorp" if os.name == "nt" else "/usr/lib/floorp"
            })
            
            with safe_file_operation(compat_file, 'w') as f:
                config.write(f)
            
            self.migration_stats["files_modified"] += 1
            
        except Exception as e:
            logger.error(f"Error modifying compatibility.ini: {e}")
            raise MigrationError(f"Failed to modify compatibility.ini: {e}")
    
    def _modify_prefs_js(self, profile_path: Path) -> None:
        """Modify prefs.js for Floorp compatibility."""
        prefs_file = profile_path / "prefs.js"
        if not prefs_file.exists():
            return
        
        try:
            with safe_file_operation(prefs_file) as f:
                lines = f.readlines()
            
            # Patterns to search and replace
            replacements = {
                r'user_pref\("app\.update\.channel",\s*".*?"\);': 
                f'user_pref("app.update.channel", "release");',
                r'user_pref\("extensions\.lastAppVersion",\s*".*?"\);': 
                f'user_pref("extensions.lastAppVersion", "{FLOORP.version}");',
                r'user_pref\("extensions\.lastPlatformVersion",\s*".*?"\);': 
                f'user_pref("extensions.lastPlatformVersion", "{FLOORP.version}");',
                r'user_pref\("browser\.startup\.homepage_override\.mstone",\s*".*?"\);': 
                f'user_pref("browser.startup.homepage_override.mstone", "{FLOORP.version}");'
            }
            
            # Patterns to filter
            filter_patterns = [
                r'user_pref\("app\.update\.lastUpdateTime\..*?",\s*\d+\);',
                r'user_pref\("gecko\.handlerService\.defaultHandlersVersion",\s*\d+\);'
            ]
            
            # Apply changes
            new_lines = []
            modified = False
            
            for line in lines:
                # Check if line should be filtered
                if any(re.match(pattern, line) for pattern in filter_patterns):
                    modified = True
                    continue
                
                # Apply replacements
                line_modified = False
                for pattern, replacement in replacements.items():
                    if re.match(pattern, line):
                        new_line = re.sub(pattern, replacement, line)
                        new_lines.append(new_line)
                        modified = True
                        line_modified = True
                        break
                
                if not line_modified:
                    new_lines.append(line)
            
            # Save changes if modified
            if modified:
                with safe_file_operation(prefs_file, 'w') as f:
                    f.writelines(new_lines)
                self.migration_stats["files_modified"] += 1
        
        except Exception as e:
            logger.error(f"Error modifying prefs.js: {e}")
            raise MigrationError(f"Failed to modify prefs.js: {e}")
    
    def _modify_extensions_json(self, profile_path: Path) -> None:
        """Modify extensions.json for Floorp compatibility."""
        extensions_file = profile_path / "extensions.json"
        if not extensions_file.exists():
            return
        
        try:
            with safe_file_operation(extensions_file) as f:
                data = json.load(f)
            
            modified = False
            
            # Process extensions
            if "addons" in data:
                for addon in data["addons"]:
                    # Remove telemetry data
                    if "installTelemetryInfo" in addon:
                        del addon["installTelemetryInfo"]
                        modified = True
                    
                    # Update version information
                    if "version" in addon and "appVersion" in addon:
                        addon["appVersion"] = FLOORP.version
                        modified = True
                    
                    # Modify target applications
                    if "targetApplications" in addon:
                        for app in addon["targetApplications"]:
                            if app.get("id") == FLOORP.app_id:
                                pass
                            elif "nightly" in app.get("id", "").lower():
                                app["id"] = FLOORP.app_id
                                modified = True
            
            # Save changes if modified
            if modified:
                with safe_file_operation(extensions_file, 'w') as f:
                    json.dump(data, f, indent=2)
                self.migration_stats["files_modified"] += 1
        
        except Exception as e:
            logger.error(f"Error modifying extensions.json: {e}")
            raise MigrationError(f"Failed to modify extensions.json: {e}")
    
    def _modify_addon_startup(self, profile_path: Path) -> None:
        """Modify addonStartup.json.lz4 for Floorp compatibility."""
        addon_startup_file = profile_path / "addonStartup.json.lz4"
        if not addon_startup_file.exists():
            return
        
        try:
            with safe_file_operation(addon_startup_file, 'rb') as f:
                compressed_data = f.read()
            
            try:
                decompressed_data = decompress_lz4(compressed_data)
                data = json.loads(decompressed_data)
                
                modified = False
                
                # Process addon startup data
                for section in ["app-system-defaults", "app-global"]:
                    if section in data:
                        for key in data[section]:
                            for addon in data[section][key]:
                                if "version" in addon:
                                    addon["version"] = FLOORP.version
                                    modified = True
                
                # Save changes if modified
                if modified:
                    new_json_data = json.dumps(data).encode("utf-8")
                    compressed_data = compress_lz4(new_json_data)
                    
                    with safe_file_operation(addon_startup_file, 'wb') as f:
                        f.write(compressed_data)
                    
                    self.migration_stats["files_modified"] += 1
            
            except Exception as e:
                logger.warning(f"Error processing addonStartup.json.lz4: {e}")
                logger.warning("This file will be recreated by Floorp, not critical")
        
        except Exception as e:
            logger.error(f"Error processing addonStartup.json.lz4: {e}")
            raise MigrationError(f"Failed to modify addonStartup.json.lz4: {e}")
    
    def _modify_session_store(self, profile_path: Path) -> None:
        """Modify session files for Floorp compatibility."""
        session_file = profile_path / "sessionstore.jsonlz4"
        if session_file.exists():
            try:
                with safe_file_operation(session_file, 'rb') as f:
                    compressed_data = f.read()
                
                try:
                    decompressed_data = decompress_lz4(compressed_data)
                    data = json.loads(decompressed_data)
                    
                    # Modify version information
                    if "version" in data:
                        data["version"] = [FLOORP.version, FLOORP.version]
                        
                        # Recompress and save
                        new_json_data = json.dumps(data).encode("utf-8")
                        compressed_data = compress_lz4(new_json_data)
                        
                        with safe_file_operation(session_file, 'wb') as f:
                            f.write(compressed_data)
                        
                        self.migration_stats["files_modified"] += 1
                
                except Exception as e:
                    logger.warning(f"Error processing sessionstore.jsonlz4: {e}")
                    logger.warning("This file will be recreated by Floorp, not critical")
            
            except Exception as e:
                logger.error(f"Error processing sessionstore.jsonlz4: {e}")
                raise MigrationError(f"Failed to modify sessionstore.jsonlz4: {e}")
        
        # Process session backup folder
        backup_dir = profile_path / "sessionstore-backups"
        if backup_dir.exists():
            backup_files = [
                backup_dir / "recovery.jsonlz4",
                backup_dir / "previous.jsonlz4",
                backup_dir / "upgrade.jsonlz4-build"
            ]
            
            for backup_file in backup_files:
                if backup_file.exists():
                    try:
                        with safe_file_operation(backup_file, 'rb') as f:
                            compressed_data = f.read()
                        
                        try:
                            decompressed_data = decompress_lz4(compressed_data)
                            data = json.loads(decompressed_data)
                            
                            if "version" in data:
                                data["version"] = [FLOORP.version, FLOORP.version]
                                
                                new_json_data = json.dumps(data).encode("utf-8")
                                compressed_data = compress_lz4(new_json_data)
                                
                                with safe_file_operation(backup_file, 'wb') as f:
                                    f.write(compressed_data)
                                
                                self.migration_stats["files_modified"] += 1
                        
                        except Exception as e:
                            logger.warning(f"Error processing backup file {backup_file}: {e}")
                            logger.warning("This file will be recreated by Floorp, not critical")
                    
                    except Exception as e:
                        logger.error(f"Error processing backup file {backup_file}: {e}")
                        raise MigrationError(f"Failed to modify backup file: {e}")
    
    def _optimize_profile(self, profile_path: Path) -> None:
        """Optimize profile files for better performance."""
        try:
            # Optimize SQLite databases
            sqlite_files = [
                "places.sqlite",
                "favicons.sqlite",
                "cookies.sqlite",
                "formhistory.sqlite",
                "permissions.sqlite",
                "content-prefs.sqlite",
                "storage.sqlite",
                "webappsstore.sqlite"
            ]
            
            for file in sqlite_files:
                file_path = profile_path / file
                if file_path.exists() and verify_sqlite_db(file_path):
                    with safe_db_connection(file_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("VACUUM")
                        cursor.execute("ANALYZE")
            
            # Optimize session store
            session_file = profile_path / "sessionstore.jsonlz4"
            if session_file.exists():
                try:
                    with safe_file_operation(session_file, 'rb') as f:
                        compressed_data = f.read()
                    
                    decompressed_data = decompress_lz4(compressed_data)
                    data = json.loads(decompressed_data)
                    
                    # Preserve essential session data
                    if "windows" in data:
                        for window in data["windows"]:
                            if "tabs" in window:
                                for tab in window["tabs"]:
                                    # Keep essential tab data
                                    essential_keys = [
                                        "entries", "index", "hidden", "lastAccessed",
                                        "title", "favicon", "lastAccessed", "userTypedValue",
                                        "scroll", "zoom", "pinned", "groupID"
                                    ]
                                    tab_data = {k: v for k, v in tab.items() if k in essential_keys}
                                    tab.clear()
                                    tab.update(tab_data)
                    
                    # Recompress and save
                    new_json_data = json.dumps(data).encode("utf-8")
                    compressed_data = compress_lz4(new_json_data)
                    
                    with safe_file_operation(session_file, 'wb') as f:
                        f.write(compressed_data)
                
                except Exception as e:
                    logger.warning(f"Error optimizing session store: {e}")
        
        except Exception as e:
            logger.error(f"Error optimizing profile: {e}")
            raise MigrationError(f"Failed to optimize profile: {e}")
    
    def _clean_profile(self, profile_path: Path) -> None:
        """Clean up unnecessary files from the profile."""
        cleaned = 0
        for root, dirs, files in os.walk(profile_path):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            
            # Remove excluded files
            for file in files:
                file_path = Path(root) / file
                if self._should_exclude(file_path) and file not in CRITICAL_FILES:
                    try:
                        file_path.unlink()
                        cleaned += 1
                        logger.info(f"Cleaned file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error cleaning file {file_path}: {e}")
                        self.migration_stats["errors"] += 1
        
        self.migration_stats["files_cleaned"] = cleaned
    
    def _verify_migration(self, profile_path: Path) -> bool:
        """Verify the integrity of migrated files."""
        critical_files = [
            'prefs.js',
            'extensions.json',
            'compatibility.ini',
            'places.sqlite',
            'cookies.sqlite',
            'sessionstore.jsonlz4'
        ]
        
        for file in critical_files:
            file_path = profile_path / file
            if file_path.exists():
                if not self._verify_file_integrity(file_path):
                    logger.error(f"Critical file {file} failed integrity check")
                    return False
            else:
                logger.warning(f"Critical file {file} not found")
        
        return True
    
    def _verify_file_integrity(self, file_path: Path) -> bool:
        """Verify file integrity by checking if it can be read and parsed."""
        try:
            if file_path.suffix == '.json':
                with safe_file_operation(file_path) as f:
                    json.load(f)
            elif file_path.suffix == '.jsonlz4':
                with safe_file_operation(file_path, 'rb') as f:
                    decompress_lz4(f.read())
            elif file_path.suffix == '.sqlite':
                with safe_db_connection(file_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return True
        except Exception as e:
            logger.error(f"File integrity check failed for {file_path}: {e}")
            return False
    
    def _restore_backup(self) -> bool:
        """Restore from backup if migration failed."""
        if self.backup_path and self.backup_path.exists():
            try:
                logger.info("Restoring from backup...")
                if self.target_profile_path.exists():
                    shutil.rmtree(self.target_profile_path)
                shutil.copytree(self.backup_path, self.target_profile_path)
                logger.info("Backup restored successfully")
                return True
            except Exception as e:
                logger.error(f"Error restoring backup: {e}")
                return False
        return False
    
    def _print_migration_stats(self) -> None:
        """Print migration statistics."""
        logger.info("Migration Statistics:")
        logger.info(f"Files copied: {self.migration_stats['files_copied']}")
        logger.info(f"Files modified: {self.migration_stats['files_modified']}")
        logger.info(f"Files skipped: {self.migration_stats['files_skipped']}")
        logger.info(f"Files cleaned: {self.migration_stats['files_cleaned']}")
        logger.info(f"Errors: {self.migration_stats['errors']}") 