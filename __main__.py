"""
Floorper - Main Entry Point

This module serves as the main entry point for the Floorper application,
providing automatic interface selection based on environment and command-line arguments.
"""

import os
import sys
import argparse
import logging
from typing import Optional, List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('floorper')

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the Floorper application.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if args is None:
        args = sys.argv[1:]
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Floorper - Universal Browser Profile Migration Tool for Floorp"
    )
    parser.add_argument(
        "--gui", 
        action="store_true", 
        help="Start with graphical user interface"
    )
    parser.add_argument(
        "--tui", 
        action="store_true", 
        help="Start with text-based user interface"
    )
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Start with command-line interface"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--version", 
        action="store_true", 
        help="Show version information and exit"
    )
    
    # Add CLI-specific arguments
    cli_group = parser.add_argument_group("CLI options")
    cli_group.add_argument(
        "command", 
        nargs="?", 
        help="CLI command (list, migrate, backup, restore)"
    )
    cli_group.add_argument(
        "--source", 
        help="Source profile path for migration"
    )
    cli_group.add_argument(
        "--target", 
        help="Target profile path for migration or restoration"
    )
    cli_group.add_argument(
        "--profile", 
        help="Profile path for backup"
    )
    cli_group.add_argument(
        "--browser", 
        help="Browser type for operations"
    )
    cli_group.add_argument(
        "--backup", 
        help="Backup file path for restoration"
    )
    
    parsed_args = parser.parse_args(args)
    
    # Configure logging
    if parsed_args.verbose:
        logging.getLogger('floorper').setLevel(logging.DEBUG)
    
    # Show version and exit if requested
    if parsed_args.version:
        from utils.app_info import get_app_info
        app_info = get_app_info()
        print(f"Floorper {app_info['version']}")
        print(f"Running on {app_info['platform']} with Python {app_info['python_version']}")
        return 0
    
    # Determine which interface to use
    if parsed_args.gui:
        return _run_gui()
    elif parsed_args.cli:
        return _run_cli(parsed_args)
    elif parsed_args.tui:
        return _run_tui()
    else:
        # Auto-detect: Use GUI if available, otherwise TUI, finally CLI
        if _is_gui_available():
            return _run_gui()
        else:
            return _run_tui()

def _is_gui_available() -> bool:
    """
    Check if GUI is available.
    
    Returns:
        True if GUI is available, False otherwise
    """
    # Check if running in a graphical environment
    if os.environ.get('DISPLAY') or os.name == 'nt' or sys.platform == 'darwin':
        try:
            # Try to import PyQt6
            from PyQt6.QtWidgets import QApplication
            return True
        except ImportError:
            return False
    return False

def _run_gui() -> int:
    """
    Run the GUI interface.
    
    Returns:
        Exit code
    """
    try:
        from interfaces.gui import FloorperGUI
        app = FloorperGUI()
        return app.run()
    except ImportError as e:
        logger.error(f"Failed to start GUI: {e}")
        logger.error("Please install PyQt6 with: pip install PyQt6")
        return 1

def _run_tui() -> int:
    """
    Run the TUI interface.
    
    Returns:
        Exit code
    """
    try:
        from interfaces.tui import FloorperTUI
        app = FloorperTUI()
        return app.run()
    except ImportError as e:
        logger.error(f"Failed to start TUI: {e}")
        logger.error("Please install Textual with: pip install textual")
        return 1

def _run_cli(args: argparse.Namespace) -> int:
    """
    Run the CLI interface.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code
    """
    from interfaces.cli import FloorperCLI
    cli = FloorperCLI()
    
    if not args.command:
        logger.error("No command specified for CLI mode")
        return 1
    
    if args.command == "list":
        cli.list_browsers()
    elif args.command == "migrate":
        if not args.source or not args.target:
            logger.error("Source and target profiles must be specified for migration")
            return 1
        cli.migrate_profile(args.source, args.target)
    elif args.command == "backup":
        if not args.profile or not args.browser:
            logger.error("Profile and browser must be specified for backup")
            return 1
        cli.backup_profile(args.profile, args.browser)
    elif args.command == "restore":
        if not args.backup or not args.target:
            logger.error("Backup file and target directory must be specified for restoration")
            return 1
        cli.restore_backup(args.backup, args.target)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
