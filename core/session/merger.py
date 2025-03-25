"""
Session Merger Module

This module provides functionality to merge Firefox sessions from multiple profiles.
Based on techniques from Firefox Session Merger (https://github.com/james-cube/firefox-session-merger)
"""

import os
import sys
import json
import logging
import lz4.block
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

# Setup logging
logger = logging.getLogger('floorper.core.session.merger')

class SessionMerger:
    """Merges Firefox sessions from multiple profiles."""
    
    def __init__(self):
        """Initialize the session merger."""
        pass
    
    def merge_sessions(
        self,
        source_profiles: List[Dict[str, Any]],
        target_profile: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Merge sessions from multiple source profiles into a target profile.
        
        Args:
            source_profiles: List of source profiles
            target_profile: Target profile
            options: Additional options for merging
            
        Returns:
            True if merge was successful, False otherwise
        """
        if options is None:
            options = {}
        
        try:
            # Get session data from all profiles
            sessions_data = []
            for profile in source_profiles:
                profile_path = Path(profile["path"])
                session_data = self._read_session_file(profile_path)
                if session_data:
                    sessions_data.append(session_data)
            
            # Get target session data
            target_path = Path(target_profile["path"])
            target_session_data = self._read_session_file(target_path)
            
            # If target has no session data, use the first source
            if not target_session_data and sessions_data:
                target_session_data = sessions_data[0]
                sessions_data = sessions_data[1:]
            
            # If still no target session data, create empty one
            if not target_session_data:
                target_session_data = {
                    "version": ["sessionrestore", 1],
                    "windows": [],
                    "selectedWindow": 0,
                    "cookies": [],
                    "_closedWindows": []
                }
            
            # Merge sessions
            merged_session = self._merge_session_data(target_session_data, sessions_data, options)
            
            # Write merged session to target
            self._write_session_file(target_path, merged_session)
            
            return True
        except Exception as e:
            logger.error(f"Error merging sessions: {e}")
            return False
    
    def _read_session_file(self, profile_path: Path) -> Optional[Dict[str, Any]]:
        """
        Read session data from a profile.
        
        Args:
            profile_path: Path to the profile directory
            
        Returns:
            Session data or None if not found
        """
        session_file = profile_path / "sessionstore.jsonlz4"
        backup_file = profile_path / "sessionstore-backups" / "recovery.jsonlz4"
        
        # Try main session file first
        if session_file.exists():
            try:
                return self._decompress_session_file(session_file)
            except Exception as e:
                logger.error(f"Error reading session file: {e}")
        
        # Try backup file
        if backup_file.exists():
            try:
                return self._decompress_session_file(backup_file)
            except Exception as e:
                logger.error(f"Error reading backup session file: {e}")
        
        return None
    
    def _decompress_session_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Decompress a Firefox session file.
        
        Args:
            file_path: Path to the session file
            
        Returns:
            Decompressed session data
        """
        with open(file_path, "rb") as f:
            # Firefox session files start with a magic header (8 bytes)
            magic = f.read(8)
            
            # Verify magic header (mozLz40)
            if magic != b"mozLz40\0":
                raise ValueError(f"Invalid session file format: {file_path}")
            
            # Read compressed data
            compressed_data = f.read()
            
            # Decompress data
            decompressed_data = lz4.block.decompress(compressed_data)
            
            # Parse JSON
            return json.loads(decompressed_data.decode("utf-8"))
    
    def _write_session_file(self, profile_path: Path, session_data: Dict[str, Any]) -> None:
        """
        Write session data to a profile.
        
        Args:
            profile_path: Path to the profile directory
            session_data: Session data to write
        """
        session_file = profile_path / "sessionstore.jsonlz4"
        backup_dir = profile_path / "sessionstore-backups"
        backup_file = backup_dir / "recovery.jsonlz4"
        
        # Create backup directory if it doesn't exist
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert session data to JSON
        json_data = json.dumps(session_data).encode("utf-8")
        
        # Compress data
        compressed_data = lz4.block.compress(json_data)
        
        # Write to session file
        with open(session_file, "wb") as f:
            f.write(b"mozLz40\0")  # Magic header
            f.write(compressed_data)
        
        # Write to backup file
        with open(backup_file, "wb") as f:
            f.write(b"mozLz40\0")  # Magic header
            f.write(compressed_data)
    
    def _merge_session_data(
        self,
        target_session: Dict[str, Any],
        source_sessions: List[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge multiple session data objects.
        
        Args:
            target_session: Target session data
            source_sessions: List of source session data
            options: Additional options for merging
            
        Returns:
            Merged session data
        """
        # Track existing URLs to avoid duplicates
        existing_urls = set()
        
        # Extract existing URLs from target session
        for window in target_session.get("windows", []):
            for tab in window.get("tabs", []):
                for entry in tab.get("entries", []):
                    if "url" in entry:
                        existing_urls.add(entry["url"])
        
        # Merge windows from source sessions
        for source in source_sessions:
            # Merge windows
            for window in source.get("windows", []):
                # Create a new window with non-duplicate tabs
                new_window = {
                    "tabs": [],
                    "selected": 1,  # Select first tab
                    "busy": False,
                    "_closedTabs": []
                }
                
                # Copy window properties
                for key, value in window.items():
                    if key != "tabs" and key != "_closedTabs":
                        new_window[key] = value
                
                # Add non-duplicate tabs
                for tab in window.get("tabs", []):
                    # Check if tab has entries
                    if not tab.get("entries"):
                        continue
                    
                    # Check if tab URL is already in target
                    tab_url = tab.get("entries", [{}])[-1].get("url")
                    if tab_url and tab_url in existing_urls and not options.get("allow_duplicates", False):
                        continue
                    
                    # Add tab to new window
                    new_window["tabs"].append(tab)
                    
                    # Add tab URL to existing URLs
                    if tab_url:
                        existing_urls.add(tab_url)
                
                # Add window to target if it has tabs
                if new_window["tabs"]:
                    target_session["windows"].append(new_window)
            
            # Merge closed windows
            for closed_window in source.get("_closedWindows", []):
                # Check if closed window has tabs
                if not closed_window.get("tabs"):
                    continue
                
                # Add closed window to target
                target_session["_closedWindows"].append(closed_window)
        
        # Update selected window
        if target_session["windows"]:
            target_session["selectedWindow"] = 0
        
        return target_session
