"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides common utilities for the Floorper application.
"""

import os
import sys
import logging
import platform
import shutil
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

# Setup logging
logger = logging.getLogger('floorper.utils')

def get_platform() -> str:
    """
    Get the current platform identifier.
    
    Returns:
        String identifying the platform: 'windows', 'macos', 'linux', 'haiku', 'os2', or 'unknown'
    """
    system = platform.system().lower()
    
    if system == 'windows' or system.startswith('win'):
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    elif system == 'haiku':
        return 'haiku'
    elif system == 'os/2' or system == 'os2':
        return 'os2'
    else:
        return 'unknown'

def get_home_dir() -> str:
    """
    Get the user's home directory in a cross-platform way.
    
    Returns:
        Path to the user's home directory
    """
    return str(Path.home())

def get_app_data_dir(app_name: str = 'floorper') -> str:
    """
    Get the application data directory in a cross-platform way.
    
    Args:
        app_name: Name of the application
        
    Returns:
        Path to the application data directory
    """
    platform_type = get_platform()
    
    if platform_type == 'windows':
        base_dir = os.environ.get('APPDATA', os.path.join(get_home_dir(), 'AppData', 'Roaming'))
        return os.path.join(base_dir, app_name)
    elif platform_type == 'macos':
        return os.path.join(get_home_dir(), 'Library', 'Application Support', app_name)
    elif platform_type == 'haiku':
        return os.path.join(get_home_dir(), 'config', 'settings', app_name)
    elif platform_type == 'os2':
        return os.path.join(get_home_dir(), app_name)
    else:  # Linux and others
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME', os.path.join(get_home_dir(), '.config'))
        return os.path.join(xdg_config_home, app_name)

def ensure_dir_exists(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def copy_file_safe(src: str, dst: str) -> bool:
    """
    Copy a file safely, ensuring the destination directory exists.
    
    Args:
        src: Source file path
        dst: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        dst_dir = os.path.dirname(dst)
        ensure_dir_exists(dst_dir)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        logger.error(f"Failed to copy file from {src} to {dst}: {str(e)}")
        return False

def merge_files(src_files: List[str], dst_file: str, append: bool = True) -> bool:
    """
    Merge multiple files into one.
    
    Args:
        src_files: List of source file paths
        dst_file: Destination file path
        append: Whether to append to the destination file if it exists
        
    Returns:
        True if successful, False otherwise
    """
    try:
        dst_dir = os.path.dirname(dst_file)
        ensure_dir_exists(dst_dir)
        
        mode = 'a' if append and os.path.exists(dst_file) else 'w'
        
        with open(dst_file, mode, encoding='utf-8') as dst_f:
            for src_file in src_files:
                if os.path.exists(src_file):
                    with open(src_file, 'r', encoding='utf-8', errors='ignore') as src_f:
                        dst_f.write(f"\n# Merged from {os.path.basename(src_file)}\n")
                        dst_f.write(src_f.read())
                        dst_f.write("\n")
        
        return True
    except Exception as e:
        logger.error(f"Failed to merge files into {dst_file}: {str(e)}")
        return False

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with the JSON data, or None if loading failed
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {str(e)}")
        return None

def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save JSON data to a file.
    
    Args:
        data: Dictionary with the JSON data
        file_path: Path to the JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        dst_dir = os.path.dirname(file_path)
        ensure_dir_exists(dst_dir)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {file_path}: {str(e)}")
        return False

def find_files(directory: str, pattern: str) -> List[str]:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search
        pattern: Regex pattern to match
        
    Returns:
        List of matching file paths
    """
    result = []
    try:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for file in files:
                    if re.search(pattern, file):
                        result.append(os.path.join(root, file))
    except Exception as e:
        logger.error(f"Error finding files in {directory} with pattern {pattern}: {str(e)}")
    
    return result

def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Size of the file in bytes, or 0 if the file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception as e:
        logger.error(f"Failed to get size of {file_path}: {str(e)}")
        return 0

def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def get_browser_icon_path(browser_id: str) -> str:
    """
    Get the path to a browser icon.
    
    Args:
        browser_id: Browser identifier
        
    Returns:
        Path to the browser icon, or empty string if not found
    """
    # In a real implementation, this would return the path to an icon file
    # For now, we'll just return a placeholder
    return ""

def is_admin() -> bool:
    """
    Check if the current process has administrator/root privileges.
    
    Returns:
        True if the process has admin privileges, False otherwise
    """
    try:
        if get_platform() == 'windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def run_as_admin(command: List[str]) -> bool:
    """
    Run a command with administrator/root privileges.
    
    Args:
        command: Command to run as a list of strings
        
    Returns:
        True if successful, False otherwise
    """
    try:
        platform_type = get_platform()
        
        if platform_type == 'windows':
            import ctypes
            import subprocess
            
            if is_admin():
                # Already running as admin, just run the command
                subprocess.run(command, check=True)
                return True
            else:
                # Try to elevate privileges
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(command), None, 1)
                return True
        else:
            # For Unix-like systems, use sudo
            if is_admin():
                # Already running as root, just run the command
                import subprocess
                subprocess.run(command, check=True)
                return True
            else:
                # Use sudo
                import subprocess
                sudo_command = ["sudo"] + command
                subprocess.run(sudo_command, check=True)
                return True
    except Exception as e:
        logger.error(f"Failed to run command as admin: {str(e)}")
        return False

def get_temp_dir() -> str:
    """
    Get a temporary directory for the application.
    
    Returns:
        Path to the temporary directory
    """
    import tempfile
    temp_dir = os.path.join(tempfile.gettempdir(), 'floorper')
    ensure_dir_exists(temp_dir)
    return temp_dir

def create_backup(source_path: str, backup_name: Optional[str] = None) -> Optional[str]:
    """
    Create a backup of a file or directory.
    
    Args:
        source_path: Path to the file or directory to backup
        backup_name: Optional name for the backup
        
    Returns:
        Path to the backup file, or None if backup failed
    """
    try:
        if not os.path.exists(source_path):
            logger.error(f"Source path does not exist: {source_path}")
            return None
        
        # Generate backup name if not provided
        if backup_name is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(source_path)}_{timestamp}"
        
        # Create backup directory
        backup_dir = os.path.join(get_app_data_dir(), 'backups')
        ensure_dir_exists(backup_dir)
        
        # Create backup path
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Create backup
        if os.path.isdir(source_path):
            shutil.copytree(source_path, backup_path)
        else:
            shutil.copy2(source_path, backup_path)
        
        logger.info(f"Created backup of {source_path} at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup of {source_path}: {str(e)}")
        return None

def restore_backup(backup_path: str, target_path: str) -> bool:
    """
    Restore a backup to a target path.
    
    Args:
        backup_path: Path to the backup
        target_path: Path to restore to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(backup_path):
            logger.error(f"Backup path does not exist: {backup_path}")
            return False
        
        # Create backup of target before restoring
        if os.path.exists(target_path):
            create_backup(target_path)
            
            # Remove target
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
        
        # Create target directory if needed
        target_dir = os.path.dirname(target_path)
        ensure_dir_exists(target_dir)
        
        # Restore backup
        if os.path.isdir(backup_path):
            shutil.copytree(backup_path, target_path)
        else:
            shutil.copy2(backup_path, target_path)
        
        logger.info(f"Restored backup from {backup_path} to {target_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to restore backup from {backup_path} to {target_path}: {str(e)}")
        return False

def list_backups() -> List[Dict[str, Any]]:
    """
    List available backups.
    
    Returns:
        List of dictionaries with backup information
    """
    result = []
    try:
        backup_dir = os.path.join(get_app_data_dir(), 'backups')
        
        if os.path.exists(backup_dir):
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                
                # Get item info
                stat_info = os.stat(item_path)
                import datetime
                
                backup_info = {
                    'name': item,
                    'path': item_path,
                    'size': get_file_size(item_path),
                    'size_formatted': format_size(get_file_size(item_path)),
                    'is_dir': os.path.isdir(item_path),
                    'created': datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                }
                
                result.append(backup_info)
    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}")
    
    return result

def delete_backup(backup_path: str) -> bool:
    """
    Delete a backup.
    
    Args:
        backup_path: Path to the backup
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(backup_path):
            logger.error(f"Backup path does not exist: {backup_path}")
            return False
        
        # Delete backup
        if os.path.isdir(backup_path):
            shutil.rmtree(backup_path)
        else:
            os.remove(backup_path)
        
        logger.info(f"Deleted backup at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete backup at {backup_path}: {str(e)}")
        return False

def get_floorp_profiles_dir() -> str:
    """
    Get the Floorp profiles directory.
    
    Returns:
        Path to the Floorp profiles directory
    """
    platform_type = get_platform()
    
    if platform_type == 'windows':
        return os.path.join(os.environ.get('APPDATA', ''), 'Floorp', 'Profiles')
    elif platform_type == 'macos':
        return os.path.join(get_home_dir(), 'Library', 'Application Support', 'Floorp', 'Profiles')
    elif platform_type == 'haiku':
        return os.path.join(get_home_dir(), 'config', 'settings', 'Floorp', 'Profiles')
    elif platform_type == 'os2':
        return os.path.join(get_home_dir(), 'Floorp', 'Profiles')
    else:  # Linux and others
        return os.path.join(get_home_dir(), '.floorp', 'Profiles')

def get_floorp_profiles() -> List[Dict[str, Any]]:
    """
    Get available Floorp profiles.
    
    Returns:
        List of dictionaries with profile information
    """
    result = []
    try:
        profiles_dir = get_floorp_profiles_dir()
        
        if os.path.exists(profiles_dir):
            # Read profiles.ini
            profiles_ini = os.path.join(os.path.dirname(profiles_dir), 'profiles.ini')
            
            if os.path.exists(profiles_ini):
                # Parse profiles.ini
                profiles = {}
                current_section = None
                
                with open(profiles_ini, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        
                        if line.startswith('[') and line.endswith(']'):
                            # Section header
                            current_section = line[1:-1]
                            if current_section.startswith('Profile'):
                                profiles[current_section] = {}
                        elif '=' in line and current_section is not None and current_section.startswith('Profile'):
                            # Key-value pair
                            key, value = line.split('=', 1)
                            profiles[current_section][key.strip()] = value.strip()
                
                # Process profiles
                for section, profile_data in profiles.items():
                    if 'Path' in profile_data:
                        path = profile_data['Path']
                        
                        # Handle relative paths
                        if not os.path.isabs(path):
                            path = os.path.join(os.path.dirname(profiles_dir), path)
                        
                        # Check if path exists
                        if os.path.exists(path):
                            profile_info = {
                                'name': profile_data.get('Name', section),
                                'path': path,
                                'is_default': profile_data.get('Default', '0') == '1',
                                'is_relative': not os.path.isabs(profile_data['Path'])
                            }
                            
                            result.append(profile_info)
            
            # If no profiles found in profiles.ini, try to find them directly
            if not result:
                for item in os.listdir(profiles_dir):
                    item_path = os.path.join(profiles_dir, item)
                    
                    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'prefs.js')):
                        profile_info = {
                            'name': item,
                            'path': item_path,
                            'is_default': 'default' in item.lower(),
                            'is_relative': False
                        }
                        
                        result.append(profile_info)
    except Exception as e:
        logger.error(f"Failed to get Floorp profiles: {str(e)}")
    
    return result

def get_browser_profiles(browser_id: str) -> List[Dict[str, Any]]:
    """
    Get profiles for a specific browser.
    
    Args:
        browser_id: Browser identifier
        
    Returns:
        List of dictionaries with profile information
    """
    # For Floorp, use the dedicated function
    if browser_id == 'floorp':
        return get_floorp_profiles()
    
    # For other browsers, this would be implemented in the browser detector
    # For now, return an empty list
    return []

def create_floorp_profile(name: str) -> Optional[Dict[str, Any]]:
    """
    Create a new Floorp profile.
    
    Args:
        name: Profile name
        
    Returns:
        Dictionary with profile information, or None if creation failed
    """
    try:
        # Get profiles directory
        profiles_dir = get_floorp_profiles_dir()
        ensure_dir_exists(profiles_dir)
        
        # Create profile directory
        import uuid
        profile_id = str(uuid.uuid4())
        profile_dir = os.path.join(profiles_dir, f"{name}.{profile_id}")
        ensure_dir_exists(profile_dir)
        
        # Create minimal profile files
        with open(os.path.join(profile_dir, 'prefs.js'), 'w', encoding='utf-8') as f:
            f.write('// Floorp preferences\n')
        
        with open(os.path.join(profile_dir, 'user.js'), 'w', encoding='utf-8') as f:
            f.write('// User preferences\n')
        
        # Update profiles.ini
        profiles_ini = os.path.join(os.path.dirname(profiles_dir), 'profiles.ini')
        
        # Read existing profiles.ini if it exists
        profiles = {}
        max_index = -1
        
        if os.path.exists(profiles_ini):
            current_section = None
            
            with open(profiles_ini, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    
                    if line.startswith('[') and line.endswith(']'):
                        # Section header
                        current_section = line[1:-1]
                        if current_section.startswith('Profile'):
                            profiles[current_section] = {}
                            
                            # Extract index
                            try:
                                index = int(current_section[7:])
                                max_index = max(max_index, index)
                            except ValueError:
                                pass
                    elif '=' in line and current_section is not None:
                        # Key-value pair
                        key, value = line.split('=', 1)
                        profiles[current_section][key.strip()] = value.strip()
        
        # Create new profile entry
        new_index = max_index + 1
        new_section = f"Profile{new_index}"
        
        profiles[new_section] = {
            'Name': name,
            'IsRelative': '1',
            'Path': f"Profiles/{name}.{profile_id}",
            'Default': '0'
        }
        
        # Write updated profiles.ini
        with open(profiles_ini, 'w', encoding='utf-8') as f:
            # Write General section if it exists
            if 'General' in profiles:
                f.write('[General]\n')
                for key, value in profiles['General'].items():
                    f.write(f"{key}={value}\n")
                f.write('\n')
            
            # Write profile sections
            for section, data in profiles.items():
                if section != 'General':
                    f.write(f"[{section}]\n")
                    for key, value in data.items():
                        f.write(f"{key}={value}\n")
                    f.write('\n')
        
        # Return profile info
        return {
            'name': name,
            'path': profile_dir,
            'is_default': False,
            'is_relative': True
        }
    except Exception as e:
        logger.error(f"Failed to create Floorp profile: {str(e)}")
        return None

def set_default_floorp_profile(profile_path: str) -> bool:
    """
    Set a Floorp profile as the default.
    
    Args:
        profile_path: Path to the profile
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get profiles directory
        profiles_dir = get_floorp_profiles_dir()
        
        # Update profiles.ini
        profiles_ini = os.path.join(os.path.dirname(profiles_dir), 'profiles.ini')
        
        if not os.path.exists(profiles_ini):
            logger.error(f"Profiles.ini not found at {profiles_ini}")
            return False
        
        # Read profiles.ini
        profiles = {}
        current_section = None
        
        with open(profiles_ini, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('[') and line.endswith(']'):
                    # Section header
                    current_section = line[1:-1]
                    if current_section not in profiles:
                        profiles[current_section] = {}
                elif '=' in line and current_section is not None:
                    # Key-value pair
                    key, value = line.split('=', 1)
                    profiles[current_section][key.strip()] = value.strip()
        
        # Find the profile and set it as default
        target_path = profile_path
        if os.path.isabs(profile_path):
            # Convert to relative path if needed
            rel_path = os.path.relpath(profile_path, os.path.dirname(profiles_dir))
            if rel_path.startswith('Profiles/'):
                target_path = rel_path
        
        found = False
        
        for section, data in profiles.items():
            if section.startswith('Profile'):
                path = data.get('Path', '')
                
                # Check if this is the target profile
                if path == target_path or os.path.join(os.path.dirname(profiles_dir), path) == profile_path:
                    # Set as default
                    profiles[section]['Default'] = '1'
                    found = True
                else:
                    # Unset default
                    profiles[section]['Default'] = '0'
        
        if not found:
            logger.error(f"Profile not found: {profile_path}")
            return False
        
        # Write updated profiles.ini
        with open(profiles_ini, 'w', encoding='utf-8') as f:
            # Write General section if it exists
            if 'General' in profiles:
                f.write('[General]\n')
                for key, value in profiles['General'].items():
                    f.write(f"{key}={value}\n")
                f.write('\n')
            
            # Write profile sections
            for section, data in profiles.items():
                if section != 'General':
                    f.write(f"[{section}]\n")
                    for key, value in data.items():
                        f.write(f"{key}={value}\n")
                    f.write('\n')
        
        return True
    except Exception as e:
        logger.error(f"Failed to set default Floorp profile: {str(e)}")
        return False

def delete_floorp_profile(profile_path: str) -> bool:
    """
    Delete a Floorp profile.
    
    Args:
        profile_path: Path to the profile
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get profiles directory
        profiles_dir = get_floorp_profiles_dir()
        
        # Check if profile exists
        if not os.path.exists(profile_path):
            logger.error(f"Profile not found: {profile_path}")
            return False
        
        # Create backup before deletion
        create_backup(profile_path)
        
        # Update profiles.ini
        profiles_ini = os.path.join(os.path.dirname(profiles_dir), 'profiles.ini')
        
        if os.path.exists(profiles_ini):
            # Read profiles.ini
            profiles = {}
            current_section = None
            
            with open(profiles_ini, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    
                    if line.startswith('[') and line.endswith(']'):
                        # Section header
                        current_section = line[1:-1]
                        if current_section not in profiles:
                            profiles[current_section] = {}
                    elif '=' in line and current_section is not None:
                        # Key-value pair
                        key, value = line.split('=', 1)
                        profiles[current_section][key.strip()] = value.strip()
            
            # Find the profile and remove it
            target_path = profile_path
            if os.path.isabs(profile_path):
                # Convert to relative path if needed
                rel_path = os.path.relpath(profile_path, os.path.dirname(profiles_dir))
                if rel_path.startswith('Profiles/'):
                    target_path = rel_path
            
            sections_to_remove = []
            
            for section, data in profiles.items():
                if section.startswith('Profile'):
                    path = data.get('Path', '')
                    
                    # Check if this is the target profile
                    if path == target_path or os.path.join(os.path.dirname(profiles_dir), path) == profile_path:
                        sections_to_remove.append(section)
            
            # Remove sections
            for section in sections_to_remove:
                del profiles[section]
            
            # Write updated profiles.ini
            with open(profiles_ini, 'w', encoding='utf-8') as f:
                # Write General section if it exists
                if 'General' in profiles:
                    f.write('[General]\n')
                    for key, value in profiles['General'].items():
                        f.write(f"{key}={value}\n")
                    f.write('\n')
                
                # Write profile sections
                for section, data in profiles.items():
                    if section != 'General':
                        f.write(f"[{section}]\n")
                        for key, value in data.items():
                            f.write(f"{key}={value}\n")
                        f.write('\n')
        
        # Delete profile directory
        if os.path.isdir(profile_path):
            shutil.rmtree(profile_path)
        
        return True
    except Exception as e:
        logger.error(f"Failed to delete Floorp profile: {str(e)}")
        return False

def get_browser_executable(browser_id: str) -> Optional[str]:
    """
    Get the path to a browser executable.
    
    Args:
        browser_id: Browser identifier
        
    Returns:
        Path to the browser executable, or None if not found
    """
    platform_type = get_platform()
    
    # Define common locations for each browser on each platform
    browser_paths = {
        'floorp': {
            'windows': [
                os.path.expandvars(r'%ProgramFiles%\Floorp\floorp.exe'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Floorp\floorp.exe'),
                os.path.expandvars(r'%LOCALAPPDATA%\Floorp\floorp.exe')
            ],
            'macos': [
                '/Applications/Floorp.app/Contents/MacOS/floorp',
                os.path.expanduser('~/Applications/Floorp.app/Contents/MacOS/floorp')
            ],
            'linux': [
                '/usr/bin/floorp',
                '/usr/local/bin/floorp',
                '/opt/floorp/floorp'
            ],
            'haiku': [
                '/boot/apps/Floorp/Floorp'
            ],
            'os2': [
                'C:\\Floorp\\floorp.exe'
            ]
        },
        'firefox': {
            'windows': [
                os.path.expandvars(r'%ProgramFiles%\Mozilla Firefox\firefox.exe'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe'),
                os.path.expandvars(r'%LOCALAPPDATA%\Mozilla Firefox\firefox.exe')
            ],
            'macos': [
                '/Applications/Firefox.app/Contents/MacOS/firefox',
                os.path.expanduser('~/Applications/Firefox.app/Contents/MacOS/firefox')
            ],
            'linux': [
                '/usr/bin/firefox',
                '/usr/local/bin/firefox',
                '/opt/firefox/firefox'
            ],
            'haiku': [
                '/boot/apps/Firefox/Firefox'
            ],
            'os2': [
                'C:\\Mozilla\\Firefox\\firefox.exe'
            ]
        },
        'chrome': {
            'windows': [
                os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
                os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe')
            ],
            'macos': [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                os.path.expanduser('~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
            ],
            'linux': [
                '/usr/bin/google-chrome',
                '/usr/local/bin/google-chrome',
                '/opt/google/chrome/chrome'
            ],
            'haiku': [
                '/boot/apps/GoogleChrome/GoogleChrome'
            ],
            'os2': [
                'C:\\Google\\Chrome\\chrome.exe'
            ]
        }
    }
    
    # Check if browser is supported
    if browser_id not in browser_paths:
        return None
    
    # Check if platform is supported
    if platform_type not in browser_paths[browser_id]:
        return None
    
    # Check each path
    for path in browser_paths[browser_id][platform_type]:
        if os.path.exists(path):
            return path
    
    return None

def launch_browser(browser_id: str, profile_path: Optional[str] = None, url: Optional[str] = None) -> bool:
    """
    Launch a browser with a specific profile and URL.
    
    Args:
        browser_id: Browser identifier
        profile_path: Optional path to the profile
        url: Optional URL to open
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get browser executable
        executable = get_browser_executable(browser_id)
        
        if executable is None:
            logger.error(f"Browser executable not found for {browser_id}")
            return False
        
        # Build command
        import subprocess
        command = [executable]
        
        # Add profile argument if provided
        if profile_path is not None:
            if browser_id in ['floorp', 'firefox']:
                command.extend(['-P', os.path.basename(profile_path)])
            elif browser_id == 'chrome':
                command.extend(['--user-data-dir=' + profile_path])
        
        # Add URL if provided
        if url is not None:
            command.append(url)
        
        # Launch browser
        subprocess.Popen(command)
        
        return True
    except Exception as e:
        logger.error(f"Failed to launch browser {browser_id}: {str(e)}")
        return False

def get_theme_colors(theme_name: str = 'default') -> Dict[str, str]:
    """
    Get color definitions for a theme.
    
    Args:
        theme_name: Theme name
        
    Returns:
        Dictionary with color definitions
    """
    # Define themes
    themes = {
        'default': {
            'primary': '#4a6ea9',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'text': '#212529',
            'link': '#007bff',
            'border': '#dee2e6'
        },
        'dark': {
            'primary': '#375a8c',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#121212',
            'text': '#e0e0e0',
            'link': '#80bdff',
            'border': '#495057'
        },
        'floorp': {
            'primary': '#4a6ea9',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'text': '#212529',
            'link': '#4a6ea9',
            'border': '#dee2e6'
        },
        'floorp_dark': {
            'primary': '#375a8c',
            'secondary': '#6c757d',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#121212',
            'text': '#e0e0e0',
            'link': '#80bdff',
            'border': '#495057'
        }
    }
    
    # Return theme colors
    return themes.get(theme_name, themes['default'])

def get_ui_scale_factor() -> float:
    """
    Get the UI scale factor based on the platform and screen resolution.
    
    Returns:
        UI scale factor
    """
    try:
        platform_type = get_platform()
        
        if platform_type == 'windows':
            # On Windows, try to get the DPI scaling
            try:
                import ctypes
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                dpi_x = ctypes.c_uint()
                ctypes.windll.gdi32.GetDeviceCaps(dc, 88, ctypes.byref(dpi_x))
                user32.ReleaseDC(0, dc)
                return dpi_x.value / 96.0
            except Exception:
                return 1.0
        elif platform_type == 'macos':
            # On macOS, assume Retina display is 2.0
            try:
                import subprocess
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True)
                if 'Retina' in result.stdout:
                    return 2.0
            except Exception:
                pass
        
        # Default to 1.0 for other platforms or if detection fails
        return 1.0
    except Exception:
        return 1.0

def get_system_locale() -> str:
    """
    Get the system locale.
    
    Returns:
        System locale string
    """
    try:
        import locale
        return locale.getdefaultlocale()[0] or 'en_US'
    except Exception:
        return 'en_US'

def get_system_language() -> str:
    """
    Get the system language.
    
    Returns:
        System language code
    """
    try:
        locale = get_system_locale()
        return locale.split('_')[0]
    except Exception:
        return 'en'

def get_translation(key: str, language: Optional[str] = None) -> str:
    """
    Get a translated string.
    
    Args:
        key: Translation key
        language: Optional language code
        
    Returns:
        Translated string
    """
    # In a real implementation, this would load translations from files
    # For now, we'll just return the key
    return key

def is_dark_mode_enabled() -> bool:
    """
    Check if dark mode is enabled in the system.
    
    Returns:
        True if dark mode is enabled, False otherwise
    """
    try:
        platform_type = get_platform()
        
        if platform_type == 'windows':
            # On Windows, check registry
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                return value == 0
            except Exception:
                return False
        elif platform_type == 'macos':
            # On macOS, check defaults
            try:
                import subprocess
                result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], capture_output=True, text=True)
                return 'Dark' in result.stdout
            except Exception:
                return False
        elif platform_type == 'linux':
            # On Linux, check gsettings
            try:
                import subprocess
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
                return 'dark' in result.stdout.lower()
            except Exception:
                return False
        
        # Default to False for other platforms or if detection fails
        return False
    except Exception:
        return False

def get_default_theme() -> str:
    """
    Get the default theme based on system settings.
    
    Returns:
        Theme name
    """
    if is_dark_mode_enabled():
        return 'floorp_dark'
    else:
        return 'floorp'

def get_system_fonts() -> List[str]:
    """
    Get available system fonts.
    
    Returns:
        List of font names
    """
    try:
        platform_type = get_platform()
        
        if platform_type == 'windows':
            # On Windows, use win32com
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                fonts_dir = shell.SpecialFolders("Fonts")
                
                fonts = []
                for file in os.listdir(fonts_dir):
                    if file.endswith(('.ttf', '.ttc', '.otf')):
                        font_name = os.path.splitext(file)[0]
                        fonts.append(font_name)
                
                return sorted(fonts)
            except Exception:
                pass
        elif platform_type == 'macos':
            # On macOS, use system_profiler
            try:
                import subprocess
                result = subprocess.run(['system_profiler', 'SPFontsDataType'], capture_output=True, text=True)
                
                fonts = []
                for line in result.stdout.splitlines():
                    if line.strip().startswith('Full Name:'):
                        font_name = line.split(':', 1)[1].strip()
                        fonts.append(font_name)
                
                return sorted(fonts)
            except Exception:
                pass
        elif platform_type == 'linux':
            # On Linux, use fc-list
            try:
                import subprocess
                result = subprocess.run(['fc-list', ':', 'family'], capture_output=True, text=True)
                
                fonts = []
                for line in result.stdout.splitlines():
                    for font in line.split(','):
                        font = font.strip()
                        if font and font not in fonts:
                            fonts.append(font)
                
                return sorted(fonts)
            except Exception:
                pass
        
        # Default to basic fonts if detection fails
        return ['Arial', 'Courier New', 'Times New Roman', 'Verdana']
    except Exception:
        return ['Arial', 'Courier New', 'Times New Roman', 'Verdana']

def get_default_font() -> str:
    """
    Get the default system font.
    
    Returns:
        Default font name
    """
    try:
        platform_type = get_platform()
        
        if platform_type == 'windows':
            return 'Segoe UI'
        elif platform_type == 'macos':
            return 'San Francisco'
        elif platform_type == 'linux':
            return 'DejaVu Sans'
        else:
            return 'Arial'
    except Exception:
        return 'Arial'

def get_system_info() -> Dict[str, str]:
    """
    Get system information.
    
    Returns:
        Dictionary with system information
    """
    try:
        import platform as plt
        
        return {
            'platform': get_platform(),
            'system': plt.system(),
            'release': plt.release(),
            'version': plt.version(),
            'machine': plt.machine(),
            'processor': plt.processor(),
            'python_version': plt.python_version(),
            'python_implementation': plt.python_implementation(),
            'locale': get_system_locale(),
            'language': get_system_language(),
            'username': os.environ.get('USER', os.environ.get('USERNAME', 'unknown')),
            'hostname': plt.node()
        }
    except Exception as e:
        logger.error(f"Failed to get system information: {str(e)}")
        return {
            'platform': get_platform(),
            'error': str(e)
        }

def get_memory_usage() -> Dict[str, Union[int, str]]:
    """
    Get memory usage information.
    
    Returns:
        Dictionary with memory usage information
    """
    try:
        import psutil
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss,
            'rss_formatted': format_size(memory_info.rss),
            'vms': memory_info.vms,
            'vms_formatted': format_size(memory_info.vms),
            'percent': process.memory_percent(),
            'system_total': psutil.virtual_memory().total,
            'system_total_formatted': format_size(psutil.virtual_memory().total),
            'system_available': psutil.virtual_memory().available,
            'system_available_formatted': format_size(psutil.virtual_memory().available),
            'system_percent': psutil.virtual_memory().percent
        }
    except Exception as e:
        logger.error(f"Failed to get memory usage: {str(e)}")
        return {
            'error': str(e)
        }

def get_disk_usage(path: str = '/') -> Dict[str, Union[int, str]]:
    """
    Get disk usage information.
    
    Args:
        path: Path to check
        
    Returns:
        Dictionary with disk usage information
    """
    try:
        import shutil
        
        usage = shutil.disk_usage(path)
        
        return {
            'total': usage.total,
            'total_formatted': format_size(usage.total),
            'used': usage.used,
            'used_formatted': format_size(usage.used),
            'free': usage.free,
            'free_formatted': format_size(usage.free),
            'percent': usage.used / usage.total * 100
        }
    except Exception as e:
        logger.error(f"Failed to get disk usage: {str(e)}")
        return {
            'error': str(e)
        }

def get_cpu_usage() -> Dict[str, Union[float, int]]:
    """
    Get CPU usage information.
    
    Returns:
        Dictionary with CPU usage information
    """
    try:
        import psutil
        
        return {
            'percent': psutil.cpu_percent(interval=0.1),
            'count_logical': psutil.cpu_count(),
            'count_physical': psutil.cpu_count(logical=False) or psutil.cpu_count()
        }
    except Exception as e:
        logger.error(f"Failed to get CPU usage: {str(e)}")
        return {
            'error': str(e)
        }

def get_network_info() -> Dict[str, Any]:
    """
    Get network information.
    
    Returns:
        Dictionary with network information
    """
    try:
        import psutil
        
        network_info = {}
        
        # Get network interfaces
        network_info['interfaces'] = []
        
        for interface, stats in psutil.net_if_addrs().items():
            interface_info = {
                'name': interface,
                'addresses': []
            }
            
            for addr in stats:
                address_info = {
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                }
                
                interface_info['addresses'].append(address_info)
            
            network_info['interfaces'].append(interface_info)
        
        # Get network connections
        network_info['connections_count'] = len(psutil.net_connections())
        
        # Get network IO counters
        io_counters = psutil.net_io_counters()
        
        network_info['io'] = {
            'bytes_sent': io_counters.bytes_sent,
            'bytes_sent_formatted': format_size(io_counters.bytes_sent),
            'bytes_recv': io_counters.bytes_recv,
            'bytes_recv_formatted': format_size(io_counters.bytes_recv),
            'packets_sent': io_counters.packets_sent,
            'packets_recv': io_counters.packets_recv,
            'errin': io_counters.errin,
            'errout': io_counters.errout,
            'dropin': io_counters.dropin,
            'dropout': io_counters.dropout
        }
        
        return network_info
    except Exception as e:
        logger.error(f"Failed to get network information: {str(e)}")
        return {
            'error': str(e)
        }

def get_process_info() -> Dict[str, Any]:
    """
    Get process information.
    
    Returns:
        Dictionary with process information
    """
    try:
        import psutil
        
        process = psutil.Process(os.getpid())
        
        return {
            'pid': process.pid,
            'name': process.name(),
            'exe': process.exe(),
            'cwd': process.cwd(),
            'cmdline': process.cmdline(),
            'status': process.status(),
            'username': process.username(),
            'create_time': process.create_time(),
            'cpu_percent': process.cpu_percent(interval=0.1),
            'memory_percent': process.memory_percent(),
            'memory_info': {
                'rss': process.memory_info().rss,
                'rss_formatted': format_size(process.memory_info().rss),
                'vms': process.memory_info().vms,
                'vms_formatted': format_size(process.memory_info().vms)
            },
            'num_threads': process.num_threads(),
            'num_fds': process.num_fds() if hasattr(process, 'num_fds') else None,
            'num_ctx_switches': process.num_ctx_switches() if hasattr(process, 'num_ctx_switches') else None
        }
    except Exception as e:
        logger.error(f"Failed to get process information: {str(e)}")
        return {
            'error': str(e)
        }

def get_python_packages() -> List[Dict[str, str]]:
    """
    Get installed Python packages.
    
    Returns:
        List of dictionaries with package information
    """
    try:
        import pkg_resources
        
        packages = []
        
        for package in pkg_resources.working_set:
            package_info = {
                'name': package.project_name,
                'version': package.version,
                'location': package.location
            }
            
            packages.append(package_info)
        
        return sorted(packages, key=lambda x: x['name'].lower())
    except Exception as e:
        logger.error(f"Failed to get Python packages: {str(e)}")
        return []

def get_environment_variables() -> Dict[str, str]:
    """
    Get environment variables.
    
    Returns:
        Dictionary with environment variables
    """
    try:
        # Filter out sensitive information
        filtered_env = {}
        
        for key, value in os.environ.items():
            # Skip keys that might contain sensitive information
            if any(sensitive in key.lower() for sensitive in ['key', 'token', 'secret', 'password', 'credential']):
                filtered_env[key] = '***REDACTED***'
            else:
                filtered_env[key] = value
        
        return filtered_env
    except Exception as e:
        logger.error(f"Failed to get environment variables: {str(e)}")
        return {}

def get_app_version() -> str:
    """
    Get the application version.
    
    Returns:
        Application version string
    """
    try:
        # Try to get version from package metadata
        import pkg_resources
        return pkg_resources.get_distribution('floorper').version
    except Exception:
        # Fallback to hardcoded version
        return '1.0.0'

def get_app_info() -> Dict[str, Any]:
    """
    Get application information.
    
    Returns:
        Dictionary with application information
    """
    return {
        'name': 'Floorper',
        'version': get_app_version(),
        'description': 'Universal Browser Profile Migration Tool for Floorp',
        'author': 'Floorper Team',
        'license': 'MIT',
        'homepage': 'https://github.com/boolforge/floorper',
        'platform': get_platform(),
        'python_version': platform.python_version(),
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine()
    }

def main():
    """Main entry point for testing."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test platform detection
    logger.info(f"Platform: {get_platform()}")
    logger.info(f"Home directory: {get_home_dir()}")
    logger.info(f"App data directory: {get_app_data_dir()}")
    
    # Test Floorp profile detection
    profiles = get_floorp_profiles()
    logger.info(f"Found {len(profiles)} Floorp profiles:")
    
    for profile in profiles:
        logger.info(f"- {profile['name']} at {profile['path']} (default: {profile['is_default']})")
    
    # Test system info
    logger.info(f"System info: {get_system_info()}")
    
    # Test app info
    logger.info(f"App info: {get_app_info()}")


if __name__ == "__main__":
    main()
