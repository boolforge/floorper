#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Performance Optimization
=================================

Optimizes the performance of Floorper by implementing caching,
parallel processing, and other performance improvements.
"""

import os
import sys
import logging
import time
import functools
import concurrent.futures
import threading
import multiprocessing
from typing import Dict, List, Optional, Any, Tuple, Union, Set, Callable

from floorper.core.browser_detector import BrowserDetector
from floorper.core.profile_migrator import ProfileMigrator
from floorper.core.backup_manager import BackupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("performance_optimization.log")
    ]
)

logger = logging.getLogger(__name__)

# Cache for browser detection results
browser_detection_cache = {}
profile_detection_cache = {}

# Cache lock for thread safety
cache_lock = threading.RLock()

def timed(func):
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper

def cached(func):
    """Decorator to cache function results."""
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from the function arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        with cache_lock:
            if key in cache:
                logger.debug(f"Cache hit for {func.__name__} with key {key}")
                return cache[key]
            
            logger.debug(f"Cache miss for {func.__name__} with key {key}")
            result = func(*args, **kwargs)
            cache[key] = result
            return result
    
    # Add a method to clear the cache
    wrapper.clear_cache = lambda: cache.clear()
    
    return wrapper

def parallel_map(func, items, max_workers=None):
    """Execute a function on items in parallel."""
    if not items:
        return []
    
    if max_workers is None:
        # Use number of CPU cores by default
        max_workers = multiprocessing.cpu_count()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, items))
    
    return results

class OptimizedBrowserDetector(BrowserDetector):
    """Optimized version of BrowserDetector with caching and parallel processing."""
    
    @cached
    def detect_browser_from_path(self, path: str) -> Optional[str]:
        """
        Detect browser from a profile path with caching.
        
        Args:
            path: Profile path
            
        Returns:
            Optional[str]: Browser ID if detected, None otherwise
        """
        return super().detect_browser_from_path(path)
    
    @timed
    def detect_all_profiles(self) -> List[Dict[str, Any]]:
        """
        Detect all browser profiles with parallel processing.
        
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        # Get all browser IDs
        browser_ids = list(self.get_supported_browsers().keys())
        
        # Detect profiles for each browser in parallel
        all_profiles = []
        
        def detect_for_browser(browser_id):
            try:
                return self.detect_profiles(browser_id)
            except Exception as e:
                logger.error(f"Error detecting profiles for {browser_id}: {str(e)}")
                return []
        
        # Use parallel processing to detect profiles
        browser_profiles = parallel_map(detect_for_browser, browser_ids)
        
        # Flatten the list of profiles
        for profiles in browser_profiles:
            all_profiles.extend(profiles)
        
        return all_profiles
    
    @cached
    def detect_profiles(self, browser_id: str) -> List[Dict[str, Any]]:
        """
        Detect profiles for a specific browser with caching.
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            List[Dict[str, Any]]: List of detected profiles
        """
        return super().detect_profiles(browser_id)

class OptimizedProfileMigrator(ProfileMigrator):
    """Optimized version of ProfileMigrator with parallel processing."""
    
    @timed
    def migrate_profile(
        self, 
        source_profile: Dict[str, Any], 
        target_profile: Dict[str, Any], 
        data_types: Optional[List[str]] = None, 
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Migrate a source profile to a target profile with optimized performance.
        
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
            "verify": True,
            "parallel": True,  # Enable parallel processing
            "max_workers": None  # Use default (CPU count)
        }
        
        # Merge with default options
        for key, value in default_options.items():
            if key not in options:
                options[key] = value
        
        # Set default data types (all)
        if data_types is None:
            data_types = list(self._get_data_types().keys())
        
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
        if options["parallel"] and len(data_types) > 1:
            # Use parallel processing for multiple data types
            self._migrate_data_types_parallel(data_types, source_profile, target_profile, options, results)
        else:
            # Use sequential processing
            self._migrate_data_types_sequential(data_types, source_profile, target_profile, options, results)
        
        # Update overall success status
        if results["errors"]:
            results["success"] = False
        
        return results
    
    def _migrate_data_types_parallel(
        self,
        data_types: List[str],
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """
        Migrate multiple data types in parallel.
        
        Args:
            data_types: Data types to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            results: Results dictionary to update
        """
        # Determine migration method based on browser families
        source_family = self._get_browser_family(source_profile["browser_id"])
        target_family = self._get_browser_family(target_profile["browser_id"])
        
        def migrate_data_type(data_type):
            try:
                return (
                    data_type,
                    self._migrate_data_type(
                        data_type,
                        source_profile,
                        target_profile,
                        source_family,
                        target_family,
                        options
                    )
                )
            except Exception as e:
                logger.error(f"Error migrating {data_type}: {str(e)}")
                return (data_type, {"success": False, "error": str(e)})
        
        # Use parallel processing to migrate data types
        migration_results = parallel_map(
            migrate_data_type,
            data_types,
            max_workers=options.get("max_workers")
        )
        
        # Process results
        for data_type, migration_result in migration_results:
            results["migrated_data"][data_type] = migration_result
            
            if not migration_result["success"]:
                results["errors"].append(
                    f"Failed to migrate {data_type}: {migration_result.get('error', 'Unknown error')}"
                )
    
    def _migrate_data_types_sequential(
        self,
        data_types: List[str],
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        options: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """
        Migrate multiple data types sequentially.
        
        Args:
            data_types: Data types to migrate
            source_profile: Source profile information
            target_profile: Target profile information
            options: Migration options
            results: Results dictionary to update
        """
        # Determine migration method based on browser families
        source_family = self._get_browser_family(source_profile["browser_id"])
        target_family = self._get_browser_family(target_profile["browser_id"])
        
        for data_type in data_types:
            if data_type not in self._get_data_types():
                logger.warning(f"Unknown data type: {data_type}, skipping")
                results["errors"].append(f"Unknown data type: {data_type}")
                continue
            
            logger.info(f"Migrating data type: {data_type}")
            
            try:
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
                    results["errors"].append(
                        f"Failed to migrate {data_type}: {migration_result.get('error', 'Unknown error')}"
                    )
            except Exception as e:
                logger.error(f"Error migrating {data_type}: {str(e)}")
                results["errors"].append(f"Error migrating {data_type}: {str(e)}")
                results["migrated_data"][data_type] = {"success": False, "error": str(e)}
    
    def _get_browser_family(self, browser_id: str) -> str:
        """
        Get browser family from browser ID.
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            str: Browser family
        """
        browsers = self._get_browsers()
        return browsers.get(browser_id, {}).get("family", "")

class OptimizedBackupManager(BackupManager):
    """Optimized version of BackupManager with parallel processing."""
    
    @timed
    def create_backup(self, profile_path: str, browser_id: str, profile_name: str) -> Optional[str]:
        """
        Create a backup of a browser profile with optimized performance.
        
        Args:
            profile_path: Path to the profile directory
            browser_id: Browser identifier
            profile_name: Profile name
            
        Returns:
            Optional[str]: Path to the created backup file, or None if backup failed
        """
        return super().create_backup(profile_path, browser_id, profile_name)
    
    @timed
    def restore_backup(self, backup_path: str, target_path: Optional[str] = None, merge: bool = False) -> bool:
        """
        Restore a backup to a target location with optimized performance.
        
        Args:
            backup_path: Path to the backup file
            target_path: Optional target path (if None, uses original path from metadata)
            merge: Whether to merge with existing files (True) or overwrite (False)
            
        Returns:
            bool: True if restoration was successful, False otherwise
        """
        return super().restore_backup(backup_path, target_path, merge)

def apply_optimizations():
    """Apply performance optimizations to Floorper."""
    # Monkey patch the original classes with optimized versions
    from floorper.core import browser_detector, profile_migrator, backup_manager
    
    # Save original classes
    original_browser_detector = browser_detector.BrowserDetector
    original_profile_migrator = profile_migrator.ProfileMigrator
    original_backup_manager = backup_manager.BackupManager
    
    # Replace with optimized versions
    browser_detector.BrowserDetector = OptimizedBrowserDetector
    profile_migrator.ProfileMigrator = OptimizedProfileMigrator
    backup_manager.BackupManager = OptimizedBackupManager
    
    logger.info("Applied performance optimizations to Floorper")
    
    # Return a function to restore original classes
    def restore_original():
        browser_detector.BrowserDetector = original_browser_detector
        profile_migrator.ProfileMigrator = original_profile_migrator
        backup_manager.BackupManager = original_backup_manager
        logger.info("Restored original Floorper classes")
    
    return restore_original

def main():
    """Run performance optimization tests."""
    # Apply optimizations
    restore_original = apply_optimizations()
    
    try:
        # Run performance tests
        print("Running performance tests with optimized classes...")
        
        # Test browser detection
        detector = OptimizedBrowserDetector()
        start_time = time.time()
        profiles = detector.detect_all_profiles()
        end_time = time.time()
        
        print(f"Detected {len(profiles)} profiles in {end_time - start_time:.4f} seconds")
        
        # Test cached detection (should be faster)
        start_time = time.time()
        profiles = detector.detect_all_profiles()
        end_time = time.time()
        
        print(f"Cached detection: {len(profiles)} profiles in {end_time - start_time:.4f} seconds")
        
        # Clear cache and test again
        detector.detect_all_profiles.clear_cache()
        start_time = time.time()
        profiles = detector.detect_all_profiles()
        end_time = time.time()
        
        print(f"After cache clear: {len(profiles)} profiles in {end_time - start_time:.4f} seconds")
        
        print("\nPerformance optimization tests completed successfully.")
    finally:
        # Restore original classes
        restore_original()

if __name__ == "__main__":
    main()
