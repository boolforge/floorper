#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - CLI Interface
======================

Command-line interface for Floorper.
Provides a simple CLI for browser profile detection and migration.
"""

import os
import sys
import logging
import argparse
import json
from typing import Dict, List, Optional, Any, Tuple, Union, Set

from ..core.constants import BROWSERS, DATA_TYPES
from ..core.browser_detector import BrowserDetector
from ..core.profile_migrator import ProfileMigrator
from ..core.backup_manager import BackupManager

logger = logging.getLogger(__name__)

class FloorperCLI:
    """Command-line interface for Floorper."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.detector = BrowserDetector()
        self.migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("floorper.log")
            ]
        )
    
    def parse_args(self):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description="Floorper - Browser Profile Migration Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # List all detected browser profiles
  floorper list
  
  # List all detected Firefox profiles
  floorper list --browser firefox
  
  # Migrate from Firefox to Chrome
  floorper migrate --source "/path/to/firefox/profile" --target "/path/to/chrome/profile" --data bookmarks,history
  
  # Create a backup of a profile
  floorper backup create --profile "/path/to/profile" --browser firefox
  
  # List available backups
  floorper backup list
  
  # Restore a backup
  floorper backup restore --backup "/path/to/backup.zip" --target "/path/to/restore/directory"
"""
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # List command
        list_parser = subparsers.add_parser("list", help="List browser profiles")
        list_parser.add_argument("--browser", help="Filter by browser ID")
        list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
        
        # Migrate command
        migrate_parser = subparsers.add_parser("migrate", help="Migrate browser profiles")
        migrate_parser.add_argument("--source", required=True, help="Source profile path")
        migrate_parser.add_argument("--source-browser", help="Source browser ID (auto-detected if not specified)")
        migrate_parser.add_argument("--target", required=True, help="Target profile path")
        migrate_parser.add_argument("--target-browser", help="Target browser ID (auto-detected if not specified)")
        migrate_parser.add_argument("--data", help="Data types to migrate (comma-separated, default: all)")
        migrate_parser.add_argument("--no-backup", action="store_true", help="Skip backup before migration")
        migrate_parser.add_argument("--no-deduplicate", action="store_true", help="Don't deduplicate items")
        migrate_parser.add_argument("--merge-strategy", choices=["smart", "overwrite", "append"], default="smart", help="Merge strategy")
        
        # Backup commands
        backup_parser = subparsers.add_parser("backup", help="Manage backups")
        backup_subparsers = backup_parser.add_subparsers(dest="backup_command", help="Backup command")
        
        # Backup create
        backup_create_parser = backup_subparsers.add_parser("create", help="Create a backup")
        backup_create_parser.add_argument("--profile", required=True, help="Profile path to backup")
        backup_create_parser.add_argument("--browser", required=True, help="Browser ID")
        backup_create_parser.add_argument("--name", help="Profile name (default: extracted from path)")
        
        # Backup list
        backup_list_parser = backup_subparsers.add_parser("list", help="List available backups")
        backup_list_parser.add_argument("--browser", help="Filter by browser ID")
        backup_list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
        
        # Backup restore
        backup_restore_parser = backup_subparsers.add_parser("restore", help="Restore a backup")
        backup_restore_parser.add_argument("--backup", required=True, help="Backup file path")
        backup_restore_parser.add_argument("--target", help="Target directory (default: original location)")
        backup_restore_parser.add_argument("--merge", action="store_true", help="Merge with existing files")
        
        # Backup verify
        backup_verify_parser = backup_subparsers.add_parser("verify", help="Verify a backup")
        backup_verify_parser.add_argument("--backup", required=True, help="Backup file path")
        
        # Version command
        version_parser = subparsers.add_parser("version", help="Show version information")
        
        return parser.parse_args()
    
    def run(self):
        """Run the CLI application."""
        args = self.parse_args()
        
        if not args.command:
            print("Error: No command specified. Use --help for usage information.")
            return 1
        
        try:
            if args.command == "list":
                return self.cmd_list(args)
            elif args.command == "migrate":
                return self.cmd_migrate(args)
            elif args.command == "backup":
                if not args.backup_command:
                    print("Error: No backup command specified. Use 'floorper backup --help' for usage information.")
                    return 1
                
                if args.backup_command == "create":
                    return self.cmd_backup_create(args)
                elif args.backup_command == "list":
                    return self.cmd_backup_list(args)
                elif args.backup_command == "restore":
                    return self.cmd_backup_restore(args)
                elif args.backup_command == "verify":
                    return self.cmd_backup_verify(args)
            elif args.command == "version":
                return self.cmd_version(args)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            print(f"Error: {str(e)}")
            return 1
        
        return 0
    
    def cmd_list(self, args):
        """List browser profiles."""
        profiles = self.detector.detect_all_profiles()
        
        # Filter by browser if specified
        if args.browser:
            profiles = [p for p in profiles if p["browser_id"] == args.browser]
        
        if not profiles:
            print("No browser profiles found.")
            return 0
        
        if args.json:
            # Output in JSON format
            print(json.dumps(profiles, indent=2))
        else:
            # Output in human-readable format
            print(f"Found {len(profiles)} browser profiles:")
            for i, profile in enumerate(profiles):
                browser_name = BROWSERS.get(profile["browser_id"], {}).get("name", "Unknown Browser")
                print(f"{i+1}. {browser_name} - {profile['name']}")
                print(f"   Path: {profile['path']}")
                print(f"   Browser ID: {profile['browser_id']}")
                print()
        
        return 0
    
    def cmd_migrate(self, args):
        """Migrate browser profiles."""
        # Prepare source profile
        source_path = os.path.abspath(args.source)
        if not os.path.exists(source_path):
            print(f"Error: Source profile path does not exist: {source_path}")
            return 1
        
        source_browser_id = args.source_browser
        if not source_browser_id:
            # Auto-detect source browser
            detected_browser = self.detector.detect_browser_from_path(source_path)
            if not detected_browser:
                print(f"Error: Could not auto-detect source browser. Please specify --source-browser.")
                return 1
            source_browser_id = detected_browser
        
        source_profile = {
            "path": source_path,
            "browser_id": source_browser_id,
            "name": os.path.basename(source_path)
        }
        
        # Prepare target profile
        target_path = os.path.abspath(args.target)
        if not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
        
        target_browser_id = args.target_browser
        if not target_browser_id:
            # Auto-detect target browser
            detected_browser = self.detector.detect_browser_from_path(target_path)
            if not detected_browser:
                print(f"Error: Could not auto-detect target browser. Please specify --target-browser.")
                return 1
            target_browser_id = detected_browser
        
        target_profile = {
            "path": target_path,
            "browser_id": target_browser_id,
            "name": os.path.basename(target_path)
        }
        
        # Prepare data types
        data_types = None
        if args.data:
            data_types = args.data.split(",")
            # Validate data types
            invalid_types = [dt for dt in data_types if dt not in DATA_TYPES]
            if invalid_types:
                print(f"Error: Invalid data types: {', '.join(invalid_types)}")
                print(f"Valid data types: {', '.join(DATA_TYPES.keys())}")
                return 1
        
        # Prepare options
        options = {
            "backup": not args.no_backup,
            "deduplicate": not args.no_deduplicate,
            "merge_strategy": args.merge_strategy
        }
        
        # Perform migration
        print(f"Migrating from {source_browser_id} to {target_browser_id}...")
        
        if options["backup"]:
            print("Creating backup of target profile...")
            backup_path = self.backup_manager.create_backup(
                target_profile["path"],
                target_profile["browser_id"],
                target_profile["name"]
            )
            
            if backup_path:
                print(f"Backup created: {backup_path}")
            else:
                print("Warning: Failed to create backup, continuing without backup")
        
        result = self.migrator.migrate_profile(
            source_profile,
            target_profile,
            data_types,
            options
        )
        
        if result["success"]:
            migrated_items = sum(
                result["migrated_data"].get(dt, {}).get("migrated_items", 0)
                for dt in (data_types or DATA_TYPES.keys())
            )
            print(f"Migration successful! Migrated {migrated_items} items.")
            return 0
        else:
            errors = result.get("errors", [])
            print(f"Migration failed with {len(errors)} errors:")
            for error in errors:
                print(f"- {error}")
            return 1
    
    def cmd_backup_create(self, args):
        """Create a backup."""
        profile_path = os.path.abspath(args.profile)
        if not os.path.exists(profile_path):
            print(f"Error: Profile path does not exist: {profile_path}")
            return 1
        
        browser_id = args.browser
        profile_name = args.name or os.path.basename(profile_path)
        
        print(f"Creating backup of {browser_id} profile '{profile_name}'...")
        
        backup_path = self.backup_manager.create_backup(
            profile_path,
            browser_id,
            profile_name
        )
        
        if backup_path:
            print(f"Backup created: {backup_path}")
            return 0
        else:
            print("Error: Failed to create backup.")
            return 1
    
    def cmd_backup_list(self, args):
        """List available backups."""
        backups = self.backup_manager.list_backups(args.browser)
        
        if not backups:
            print("No backups found.")
            return 0
        
        if args.json:
            # Output in JSON format
            print(json.dumps(backups, indent=2))
        else:
            # Output in human-readable format
            print(f"Found {len(backups)} backups:")
            for i, backup in enumerate(backups):
                browser_id = backup.get("browser_id", "")
                browser_name = BROWSERS.get(browser_id, {}).get("name", "Unknown Browser")
                profile_name = backup.get("profile_name", "")
                created_at = backup.get("created_at", "")
                
                summary = backup.get("summary", {})
                file_count = summary.get("file_count", 0)
                total_size = summary.get("total_size", 0)
                size_str = f"{total_size / 1024 / 1024:.2f} MB" if total_size else "Unknown"
                
                print(f"{i+1}. {browser_name} - {profile_name}")
                print(f"   Created: {created_at}")
                print(f"   Files: {file_count}")
                print(f"   Size: {size_str}")
                print(f"   Path: {backup.get('path', '')}")
                print()
        
        return 0
    
    def cmd_backup_restore(self, args):
        """Restore a backup."""
        backup_path = os.path.abspath(args.backup)
        if not os.path.exists(backup_path):
            print(f"Error: Backup file does not exist: {backup_path}")
            return 1
        
        target_path = args.target
        merge = args.merge
        
        print(f"Restoring backup from {backup_path}...")
        
        # Verify backup first
        is_valid, verification_results = self.backup_manager.verify_backup(backup_path)
        if not is_valid:
            error = verification_results.get("error", "Unknown error")
            print(f"Error: Backup verification failed: {error}")
            return 1
        
        success = self.backup_manager.restore_backup(
            backup_path,
            target_path,
            merge
        )
        
        if success:
            print("Backup restored successfully.")
            return 0
        else:
            print("Error: Failed to restore backup.")
            return 1
    
    def cmd_backup_verify(self, args):
        """Verify a backup."""
        backup_path = os.path.abspath(args.backup)
        if not os.path.exists(backup_path):
            print(f"Error: Backup file does not exist: {backup_path}")
            return 1
        
        print(f"Verifying backup: {backup_path}...")
        
        is_valid, verification_results = self.backup_manager.verify_backup(backup_path)
        
        if is_valid:
            metadata = verification_results.get("metadata", {})
            verified_files = verification_results.get("verified_files", 0)
            
            browser_id = metadata.get("browser_id", "")
            browser_name = BROWSERS.get(browser_id, {}).get("name", "Unknown Browser")
            profile_name = metadata.get("profile_name", "")
            
            print(f"Backup is valid!")
            print(f"Browser: {browser_name}")
            print(f"Profile: {profile_name}")
            print(f"Verified files: {verified_files}")
            return 0
        else:
            error = verification_results.get("error", "Unknown error")
            missing_files = verification_results.get("missing_files", [])
            corrupted_files = verification_results.get("corrupted_files", [])
            
            print(f"Backup verification failed: {error}")
            
            if missing_files:
                print(f"Missing files: {len(missing_files)}")
                for file in missing_files[:5]:
                    print(f"- {file}")
                if len(missing_files) > 5:
                    print(f"  ... and {len(missing_files) - 5} more")
            
            if corrupted_files:
                print(f"Corrupted files: {len(corrupted_files)}")
                for file in corrupted_files[:5]:
                    print(f"- {file}")
                if len(corrupted_files) > 5:
                    print(f"  ... and {len(corrupted_files) - 5} more")
            
            return 1
    
    def cmd_version(self, args):
        """Show version information."""
        print("Floorper - Browser Profile Migration Tool")
        print("Version: 1.0.0")
        print("https://github.com/boolforge/floorper")
        return 0


def main():
    """Run the Floorper CLI application."""
    cli = FloorperCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
