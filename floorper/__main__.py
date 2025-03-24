#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Main Entry Point
=========================

Main entry point for the Floorper application.
Provides access to all interfaces (CLI, TUI, GUI).
"""

import os
import sys
import logging
import argparse
from typing import Dict, List, Optional, Any, Tuple, Union, Set

from floorper.interfaces.cli import FloorperCLI
from floorper.interfaces.tui import FloorperTUI
from floorper.interfaces.gui import FloorperGUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("floorper.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for Floorper."""
    parser = argparse.ArgumentParser(
        description="Floorper - Browser Profile Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Interface Modes:
  --cli    Command-line interface mode
  --tui    Text user interface mode (default if no mode specified)
  --gui    Graphical user interface mode

Examples:
  # Start the TUI (default)
  floorper

  # Start the GUI
  floorper --gui

  # Use CLI mode to list profiles
  floorper --cli list

  # Use CLI mode to migrate profiles
  floorper --cli migrate --source "/path/to/source" --target "/path/to/target"
"""
    )
    
    # Interface mode arguments
    mode_group = parser.add_argument_group("Interface Mode")
    mode_group.add_argument("--cli", action="store_true", help="Use command-line interface")
    mode_group.add_argument("--tui", action="store_true", help="Use text user interface (default)")
    mode_group.add_argument("--gui", action="store_true", help="Use graphical user interface")
    
    # Parse only known args for mode selection
    args, remaining = parser.parse_known_args()
    
    # Determine which interface to use
    if args.cli:
        # CLI mode - pass remaining args to CLI
        sys.argv = [sys.argv[0]] + remaining
        return FloorperCLI().run()
    elif args.gui:
        # GUI mode
        return FloorperGUI().run()
    else:
        # Default to TUI mode
        return FloorperTUI().run()

if __name__ == "__main__":
    sys.exit(main())
