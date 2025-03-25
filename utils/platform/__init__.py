"""
Floorper - Platform Utilities Module

This module provides platform-specific utilities.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def is_windows():
    """Check if the current platform is Windows."""
    return platform.system() == "Windows"

def is_macos():
    """Check if the current platform is macOS."""
    return platform.system() == "Darwin"

def is_linux():
    """Check if the current platform is Linux."""
    return platform.system() == "Linux"

def get_home_dir():
    """Get the user's home directory."""
    return Path.home()

def has_display():
    """Check if a display is available for GUI applications."""
    if is_windows():
        return True
    elif is_macos():
        return True
    else:
        return "DISPLAY" in os.environ

def get_installed_browsers():
    """Get a list of installed browsers on the system."""
    browsers = []
    
    if is_windows():
        # Check common Windows browser locations
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        
        browser_paths = [
            (Path(program_files) / "Mozilla Firefox" / "firefox.exe", "firefox"),
            (Path(program_files_x86) / "Mozilla Firefox" / "firefox.exe", "firefox"),
            (Path(program_files) / "Floorp" / "floorp.exe", "floorp"),
            (Path(program_files_x86) / "Floorp" / "floorp.exe", "floorp"),
            (Path(program_files) / "Waterfox" / "waterfox.exe", "waterfox"),
            (Path(program_files_x86) / "Waterfox" / "waterfox.exe", "waterfox"),
            (Path(program_files) / "LibreWolf" / "librewolf.exe", "librewolf"),
            (Path(program_files_x86) / "LibreWolf" / "librewolf.exe", "librewolf"),
            (Path(program_files) / "Pale Moon" / "palemoon.exe", "pale_moon"),
            (Path(program_files_x86) / "Pale Moon" / "palemoon.exe", "pale_moon"),
            (Path(program_files) / "Basilisk" / "basilisk.exe", "basilisk"),
            (Path(program_files_x86) / "Basilisk" / "basilisk.exe", "basilisk"),
        ]
        
        for path, browser_id in browser_paths:
            if path.exists():
                browsers.append(browser_id)
    
    elif is_macos():
        # Check common macOS browser locations
        applications = Path("/Applications")
        
        browser_paths = [
            (applications / "Firefox.app", "firefox"),
            (applications / "Floorp.app", "floorp"),
            (applications / "Waterfox.app", "waterfox"),
            (applications / "LibreWolf.app", "librewolf"),
            (applications / "Pale Moon.app", "pale_moon"),
            (applications / "Basilisk.app", "basilisk"),
        ]
        
        for path, browser_id in browser_paths:
            if path.exists():
                browsers.append(browser_id)
    
    else:  # Linux and others
        # Check if browsers are in PATH
        browser_commands = [
            ("firefox", "firefox"),
            ("floorp", "floorp"),
            ("waterfox", "waterfox"),
            ("librewolf", "librewolf"),
            ("palemoon", "pale_moon"),
            ("basilisk", "basilisk"),
        ]
        
        for command, browser_id in browser_commands:
            try:
                result = subprocess.run(
                    ["which", command],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    browsers.append(browser_id)
            except Exception:
                pass
    
    return browsers

def open_directory(path):
    """Open a directory in the file explorer."""
    path = Path(path)
    
    if not path.exists():
        return False
    
    try:
        if is_windows():
            os.startfile(path)
        elif is_macos():
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
        return True
    except Exception:
        return False

def open_url(url):
    """Open a URL in the default browser."""
    try:
        if is_windows():
            os.startfile(url)
        elif is_macos():
            subprocess.run(["open", url])
        else:
            subprocess.run(["xdg-open", url])
        return True
    except Exception:
        return False
