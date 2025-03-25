"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides the command-line interface for the Floorper application,
allowing for scripted and automated profile migrations.
"""

import os
import sys
import logging
import argparse
import json
from typing import Dict, List, Optional, Any, Tuple

from floorper.core import FloorperCore

# Setup logging
logger = logging.getLogger('floorper.cli')

class FloorperCLI:
    """
    Command-line interface for the Floorper application.
    
    This class provides a comprehensive CLI for browser profile migration,
    supporting both interactive and non-interactive modes.
    """
    
    def __init__(self, controller: Optional[FloorperCore] = None):
        """
        Initialize the CLI.
        
        Args:
            controller: Optional FloorperCore controller instance
        """
        self.controller = controller or FloorperCore()
        
        # Configure logging
        self._setup_logging()
        
        logger.info("CLI initialized")
    
    def _setup_logging(self):
        """Configure logging for the CLI."""
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    def run(self, args=None):
        """
        Run the CLI application.
        
        Args:
            args: Command-line arguments (defaults to sys.argv)
        """
        try:
            # Parse arguments
            parser = self._create_parser()
            parsed_args = parser.parse_args(args)
            
            # Process arguments
            if parsed_args.version:
                self._show_version()
                return
            
            if parsed_args.list_browsers:
                self._list_browsers()
                return
            
            if parsed_args.list_profiles:
                self._list_profiles(parsed_args.browser)
                return
            
            if parsed_args.interactive:
                self._run_interactive()
                return
            
            # Validate required arguments for migration
            if not parsed_args.source_browser:
                logger.error("Source browser not specified")
                print("Error: Source browser not specified. Use --source-browser or -s.")
                return
            
            if not parsed_args.source_profile:
                logger.error("Source profile not specified")
                print("Error: Source profile not specified. Use --source-profile or -p.")
                return
            
            if not parsed_args.target_profile:
                logger.error("Target profile not specified")
                print("Error: Target profile not specified. Use --target-profile or -t.")
                return
            
            # Perform migration
            self._perform_migration(
                parsed_args.source_browser,
                parsed_args.source_profile,
                parsed_args.target_profile,
                parsed_args.data_types,
                {
                    "backup": not parsed_args.no_backup,
                    "deduplicate": not parsed_args.no_deduplicate,
                    "merge_strategy": parsed_args.merge_strategy
                }
            )
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
            print("\nOperation cancelled by user")
        except Exception as e:
            logger.error(f"Error in CLI: {str(e)}")
            print(f"Error: {str(e)}")
    
    def _create_parser(self):
        """
        Create the argument parser.
        
        Returns:
            ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="Floorper - Universal Browser Profile Migration Tool for Floorp",
            epilog="For more information, visit: https://github.com/boolforge/floorper"
        )
        
        # General options
        parser.add_argument(
            "-v", "--version",
            action="store_true",
            help="Show version information and exit"
        )
        
        parser.add_argument(
            "-i", "--interactive",
            action="store_true",
            help="Run in interactive mode"
        )
        
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--log-file",
            help="Log file path"
        )
        
        # Information options
        parser.add_argument(
            "--list-browsers",
            action="store_true",
            help="List detected browsers and exit"
        )
        
        parser.add_argument(
            "--list-profiles",
            action="store_true",
            help="List profiles for a browser and exit"
        )
        
        parser.add_argument(
            "--browser",
            help="Browser ID for --list-profiles"
        )
        
        # Migration options
        parser.add_argument(
            "-s", "--source-browser",
            help="Source browser ID"
        )
        
        parser.add_argument(
            "-p", "--source-profile",
            help="Source profile name or path"
        )
        
        parser.add_argument(
            "-t", "--target-profile",
            help="Target Floorp profile name or path"
        )
        
        parser.add_argument(
            "-d", "--data-types",
            nargs="+",
            default=["bookmarks", "history", "passwords", "cookies", "extensions", "preferences", "sessions"],
            choices=["bookmarks", "history", "passwords", "cookies", "extensions", "preferences", "sessions", "all"],
            help="Data types to migrate (default: all)"
        )
        
        parser.add_argument(
            "--merge-strategy",
            choices=["smart", "append", "overwrite"],
            default="smart",
            help="Merge strategy (default: smart)"
        )
        
        parser.add_argument(
            "--no-backup",
            action="store_true",
            help="Disable backup before migration"
        )
        
        parser.add_argument(
            "--no-deduplicate",
            action="store_true",
            help="Disable deduplication"
        )
        
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results in JSON format"
        )
        
        parser.add_argument(
            "--config",
            help="Path to configuration file"
        )
        
        return parser
    
    def _show_version(self):
        """Show version information."""
        print("Floorper - Universal Browser Profile Migration Tool for Floorp")
        print("Version: 1.0.0")
        print("Copyright (c) 2025 BoolForge")
    
    def _list_browsers(self):
        """List detected browsers."""
        print("Detecting browsers...")
        browsers = self.controller.detect_browsers()
        
        if not browsers:
            print("No browsers detected.")
            return
        
        print(f"\nDetected {len(browsers)} browsers:\n")
        
        # Calculate column widths
        id_width = max(len("ID"), max(len(b.get("id", "")) for b in browsers))
        name_width = max(len("Name"), max(len(b.get("name", "")) for b in browsers))
        version_width = max(len("Version"), max(len(str(b.get("version", ""))) for b in browsers))
        
        # Print header
        print(f"{'ID':{id_width}} | {'Name':{name_width}} | {'Version':{version_width}} | Path")
        print(f"{'-' * id_width}-+-{'-' * name_width}-+-{'-' * version_width}-+-------")
        
        # Print browsers
        for browser in browsers:
            print(
                f"{browser.get('id', ''):{id_width}} | "
                f"{browser.get('name', ''):{name_width}} | "
                f"{browser.get('version', ''):{version_width}} | "
                f"{browser.get('path', '')}"
            )
    
    def _list_profiles(self, browser_id):
        """
        List profiles for a browser.
        
        Args:
            browser_id: Browser identifier
        """
        if not browser_id:
            print("Error: Browser ID not specified. Use --browser.")
            return
        
        print(f"Detecting profiles for browser '{browser_id}'...")
        profiles = self.controller.get_browser_profiles(browser_id)
        
        if not profiles:
            print(f"No profiles detected for browser '{browser_id}'.")
            return
        
        print(f"\nDetected {len(profiles)} profiles for browser '{browser_id}':\n")
        
        # Calculate column widths
        name_width = max(len("Name"), max(len(p.get("name", "")) for p in profiles))
        
        # Print header
        print(f"{'Name':{name_width}} | Path")
        print(f"{'-' * name_width}-+-------")
        
        # Print profiles
        for profile in profiles:
            print(
                f"{profile.get('name', ''):{name_width}} | "
                f"{profile.get('path', '')}"
            )
    
    def _run_interactive(self):
        """Run in interactive mode."""
        print("Floorper - Universal Browser Profile Migration Tool for Floorp")
        print("Interactive Mode\n")
        
        # Detect browsers
        print("Detecting browsers...")
        browsers = self.controller.detect_browsers()
        
        if not browsers:
            print("No browsers detected.")
            return
        
        # Select source browser
        source_browser = self._select_browser(browsers, "source", exclude_id="floorp")
        if not source_browser:
            return
        
        # Select source profile
        source_profiles = self.controller.get_browser_profiles(source_browser.get("id"))
        if not source_profiles:
            print(f"No profiles detected for browser '{source_browser.get('name')}'.")
            return
        
        source_profile = self._select_profile(source_profiles, "source")
        if not source_profile:
            return
        
        # Select target profile (Floorp)
        floorp_browser = next((b for b in browsers if b.get("id") == "floorp"), None)
        if not floorp_browser:
            print("Floorp browser not detected.")
            return
        
        target_profiles = self.controller.get_browser_profiles(floorp_browser.get("id"))
        if not target_profiles:
            print("No Floorp profiles detected.")
            return
        
        target_profile = self._select_profile(target_profiles, "target Floorp")
        if not target_profile:
            return
        
        # Select data types
        data_types = self._select_data_types()
        if not data_types:
            return
        
        # Configure options
        options = self._configure_options()
        
        # Confirm migration
        print("\nMigration Summary:")
        print(f"Source: {source_browser.get('name')} - {source_profile.get('name')}")
        print(f"Target: Floorp - {target_profile.get('name')}")
        print(f"Data Types: {', '.join(dt.capitalize() for dt in data_types)}")
        print(f"Backup: {'Yes' if options.get('backup', True) else 'No'}")
        print(f"Deduplicate: {'Yes' if options.get('deduplicate', True) else 'No'}")
        print(f"Merge Strategy: {options.get('merge_strategy', 'smart').capitalize()}")
        
        confirm = input("\nStart migration? (y/n): ").lower()
        if confirm != 'y':
            print("Migration cancelled.")
            return
        
        # Perform migration
        self._perform_migration(
            source_browser.get("id"),
            source_profile.get("name"),
            target_profile.get("name"),
            data_types,
            options
        )
    
    def _select_browser(self, browsers, browser_type, exclude_id=None):
        """
        Select a browser from a list.
        
        Args:
            browsers: List of browsers
            browser_type: Type of browser (source/target)
            exclude_id: Optional browser ID to exclude
            
        Returns:
            Selected browser or None
        """
        # Filter browsers
        if exclude_id:
            filtered_browsers = [b for b in browsers if b.get("id") != exclude_id]
        else:
            filtered_browsers = browsers
        
        if not filtered_browsers:
            print(f"No suitable {browser_type} browsers detected.")
            return None
        
        print(f"\nSelect {browser_type} browser:")
        
        for i, browser in enumerate(filtered_browsers):
            print(f"{i + 1}. {browser.get('name')} {browser.get('version', '')}")
        
        while True:
            try:
                choice = input(f"\nEnter {browser_type} browser number (or 'q' to quit): ")
                
                if choice.lower() == 'q':
                    print("Operation cancelled.")
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(filtered_browsers):
                    return filtered_browsers[index]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def _select_profile(self, profiles, profile_type):
        """
        Select a profile from a list.
        
        Args:
            profiles: List of profiles
            profile_type: Type of profile (source/target)
            
        Returns:
            Selected profile or None
        """
        print(f"\nSelect {profile_type} profile:")
        
        for i, profile in enumerate(profiles):
            print(f"{i + 1}. {profile.get('name')}")
        
        while True:
            try:
                choice = input(f"\nEnter {profile_type} profile number (or 'q' to quit): ")
                
                if choice.lower() == 'q':
                    print("Operation cancelled.")
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(profiles):
                    return profiles[index]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def _select_data_types(self):
        """
        Select data types to migrate.
        
        Returns:
            List of selected data types
        """
        data_types = ["bookmarks", "history", "passwords", "cookies", "extensions", "preferences", "sessions"]
        selected_data_types = data_types.copy()
        
        print("\nSelect data types to migrate:")
        print("(All types are selected by default. Enter numbers to toggle selection.)")
        
        while True:
            # Show current selection
            for i, data_type in enumerate(data_types):
                selected = data_type in selected_data_types
                print(f"{i + 1}. {data_type.capitalize()} {'[X]' if selected else '[ ]'}")
            
            print("\nOptions:")
            print("1-7: Toggle individual data types")
            print("a: Select all")
            print("n: Select none")
            print("c: Continue with current selection")
            print("q: Quit")
            
            choice = input("\nEnter your choice: ").lower()
            
            if choice == 'q':
                print("Operation cancelled.")
                return None
            elif choice == 'c':
                if not selected_data_types:
                    print("Error: No data types selected. Please select at least one.")
                    continue
                return selected_data_types
            elif choice == 'a':
                selected_data_types = data_types.copy()
            elif choice == 'n':
                selected_data_types = []
            elif choice in ['1', '2', '3', '4', '5', '6', '7']:
                index = int(choice) - 1
                data_type = data_types[index]
                
                if data_type in selected_data_types:
                    selected_data_types.remove(data_type)
                else:
                    selected_data_types.append(data_type)
            else:
                print("Invalid choice. Please try again.")
    
    def _configure_options(self):
        """
        Configure migration options.
        
        Returns:
            Dictionary of options
        """
        options = {
            "backup": True,
            "deduplicate": True,
            "merge_strategy": "smart"
        }
        
        print("\nConfigure migration options:")
        
        # Backup option
        backup = input("Create backup before migration? (Y/n): ").lower()
        options["backup"] = backup != 'n'
        
        # Deduplicate option
        deduplicate = input("Deduplicate items? (Y/n): ").lower()
        options["deduplicate"] = deduplicate != 'n'
        
        # Merge strategy
        print("\nSelect merge strategy:")
        print("1. Smart Merge (Recommended) - Intelligently merges data, avoiding duplicates")
        print("2. Append Only - Adds new data without modifying existing data")
        print("3. Overwrite - Replaces existing data with new data")
        
        while True:
            strategy = input("\nEnter strategy number (1-3): ")
            
            if strategy == '1':
                options["merge_strategy"] = "smart"
                break
            elif strategy == '2':
                options["merge_strategy"] = "append"
                break
            elif strategy == '3':
                options["merge_strategy"] = "overwrite"
                break
            else:
                print("Invalid choice. Please try again.")
        
        return options
    
    def _perform_migration(self, source_browser_id, source_profile_name, target_profile_name, data_types, options):
        """
        Perform the migration.
        
        Args:
            source_browser_id: Source browser ID
            source_profile_name: Source profile name
            target_profile_name: Target profile name
            data_types: Data types to migrate
            options: Migration options
        """
        # Handle 'all' data type
        if "all" in data_types:
            data_types = ["bookmarks", "history", "passwords", "cookies", "extensions", "preferences", "sessions"]
        
        # Get source profile
        source_profiles = self.controller.get_browser_profiles(source_browser_id)
        source_profile = next((p for p in source_profiles if p.get("name") == source_profile_name), None)
        
        if not source_profile:
            print(f"Error: Source profile '{source_profile_name}' not found.")
            return
        
        # Get target profile
        floorp_browser = next((b for b in self.controller.detect_browsers() if b.get("id") == "floorp"), None)
        if not floorp_browser:
            print("Error: Floorp browser not detected.")
            return
        
        target_profiles = self.controller.get_browser_profiles(floorp_browser.get("id"))
        target_profile = next((p for p in target_profiles if p.get("name") == target_profile_name), None)
        
        if not target_profile:
            print(f"Error: Target profile '{target_profile_name}' not found.")
            return
        
        # Perform migration
        print("\nStarting migration...")
        print(f"Source: {source_browser_id} - {source_profile_name}")
        print(f"Target: Floorp - {target_profile_name}")
        print(f"Data Types: {', '.join(dt.capitalize() for dt in data_types)}")
        
        # Show progress
        for data_type in data_types:
            print(f"Migrating {data_type.capitalize()}...")
        
        # Actual migration
        result = self.controller.migrate_profile(
            source_profile,
            target_profile,
            data_types,
            options
        )
        
        # Show results
        self._show_migration_results(result)
    
    def _show_migration_results(self, result):
        """
        Show migration results.
        
        Args:
            result: Migration result
        """
        success = result.get("success", False)
        
        if success:
            print("\nMigration completed successfully!")
        else:
            print(f"\nMigration completed with issues: {result.get('message', '')}")
        
        print("\nDetails:")
        
        for data_type, data_result in result.get("details", {}).items():
            success = data_result.get("success", False)
            message = data_result.get("message", "")
            stats = data_result.get("stats", {})
            
            status = "Success" if success else "Failed"
            
            print(f"- {data_type.capitalize()}: {status}")
            if message:
                print(f"  Message: {message}")
            
            if stats:
                print("  Statistics:")
                for key, value in stats.items():
                    print(f"    {key}: {value}")


def main():
    """Main entry point for the CLI."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create controller
    controller = FloorperCore()
    
    # Create and run CLI
    cli = FloorperCLI(controller)
    cli.run()


if __name__ == "__main__":
    main()
