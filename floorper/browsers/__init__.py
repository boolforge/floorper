"""
Browser module for Floorper.
This module provides handlers for different browser families (Firefox-based, Chromium-based, etc.).
"""

# This file marks the 'browsers' directory as a Python package.

from .handlers.base_handler import BaseBrowserHandler

__all__ = [
    'BaseBrowserHandler',
] 