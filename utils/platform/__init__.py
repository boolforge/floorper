"""
Floorper - Platform Detection Utilities

This module provides platform detection and platform-specific functionality.
"""

import os
import sys
import platform
from typing import Dict, Any, Optional

def get_platform() -> str:
    """
    Detect the current platform.
    
    Returns:
        Platform identifier (windows, macos, linux, haiku, os2, other)
    """
    system = platform.system().lower()
    
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "haiku":
        return "haiku"
    elif system == "os/2":
        return "os2"
    else:
        return "other"

def get_platform_info() -> Dict[str, Any]:
    """
    Get detailed information about the current platform.
    
    Returns:
        Dictionary containing platform information
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "platform_id": get_platform()
    }

def get_home_directory() -> str:
    """
    Get the user's home directory in a platform-independent way.
    
    Returns:
        Path to the user's home directory
    """
    return os.path.expanduser("~")

def get_app_data_directory() -> str:
    """
    Get the appropriate application data directory for the current platform.
    
    Returns:
        Path to the application data directory
    """
    platform_id = get_platform()
    
    if platform_id == "windows":
        return os.path.join(os.environ.get("APPDATA", ""), "Floorper")
    elif platform_id == "macos":
        return os.path.join(get_home_directory(), "Library", "Application Support", "Floorper")
    else:  # Linux, Haiku, etc.
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            return os.path.join(xdg_config_home, "floorper")
        else:
            return os.path.join(get_home_directory(), ".config", "floorper")
