"""
Browser handler classes for different browsers.
This module provides handlers for different browsers (Chrome, Firefox, Edge, etc.).
"""

# This file marks the 'handlers' directory as a Python package.

from .base_handler import BaseBrowserHandler
from .chrome_handler import ChromeHandler
from .firefox_handler import FirefoxHandler

__all__ = [
    'BaseBrowserHandler',
    'ChromeHandler',
    'FirefoxHandler',
] 