"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides backup and restoration functionality for browser profiles,
allowing users to create, manage, and restore backups of their profiles.
"""

import os
import sys
import logging
import json
import shutil
import datetime
import zipfile
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from floorper.core import FloorperCore

# Setup logging
logger = logging.getLogger('floorper.backup')

class BackupManager:
    """
    Manages backup and restoration of browser profiles.
    
    This class provides functionality to create, list, and restore backups
    of browser profiles, supporting multiple backup formats and compression.
    """
    
    def __init__(self, controller: Optional[FloorperCore] = None):
        """
        Initialize the backup manager.
        
        Args:
            controller: Optional FloorperCore controller instance
        """
        self.controller = controller or FloorperCore()
        
        # Default backup directory
        self.backup_dir = self._get_default_backup_dir()
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        logger.info(f"Backup manager initialized with backup directory: {self.backup_dir}")
    
    def _get_default_backup_dir(self) -> str:
        """
        Get the default backup directory.
        
        Returns:
            Default backup directory path
        """
        # Use platform-specific locations
        if sys.platform == 'win32':
            # Windows: AppData/Local/Floorper/Backups
            appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            return os.path.join(appdata, 'Floorper', 'Backups')
        elif sys.platform == 'darwin':
            # macOS: ~/Library/Application Support/Floorper/Backups
            return os.path.expanduser('~/Library/Application Support/Floorper/Backups')
        else:
            # Linux/Unix: ~/.local/share/floorper/backups
            return os.path.expanduser('~/.local/share/floorper/backups')
    
    def set_backup_directory(self, directory: str) -> bool:
        """
        Set the backup directory.
        
        Args:
            directory: Directory path for backups
            
        Returns:
            True if successful, False otherwise
        """
        try:
            directory = os.path.abspath(directory)
            os.makedirs(directory, exist_ok=True)
            self.backup_dir = directory
            logger.info(f"Backup directory set to: {directory}")
            return True
        except Exception as e:
            logger.error(f"Failed to set backup directory: {str(e)}")
            return False
    
    def create_backup(self, profile: Dict[str, Any], name: Optional[str] = None, 
                     compression: str = 'zip', password: Optional[str] = None,
                     include_data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a backup of a browser profile.
        
        Args:
            profile: Profile information dictionary
            name: Optional backup name (defaults to auto-generated name)
            compression: Compression format ('zip', 'tar', 'none')
            password: Optional password for encryption
            include_data_types: Optional list of data types to include
            
        Returns:
            Dictionary with backup information
        """
        try:
            # Generate backup name if not provided
            if not name:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                browser_name = profile.get('browser_name', 'unknown')
                profile_name = profile.get('name', 'unknown')
                name = f"{browser_name}_{profile_name}_{timestamp}"
            
            # Sanitize name for filesystem
            name = self._sanitize_filename(name)
            
            # Create backup directory
            backup_path = os.path.join(self.backup_dir, name)
            os.makedirs(backup_path, exist_ok=True)
            
            # Determine what to backup
            profile_path = profile.get('path')
            if not profile_path or not os.path.exists(profile_path):
                raise ValueError(f"Profile path does not exist: {profile_path}")
            
            # Filter data types if specified
            if include_data_types:
                # Map data types to directories/files
                data_type_paths = self._map_data_types_to_paths(profile)
                # Filter paths based on included data types
                paths_to_backup = []
                for data_type in include_data_types:
                    if data_type in data_type_paths:
                        paths_to_backup.extend(data_type_paths[data_type])
            else:
                # Backup entire profile
                paths_to_backup = [profile_path]
            
            # Create metadata
            metadata = {
                'name': name,
                'browser_name': profile.get('browser_name', 'unknown'),
                'browser_id': profile.get('browser_id', 'unknown'),
                'profile_name': profile.get('name', 'unknown'),
                'created': datetime.datetime.now().isoformat(),
                'data_types': include_data_types or ['all'],
                'compression': compression,
                'encrypted': password is not None
            }
            
            # Save metadata
            metadata_path = os.path.join(backup_path, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Copy profile data
            for path in paths_to_backup:
                if os.path.exists(path):
                    dest = os.path.join(backup_path, os.path.basename(path))
                    if os.path.isdir(path):
                        shutil.copytree(path, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(path, dest)
            
            # Compress if requested
            archive_path = None
            if compression != 'none':
                archive_path = self._compress_backup(backup_path, name, compression, password)
                # Remove original directory if compression successful
                if archive_path and os.path.exists(archive_path):
                    shutil.rmtree(backup_path)
                    backup_path = archive_path
            
            logger.info(f"Backup created successfully: {backup_path}")
            
            # Return backup information
            return {
                'success': True,
                'name': name,
                'path': backup_path,
                'metadata': metadata
            }
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self, filter_browser: Optional[str] = None, 
                    filter_profile: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            filter_browser: Optional browser ID to filter by
            filter_profile: Optional profile name to filter by
            
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        try:
            # Scan backup directory
            for item in os.listdir(self.backup_dir):
                item_path = os.path.join(self.backup_dir, item)
                
                # Check if it's a directory or archive
                if os.path.isdir(item_path) or item.endswith(('.zip', '.tar.gz')):
                    # Try to get metadata
                    metadata = self._get_backup_metadata(item_path)
                    
                    if metadata:
                        # Apply filters if specified
                        if filter_browser and metadata.get('browser_id') != filter_browser:
                            continue
                        
                        if filter_profile and metadata.get('profile_name') != filter_profile:
                            continue
                        
                        # Add to list
                        backups.append({
                            'name': metadata.get('name', item),
                            'path': item_path,
                            'browser_name': metadata.get('browser_name', 'Unknown'),
                            'profile_name': metadata.get('profile_name', 'Unknown'),
                            'created': metadata.get('created', 'Unknown'),
                            'data_types': metadata.get('data_types', ['all']),
                            'compression': metadata.get('compression', 'none'),
                            'encrypted': metadata.get('encrypted', False),
                            'metadata': metadata
                        })
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.get('created', ''), reverse=True)
            
            logger.info(f"Found {len(backups)} backups")
            return backups
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            return []
    
    def restore_backup(self, backup_name_or_path: str, target_profile: Optional[Dict[str, Any]] = None,
                      password: Optional[str] = None, merge_strategy: str = 'smart',
                      include_data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Restore a backup to a profile.
        
        Args:
            backup_name_or_path: Backup name or path
            target_profile: Optional target profile (if None, restore to original profile)
            password: Optional password for encrypted backups
            merge_strategy: Merge strategy ('smart', 'append', 'overwrite')
            include_data_types: Optional list of data types to restore
            
        Returns:
            Dictionary with restoration result
        """
        try:
            # Find backup
            backup_path = backup_name_or_path
            if not os.path.exists(backup_path):
                # Try as a name in the backup directory
                backup_path = os.path.join(self.backup_dir, backup_name_or_path)
                
                # Try with extensions
                if not os.path.exists(backup_path):
                    for ext in ['.zip', '.tar.gz']:
                        if os.path.exists(backup_path + ext):
                            backup_path = backup_path + ext
                            break
            
            if not os.path.exists(backup_path):
                raise ValueError(f"Backup not found: {backup_name_or_path}")
            
            # Get metadata
            metadata = self._get_backup_metadata(backup_path)
            if not metadata:
                raise ValueError(f"Invalid backup (no metadata): {backup_path}")
            
            # Extract if necessary
            temp_dir = None
            if os.path.isfile(backup_path):
                temp_dir = self._extract_backup(backup_path, password)
                if not temp_dir:
                    raise ValueError(f"Failed to extract backup: {backup_path}")
                backup_path = temp_dir
            
            # Determine target profile
            if not target_profile:
                # Try to find original profile
                browser_id = metadata.get('browser_id')
                profile_name = metadata.get('profile_name')
                
                if browser_id and profile_name:
                    profiles = self.controller.get_browser_profiles(browser_id)
                    target_profile = next((p for p in profiles if p.get('name') == profile_name), None)
            
            if not target_profile:
                raise ValueError("Target profile not specified and original profile not found")
            
            # Filter data types if specified
            if include_data_types:
                data_types = include_data_types
            else:
                data_types = metadata.get('data_types', ['all'])
            
            # Perform restoration
            result = self._restore_profile_data(backup_path, target_profile, data_types, merge_strategy)
            
            # Clean up temp directory if created
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            logger.info(f"Backup restored successfully to {target_profile.get('name')}")
            return {
                'success': True,
                'target_profile': target_profile.get('name'),
                'data_types': data_types,
                'details': result
            }
        except Exception as e:
            logger.error(f"Failed to restore backup: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_backup(self, backup_name_or_path: str) -> bool:
        """
        Delete a backup.
        
        Args:
            backup_name_or_path: Backup name or path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find backup
            backup_path = backup_name_or_path
            if not os.path.exists(backup_path):
                # Try as a name in the backup directory
                backup_path = os.path.join(self.backup_dir, backup_name_or_path)
                
                # Try with extensions
                if not os.path.exists(backup_path):
                    for ext in ['.zip', '.tar.gz']:
                        if os.path.exists(backup_path + ext):
                            backup_path = backup_path + ext
                            break
            
            if not os.path.exists(backup_path):
                raise ValueError(f"Backup not found: {backup_name_or_path}")
            
            # Delete backup
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            else:
                os.remove(backup_path)
            
            logger.info(f"Backup deleted: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup: {str(e)}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename for filesystem compatibility.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:97] + '...'
        
        return filename
    
    def _map_data_types_to_paths(self, profile: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Map data types to file/directory paths.
        
        Args:
            profile: Profile information
            
        Returns:
            Dictionary mapping data types to paths
        """
        profile_path = profile.get('path', '')
        browser_id = profile.get('browser_id', '')
        
        # Default mappings (will be overridden based on browser type)
        mappings = {
            'bookmarks': [],
            'history': [],
            'passwords': [],
            'cookies': [],
            'extensions': [],
            'preferences': [],
            'sessions': []
        }
        
        # Firefox-based browsers
        if browser_id in ['firefox', 'floorp', 'waterfox', 'librewolf', 'palemoon', 'seamonkey']:
            mappings = {
                'bookmarks': [os.path.join(profile_path, 'places.sqlite')],
                'history': [os.path.join(profile_path, 'places.sqlite')],
                'passwords': [
                    os.path.join(profile_path, 'logins.json'),
                    os.path.join(profile_path, 'key4.db'),
                    os.path.join(profile_path, 'signons.sqlite')
                ],
                'cookies': [os.path.join(profile_path, 'cookies.sqlite')],
                'extensions': [os.path.join(profile_path, 'extensions')],
                'preferences': [
                    os.path.join(profile_path, 'prefs.js'),
                    os.path.join(profile_path, 'user.js')
                ],
                'sessions': [
                    os.path.join(profile_path, 'sessionstore.js'),
                    os.path.join(profile_path, 'sessionstore.jsonlz4')
                ]
            }
        # Chrome-based browsers
        elif browser_id in ['chrome', 'chromium', 'edge', 'brave', 'opera', 'vivaldi']:
            mappings = {
                'bookmarks': [os.path.join(profile_path, 'Bookmarks')],
                'history': [os.path.join(profile_path, 'History')],
                'passwords': [
                    os.path.join(profile_path, 'Login Data'),
                    os.path.join(profile_path, 'Login Data For Account')
                ],
                'cookies': [os.path.join(profile_path, 'Cookies')],
                'extensions': [os.path.join(profile_path, 'Extensions')],
                'preferences': [
                    os.path.join(profile_path, 'Preferences'),
                    os.path.join(profile_path, 'Secure Preferences')
                ],
                'sessions': [
                    os.path.join(profile_path, 'Current Session'),
                    os.path.join(profile_path, 'Current Tabs')
                ]
            }
        
        return mappings
    
    def _get_backup_metadata(self, backup_path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata from a backup.
        
        Args:
            backup_path: Backup path
            
        Returns:
            Metadata dictionary or None if not found
        """
        try:
            metadata_path = os.path.join(backup_path, 'metadata.json')
            
            # If it's a directory, check for metadata file
            if os.path.isdir(backup_path) and os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            
            # If it's a zip file, extract metadata
            elif backup_path.endswith('.zip') and os.path.isfile(backup_path):
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    if 'metadata.json' in zip_ref.namelist():
                        with zip_ref.open('metadata.json') as f:
                            return json.loads(f.read().decode('utf-8'))
            
            # If it's a tar.gz file, extract metadata
            elif backup_path.endswith('.tar.gz') and os.path.isfile(backup_path):
                import tarfile
                with tarfile.open(backup_path, 'r:gz') as tar_ref:
                    for member in tar_ref.getmembers():
                        if member.name.endswith('metadata.json'):
                            f = tar_ref.extractfile(member)
                            if f:
                                return json.loads(f.read().decode('utf-8'))
            
            return None
        except Exception as e:
            logger.error(f"Failed to get backup metadata: {str(e)}")
            return None
    
    def _compress_backup(self, backup_path: str, name: str, compression: str, 
                        password: Optional[str] = None) -> Optional[str]:
        """
        Compress a backup directory.
        
        Args:
            backup_path: Path to backup directory
            name: Backup name
            compression: Compression format ('zip', 'tar')
            password: Optional password for encryption
            
        Returns:
            Path to compressed file or None if failed
        """
        try:
            if compression == 'zip':
                archive_path = os.path.join(self.backup_dir, f"{name}.zip")
                
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    # Add all files in the backup directory
                    for root, _, files in os.walk(backup_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(backup_path))
                            zip_ref.write(file_path, arcname)
                
                return archive_path
            
            elif compression == 'tar':
                import tarfile
                archive_path = os.path.join(self.backup_dir, f"{name}.tar.gz")
                
                with tarfile.open(archive_path, 'w:gz') as tar_ref:
                    # Add all files in the backup directory
                    tar_ref.add(backup_path, arcname=name)
                
                return archive_path
            
            else:
                logger.warning(f"Unsupported compression format: {compression}")
                return None
        except Exception as e:
            logger.error(f"Failed to compress backup: {str(e)}")
            return None
    
    def _extract_backup(self, backup_path: str, password: Optional[str] = None) -> Optional[str]:
        """
        Extract a compressed backup.
        
        Args:
            backup_path: Path to compressed backup
            password: Optional password for encrypted backups
            
        Returns:
            Path to extracted directory or None if failed
        """
        try:
            # Create temporary directory
            temp_dir = os.path.join(self.backup_dir, f"temp_{os.path.basename(backup_path)}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract based on file type
            if backup_path.endswith('.zip'):
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    # Handle password if provided
                    if password:
                        zip_ref.setpassword(password.encode())
                    zip_ref.extractall(temp_dir)
                
                return temp_dir
            
            elif backup_path.endswith('.tar.gz'):
                import tarfile
                with tarfile.open(backup_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(temp_dir)
                
                return temp_dir
            
            else:
                logger.warning(f"Unsupported archive format: {backup_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to extract backup: {str(e)}")
            return None
    
    def _restore_profile_data(self, backup_path: str, target_profile: Dict[str, Any],
                             data_types: List[str], merge_strategy: str) -> Dict[str, Any]:
        """
        Restore profile data from a backup.
        
        Args:
            backup_path: Path to extracted backup
            target_profile: Target profile information
            data_types: Data types to restore
            merge_strategy: Merge strategy
            
        Returns:
            Dictionary with restoration details
        """
        result = {
            'success': True,
            'details': {}
        }
        
        target_path = target_profile.get('path')
        if not target_path or not os.path.exists(target_path):
            raise ValueError(f"Target profile path does not exist: {target_path}")
        
        # Create backup of target profile before restoration
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        target_backup_dir = os.path.join(self.backup_dir, f"pre_restore_{os.path.basename(target_path)}_{timestamp}")
        
        try:
            # Copy target profile to backup
            shutil.copytree(target_path, target_backup_dir)
            
            # Map data types to paths
            data_type_paths = self._map_data_types_to_paths(target_profile)
            
            # Handle 'all' data type
            if 'all' in data_types:
                data_types = list(data_type_paths.keys())
            
            # Restore each data type
            for data_type in data_types:
                try:
                    if data_type in data_type_paths:
                        paths = data_type_paths[data_type]
                        
                        # Find corresponding files in backup
                        for path in paths:
                            rel_path = os.path.basename(path)
                            backup_file = self._find_file_in_backup(backup_path, rel_path)
                            
                            if backup_file and os.path.exists(backup_file):
                                # Restore based on merge strategy
                                if merge_strategy == 'overwrite':
                                    # Make sure target directory exists
                                    os.makedirs(os.path.dirname(path), exist_ok=True)
                                    
                                    # Copy file or directory
                                    if os.path.isdir(backup_file):
                                        if os.path.exists(path):
                                            shutil.rmtree(path)
                                        shutil.copytree(backup_file, path)
                                    else:
                                        shutil.copy2(backup_file, path)
                                
                                elif merge_strategy == 'append':
                                    # For directories, copy contents without overwriting
                                    if os.path.isdir(backup_file):
                                        os.makedirs(path, exist_ok=True)
                                        for item in os.listdir(backup_file):
                                            src = os.path.join(backup_file, item)
                                            dst = os.path.join(path, item)
                                            if not os.path.exists(dst):
                                                if os.path.isdir(src):
                                                    shutil.copytree(src, dst)
                                                else:
                                                    shutil.copy2(src, dst)
                                    # For files, use specialized merging based on file type
                                    else:
                                        self._merge_files(backup_file, path, data_type)
                                
                                elif merge_strategy == 'smart':
                                    # Use specialized merging based on data type
                                    if os.path.isdir(backup_file):
                                        self._smart_merge_directory(backup_file, path, data_type)
                                    else:
                                        self._smart_merge_file(backup_file, path, data_type)
                        
                        result['details'][data_type] = {
                            'success': True,
                            'message': f"Restored {data_type} data"
                        }
                    else:
                        result['details'][data_type] = {
                            'success': False,
                            'message': f"No paths defined for data type: {data_type}"
                        }
                except Exception as e:
                    logger.error(f"Failed to restore {data_type}: {str(e)}")
                    result['details'][data_type] = {
                        'success': False,
                        'message': f"Error: {str(e)}"
                    }
                    result['success'] = False
            
            return result
        except Exception as e:
            logger.error(f"Failed to restore profile data: {str(e)}")
            
            # Try to restore from backup if something went wrong
            if os.path.exists(target_backup_dir):
                try:
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    shutil.copytree(target_backup_dir, target_path)
                    logger.info(f"Restored target profile from backup after error")
                except Exception as restore_error:
                    logger.error(f"Failed to restore from backup: {str(restore_error)}")
            
            raise
    
    def _find_file_in_backup(self, backup_path: str, filename: str) -> Optional[str]:
        """
        Find a file in the backup directory.
        
        Args:
            backup_path: Backup directory path
            filename: Filename to find
            
        Returns:
            Full path to file or None if not found
        """
        # First try direct match
        direct_match = os.path.join(backup_path, filename)
        if os.path.exists(direct_match):
            return direct_match
        
        # Search recursively
        for root, _, files in os.walk(backup_path):
            if filename in files:
                return os.path.join(root, filename)
            
            # Also check directories
            if os.path.basename(root) == filename:
                return root
        
        return None
    
    def _merge_files(self, source: str, target: str, data_type: str) -> None:
        """
        Merge two files based on data type.
        
        Args:
            source: Source file path
            target: Target file path
            data_type: Data type
        """
        # Simple append for text files
        if data_type in ['preferences']:
            # Ensure target exists
            if not os.path.exists(target):
                shutil.copy2(source, target)
                return
            
            # Append content
            with open(source, 'r', encoding='utf-8', errors='ignore') as src_file:
                with open(target, 'a', encoding='utf-8') as tgt_file:
                    tgt_file.write('\n\n// Merged from backup\n')
                    tgt_file.write(src_file.read())
        
        # For other types, just copy if target doesn't exist
        elif not os.path.exists(target):
            shutil.copy2(source, target)
    
    def _smart_merge_directory(self, source: str, target: str, data_type: str) -> None:
        """
        Smart merge directories based on data type.
        
        Args:
            source: Source directory path
            target: Target directory path
            data_type: Data type
        """
        # Create target if it doesn't exist
        os.makedirs(target, exist_ok=True)
        
        # Extensions: copy missing extensions
        if data_type == 'extensions':
            for item in os.listdir(source):
                src = os.path.join(source, item)
                dst = os.path.join(target, item)
                
                # Only copy if doesn't exist
                if not os.path.exists(dst):
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
        
        # For other types, recursively copy missing files
        else:
            for root, dirs, files in os.walk(source):
                # Get relative path
                rel_path = os.path.relpath(root, source)
                target_dir = os.path.join(target, rel_path)
                
                # Create target directory
                os.makedirs(target_dir, exist_ok=True)
                
                # Copy files
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    
                    if not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)
    
    def _smart_merge_file(self, source: str, target: str, data_type: str) -> None:
        """
        Smart merge files based on data type.
        
        Args:
            source: Source file path
            target: Target file path
            data_type: Data type
        """
        # If target doesn't exist, just copy
        if not os.path.exists(target):
            shutil.copy2(source, target)
            return
        
        # SQLite databases: use specialized merging
        if data_type in ['bookmarks', 'history', 'cookies'] and (
                target.endswith('.sqlite') or target.endswith('.db')):
            self._merge_sqlite_database(source, target, data_type)
        
        # JSON files: merge objects
        elif target.endswith('.json'):
            self._merge_json_file(source, target)
        
        # Preferences: append with conflict resolution
        elif data_type == 'preferences':
            self._merge_preferences_file(source, target)
        
        # Default: overwrite if source is newer
        elif os.path.getmtime(source) > os.path.getmtime(target):
            shutil.copy2(source, target)
    
    def _merge_sqlite_database(self, source: str, target: str, data_type: str) -> None:
        """
        Merge SQLite databases.
        
        Args:
            source: Source database path
            target: Target database path
            data_type: Data type
        """
        # This requires specialized handling based on schema
        # For now, we'll use a simple approach of attaching and copying
        try:
            import sqlite3
            
            # Create backup of target
            backup_file = f"{target}.bak"
            shutil.copy2(target, backup_file)
            
            # Connect to target database
            conn = sqlite3.connect(target)
            cursor = conn.cursor()
            
            # Attach source database
            cursor.execute(f"ATTACH DATABASE ? AS source", (source,))
            
            # Merge based on data type
            if data_type == 'bookmarks':
                # For Firefox places.sqlite
                if 'moz_bookmarks' in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
                    # Copy bookmarks from source to target
                    cursor.execute("""
                        INSERT OR IGNORE INTO moz_bookmarks 
                        SELECT * FROM source.moz_bookmarks
                    """)
                    
                    # Copy bookmark metadata
                    cursor.execute("""
                        INSERT OR IGNORE INTO moz_places 
                        SELECT * FROM source.moz_places
                    """)
            
            elif data_type == 'history':
                # For Firefox places.sqlite
                if 'moz_places' in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
                    # Copy history entries
                    cursor.execute("""
                        INSERT OR IGNORE INTO moz_places 
                        SELECT * FROM source.moz_places
                    """)
                    
                    # Copy visit history
                    cursor.execute("""
                        INSERT OR IGNORE INTO moz_historyvisits 
                        SELECT * FROM source.moz_historyvisits
                    """)
            
            elif data_type == 'cookies':
                # For Firefox cookies.sqlite
                if 'moz_cookies' in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")]:
                    # Copy cookies
                    cursor.execute("""
                        INSERT OR IGNORE INTO moz_cookies 
                        SELECT * FROM source.moz_cookies
                    """)
            
            # Commit changes and detach
            conn.commit()
            cursor.execute("DETACH DATABASE source")
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to merge SQLite database: {str(e)}")
            # Restore from backup
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, target)
            raise
    
    def _merge_json_file(self, source: str, target: str) -> None:
        """
        Merge JSON files.
        
        Args:
            source: Source JSON file path
            target: Target JSON file path
        """
        try:
            # Load JSON files
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                source_data = json.load(f)
            
            with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                target_data = json.load(f)
            
            # Merge based on data structure
            if isinstance(source_data, dict) and isinstance(target_data, dict):
                # Deep merge dictionaries
                merged_data = self._deep_merge_dicts(target_data, source_data)
            elif isinstance(source_data, list) and isinstance(target_data, list):
                # Combine lists, removing duplicates
                merged_data = target_data
                for item in source_data:
                    if item not in target_data:
                        merged_data.append(item)
            else:
                # If structures don't match, prefer target
                merged_data = target_data
            
            # Write merged data
            with open(target, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to merge JSON file: {str(e)}")
            # If error, keep target unchanged
    
    def _deep_merge_dicts(self, target: Dict, source: Dict) -> Dict:
        """
        Deep merge two dictionaries.
        
        Args:
            target: Target dictionary
            source: Source dictionary
            
        Returns:
            Merged dictionary
        """
        result = target.copy()
        
        for key, value in source.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge_dicts(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # Combine lists, removing duplicates
                for item in value:
                    if item not in result[key]:
                        result[key].append(item)
            elif key not in result:
                # Add new keys
                result[key] = value
        
        return result
    
    def _merge_preferences_file(self, source: str, target: str) -> None:
        """
        Merge preferences files.
        
        Args:
            source: Source preferences file path
            target: Target preferences file path
        """
        try:
            # Read files
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                source_content = f.readlines()
            
            with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                target_content = f.readlines()
            
            # Extract preferences from source
            source_prefs = {}
            for line in source_content:
                line = line.strip()
                if line.startswith('user_pref(') or line.startswith('pref('):
                    try:
                        # Extract key and value
                        key_start = line.find('"') + 1
                        key_end = line.find('"', key_start)
                        key = line[key_start:key_end]
                        
                        value_start = line.find(',', key_end) + 1
                        value_end = line.rfind(')')
                        value = line[value_start:value_end].strip()
                        
                        source_prefs[key] = (line, value)
                    except:
                        pass
            
            # Extract preferences from target
            target_prefs = {}
            for line in target_content:
                line = line.strip()
                if line.startswith('user_pref(') or line.startswith('pref('):
                    try:
                        # Extract key and value
                        key_start = line.find('"') + 1
                        key_end = line.find('"', key_start)
                        key = line[key_start:key_end]
                        
                        value_start = line.find(',', key_end) + 1
                        value_end = line.rfind(')')
                        value = line[value_start:value_end].strip()
                        
                        target_prefs[key] = (line, value)
                    except:
                        pass
            
            # Merge preferences
            merged_content = target_content.copy()
            
            # Add comment for merged preferences
            merged_content.append('\n// Merged preferences from backup\n')
            
            # Add new preferences from source
            for key, (line, _) in source_prefs.items():
                if key not in target_prefs:
                    merged_content.append(line + '\n')
            
            # Write merged content
            with open(target, 'w', encoding='utf-8') as f:
                f.writelines(merged_content)
            
        except Exception as e:
            logger.error(f"Failed to merge preferences file: {str(e)}")
            # If error, keep target unchanged


def main():
    """Main entry point for testing."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create controller
    controller = FloorperCore()
    
    # Create backup manager
    backup_manager = BackupManager(controller)
    
    # Test functionality
    print(f"Backup directory: {backup_manager.backup_dir}")
    
    # List backups
    backups = backup_manager.list_backups()
    print(f"Found {len(backups)} backups")
    
    for backup in backups:
        print(f"- {backup['name']} ({backup['browser_name']} - {backup['profile_name']})")


if __name__ == "__main__":
    main()
