"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides support for retro and legacy web browsers, allowing
users to migrate profiles from older browsers to Floorp.
"""

import os
import sys
import logging
import json
import shutil
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from floorper.core import FloorperCore

# Setup logging
logger = logging.getLogger('floorper.retro')

class RetroBrowserHandler:
    """
    Handles detection and migration of profiles from retro and legacy web browsers.
    
    This class provides specialized functionality for working with older browsers
    that may have different profile structures and data formats.
    """
    
    def __init__(self, controller: Optional[FloorperCore] = None):
        """
        Initialize the retro browser handler.
        
        Args:
            controller: Optional FloorperCore controller instance
        """
        self.controller = controller or FloorperCore()
        logger.info("Retro browser handler initialized")
        
        # Define retro browser detection patterns
        self.retro_browsers = {
            # Netscape family
            'netscape': {
                'name': 'Netscape Navigator',
                'paths': self._get_netscape_paths(),
                'profile_pattern': r'.*\.slt$',
                'data_files': {
                    'bookmarks': ['bookmarks.html'],
                    'history': ['history.dat'],
                    'cookies': ['cookies.txt'],
                    'preferences': ['prefs.js']
                }
            },
            'mosaic': {
                'name': 'NCSA Mosaic',
                'paths': self._get_mosaic_paths(),
                'profile_pattern': r'mosaic\.ini$',
                'data_files': {
                    'bookmarks': ['mosaic.hot'],
                    'history': ['mosaic.hst'],
                    'preferences': ['mosaic.ini']
                }
            },
            'opera_legacy': {
                'name': 'Opera (Legacy)',
                'paths': self._get_opera_legacy_paths(),
                'profile_pattern': r'opera6\.ini$',
                'data_files': {
                    'bookmarks': ['bookmarks.adr', 'opera6.adr'],
                    'history': ['global.dat'],
                    'cookies': ['cookies4.dat'],
                    'preferences': ['opera6.ini', 'operaprefs.ini']
                }
            },
            'ie_legacy': {
                'name': 'Internet Explorer (Legacy)',
                'paths': self._get_ie_legacy_paths(),
                'profile_pattern': r'index\.dat$',
                'data_files': {
                    'bookmarks': ['Favorites'],
                    'history': ['History', 'index.dat'],
                    'cookies': ['Cookies', 'cookies.txt']
                }
            },
            'lynx': {
                'name': 'Lynx',
                'paths': self._get_lynx_paths(),
                'profile_pattern': r'lynx\.cfg$',
                'data_files': {
                    'bookmarks': ['lynx_bookmarks.html'],
                    'history': ['lynx.history'],
                    'cookies': ['lynx.cookies'],
                    'preferences': ['lynx.cfg']
                }
            },
            'elinks': {
                'name': 'ELinks',
                'paths': self._get_elinks_paths(),
                'profile_pattern': r'elinks\.conf$',
                'data_files': {
                    'bookmarks': ['bookmarks'],
                    'history': ['globhist'],
                    'cookies': ['cookies'],
                    'preferences': ['elinks.conf']
                }
            },
            'links': {
                'name': 'Links',
                'paths': self._get_links_paths(),
                'profile_pattern': r'links\.cfg$',
                'data_files': {
                    'bookmarks': ['bookmarks'],
                    'history': ['links.his'],
                    'cookies': ['cookies'],
                    'preferences': ['links.cfg']
                }
            },
            'w3m': {
                'name': 'w3m',
                'paths': self._get_w3m_paths(),
                'profile_pattern': r'config$',
                'data_files': {
                    'bookmarks': ['bookmark.html'],
                    'history': ['history'],
                    'cookies': ['cookie'],
                    'preferences': ['config']
                }
            },
            'dillo': {
                'name': 'Dillo',
                'paths': self._get_dillo_paths(),
                'profile_pattern': r'dillorc$',
                'data_files': {
                    'bookmarks': ['bm.txt'],
                    'cookies': ['cookies.txt'],
                    'preferences': ['dillorc']
                }
            },
            'arachne': {
                'name': 'Arachne',
                'paths': self._get_arachne_paths(),
                'profile_pattern': r'arachne\.cfg$',
                'data_files': {
                    'bookmarks': ['bookmark.htm'],
                    'history': ['history.txt'],
                    'preferences': ['arachne.cfg']
                }
            },
            'phoenix': {
                'name': 'Phoenix/Firebird',
                'paths': self._get_phoenix_paths(),
                'profile_pattern': r'prefs\.js$',
                'data_files': {
                    'bookmarks': ['bookmarks.html'],
                    'history': ['history.dat'],
                    'cookies': ['cookies.txt'],
                    'preferences': ['prefs.js', 'user.js']
                }
            },
            'k_meleon': {
                'name': 'K-Meleon',
                'paths': self._get_k_meleon_paths(),
                'profile_pattern': r'prefs\.js$',
                'data_files': {
                    'bookmarks': ['bookmarks.html'],
                    'history': ['history.dat'],
                    'cookies': ['cookies.txt'],
                    'preferences': ['prefs.js', 'kmeleon.cfg']
                }
            },
            'galeon': {
                'name': 'Galeon',
                'paths': self._get_galeon_paths(),
                'profile_pattern': r'prefs\.js$',
                'data_files': {
                    'bookmarks': ['bookmarks.xbel'],
                    'history': ['history.xml'],
                    'cookies': ['cookies.txt'],
                    'preferences': ['prefs.js']
                }
            },
            'konqueror_legacy': {
                'name': 'Konqueror (Legacy)',
                'paths': self._get_konqueror_legacy_paths(),
                'profile_pattern': r'konq_history$',
                'data_files': {
                    'bookmarks': ['bookmarks.xml'],
                    'history': ['konq_history'],
                    'cookies': ['cookies'],
                    'preferences': ['konquerorrc']
                }
            },
            'amaya': {
                'name': 'Amaya',
                'paths': self._get_amaya_paths(),
                'profile_pattern': r'amaya\.cfg$',
                'data_files': {
                    'bookmarks': ['bookmarks.html', 'bookmarks.rdf'],
                    'history': ['amaya.history'],
                    'preferences': ['amaya.cfg']
                }
            },
            'arena': {
                'name': 'Arena',
                'paths': self._get_arena_paths(),
                'profile_pattern': r'arena\.ini$',
                'data_files': {
                    'bookmarks': ['hotlist.html'],
                    'history': ['history.html'],
                    'preferences': ['arena.ini']
                }
            },
            'cello': {
                'name': 'Cello',
                'paths': self._get_cello_paths(),
                'profile_pattern': r'cello\.ini$',
                'data_files': {
                    'bookmarks': ['bookmark.txt'],
                    'preferences': ['cello.ini']
                }
            },
            'chimera': {
                'name': 'Chimera',
                'paths': self._get_chimera_paths(),
                'profile_pattern': r'chimera\.config$',
                'data_files': {
                    'bookmarks': ['bookmarks.html'],
                    'history': ['history.dat'],
                    'preferences': ['chimera.config']
                }
            },
            'browsex': {
                'name': 'BrowseX',
                'paths': self._get_browsex_paths(),
                'profile_pattern': r'browsex\.ini$',
                'data_files': {
                    'bookmarks': ['bookmarks.html'],
                    'preferences': ['browsex.ini']
                }
            },
            'ibrowse': {
                'name': 'IBrowse',
                'paths': self._get_ibrowse_paths(),
                'profile_pattern': r'ibrowse\.prefs$',
                'data_files': {
                    'bookmarks': ['bookmarks'],
                    'history': ['history'],
                    'cookies': ['cookies'],
                    'preferences': ['ibrowse.prefs']
                }
            },
            'voyager': {
                'name': 'Voyager',
                'paths': self._get_voyager_paths(),
                'profile_pattern': r'voyager\.config$',
                'data_files': {
                    'bookmarks': ['bookmarks.html'],
                    'preferences': ['voyager.config']
                }
            },
            'aweb': {
                'name': 'AWeb',
                'paths': self._get_aweb_paths(),
                'profile_pattern': r'aweb\.prefs$',
                'data_files': {
                    'bookmarks': ['hotlist'],
                    'history': ['history'],
                    'cookies': ['cookies'],
                    'preferences': ['aweb.prefs']
                }
            }
        }
    
    def detect_retro_browsers(self) -> List[Dict[str, Any]]:
        """
        Detect installed retro browsers and their profiles.
        
        Returns:
            List of detected retro browser information dictionaries
        """
        detected_browsers = []
        
        for browser_id, browser_info in self.retro_browsers.items():
            try:
                # Check each potential path
                for path in browser_info['paths']:
                    if os.path.exists(path):
                        # Look for profile pattern
                        profiles = self._find_profiles(path, browser_info['profile_pattern'])
                        
                        if profiles:
                            browser_data = {
                                'id': browser_id,
                                'name': browser_info['name'],
                                'path': path,
                                'profiles': profiles
                            }
                            detected_browsers.append(browser_data)
                            logger.info(f"Detected retro browser: {browser_info['name']} at {path} with {len(profiles)} profiles")
                            break  # Found this browser, no need to check other paths
            except Exception as e:
                logger.error(f"Error detecting {browser_info['name']}: {str(e)}")
        
        return detected_browsers
    
    def migrate_profile(self, source_profile: Dict[str, Any], target_profile: Dict[str, Any],
                       data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Migrate data from a retro browser profile to a Floorp profile.
        
        Args:
            source_profile: Source profile information
            target_profile: Target Floorp profile information
            data_types: Optional list of data types to migrate
            
        Returns:
            Dictionary with migration results
        """
        try:
            browser_id = source_profile.get('browser_id')
            if browser_id not in self.retro_browsers:
                raise ValueError(f"Unsupported retro browser: {browser_id}")
            
            browser_info = self.retro_browsers[browser_id]
            source_path = source_profile.get('path')
            target_path = target_profile.get('path')
            
            if not source_path or not os.path.exists(source_path):
                raise ValueError(f"Source profile path does not exist: {source_path}")
            
            if not target_path or not os.path.exists(target_path):
                raise ValueError(f"Target profile path does not exist: {target_path}")
            
            # Determine data types to migrate
            if not data_types:
                data_types = list(browser_info['data_files'].keys())
            
            results = {}
            
            # Migrate each data type
            for data_type in data_types:
                if data_type in browser_info['data_files']:
                    file_patterns = browser_info['data_files'][data_type]
                    result = self._migrate_data_type(browser_id, source_path, target_path, data_type, file_patterns)
                    results[data_type] = result
            
            logger.info(f"Migration completed from {browser_info['name']} to Floorp")
            return {
                'success': True,
                'source': browser_info['name'],
                'target': 'Floorp',
                'data_types': results
            }
        except Exception as e:
            logger.error(f"Failed to migrate profile: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_profiles(self, base_path: str, profile_pattern: str) -> List[Dict[str, Any]]:
        """
        Find profiles in a browser installation directory.
        
        Args:
            base_path: Base path to search
            profile_pattern: Regex pattern to identify profiles
            
        Returns:
            List of profile information dictionaries
        """
        profiles = []
        pattern = re.compile(profile_pattern)
        
        # Walk through directory structure
        for root, dirs, files in os.walk(base_path):
            # Check files against pattern
            for file in files:
                if pattern.match(file):
                    profile_path = root
                    profile_name = os.path.basename(root)
                    
                    # Special case for single-profile browsers
                    if profile_name == os.path.basename(base_path):
                        profile_name = "Default"
                    
                    profiles.append({
                        'name': profile_name,
                        'path': profile_path,
                        'is_default': profile_name.lower() == "default"
                    })
                    break  # Found a profile in this directory
        
        return profiles
    
    def _migrate_data_type(self, browser_id: str, source_path: str, target_path: str,
                          data_type: str, file_patterns: List[str]) -> Dict[str, Any]:
        """
        Migrate a specific data type from source to target profile.
        
        Args:
            browser_id: Browser identifier
            source_path: Source profile path
            target_path: Target profile path
            data_type: Data type to migrate
            file_patterns: List of file patterns to look for
            
        Returns:
            Dictionary with migration result
        """
        try:
            # Find source files
            source_files = []
            for pattern in file_patterns:
                # Handle directory patterns
                if not pattern.endswith(('.dat', '.txt', '.html', '.js', '.cfg', '.ini', '.xml', '.rdf')):
                    dir_path = os.path.join(source_path, pattern)
                    if os.path.isdir(dir_path):
                        source_files.append(dir_path)
                else:
                    # Handle file patterns
                    file_path = os.path.join(source_path, pattern)
                    if os.path.exists(file_path):
                        source_files.append(file_path)
            
            if not source_files:
                return {
                    'success': False,
                    'message': f"No {data_type} files found in source profile"
                }
            
            # Migrate based on data type
            if data_type == 'bookmarks':
                return self._migrate_bookmarks(browser_id, source_files, target_path)
            elif data_type == 'history':
                return self._migrate_history(browser_id, source_files, target_path)
            elif data_type == 'cookies':
                return self._migrate_cookies(browser_id, source_files, target_path)
            elif data_type == 'preferences':
                return self._migrate_preferences(browser_id, source_files, target_path)
            else:
                return {
                    'success': False,
                    'message': f"Unsupported data type: {data_type}"
                }
        except Exception as e:
            logger.error(f"Failed to migrate {data_type}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _migrate_bookmarks(self, browser_id: str, source_files: List[str], target_path: str) -> Dict[str, Any]:
        """
        Migrate bookmarks from source to target profile.
        
        Args:
            browser_id: Browser identifier
            source_files: Source bookmark files
            target_path: Target profile path
            
        Returns:
            Dictionary with migration result
        """
        try:
            # Determine target format (Firefox/Floorp uses places.sqlite)
            target_file = os.path.join(target_path, 'places.sqlite')
            
            # Create temporary HTML file for conversion
            temp_html = os.path.join(target_path, 'imported_bookmarks.html')
            
            # Process based on source browser
            if browser_id in ['netscape', 'phoenix', 'k_meleon', 'chimera']:
                # These browsers use HTML bookmarks that can be imported directly
                for source_file in source_files:
                    if source_file.endswith('.html'):
                        shutil.copy2(source_file, temp_html)
                        break
            
            elif browser_id in ['mosaic', 'lynx', 'elinks', 'links', 'w3m', 'dillo', 'arachne']:
                # Text-based bookmarks need conversion to HTML
                self._convert_text_bookmarks_to_html(source_files[0], temp_html)
            
            elif browser_id in ['opera_legacy']:
                # Opera uses a special format
                self._convert_opera_bookmarks_to_html(source_files[0], temp_html)
            
            elif browser_id in ['ie_legacy']:
                # IE uses a directory structure
                self._convert_ie_bookmarks_to_html(source_files[0], temp_html)
            
            elif browser_id in ['galeon', 'konqueror_legacy']:
                # XML-based bookmarks
                self._convert_xml_bookmarks_to_html(source_files[0], temp_html)
            
            else:
                # Generic conversion attempt
                self._convert_generic_bookmarks_to_html(source_files[0], temp_html)
            
            # Now we have an HTML file that Firefox/Floorp can import
            # In a real implementation, we would use the Firefox/Floorp API to import this file
            # For now, we'll just copy it to the target profile
            
            return {
                'success': True,
                'message': f"Bookmarks migrated to {temp_html}",
                'note': "To complete import, open Floorp and use Bookmarks > Import Bookmarks from HTML"
            }
        except Exception as e:
            logger.error(f"Failed to migrate bookmarks: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _migrate_history(self, browser_id: str, source_files: List[str], target_path: str) -> Dict[str, Any]:
        """
        Migrate history from source to target profile.
        
        Args:
            browser_id: Browser identifier
            source_files: Source history files
            target_path: Target profile path
            
        Returns:
            Dictionary with migration result
        """
        try:
            # Determine target format (Firefox/Floorp uses places.sqlite)
            target_file = os.path.join(target_path, 'places.sqlite')
            
            # History migration is complex and requires direct database manipulation
            # For now, we'll just provide a message about the complexity
            
            return {
                'success': False,
                'message': "History migration from retro browsers is not fully supported",
                'note': "History data formats vary significantly between browsers and may require manual conversion"
            }
        except Exception as e:
            logger.error(f"Failed to migrate history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _migrate_cookies(self, browser_id: str, source_files: List[str], target_path: str) -> Dict[str, Any]:
        """
        Migrate cookies from source to target profile.
        
        Args:
            browser_id: Browser identifier
            source_files: Source cookie files
            target_path: Target profile path
            
        Returns:
            Dictionary with migration result
        """
        try:
            # Determine target format (Firefox/Floorp uses cookies.sqlite)
            target_file = os.path.join(target_path, 'cookies.sqlite')
            
            # Cookie migration is complex and requires direct database manipulation
            # For now, we'll just provide a message about the complexity
            
            return {
                'success': False,
                'message': "Cookie migration from retro browsers is not fully supported",
                'note': "Cookie data formats vary significantly between browsers and may require manual conversion"
            }
        except Exception as e:
            logger.error(f"Failed to migrate cookies: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _migrate_preferences(self, browser_id: str, source_files: List[str], target_path: str) -> Dict[str, Any]:
        """
        Migrate preferences from source to target profile.
        
        Args:
            browser_id: Browser identifier
            source_files: Source preference files
            target_path: Target profile path
            
        Returns:
            Dictionary with migration result
        """
        try:
            # Determine target format (Firefox/Floorp uses prefs.js)
            target_file = os.path.join(target_path, 'prefs.js')
            
            # For Firefox-like browsers, we can try to merge prefs.js
            if browser_id in ['phoenix', 'k_meleon']:
                for source_file in source_files:
                    if os.path.basename(source_file) == 'prefs.js':
                        # Read source prefs
                        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                            source_prefs = f.readlines()
                        
                        # Read target prefs
                        with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
                            target_prefs = f.readlines()
                        
                        # Append source prefs with a comment
                        with open(target_file, 'a', encoding='utf-8') as f:
                            f.write('\n// Imported preferences from retro browser\n')
                            for line in source_prefs:
                                if line.strip().startswith('user_pref('):
                                    f.write(line)
                        
                        return {
                            'success': True,
                            'message': f"Preferences migrated to {target_file}"
                        }
            
            # For other browsers, we can't easily migrate preferences
            return {
                'success': False,
                'message': "Preference migration from this retro browser is not fully supported",
                'note': "Preference formats vary significantly between browsers and may require manual configuration"
            }
        except Exception as e:
            logger.error(f"Failed to migrate preferences: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_text_bookmarks_to_html(self, source_file: str, target_file: str) -> None:
        """
        Convert text-based bookmarks to HTML format.
        
        Args:
            source_file: Source bookmark file
            target_file: Target HTML file
        """
        try:
            bookmarks = []
            
            # Read source file
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Parse based on format
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Try to extract URL and title
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2 and parts[0].startswith(('http://', 'https://', 'ftp://')):
                        url = parts[0]
                        title = parts[1]
                        bookmarks.append((title, url))
                    elif len(parts) == 1 and parts[0].startswith(('http://', 'https://', 'ftp://')):
                        url = parts[0]
                        title = url
                        bookmarks.append((title, url))
            
            # Write HTML file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write('<TITLE>Bookmarks</TITLE>\n')
                f.write('<H1>Bookmarks</H1>\n')
                f.write('<DL><p>\n')
                f.write('    <DT><H3>Imported Bookmarks</H3>\n')
                f.write('    <DL><p>\n')
                
                for title, url in bookmarks:
                    f.write(f'        <DT><A HREF="{url}">{title}</A>\n')
                
                f.write('    </DL><p>\n')
                f.write('</DL><p>\n')
        except Exception as e:
            logger.error(f"Failed to convert text bookmarks to HTML: {str(e)}")
            raise
    
    def _convert_opera_bookmarks_to_html(self, source_file: str, target_file: str) -> None:
        """
        Convert Opera bookmarks to HTML format.
        
        Args:
            source_file: Source Opera bookmark file
            target_file: Target HTML file
        """
        try:
            bookmarks = []
            current_folder = None
            folders = {}
            
            # Read source file
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Parse Opera bookmark format
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    continue
                
                if line == '-':
                    # Folder separator
                    current_folder = None
                elif line.startswith('NAME=') and current_folder is None:
                    # New folder
                    folder_name = line[5:]
                    current_folder = folder_name
                    folders[current_folder] = []
                elif line.startswith('URL=') and current_folder is not None:
                    # URL in current folder
                    url = line[4:]
                    # Look for title in next line
                    title_index = lines.index(line) + 1
                    title = url
                    if title_index < len(lines) and lines[title_index].startswith('NAME='):
                        title = lines[title_index][5:]
                    
                    folders[current_folder].append((title, url))
                elif line.startswith('URL='):
                    # URL without folder
                    url = line[4:]
                    # Look for title in next line
                    title_index = lines.index(line) + 1
                    title = url
                    if title_index < len(lines) and lines[title_index].startswith('NAME='):
                        title = lines[title_index][5:]
                    
                    bookmarks.append((title, url))
            
            # Write HTML file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write('<TITLE>Bookmarks</TITLE>\n')
                f.write('<H1>Bookmarks</H1>\n')
                f.write('<DL><p>\n')
                f.write('    <DT><H3>Imported Opera Bookmarks</H3>\n')
                f.write('    <DL><p>\n')
                
                # Write bookmarks without folders
                for title, url in bookmarks:
                    f.write(f'        <DT><A HREF="{url}">{title}</A>\n')
                
                # Write folders
                for folder_name, folder_bookmarks in folders.items():
                    f.write(f'        <DT><H3>{folder_name}</H3>\n')
                    f.write('        <DL><p>\n')
                    
                    for title, url in folder_bookmarks:
                        f.write(f'            <DT><A HREF="{url}">{title}</A>\n')
                    
                    f.write('        </DL><p>\n')
                
                f.write('    </DL><p>\n')
                f.write('</DL><p>\n')
        except Exception as e:
            logger.error(f"Failed to convert Opera bookmarks to HTML: {str(e)}")
            raise
    
    def _convert_ie_bookmarks_to_html(self, source_dir: str, target_file: str) -> None:
        """
        Convert Internet Explorer Favorites to HTML format.
        
        Args:
            source_dir: Source Favorites directory
            target_file: Target HTML file
        """
        try:
            # Write HTML file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write('<TITLE>Bookmarks</TITLE>\n')
                f.write('<H1>Bookmarks</H1>\n')
                f.write('<DL><p>\n')
                f.write('    <DT><H3>Imported IE Favorites</H3>\n')
                f.write('    <DL><p>\n')
                
                # Process Favorites directory
                self._process_ie_favorites_dir(source_dir, f, 2)
                
                f.write('    </DL><p>\n')
                f.write('</DL><p>\n')
        except Exception as e:
            logger.error(f"Failed to convert IE Favorites to HTML: {str(e)}")
            raise
    
    def _process_ie_favorites_dir(self, directory: str, file_handle, indent_level: int) -> None:
        """
        Process Internet Explorer Favorites directory recursively.
        
        Args:
            directory: Directory to process
            file_handle: Open file handle for writing
            indent_level: Current indentation level
        """
        indent = '    ' * indent_level
        
        # List items in directory
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            
            if os.path.isdir(item_path):
                # Directory (folder)
                folder_name = item
                file_handle.write(f'{indent}<DT><H3>{folder_name}</H3>\n')
                file_handle.write(f'{indent}<DL><p>\n')
                
                # Process subdirectory
                self._process_ie_favorites_dir(item_path, file_handle, indent_level + 1)
                
                file_handle.write(f'{indent}</DL><p>\n')
            
            elif item.endswith('.url'):
                # URL file
                title = os.path.splitext(item)[0]
                url = self._extract_url_from_ie_shortcut(item_path)
                
                if url:
                    file_handle.write(f'{indent}<DT><A HREF="{url}">{title}</A>\n')
    
    def _extract_url_from_ie_shortcut(self, url_file: str) -> Optional[str]:
        """
        Extract URL from Internet Explorer shortcut file.
        
        Args:
            url_file: Path to .url file
            
        Returns:
            URL string or None if not found
        """
        try:
            with open(url_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.startswith('URL='):
                        return line[4:].strip()
            return None
        except Exception:
            return None
    
    def _convert_xml_bookmarks_to_html(self, source_file: str, target_file: str) -> None:
        """
        Convert XML bookmarks to HTML format.
        
        Args:
            source_file: Source XML bookmark file
            target_file: Target HTML file
        """
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML
            tree = ET.parse(source_file)
            root = tree.getroot()
            
            # Write HTML file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write('<TITLE>Bookmarks</TITLE>\n')
                f.write('<H1>Bookmarks</H1>\n')
                f.write('<DL><p>\n')
                f.write('    <DT><H3>Imported XML Bookmarks</H3>\n')
                f.write('    <DL><p>\n')
                
                # Process XML structure
                # This is a simplified approach; actual implementation would need to handle
                # specific XML formats for different browsers
                for bookmark in root.findall('.//bookmark'):
                    url = bookmark.get('href', '')
                    title = bookmark.text or url
                    
                    if url:
                        f.write(f'        <DT><A HREF="{url}">{title}</A>\n')
                
                f.write('    </DL><p>\n')
                f.write('</DL><p>\n')
        except Exception as e:
            logger.error(f"Failed to convert XML bookmarks to HTML: {str(e)}")
            raise
    
    def _convert_generic_bookmarks_to_html(self, source_file: str, target_file: str) -> None:
        """
        Convert generic bookmarks to HTML format using best-effort approach.
        
        Args:
            source_file: Source bookmark file
            target_file: Target HTML file
        """
        try:
            bookmarks = []
            
            # Read source file
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Try to extract URLs using regex
            url_pattern = re.compile(r'https?://[^\s<>"\']+|www\.[^\s<>"\']+')
            urls = url_pattern.findall(content)
            
            for url in urls:
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                bookmarks.append((url, url))
            
            # Write HTML file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                f.write('<TITLE>Bookmarks</TITLE>\n')
                f.write('<H1>Bookmarks</H1>\n')
                f.write('<DL><p>\n')
                f.write('    <DT><H3>Imported Bookmarks</H3>\n')
                f.write('    <DL><p>\n')
                
                for title, url in bookmarks:
                    f.write(f'        <DT><A HREF="{url}">{title}</A>\n')
                
                f.write('    </DL><p>\n')
                f.write('</DL><p>\n')
        except Exception as e:
            logger.error(f"Failed to convert generic bookmarks to HTML: {str(e)}")
            raise
    
    # Platform-specific path methods
    
    def _get_netscape_paths(self) -> List[str]:
        """Get potential Netscape installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\Netscape\Navigator'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Netscape\Navigator'),
                os.path.expandvars(r'%APPDATA%\Netscape\Navigator'),
                os.path.expanduser('~\\Application Data\\Netscape\\Navigator')
            ])
        elif sys.platform == 'darwin':
            paths.extend([
                '/Applications/Netscape Navigator.app',
                os.path.expanduser('~/Library/Application Support/Netscape/Navigator')
            ])
        else:  # Linux/Unix
            paths.extend([
                '/usr/lib/netscape',
                '/opt/netscape',
                os.path.expanduser('~/.netscape')
            ])
        
        return paths
    
    def _get_mosaic_paths(self) -> List[str]:
        """Get potential NCSA Mosaic installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\NCSA Mosaic'),
                os.path.expandvars(r'%ProgramFiles(x86)%\NCSA Mosaic'),
                os.path.expanduser('~\\Application Data\\NCSA Mosaic')
            ])
        elif sys.platform == 'darwin':
            paths.extend([
                '/Applications/NCSA Mosaic.app',
                os.path.expanduser('~/Library/Application Support/NCSA Mosaic')
            ])
        else:  # Linux/Unix
            paths.extend([
                '/usr/lib/Mosaic',
                '/opt/Mosaic',
                os.path.expanduser('~/.mosaic')
            ])
        
        return paths
    
    def _get_opera_legacy_paths(self) -> List[str]:
        """Get potential Opera (Legacy) installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\Opera'),
                os.path.expanduser('~\\Application Data\\Opera')
            ])
        elif sys.platform == 'darwin':
            paths.extend([
                os.path.expanduser('~/Library/Preferences/Opera')
            ])
        else:  # Linux/Unix
            paths.extend([
                os.path.expanduser('~/.opera')
            ])
        
        return paths
    
    def _get_ie_legacy_paths(self) -> List[str]:
        """Get potential Internet Explorer (Legacy) installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%USERPROFILE%\Favorites'),
                os.path.expandvars(r'%APPDATA%\Microsoft\Internet Explorer'),
                os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Internet Explorer')
            ])
        
        return paths
    
    def _get_lynx_paths(self) -> List[str]:
        """Get potential Lynx installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\lynx'),
                os.path.expanduser('~\\Application Data\\lynx')
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                os.path.expanduser('~/.lynx'),
                os.path.expanduser('~/.config/lynx')
            ])
        
        return paths
    
    def _get_elinks_paths(self) -> List[str]:
        """Get potential ELinks installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\ELinks'),
                os.path.expanduser('~\\Application Data\\ELinks')
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                os.path.expanduser('~/.elinks'),
                os.path.expanduser('~/.config/elinks')
            ])
        
        return paths
    
    def _get_links_paths(self) -> List[str]:
        """Get potential Links installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\links'),
                os.path.expanduser('~\\Application Data\\links')
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                os.path.expanduser('~/.links'),
                os.path.expanduser('~/.config/links')
            ])
        
        return paths
    
    def _get_w3m_paths(self) -> List[str]:
        """Get potential w3m installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\w3m'),
                os.path.expanduser('~\\Application Data\\w3m')
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                os.path.expanduser('~/.w3m'),
                os.path.expanduser('~/.config/w3m')
            ])
        
        return paths
    
    def _get_dillo_paths(self) -> List[str]:
        """Get potential Dillo installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\dillo'),
                os.path.expanduser('~\\Application Data\\dillo')
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                os.path.expanduser('~/.dillo'),
                os.path.expanduser('~/.config/dillo')
            ])
        
        return paths
    
    def _get_arachne_paths(self) -> List[str]:
        """Get potential Arachne installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\Arachne'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Arachne'),
                'C:\\Arachne'
            ])
        else:  # Unix/Linux/macOS (less common)
            paths.extend([
                '/usr/local/arachne',
                '/opt/arachne',
                os.path.expanduser('~/.arachne')
            ])
        
        return paths
    
    def _get_phoenix_paths(self) -> List[str]:
        """Get potential Phoenix/Firebird installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\Phoenix'),
                os.path.expanduser('~\\Application Data\\Phoenix'),
                os.path.expandvars(r'%APPDATA%\Firebird'),
                os.path.expanduser('~\\Application Data\\Firebird')
            ])
        elif sys.platform == 'darwin':
            paths.extend([
                os.path.expanduser('~/Library/Application Support/Phoenix'),
                os.path.expanduser('~/Library/Phoenix'),
                os.path.expanduser('~/Library/Application Support/Firebird'),
                os.path.expanduser('~/Library/Firebird')
            ])
        else:  # Linux/Unix
            paths.extend([
                os.path.expanduser('~/.phoenix'),
                os.path.expanduser('~/.firebird')
            ])
        
        return paths
    
    def _get_k_meleon_paths(self) -> List[str]:
        """Get potential K-Meleon installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\K-Meleon'),
                os.path.expanduser('~\\Application Data\\K-Meleon'),
                os.path.expandvars(r'%ProgramFiles%\K-Meleon\Profiles'),
                os.path.expandvars(r'%ProgramFiles(x86)%\K-Meleon\Profiles')
            ])
        
        return paths
    
    def _get_galeon_paths(self) -> List[str]:
        """Get potential Galeon installation paths."""
        paths = []
        
        if sys.platform == 'darwin':
            paths.extend([
                os.path.expanduser('~/Library/Application Support/Galeon'),
                os.path.expanduser('~/Library/Galeon')
            ])
        else:  # Linux/Unix
            paths.extend([
                os.path.expanduser('~/.galeon'),
                os.path.expanduser('~/.config/galeon')
            ])
        
        return paths
    
    def _get_konqueror_legacy_paths(self) -> List[str]:
        """Get potential Konqueror (Legacy) installation paths."""
        paths = []
        
        # Primarily a Linux/Unix browser
        paths.extend([
            os.path.expanduser('~/.kde/share/apps/konqueror'),
            os.path.expanduser('~/.kde4/share/apps/konqueror'),
            os.path.expanduser('~/.local/share/konqueror')
        ])
        
        return paths
    
    def _get_amaya_paths(self) -> List[str]:
        """Get potential Amaya installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%APPDATA%\Amaya'),
                os.path.expanduser('~\\Application Data\\Amaya')
            ])
        elif sys.platform == 'darwin':
            paths.extend([
                os.path.expanduser('~/Library/Application Support/Amaya'),
                os.path.expanduser('~/Library/Amaya')
            ])
        else:  # Linux/Unix
            paths.extend([
                os.path.expanduser('~/.amaya'),
                os.path.expanduser('~/.config/amaya')
            ])
        
        return paths
    
    def _get_arena_paths(self) -> List[str]:
        """Get potential Arena installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\Arena'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Arena'),
                os.path.expanduser('~\\Application Data\\Arena')
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                '/usr/local/arena',
                '/opt/arena',
                os.path.expanduser('~/.arena')
            ])
        
        return paths
    
    def _get_cello_paths(self) -> List[str]:
        """Get potential Cello installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\Cello'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Cello'),
                'C:\\Cello'
            ])
        
        return paths
    
    def _get_chimera_paths(self) -> List[str]:
        """Get potential Chimera installation paths."""
        paths = []
        
        if sys.platform == 'darwin':
            paths.extend([
                os.path.expanduser('~/Library/Application Support/Chimera'),
                os.path.expanduser('~/Library/Chimera')
            ])
        else:  # Unix/Linux
            paths.extend([
                os.path.expanduser('~/.chimera')
            ])
        
        return paths
    
    def _get_browsex_paths(self) -> List[str]:
        """Get potential BrowseX installation paths."""
        paths = []
        
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\BrowseX'),
                os.path.expandvars(r'%ProgramFiles(x86)%\BrowseX'),
                os.path.expanduser('~\\Application Data\\BrowseX')
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                '/usr/local/browsex',
                '/opt/browsex',
                os.path.expanduser('~/.browsex')
            ])
        
        return paths
    
    def _get_ibrowse_paths(self) -> List[str]:
        """Get potential IBrowse installation paths."""
        paths = []
        
        # Primarily an Amiga browser, but might be used in emulation
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\IBrowse'),
                os.path.expandvars(r'%ProgramFiles(x86)%\IBrowse'),
                'C:\\Amiga\\IBrowse'
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                '/usr/local/amiga/ibrowse',
                '/opt/amiga/ibrowse',
                os.path.expanduser('~/.ibrowse')
            ])
        
        return paths
    
    def _get_voyager_paths(self) -> List[str]:
        """Get potential Voyager installation paths."""
        paths = []
        
        # Primarily an Amiga browser, but might be used in emulation
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\Voyager'),
                os.path.expandvars(r'%ProgramFiles(x86)%\Voyager'),
                'C:\\Amiga\\Voyager'
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                '/usr/local/amiga/voyager',
                '/opt/amiga/voyager',
                os.path.expanduser('~/.voyager')
            ])
        
        return paths
    
    def _get_aweb_paths(self) -> List[str]:
        """Get potential AWeb installation paths."""
        paths = []
        
        # Primarily an Amiga browser, but might be used in emulation
        if sys.platform == 'win32':
            paths.extend([
                os.path.expandvars(r'%ProgramFiles%\AWeb'),
                os.path.expandvars(r'%ProgramFiles(x86)%\AWeb'),
                'C:\\Amiga\\AWeb'
            ])
        else:  # Unix/Linux/macOS
            paths.extend([
                '/usr/local/amiga/aweb',
                '/opt/amiga/aweb',
                os.path.expanduser('~/.aweb')
            ])
        
        return paths


def main():
    """Main entry point for testing."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create controller
    controller = FloorperCore()
    
    # Create retro browser handler
    retro_handler = RetroBrowserHandler(controller)
    
    # Test detection
    browsers = retro_handler.detect_retro_browsers()
    print(f"Detected {len(browsers)} retro browsers:")
    
    for browser in browsers:
        print(f"- {browser['name']} at {browser['path']} with {len(browser['profiles'])} profiles")


if __name__ == "__main__":
    main()
