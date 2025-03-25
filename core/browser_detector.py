"""
Core Browser Detector Module

This module provides functionality to detect installed browsers and their profiles.
"""

import os
import sys
import platform
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Import browser handlers
from browsers.firefox_based import FirefoxBasedHandler
from browsers.handlers.firefox_handler import FirefoxHandler

# Setup logging
logger = logging.getLogger('floorper.core.browser_detector')

class BrowserDetector:
    """Detects installed browsers and their profiles."""
    
    def __init__(self):
        """Initialize the browser detector."""
        self.handlers = {}
        self.detected_browsers = []
        self.browser_profiles = {}
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register browser handlers."""
        # Firefox-based browsers
        self.handlers["firefox"] = FirefoxHandler()
        self.handlers["floorp"] = FirefoxBasedHandler("floorp")
        self.handlers["waterfox"] = FirefoxBasedHandler("waterfox")
        self.handlers["librewolf"] = FirefoxBasedHandler("librewolf")
        self.handlers["pale_moon"] = FirefoxBasedHandler("pale_moon")
        self.handlers["basilisk"] = FirefoxBasedHandler("basilisk")
        
        # TODO: Add handlers for other browser types
    
    def detect_browsers(self) -> List[Dict[str, Any]]:
        """
        Detect installed browsers.
        
        Returns:
            List of detected browsers with their information
        """
        self.detected_browsers = []
        
        # Detect browsers using handlers
        for browser_id, handler in self.handlers.items():
            try:
                if handler.detect_browser():
                    browser_info = {
                        "id": browser_id,
                        "name": handler.name.capitalize(),
                        "handler": handler
                    }
                    
                    # Add version if available
                    if hasattr(handler, "version") and handler.version:
                        browser_info["version"] = handler.version
                    
                    # Add path if available
                    if hasattr(handler, "profiles_dir") and handler.profiles_dir:
                        browser_info["path"] = str(handler.profiles_dir)
                    
                    self.detected_browsers.append(browser_info)
                    logger.info(f"Detected browser: {browser_info['name']}")
            except Exception as e:
                logger.error(f"Error detecting browser {browser_id}: {e}")
        
        return self.detected_browsers
    
    def get_profiles(self, browser_id: str) -> List[Dict[str, Any]]:
        """
        Get profiles for a specific browser.
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            List of profiles with their information
        """
        # Check if browser is detected
        browser = None
        for b in self.detected_browsers:
            if b["id"] == browser_id:
                browser = b
                break
        
        if not browser:
            logger.error(f"Browser {browser_id} not detected")
            return []
        
        # Get profiles using handler
        try:
            handler = browser["handler"]
            profiles = handler.get_profiles()
            
            # Cache profiles
            self.browser_profiles[browser_id] = profiles
            
            return profiles
        except Exception as e:
            logger.error(f"Error getting profiles for {browser_id}: {e}")
            return []
    
    def get_profile_data(self, browser_id: str, profile_path: str) -> Dict[str, Any]:
        """
        Get data from a specific profile.
        
        Args:
            browser_id: Browser identifier
            profile_path: Path to the profile
            
        Returns:
            Profile data
        """
        # Check if browser is detected
        browser = None
        for b in self.detected_browsers:
            if b["id"] == browser_id:
                browser = b
                break
        
        if not browser:
            logger.error(f"Browser {browser_id} not detected")
            return {}
        
        # Get profile data using handler
        try:
            handler = browser["handler"]
            profile_data = handler.get_profile_data(Path(profile_path))
            return profile_data
        except Exception as e:
            logger.error(f"Error getting profile data for {browser_id}: {e}")
            return {}
    
    def get_browser_info(self, browser_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific browser.
        
        Args:
            browser_id: Browser identifier
            
        Returns:
            Browser information or None if not found
        """
        for browser in self.detected_browsers:
            if browser["id"] == browser_id:
                return browser
        return None
