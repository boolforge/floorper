"""
Floorper Core Module
===================

This module provides the core functionality for the Floorper application,
including browser detection, profile migration, and backup management.
"""

from .browser_detector import BrowserDetector
from .profile_migrator import ProfileMigrator
from .backup_manager import BackupManager
from .constants import BROWSERS, FLOORP, VERSION

__all__ = [
    'BrowserDetector',
    'ProfileMigrator',
    'BackupManager',
    'BROWSERS',
    'FLOORP',
    'VERSION'
]
