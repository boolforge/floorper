"""
Base browser handler class.
All browser-specific handlers should inherit from this class.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set


class BaseBrowserHandler(ABC):
    """Base class for browser handlers."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the browser handler.
        
        Args:
            data_dir: Directory where browser data is stored
        """
        self.data_dir = Path(data_dir) if data_dir else None
    
    @abstractmethod
    def is_installed(self) -> bool:
        """
        Check if the browser is installed.
        
        Returns:
            True if the browser is installed, False otherwise
        """
        pass
    
    @abstractmethod
    def get_profiles(self) -> List[str]:
        """
        Get all available profiles for the browser.
        
        Returns:
            List of profile names
        """
        pass
    
    @abstractmethod
    def get_profile_data(self, profile_name: str) -> Dict[str, Any]:
        """
        Get data from a browser profile.
        
        Args:
            profile_name: Name of the profile to get data from
            
        Returns:
            Dictionary containing profile data (bookmarks, history, cookies, etc.)
        """
        pass
    
    @abstractmethod
    def migrate_profile(self, profile_name: str, target_dir: str) -> bool:
        """
        Migrate a profile to a different directory.
        
        Args:
            profile_name: Name of the profile to migrate
            target_dir: Target directory to migrate to
            
        Returns:
            True if migration was successful, False otherwise
        """
        pass
    
    def backup_profile(self, profile_name: str, backup_dir: str) -> str:
        """
        Create a backup of a profile.
        
        Args:
            profile_name: Name of the profile to backup
            backup_dir: Directory to store the backup
            
        Returns:
            Path to the backup directory
        """
        import shutil
        import datetime
        
        # Get profile directory
        profiles = self.get_profiles()
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        
        # Create backup directory
        backup_path = Path(backup_dir) / f"{self.__class__.__name__}_{profile_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Get profile data
        profile_data = self.get_profile_data(profile_name)
        
        # Store profile data as JSON
        import json
        with open(backup_path / "profile_data.json", "w") as f:
            json.dump(profile_data, f, indent=2, default=str)
        
        return str(backup_path) 