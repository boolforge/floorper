"""
Floorper - CLI Interface

This module provides a command-line interface for Floorper,
allowing for scripted and automated profile migrations.
"""

import os
import sys
import logging
import argparse
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from core.browser_detector import BrowserDetector
from core.profile_migrator import ProfileMigrator
from core.backup_manager import BackupManager
from utils.app_info import get_app_info

# Setup logging
logger = logging.getLogger('floorper.cli')

class FloorperCLI:
    """Command-line interface for the Floorper application."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.browser_detector = BrowserDetector()
        self.profile_migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI with the given arguments.
        
        Args:
            args: Command-line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        if args is None:
            args = sys.argv[1:]
        
        # Parse arguments
        parser = argparse.ArgumentParser(
            description="Floorper - Universal Browser Profile Migration Tool for Floorp"
        )
        
        # Add subparsers for commands
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # List command
        list_parser = subparsers.add_parser("list", help="List detected browsers and profiles")
        list_parser.add_argument(
            "--json", 
            action="store_true", 
            help="Output in JSON format"
        )
        
        # Migrate command
        migrate_parser = subparsers.add_parser("migrate", help="Migrate a browser profile")
        migrate_parser.add_argument(
            "--source", 
            required=True, 
            help="Source profile path"
        )
        migrate_parser.add_argument(
            "--target", 
            required=True, 
            help="Target profile path"
        )
        migrate_parser.add_argument(
            "--data-types", 
            help="Data types to migrate (comma-separated)"
        )
        
        # Backup command
        backup_parser = subparsers.add_parser("backup", help="Backup and restore profiles")
        backup_subparsers = backup_parser.add_subparsers(dest="backup_command", help="Backup command")
        
        # Create backup command
        create_parser = backup_subparsers.add_parser("create", help="Create a profile backup")
        create_parser.add_argument(
            "--profile", 
            required=True, 
            help="Profile path to backup"
        )
        create_parser.add_argument(
            "--browser", 
            required=True, 
            help="Browser type"
        )
        create_parser.add_argument(
            "--output", 
            help="Output directory for backup file"
        )
        
        # Restore backup command
        restore_parser = backup_subparsers.add_parser("restore", help="Restore a profile backup")
        restore_parser.add_argument(
            "--backup", 
            required=True, 
            help="Backup file to restore"
        )
        restore_parser.add_argument(
            "--target", 
            required=True, 
            help="Target directory to restore to"
        )
        
        # Version command
        version_parser = subparsers.add_parser("version", help="Show version information")
        
        # Parse arguments
        parsed_args = parser.parse_args(args)
        
        # Execute command
        if parsed_args.command == "list":
            return self._list_browsers(parsed_args.json)
        elif parsed_args.command == "migrate":
            return self._migrate_profile(
                parsed_args.source,
                parsed_args.target,
                parsed_args.data_types
            )
        elif parsed_args.command == "backup":
            if parsed_args.backup_command == "create":
                return self._create_backup(
                    parsed_args.profile,
                    parsed_args.browser,
                    parsed_args.output
                )
            elif parsed_args.backup_command == "restore":
                return self._restore_backup(
                    parsed_args.backup,
                    parsed_args.target
                )
            else:
                logger.error("No backup command specified")
                return 1
        elif parsed_args.command == "version":
            return self._show_version()
        else:
            logger.error("No command specified")
            parser.print_help()
            return 1
    
    def _list_browsers(self, json_output: bool = False) -> int:
        """
        List detected browsers and their profiles.
        
        Args:
            json_output: Whether to output in JSON format
            
        Returns:
            Exit code
        """
        try:
            # Detect browsers
            browsers = self.browser_detector.detect_browsers()
            
            if json_output:
                # Output as JSON
                browser_data = []
                
                for browser in browsers:
                    profiles = self.browser_detector.get_profiles(browser["id"])
                    browser_data.append({
                        "id": browser["id"],
                        "name": browser["name"],
                        "version": browser.get("version", ""),
                        "path": browser.get("path", ""),
                        "profiles": profiles
                    })
                
                print(json.dumps(browser_data, indent=2))
            else:
                # Output as text
                print(f"Detected {len(browsers)} browsers:")
                
                for browser in browsers:
                    print(f"\n{browser['name']} ({browser['id']})")
                    if "version" in browser:
                        print(f"  Version: {browser['version']}")
                    if "path" in browser:
                        print(f"  Path: {browser['path']}")
                    
                    # Get profiles
                    profiles = self.browser_detector.get_profiles(browser["id"])
                    
                    print(f"  Profiles ({len(profiles)}):")
                    for profile in profiles:
                        print(f"    - {profile['name']}")
                        print(f"      Path: {profile['path']}")
            
            return 0
        except Exception as e:
            logger.error(f"Error listing browsers: {e}")
            return 1
    
    def _migrate_profile(
        self, 
        source_path: str, 
        target_path: str, 
        data_types: Optional[str] = None
    ) -> int:
        """
        Migrate a browser profile.
        
        Args:
            source_path: Path to source profile
            target_path: Path to target profile
            data_types: Data types to migrate (comma-separated)
            
        Returns:
            Exit code
        """
        try:
            # Parse data types
            data_type_list = None
            if data_types:
                data_type_list = [dt.strip() for dt in data_types.split(",")]
            
            # Create source and target profile objects
            source_profile = {
                "path": source_path
            }
            
            target_profile = {
                "path": target_path
            }
            
            # Migrate profile
            print(f"Migrating profile from {source_path} to {target_path}...")
            
            result = self.profile_migrator.migrate_profile(
                source_profile,
                target_profile,
                data_type_list
            )
            
            if result.get("success", False):
                print("Migration completed successfully")
                return 0
            else:
                logger.error(f"Migration failed: {result.get('error', 'Unknown error')}")
                return 1
        except Exception as e:
            logger.error(f"Error migrating profile: {e}")
            return 1
    
    def _create_backup(
        self, 
        profile_path: str, 
        browser_type: str, 
        output_dir: Optional[str] = None
    ) -> int:
        """
        Create a backup of a browser profile.
        
        Args:
            profile_path: Path to profile
            browser_type: Browser type
            output_dir: Output directory for backup file
            
        Returns:
            Exit code
        """
        try:
            # Create backup
            print(f"Creating backup of {browser_type} profile at {profile_path}...")
            
            backup_file = self.backup_manager.create_backup(
                profile_path,
                browser_type,
                output_dir
            )
            
            print(f"Backup created: {backup_file}")
            return 0
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return 1
    
    def _restore_backup(self, backup_file: str, target_dir: str) -> int:
        """
        Restore a backup to a target directory.
        
        Args:
            backup_file: Path to backup file
            target_dir: Target directory to restore to
            
        Returns:
            Exit code
        """
        try:
            # Restore backup
            print(f"Restoring backup {backup_file} to {target_dir}...")
            
            self.backup_manager.restore_backup(
                backup_file,
                target_dir
            )
            
            print("Backup restored successfully")
            return 0
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return 1
    
    def _show_version(self) -> int:
        """
        Show version information.
        
        Returns:
            Exit code
        """
        app_info = get_app_info()
        
        print(f"Floorper {app_info['version']}")
        print(f"{app_info['description']}")
        print(f"Author: {app_info['author']}")
        print(f"License: {app_info['license']}")
        print(f"Running on {app_info['platform']} with Python {app_info['python_version']}")
        
        return 0

# Command-line entry point
def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code
    """
    cli = FloorperCLI()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main())
