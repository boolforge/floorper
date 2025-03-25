"""
Core Backup Manager Module

This module provides functionality to create and restore backups of browser profiles.
"""

import os
import sys
import logging
import shutil
import json
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Setup logging
logger = logging.getLogger('floorper.core.backup_manager')

class BackupManager:
    """Manages backups of browser profiles."""
    
    def __init__(self):
        """Initialize the backup manager."""
        pass
    
    def create_backup(
        self,
        profile_path: str,
        browser_type: str,
        output_dir: Optional[str] = None
    ) -> str:
        """
        Create a backup of a browser profile.
        
        Args:
            profile_path: Path to the profile
            browser_type: Type of browser
            output_dir: Output directory for backup file
            
        Returns:
            Path to the created backup file
        """
        # Validate profile path
        profile_path = Path(profile_path)
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile path does not exist: {profile_path}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = Path.home() / "floorper_backups"
        else:
            output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        profile_name = profile_path.name
        backup_filename = f"{browser_type}_{profile_name}_{timestamp}.zip"
        backup_file = output_dir / backup_filename
        
        # Create backup
        logger.info(f"Creating backup of {browser_type} profile at {profile_path}")
        logger.info(f"Backup file: {backup_file}")
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add metadata
            metadata = {
                "browser_type": browser_type,
                "profile_name": profile_name,
                "created_at": timestamp,
                "created_by": "Floorper Backup Manager"
            }
            
            zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
            
            # Add profile files
            for item in profile_path.rglob('*'):
                if item.is_file():
                    # Get relative path
                    relative_path = item.relative_to(profile_path)
                    zipf.write(item, relative_path)
        
        logger.info(f"Backup created: {backup_file}")
        return str(backup_file)
    
    def restore_backup(
        self,
        backup_file: str,
        target_dir: str
    ) -> None:
        """
        Restore a backup to a target directory.
        
        Args:
            backup_file: Path to the backup file
            target_dir: Target directory to restore to
        """
        # Validate backup file
        backup_file = Path(backup_file)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file does not exist: {backup_file}")
        
        # Validate target directory
        target_dir = Path(target_dir)
        
        # Create target directory if it doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract backup
        logger.info(f"Restoring backup from {backup_file} to {target_dir}")
        
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            # Extract metadata
            try:
                metadata = json.loads(zipf.read("metadata.json"))
                logger.info(f"Backup metadata: {metadata}")
            except Exception as e:
                logger.warning(f"Error reading backup metadata: {e}")
            
            # Extract files
            for item in zipf.namelist():
                if item != "metadata.json":
                    zipf.extract(item, target_dir)
        
        logger.info(f"Backup restored to {target_dir}")
    
    def list_backups(
        self,
        directory: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            directory: Directory to search for backups
            
        Returns:
            List of backup information
        """
        # Determine directory
        if directory is None:
            directory = Path.home() / "floorper_backups"
        else:
            directory = Path(directory)
        
        # Check if directory exists
        if not directory.exists():
            return []
        
        # Find backup files
        backups = []
        for item in directory.glob("*.zip"):
            if item.is_file():
                try:
                    # Extract metadata
                    with zipfile.ZipFile(item, 'r') as zipf:
                        try:
                            metadata = json.loads(zipf.read("metadata.json"))
                        except Exception:
                            # If metadata is not available, create basic info
                            metadata = {
                                "browser_type": "unknown",
                                "profile_name": "unknown",
                                "created_at": "unknown"
                            }
                    
                    # Add backup info
                    backups.append({
                        "file": str(item),
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        "browser_type": metadata.get("browser_type", "unknown"),
                        "profile_name": metadata.get("profile_name", "unknown"),
                        "created_at": metadata.get("created_at", "unknown")
                    })
                except Exception as e:
                    logger.warning(f"Error reading backup file {item}: {e}")
        
        return backups
