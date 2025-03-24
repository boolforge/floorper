#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Backup Manager
========================

Manages backup and restoration of browser profiles.
Provides functionality to create, verify, and restore backups.
"""

import os
import sys
import logging
import shutil
import json
import datetime
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

logger = logging.getLogger(__name__)

class BackupManager:
    """
    Manages backup and restoration of browser profiles.
    
    This class provides functionality to create, verify, and restore backups
    of browser profiles, ensuring data safety during migration operations.
    """
    
    def __init__(self, backup_dir: Optional[str] = None):
        """
        Initialize the backup manager.
        
        Args:
            backup_dir: Optional custom backup directory path
        """
        self.backup_dir = backup_dir or self._get_default_backup_dir()
        os.makedirs(self.backup_dir, exist_ok=True)
        logger.info(f"Backup manager initialized with backup directory: {self.backup_dir}")
    
    def _get_default_backup_dir(self) -> str:
        """
        Get the default backup directory path.
        
        Returns:
            str: Default backup directory path
        """
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".floorper", "backups")
    
    def create_backup(self, profile_path: str, browser_id: str, profile_name: str) -> Optional[str]:
        """
        Create a backup of a browser profile.
        
        Args:
            profile_path: Path to the profile directory
            browser_id: Browser identifier
            profile_name: Profile name
            
        Returns:
            Optional[str]: Path to the created backup file, or None if backup failed
        """
        if not os.path.exists(profile_path):
            logger.error(f"Profile path does not exist: {profile_path}")
            return None
        
        try:
            # Create a timestamp for the backup filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{browser_id}_{profile_name}_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create metadata
            metadata = {
                "browser_id": browser_id,
                "profile_name": profile_name,
                "timestamp": timestamp,
                "source_path": profile_path,
                "created_at": datetime.datetime.now().isoformat(),
                "files": []
            }
            
            # Create zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add metadata file
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
                
                # Add profile files
                file_count = 0
                total_size = 0
                
                for root, dirs, files in os.walk(profile_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Skip large cache files and lock files
                            if any(skip in file.lower() for skip in ['cache', '.lock', 'lock', '.tmp', '.temp']):
                                continue
                                
                            # Calculate relative path for zip
                            rel_path = os.path.relpath(file_path, profile_path)
                            zip_path = os.path.join('profile', rel_path)
                            
                            # Add file to zip
                            zipf.write(file_path, zip_path)
                            
                            # Update metadata
                            file_size = os.path.getsize(file_path)
                            file_hash = self._calculate_file_hash(file_path)
                            
                            metadata['files'].append({
                                'path': rel_path,
                                'size': file_size,
                                'hash': file_hash
                            })
                            
                            file_count += 1
                            total_size += file_size
                        except Exception as e:
                            logger.warning(f"Error adding file to backup: {file_path}, Error: {str(e)}")
                
                # Update metadata with summary
                metadata['summary'] = {
                    'file_count': file_count,
                    'total_size': total_size
                }
                
                # Update metadata file with complete information
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
            
            logger.info(f"Created backup: {backup_path} with {file_count} files, {total_size} bytes")
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return None
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Hexadecimal hash string
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Error calculating hash for {file_path}: {str(e)}")
            return ""
    
    def list_backups(self, browser_id: Optional[str] = None, profile_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available backups, optionally filtered by browser and profile.
        
        Args:
            browser_id: Optional browser identifier filter
            profile_name: Optional profile name filter
            
        Returns:
            List[Dict[str, Any]]: List of backup information dictionaries
        """
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if not filename.endswith('.zip'):
                    continue
                
                backup_path = os.path.join(self.backup_dir, filename)
                
                try:
                    with zipfile.ZipFile(backup_path, 'r') as zipf:
                        if 'metadata.json' not in zipf.namelist():
                            logger.warning(f"No metadata found in backup: {backup_path}")
                            continue
                        
                        metadata_str = zipf.read('metadata.json').decode('utf-8')
                        metadata = json.loads(metadata_str)
                        
                        # Apply filters if specified
                        if browser_id and metadata.get('browser_id') != browser_id:
                            continue
                        if profile_name and metadata.get('profile_name') != profile_name:
                            continue
                        
                        # Add backup info
                        backup_info = {
                            'path': backup_path,
                            'filename': filename,
                            'browser_id': metadata.get('browser_id', ''),
                            'profile_name': metadata.get('profile_name', ''),
                            'timestamp': metadata.get('timestamp', ''),
                            'created_at': metadata.get('created_at', ''),
                            'summary': metadata.get('summary', {})
                        }
                        
                        backups.append(backup_info)
                except Exception as e:
                    logger.warning(f"Error reading backup {backup_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return backups
    
    def verify_backup(self, backup_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify the integrity of a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (is_valid, verification_results)
        """
        if not os.path.exists(backup_path):
            return False, {'error': 'Backup file does not exist'}
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Check if metadata exists
                if 'metadata.json' not in zipf.namelist():
                    return False, {'error': 'No metadata found in backup'}
                
                # Read metadata
                metadata_str = zipf.read('metadata.json').decode('utf-8')
                metadata = json.loads(metadata_str)
                
                # Verify file list
                verification_results = {
                    'metadata': metadata,
                    'verified_files': 0,
                    'missing_files': [],
                    'corrupted_files': [],
                    'is_valid': True
                }
                
                # Check each file in metadata
                for file_info in metadata.get('files', []):
                    file_path = file_info.get('path', '')
                    zip_path = os.path.join('profile', file_path)
                    
                    if zip_path not in zipf.namelist():
                        verification_results['missing_files'].append(file_path)
                        verification_results['is_valid'] = False
                        continue
                    
                    verification_results['verified_files'] += 1
                
                return verification_results['is_valid'], verification_results
        except Exception as e:
            logger.error(f"Error verifying backup: {str(e)}")
            return False, {'error': str(e)}
    
    def restore_backup(self, backup_path: str, target_path: Optional[str] = None, merge: bool = False) -> bool:
        """
        Restore a backup to a target location.
        
        Args:
            backup_path: Path to the backup file
            target_path: Optional target path (if None, uses original path from metadata)
            merge: Whether to merge with existing files (True) or overwrite (False)
            
        Returns:
            bool: True if restoration was successful, False otherwise
        """
        if not os.path.exists(backup_path):
            logger.error(f"Backup file does not exist: {backup_path}")
            return False
        
        try:
            # Verify backup first
            is_valid, verification_results = self.verify_backup(backup_path)
            if not is_valid:
                logger.error(f"Backup verification failed: {verification_results.get('error', 'Unknown error')}")
                return False
            
            metadata = verification_results['metadata']
            
            # Determine target path
            if target_path is None:
                target_path = metadata.get('source_path')
                if not target_path:
                    logger.error("No target path specified and no source path in metadata")
                    return False
            
            # Create target directory if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # Extract files
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                profile_prefix = 'profile/'
                
                for zip_info in zipf.infolist():
                    if not zip_info.filename.startswith(profile_prefix) or zip_info.filename == profile_prefix:
                        continue
                    
                    # Get relative path
                    rel_path = zip_info.filename[len(profile_prefix):]
                    target_file_path = os.path.join(target_path, rel_path)
                    
                    # Create parent directories
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                    
                    # Check if file exists and we're in merge mode
                    if os.path.exists(target_file_path) and merge:
                        # For now, skip existing files in merge mode
                        # More sophisticated merging could be implemented here
                        continue
                    
                    # Extract file
                    zipf.extract(zip_info, path=os.path.dirname(target_path))
                    
                    # Move from profile/ subdirectory to target directory
                    extracted_path = os.path.join(os.path.dirname(target_path), zip_info.filename)
                    if os.path.exists(extracted_path) and extracted_path != target_file_path:
                        shutil.move(extracted_path, target_file_path)
            
            # Clean up any empty profile directory that might have been created
            profile_dir = os.path.join(os.path.dirname(target_path), 'profile')
            if os.path.exists(profile_dir) and os.path.isdir(profile_dir):
                try:
                    os.rmdir(profile_dir)
                except OSError:
                    # Directory not empty, which is fine
                    pass
            
            logger.info(f"Restored backup to {target_path}")
            return True
        except Exception as e:
            logger.error(f"Error restoring backup: {str(e)}")
            return False
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        Delete a backup file.
        
        Args:
            backup_path: Path to the backup file
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not os.path.exists(backup_path):
            logger.error(f"Backup file does not exist: {backup_path}")
            return False
        
        try:
            os.remove(backup_path)
            logger.info(f"Deleted backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting backup: {str(e)}")
            return False
