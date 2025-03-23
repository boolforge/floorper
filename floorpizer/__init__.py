"""
Floorpizer - Universal Browser Profile Migration Tool
===================================================

A powerful tool to migrate profiles from various browsers to Floorp.
"""

from .floorpizer import main
from .browser_detection import BrowserDetector, Profile
from .profile_migration import ProfileMigrator
from .gui import FloorpizerGUI
from .config import BROWSERS, FLOORP, VERSION

__version__ = VERSION
__all__ = [
    'main',
    'BrowserDetector',
    'Profile',
    'ProfileMigrator',
    'FloorpizerGUI',
    'BROWSERS',
    'FLOORP',
    'VERSION',
] 