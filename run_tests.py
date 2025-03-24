#!/usr/bin/env python3
"""
Test runner script for Floorper browser compatibility tests.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run browser compatibility tests")
    
    parser.add_argument(
        "-b", "--browser",
        choices=["chrome", "firefox", "edge", "opera", "brave", "vivaldi", "all"],
        default="all",
        help="Browser to test (default: all)"
    )
    
    parser.add_argument(
        "-m", "--mode",
        choices=["unit", "integration", "all"],
        default="all",
        help="Test mode (default: all)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase verbosity"
    )
    
    parser.add_argument(
        "--real-browsers",
        action="store_true",
        help="Run tests that require real browsers to be installed"
    )
    
    return parser.parse_args()

def main():
    """Main function to run tests."""
    args = parse_args()
    
    # Set up the base command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add test selection based on browser
    if args.browser != "all":
        cmd.extend(["-m", args.browser])
    
    # Skip tests requiring real browsers unless specified
    if not args.real_browsers:
        cmd.extend(["-k", "not real_browser"])
    
    # Add test mode selection
    if args.mode == "unit":
        cmd.append("tests/test_browser_handlers.py")
    elif args.mode == "integration":
        cmd.append("tests/test_browser_integration.py")
    
    # Add coverage reporting
    cmd.extend(["--cov=floorper", "--cov-report=term", "--cov-report=html:coverage_html"])
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 