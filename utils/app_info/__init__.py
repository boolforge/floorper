"""
Floorper - Application Information Utilities

This module provides utilities for retrieving application information,
including Floorp profile detection and theme management.
"""

import os
import sys
import json
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from utils.platform import get_platform, get_home_directory

def get_app_info() -> Dict[str, Any]:
    """
    Get information about the Floorper application.
    
    Returns:
        Dictionary containing application information
    """
    return {
        "name": "Floorper",
        "version": "1.2.0",
        "description": "Universal Browser Profile Migration Tool for Floorp",
        "author": "Floorper Team",
        "license": "MIT",
        "platform": get_platform(),
        "python_version": platform.python_version()
    }

def get_floorp_profiles() -> List[Dict[str, Any]]:
    """
    Get list of Floorp browser profiles.
    
    Returns:
        List of dictionaries containing profile information
    """
    profiles = []
    profile_dirs = _get_floorp_profile_dirs()
    
    for profile_dir in profile_dirs:
        if profile_dir.exists() and profile_dir.is_dir():
            for item in profile_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    profile_info = _get_profile_info(item)
                    if profile_info:
                        profiles.append({
                            "name": item.name,
                            "path": str(item),
                            "info": profile_info
                        })
    
    return profiles

def _get_floorp_profile_dirs() -> List[Path]:
    """
    Get directories where Floorp profiles might be stored.
    
    Returns:
        List of potential profile directory paths
    """
    platform_id = get_platform()
    home_dir = get_home_directory()
    
    if platform_id == "windows":
        return [
            Path(os.environ.get("APPDATA", "")) / "Floorp" / "Profiles",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Floorp" / "Profiles"
        ]
    elif platform_id == "macos":
        return [
            home_dir / "Library" / "Application Support" / "Floorp" / "Profiles"
        ]
    else:  # Linux, Haiku, etc.
        return [
            home_dir / ".floorp",
            home_dir / ".mozilla" / "floorp"
        ]

def _get_profile_info(profile_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Get information about a Floorp profile.
    
    Args:
        profile_dir: Path to the profile directory
        
    Returns:
        Dictionary containing profile information, or None if not a valid profile
    """
    # Check if this is a valid profile directory
    if not (profile_dir / "prefs.js").exists():
        return None
    
    # Get basic profile information
    info = {
        "last_modified": None,
        "size": 0,
        "bookmarks_count": 0,
        "history_count": 0,
        "extensions_count": 0
    }
    
    # Get last modified time
    try:
        info["last_modified"] = profile_dir.stat().st_mtime
    except Exception:
        pass
    
    # Calculate profile size
    try:
        info["size"] = sum(f.stat().st_size for f in profile_dir.glob('**/*') if f.is_file())
    except Exception:
        pass
    
    # Count bookmarks (if places.sqlite exists)
    places_db = profile_dir / "places.sqlite"
    if places_db.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(places_db)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM moz_bookmarks WHERE type = 1")
            info["bookmarks_count"] = cursor.fetchone()[0]
            
            # Count history entries
            cursor.execute("SELECT COUNT(*) FROM moz_places")
            info["history_count"] = cursor.fetchone()[0]
            
            conn.close()
        except Exception:
            pass
    
    # Count extensions
    extensions_dir = profile_dir / "extensions"
    if extensions_dir.exists() and extensions_dir.is_dir():
        try:
            info["extensions_count"] = len(list(extensions_dir.glob('*')))
        except Exception:
            pass
    
    return info

def get_theme_colors() -> Dict[str, str]:
    """
    Get theme colors for the application UI.
    
    Returns:
        Dictionary mapping color names to hex values
    """
    # Default theme colors
    colors = {
        "primary": "#4a6cf7",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#343a40",
        "background": "#ffffff",
        "text": "#212529",
        "link": "#007bff",
        "border": "#dee2e6",
        "highlight": "#f8f9fa"
    }
    
    # Try to load user theme if available
    try:
        config_dir = _get_config_dir()
        theme_file = config_dir / "theme.json"
        
        if theme_file.exists():
            with open(theme_file, 'r', encoding='utf-8') as f:
                user_theme = json.load(f)
                colors.update(user_theme)
    except Exception:
        pass
    
    return colors

def _get_config_dir() -> Path:
    """
    Get the configuration directory for Floorper.
    
    Returns:
        Path to the configuration directory
    """
    platform_id = get_platform()
    home_dir = get_home_directory()
    
    if platform_id == "windows":
        config_dir = Path(os.environ.get("APPDATA", "")) / "Floorper"
    elif platform_id == "macos":
        config_dir = home_dir / "Library" / "Application Support" / "Floorper"
    else:  # Linux, Haiku, etc.
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_dir = Path(xdg_config_home) / "floorper"
        else:
            config_dir = home_dir / ".config" / "floorper"
    
    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    return config_dir
