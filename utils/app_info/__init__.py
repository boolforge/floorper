"""
Floorper - Application Information Module

This module provides information about the application.
"""

import os
import sys
from pathlib import Path

# Application information
APP_NAME = "Floorper"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Browser Profile Migration Tool"
APP_AUTHOR = "BoolForge"
APP_URL = "https://github.com/boolforge/floorper"

def get_version():
    """Get the application version."""
    return APP_VERSION

def get_app_dir():
    """Get the application directory."""
    return Path(__file__).parent.parent.parent

def get_data_dir():
    """Get the data directory."""
    system = os.name
    if system == 'nt':  # Windows
        return Path(os.environ.get('APPDATA', '')) / APP_NAME
    else:  # Unix/Linux/Mac
        return Path.home() / f".{APP_NAME.lower()}"

def get_config_dir():
    """Get the configuration directory."""
    system = os.name
    if system == 'nt':  # Windows
        return Path(os.environ.get('APPDATA', '')) / APP_NAME
    else:  # Unix/Linux/Mac
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config_home:
            return Path(xdg_config_home) / APP_NAME.lower()
        else:
            return Path.home() / ".config" / APP_NAME.lower()

def get_cache_dir():
    """Get the cache directory."""
    system = os.name
    if system == 'nt':  # Windows
        return Path(os.environ.get('LOCALAPPDATA', '')) / APP_NAME / 'Cache'
    else:  # Unix/Linux/Mac
        xdg_cache_home = os.environ.get('XDG_CACHE_HOME')
        if xdg_cache_home:
            return Path(xdg_cache_home) / APP_NAME.lower()
        else:
            return Path.home() / ".cache" / APP_NAME.lower()

def ensure_app_dirs():
    """Ensure all application directories exist."""
    dirs = [get_data_dir(), get_config_dir(), get_cache_dir()]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    return dirs
