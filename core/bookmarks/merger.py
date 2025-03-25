"""
Bookmarks Merger Module

This module provides functionality to merge bookmarks from multiple Firefox profiles.
Based on techniques from Firefox Bookmarks Merger (https://github.com/james-cube/firefox-bookmarks-merger)
"""

import os
import sys
import sqlite3
import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

# Setup logging
logger = logging.getLogger('floorper.core.bookmarks.merger')

class BookmarksMerger:
    """Merges bookmarks from multiple Firefox profiles."""
    
    def __init__(self):
        """Initialize the bookmarks merger."""
        pass
    
    def merge_bookmarks(
        self,
        source_profiles: List[Dict[str, Any]],
        target_profile: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Merge bookmarks from multiple source profiles into a target profile.
        
        Args:
            source_profiles: List of source profiles
            target_profile: Target profile
            options: Additional options for merging
            
        Returns:
            Dictionary with results of the merge process
        """
        if options is None:
            options = {}
        
        # Default options
        preserve_structure = options.get('preserve_structure', True)
        avoid_duplicates = options.get('avoid_duplicates', True)
        import_tags = options.get('import_tags', True)
        
        results = {
            'total_bookmarks_imported': 0,
            'duplicate_bookmarks_skipped': 0,
            'folders_created': 0,
            'errors': 0
        }
        
        try:
            # Connect to target database
            target_path = Path(target_profile["path"])
            target_db_path = target_path / "places.sqlite"
            
            # Create a backup before modifying
            self._backup_places_db(target_db_path)
            
            # Connect to target database
            target_conn = sqlite3.connect(target_db_path)
            target_conn.row_factory = sqlite3.Row
            target_cursor = target_conn.cursor()
            
            # Get existing bookmarks in target
            existing_bookmarks = self._get_all_bookmarks(target_cursor)
            existing_urls = {bookmark['url'] for bookmark in existing_bookmarks}
            
            # Get existing folders in target
            existing_folders = self._get_all_folders(target_cursor)
            folder_map = {folder['title']: folder['id'] for folder in existing_folders}
            
            # Process each source profile
            for source_profile in source_profiles:
                source_path = Path(source_profile["path"])
                source_db_path = source_path / "places.sqlite"
                
                # Skip if database doesn't exist
                if not source_db_path.exists():
                    logger.warning(f"Places database not found at {source_db_path}")
                    continue
                
                # Connect to source database
                source_conn = sqlite3.connect(source_db_path)
                source_conn.row_factory = sqlite3.Row
                source_cursor = source_conn.cursor()
                
                # Get bookmarks from source
                source_bookmarks = self._get_all_bookmarks(source_cursor)
                
                # Get folders from source
                source_folders = self._get_all_folders(source_cursor)
                
                # Create folder structure if preserving structure
                if preserve_structure:
                    # Create profile-specific folder in target
                    profile_name = source_profile.get("name", f"Imported Profile {source_path.name}")
                    profile_folder_id = self._ensure_folder_exists(
                        target_cursor, profile_name, 3, folder_map
                    )
                    results['folders_created'] += 1
                    
                    # Create folder structure
                    source_folder_map = {folder['id']: folder for folder in source_folders}
                    target_folder_map = {}
                    
                    # Map source folder IDs to target folder IDs
                    for folder in source_folders:
                        if folder['id'] in [1, 2, 3, 4, 5, 6]:  # Skip special folders
                            continue
                        
                        # Determine parent folder
                        parent_id = folder['parent']
                        if parent_id in [1, 2, 3, 4, 5, 6]:
                            # If parent is a special folder, use profile folder
                            target_parent_id = profile_folder_id
                        elif parent_id in target_folder_map:
                            # If parent has been mapped, use mapped ID
                            target_parent_id = target_folder_map[parent_id]
                        else:
                            # Otherwise, use profile folder
                            target_parent_id = profile_folder_id
                        
                        # Create folder in target
                        target_folder_id = self._create_folder(
                            target_cursor, folder['title'], target_parent_id
                        )
                        target_folder_map[folder['id']] = target_folder_id
                        results['folders_created'] += 1
                else:
                    # Use bookmarks menu folder as target
                    profile_folder_id = 3
                    target_folder_map = {}
                
                # Import bookmarks
                for bookmark in source_bookmarks:
                    # Skip if avoiding duplicates and URL already exists
                    if avoid_duplicates and bookmark['url'] in existing_urls:
                        results['duplicate_bookmarks_skipped'] += 1
                        continue
                    
                    # Determine parent folder
                    parent_id = bookmark['parent']
                    if parent_id in target_folder_map:
                        # If parent has been mapped, use mapped ID
                        target_parent_id = target_folder_map[parent_id]
                    else:
                        # Otherwise, use profile folder
                        target_parent_id = profile_folder_id
                    
                    # Create bookmark in target
                    bookmark_id = self._create_bookmark(
                        target_cursor, bookmark['title'], bookmark['url'], target_parent_id
                    )
                    
                    # Import tags if requested
                    if import_tags and bookmark['tags']:
                        self._import_tags(target_cursor, bookmark_id, bookmark['tags'])
                    
                    # Add URL to existing URLs
                    existing_urls.add(bookmark['url'])
                    results['total_bookmarks_imported'] += 1
                
                # Close source connection
                source_conn.close()
            
            # Commit changes
            target_conn.commit()
            
            # Close target connection
            target_conn.close()
            
            return results
        except Exception as e:
            logger.error(f"Error merging bookmarks: {e}")
            results['errors'] += 1
            return results
    
    def _backup_places_db(self, db_path: Path) -> None:
        """
        Create a backup of the places database.
        
        Args:
            db_path: Path to the places database
        """
        import shutil
        backup_path = db_path.with_suffix('.sqlite.bak')
        shutil.copy2(db_path, backup_path)
        logger.info(f"Created backup of places database at {backup_path}")
    
    def _get_all_bookmarks(self, cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
        """
        Get all bookmarks from the places database.
        
        Args:
            cursor: SQLite cursor
            
        Returns:
            List of bookmarks
        """
        query = """
        SELECT b.id, b.title, p.url, b.dateAdded, b.lastModified, b.parent
        FROM moz_bookmarks b
        JOIN moz_places p ON b.fk = p.id
        WHERE b.type = 1
        """
        cursor.execute(query)
        
        bookmarks = []
        for row in cursor.fetchall():
            bookmark = {
                'id': row['id'],
                'title': row['title'],
                'url': row['url'],
                'date_added': row['dateAdded'],
                'last_modified': row['lastModified'],
                'parent': row['parent'],
                'tags': self._get_bookmark_tags(cursor, row['id'])
            }
            bookmarks.append(bookmark)
        
        return bookmarks
    
    def _get_all_folders(self, cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
        """
        Get all folders from the places database.
        
        Args:
            cursor: SQLite cursor
            
        Returns:
            List of folders
        """
        query = """
        SELECT id, title, parent, dateAdded, lastModified
        FROM moz_bookmarks
        WHERE type = 2
        """
        cursor.execute(query)
        
        folders = []
        for row in cursor.fetchall():
            folder = {
                'id': row['id'],
                'title': row['title'],
                'parent': row['parent'],
                'date_added': row['dateAdded'],
                'last_modified': row['lastModified']
            }
            folders.append(folder)
        
        return folders
    
    def _get_bookmark_tags(self, cursor: sqlite3.Cursor, bookmark_id: int) -> List[str]:
        """
        Get tags for a bookmark.
        
        Args:
            cursor: SQLite cursor
            bookmark_id: Bookmark ID
            
        Returns:
            List of tags
        """
        query = """
        SELECT t.title
        FROM moz_bookmarks b
        JOIN moz_bookmarks t ON b.parent = t.id
        WHERE b.id = ? AND t.parent = 4
        """
        cursor.execute(query, (bookmark_id,))
        
        tags = []
        for row in cursor.fetchall():
            tags.append(row['title'])
        
        return tags
    
    def _ensure_folder_exists(
        self,
        cursor: sqlite3.Cursor,
        folder_name: str,
        parent_id: int,
        folder_map: Dict[str, int]
    ) -> int:
        """
        Ensure a folder exists, creating it if necessary.
        
        Args:
            cursor: SQLite cursor
            folder_name: Folder name
            parent_id: Parent folder ID
            folder_map: Map of folder names to IDs
            
        Returns:
            Folder ID
        """
        if folder_name in folder_map:
            return folder_map[folder_name]
        
        return self._create_folder(cursor, folder_name, parent_id)
    
    def _create_folder(
        self,
        cursor: sqlite3.Cursor,
        folder_name: str,
        parent_id: int
    ) -> int:
        """
        Create a folder.
        
        Args:
            cursor: SQLite cursor
            folder_name: Folder name
            parent_id: Parent folder ID
            
        Returns:
            Folder ID
        """
        query = """
        INSERT INTO moz_bookmarks (type, parent, title, dateAdded, lastModified)
        VALUES (2, ?, ?, strftime('%s', 'now') * 1000000, strftime('%s', 'now') * 1000000)
        """
        cursor.execute(query, (parent_id, folder_name))
        return cursor.lastrowid
    
    def _create_bookmark(
        self,
        cursor: sqlite3.Cursor,
        title: str,
        url: str,
        parent_id: int
    ) -> int:
        """
        Create a bookmark.
        
        Args:
            cursor: SQLite cursor
            title: Bookmark title
            url: Bookmark URL
            parent_id: Parent folder ID
            
        Returns:
            Bookmark ID
        """
        # First, ensure the URL exists in moz_places
        query = "SELECT id FROM moz_places WHERE url = ?"
        cursor.execute(query, (url,))
        result = cursor.fetchone()
        
        if result:
            place_id = result['id']
        else:
            # Create new place
            query = """
            INSERT INTO moz_places (url, title, frecency, guid)
            VALUES (?, ?, 0, ?)
            """
            guid = self._generate_guid()
            cursor.execute(query, (url, title, guid))
            place_id = cursor.lastrowid
        
        # Create bookmark
        query = """
        INSERT INTO moz_bookmarks (type, fk, parent, title, dateAdded, lastModified, guid)
        VALUES (1, ?, ?, ?, strftime('%s', 'now') * 1000000, strftime('%s', 'now') * 1000000, ?)
        """
        guid = self._generate_guid()
        cursor.execute(query, (place_id, parent_id, title, guid))
        return cursor.lastrowid
    
    def _import_tags(
        self,
        cursor: sqlite3.Cursor,
        bookmark_id: int,
        tags: List[str]
    ) -> None:
        """
        Import tags for a bookmark.
        
        Args:
            cursor: SQLite cursor
            bookmark_id: Bookmark ID
            tags: List of tags
        """
        for tag in tags:
            # Get or create tag folder
            query = "SELECT id FROM moz_bookmarks WHERE parent = 4 AND title = ?"
            cursor.execute(query, (tag,))
            result = cursor.fetchone()
            
            if result:
                tag_folder_id = result['id']
            else:
                # Create new tag folder
                query = """
                INSERT INTO moz_bookmarks (type, parent, title, dateAdded, lastModified, guid)
                VALUES (2, 4, ?, strftime('%s', 'now') * 1000000, strftime('%s', 'now') * 1000000, ?)
                """
                guid = self._generate_guid()
                cursor.execute(query, (tag, guid))
                tag_folder_id = cursor.lastrowid
            
            # Get bookmark place ID
            query = "SELECT fk FROM moz_bookmarks WHERE id = ?"
            cursor.execute(query, (bookmark_id,))
            result = cursor.fetchone()
            place_id = result['fk']
            
            # Add bookmark to tag folder
            query = """
            INSERT INTO moz_bookmarks (type, fk, parent, dateAdded, lastModified, guid)
            VALUES (1, ?, ?, strftime('%s', 'now') * 1000000, strftime('%s', 'now') * 1000000, ?)
            """
            guid = self._generate_guid()
            cursor.execute(query, (place_id, tag_folder_id, guid))
    
    def _generate_guid(self) -> str:
        """
        Generate a GUID for Firefox database entries.
        
        Returns:
            GUID string
        """
        import uuid
        return str(uuid.uuid4()).replace('-', '').upper()
