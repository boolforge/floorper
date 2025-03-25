#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Browser Compatibility Test
===================================

Tests the compatibility of Floorper with various browsers.
"""

import os
import sys
import logging
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Set

from floorper.core.constants import BROWSERS
from floorper.core.browser_detector import BrowserDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("browser_compatibility_test.log")
    ]
)

logger = logging.getLogger(__name__)

class BrowserCompatibilityTest:
    """Tests browser compatibility with Floorper."""
    
    def __init__(self):
        """Initialize the test."""
        self.detector = BrowserDetector()
        self.results = {
            "system_info": self._get_system_info(),
            "browsers": {},
            "exotic_browsers": {},
            "retro_browsers": {},
            "summary": {
                "total_browsers": 0,
                "detected_browsers": 0,
                "exotic_browsers": 0,
                "retro_browsers": 0
            }
        }
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
    
    def run_tests(self):
        """Run all compatibility tests."""
        logger.info("Starting browser compatibility tests")
        
        # Test standard browsers
        self._test_standard_browsers()
        
        # Test exotic browsers
        self._test_exotic_browsers()
        
        # Test retro browsers
        self._test_retro_browsers()
        
        # Update summary
        self.results["summary"]["total_browsers"] = (
            len(self.results["browsers"]) +
            len(self.results["exotic_browsers"]) +
            len(self.results["retro_browsers"])
        )
        
        self.results["summary"]["detected_browsers"] = sum(
            1 for browser in self.results["browsers"].values() if browser.get("detected", False)
        )
        
        self.results["summary"]["exotic_browsers"] = sum(
            1 for browser in self.results["exotic_browsers"].values() if browser.get("detected", False)
        )
        
        self.results["summary"]["retro_browsers"] = sum(
            1 for browser in self.results["retro_browsers"].values() if browser.get("detected", False)
        )
        
        logger.info(f"Completed browser compatibility tests. Detected {self.results['summary']['detected_browsers']} standard browsers, {self.results['summary']['exotic_browsers']} exotic browsers, and {self.results['summary']['retro_browsers']} retro browsers.")
        
        return self.results
    
    def _test_standard_browsers(self):
        """Test compatibility with standard browsers."""
        logger.info("Testing standard browsers")
        
        # Get all standard browsers from constants
        standard_browsers = {
            browser_id: browser_info
            for browser_id, browser_info in BROWSERS.items()
            if not browser_info.get("exotic", False) and not browser_info.get("retro", False)
        }
        
        for browser_id, browser_info in standard_browsers.items():
            self._test_browser(browser_id, browser_info, "browsers")
    
    def _test_exotic_browsers(self):
        """Test compatibility with exotic browsers."""
        logger.info("Testing exotic browsers")
        
        # Get all exotic browsers from constants
        exotic_browsers = {
            browser_id: browser_info
            for browser_id, browser_info in BROWSERS.items()
            if browser_info.get("exotic", False)
        }
        
        for browser_id, browser_info in exotic_browsers.items():
            self._test_browser(browser_id, browser_info, "exotic_browsers")
    
    def _test_retro_browsers(self):
        """Test compatibility with retro browsers."""
        logger.info("Testing retro browsers")
        
        # Get all retro browsers from constants
        retro_browsers = {
            browser_id: browser_info
            for browser_id, browser_info in BROWSERS.items()
            if browser_info.get("retro", False)
        }
        
        for browser_id, browser_info in retro_browsers.items():
            self._test_browser(browser_id, browser_info, "retro_browsers")
    
    def _test_browser(self, browser_id: str, browser_info: Dict[str, Any], category: str):
        """Test compatibility with a specific browser."""
        browser_name = browser_info.get("name", browser_id)
        logger.info(f"Testing {browser_name} ({browser_id})")
        
        # Initialize result
        self.results[category][browser_id] = {
            "name": browser_name,
            "family": browser_info.get("family", ""),
            "detected": False,
            "profiles": [],
            "detection_time": 0,
            "errors": []
        }
        
        try:
            # Try to detect browser
            import time
            start_time = time.time()
            
            # Check if browser is installed
            installed = self._check_browser_installed(browser_id, browser_info)
            self.results[category][browser_id]["installed"] = installed
            
            if not installed:
                logger.info(f"{browser_name} is not installed")
                return
            
            # Detect profiles
            profiles = self.detector.detect_profiles(browser_id)
            
            end_time = time.time()
            detection_time = end_time - start_time
            
            # Update result
            self.results[category][browser_id]["detected"] = True
            self.results[category][browser_id]["profiles"] = profiles
            self.results[category][browser_id]["detection_time"] = detection_time
            
            logger.info(f"Detected {len(profiles)} profiles for {browser_name} in {detection_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Error testing {browser_name}: {str(e)}")
            self.results[category][browser_id]["errors"].append(str(e))
    
    def _check_browser_installed(self, browser_id: str, browser_info: Dict[str, Any]) -> bool:
        """Check if a browser is installed."""
        # Check common installation paths
        paths = browser_info.get("paths", {}).get(platform.system(), [])
        
        for path in paths:
            if os.path.exists(path):
                return True
        
        # Check if browser is in PATH
        executables = browser_info.get("executables", [])
        
        for executable in executables:
            try:
                # Try to find executable in PATH
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["where", executable],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                else:
                    result = subprocess.run(
                        ["which", executable],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                
                if result.returncode == 0 and result.stdout.strip():
                    return True
            except Exception:
                pass
        
        # Check for browser-specific detection methods
        if browser_id == "firefox":
            # Check for Firefox in registry on Windows
            if platform.system() == "Windows":
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Mozilla\Firefox") as key:
                        return True
                except Exception:
                    pass
        
        return False
    
    def save_results(self, output_file: str = "browser_compatibility_results.json"):
        """Save test results to a file."""
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to {output_file}")


def main():
    """Run the browser compatibility test."""
    test = BrowserCompatibilityTest()
    results = test.run_tests()
    test.save_results()
    
    # Print summary
    print("\nBrowser Compatibility Test Summary:")
    print(f"Total browsers tested: {results['summary']['total_browsers']}")
    print(f"Standard browsers detected: {results['summary']['detected_browsers']}")
    print(f"Exotic browsers detected: {results['summary']['exotic_browsers']}")
    print(f"Retro browsers detected: {results['summary']['retro_browsers']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
