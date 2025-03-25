"""
Floorper - Main Module

This module serves as the entry point for the Floorper application, which provides
functionality for detecting, migrating, and managing browser profiles with a focus
on Firefox-based browsers, especially Floorp.

The application supports three interfaces:
- GUI: Graphical User Interface using PyQt6
- TUI: Text User Interface using Textual
- CLI: Command Line Interface using argparse

Usage:
    python -m floorper          # Launches GUI if available, falls back to TUI or CLI
    python -m floorper --tui    # Forces TUI mode
    python -m floorper --cli    # Forces CLI mode
    python -m floorper --help   # Shows help message
"""

import os
import sys
import platform
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('floorper')

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Floorper - Browser Profile Migration Tool'
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Force GUI mode'
    )
    parser.add_argument(
        '--tui',
        action='store_true',
        help='Force TUI mode'
    )
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Force CLI mode'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    # Add CLI-specific arguments
    parser.add_argument(
        '--detect',
        action='store_true',
        help='Detect installed browsers'
    )
    parser.add_argument(
        '--list-profiles',
        metavar='BROWSER',
        help='List profiles for a specific browser'
    )
    parser.add_argument(
        '--migrate',
        nargs=2,
        metavar=('SOURCE', 'TARGET'),
        help='Migrate from SOURCE to TARGET (format: browser:profile)'
    )
    parser.add_argument(
        '--backup',
        metavar='BROWSER:PROFILE',
        help='Create backup of a browser profile'
    )
    parser.add_argument(
        '--restore',
        nargs=2,
        metavar=('BACKUP_FILE', 'TARGET'),
        help='Restore backup to a target location'
    )
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger('floorper').setLevel(logging.DEBUG)
    
    # Show version if requested
    if args.version:
        from utils.app_info import get_version
        print(f"Floorper version {get_version()}")
        return
    
    # Determine which interface to use
    if args.gui:
        use_gui = True
        use_tui = False
        use_cli = False
    elif args.tui:
        use_gui = False
        use_tui = True
        use_cli = False
    elif args.cli:
        use_gui = False
        use_tui = False
        use_cli = True
    else:
        # Auto-detect based on environment and available interfaces
        use_gui = _can_use_gui()
        use_tui = not use_gui and _can_use_tui()
        use_cli = not use_gui and not use_tui
    
    # Launch appropriate interface
    if use_gui:
        logger.info("Starting GUI interface")
        from interfaces.gui import start_gui
        start_gui()
    elif use_tui:
        logger.info("Starting TUI interface")
        from interfaces.tui import start_tui
        start_tui()
    else:
        logger.info("Starting CLI interface")
        from interfaces.cli import handle_cli_args
        handle_cli_args(args)

def _can_use_gui():
    """Check if GUI can be used."""
    # Check if running in a graphical environment
    if not os.environ.get('DISPLAY') and platform.system() != 'Windows':
        return False
    
    # Check if PyQt6 is available
    try:
        import PyQt6
        return True
    except ImportError:
        return False

def _can_use_tui():
    """Check if TUI can be used."""
    # Check if running in a terminal
    if not sys.stdout.isatty():
        return False
    
    # Check if Textual is available
    try:
        import textual
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    main()
