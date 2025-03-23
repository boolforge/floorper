#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Migrate browser profiles TO Floorp
===========================================

This script launches the Floorper application, which allows users
to migrate their browser profiles specifically to Floorp.
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from browsermigrator.main_window import FloorperWindow

# Configure logging
def setup_logging():
    """Configure logging for the application."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('floorper.log', 'a')
        ]
    )
    return logging.getLogger(__name__)

# Add current directory to path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the Floorper application."""
    logger = setup_logging()
    logger.info("Starting Floorper v3.0.0")
    
    # Create the PyQt application
    app = QApplication(sys.argv)
    app.setApplicationName("Floorper")
    app.setApplicationVersion("3.0.0")
    app.setStyle("Fusion")
    app.setOrganizationName("Floorper")
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "floorp_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show the main window
    window = FloorperWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
