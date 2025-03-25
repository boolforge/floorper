"""
Bookmarks Deduplicator Module

This module provides functionality to detect and remove duplicate bookmarks in Firefox profiles.
Based on techniques from Firefox Bookmarks Deduplicator (https://github.com/james-cube/firefox-bookmarks-deduplicator)
"""

import os
import sys
import sqlite3
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

# Setup logging
logger = logging.getLogger('floorper.core.bookmarks.deduplicator')

class BookmarksDeduplicator:
    """Detects and removes duplicate bookmarks in Firefox profiles."""
    
    def __init__(self):
        """Initialize the bookmarks deduplicator."""
        pass
    
    def deduplicate_bookmarks(
        self,
        profile_path: Path,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect and remove duplicate bookmarks in a Firefox profile.
        
        Args:
            profile_path: Path to the profile directory
            options: Additional options for deduplication
            
        Returns:
            Dictionary with results of the deduplication process
        """
        if options is None:
            options = {}
        
        # Default options
        dry_run = options.get('dry_run', False)
        preserve_newest = options.get('preserve_newest', True)
        preserve_tags = options.get('preserve_tags', True)
        
        results = {
            'total_bookmarks': 0,
            'duplicate_sets': 0,
            'duplicates_removed': 0,
            'errors': 0
        }
        
        try:
            # Connect to places database
            places_db_path = profile_path / "places.sqlite"
            
            # Create a backup before modifying
            if not dry_run:
                self._backup_places_db(places_db_path)
            
            # Connect to database
            conn = sqlite3.connect(places_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all bookmarks
            bookmarks = self._get_all_bookmarks(cursor)
            results['total_bookmarks'] = len(bookmarks)
            
            # Find duplicates
            duplicate_sets = self._find_duplicate_bookmarks(bookmarks)
            results['duplicate_sets'] = len(duplicate_sets)
            
            # Remove duplicates if not dry run
            if not dry_run:
                removed = self._remove_duplicate_bookmarks(
                    cursor, duplicate_sets, preserve_newest, preserve_tags
                )
                results['duplicates_removed'] = removed
                
                # Commit changes
                conn.commit()
            
            # Close connection
            conn.close()
            
            return results
        except Exception as e:
            logger.error(f"Error deduplicating bookmarks: {e}")
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
    
    def _find_duplicate_bookmarks(self, bookmarks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Find duplicate bookmarks based on URL.
        
        Args:
            bookmarks: List of bookmarks
            
        Returns:
            List of duplicate bookmark sets
        """
        # Group bookmarks by URL
        url_groups = {}
        for bookmark in bookmarks:
            url = bookmark['url']
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(bookmark)
        
        # Filter groups with more than one bookmark
        duplicate_sets = [group for group in url_groups.values() if len(group) > 1]
        
        return duplicate_sets
    
    def _remove_duplicate_bookmarks(
        self,
        cursor: sqlite3.Cursor,
        duplicate_sets: List[List[Dict[str, Any]]],
        preserve_newest: bool,
        preserve_tags: bool
    ) -> int:
        """
        Remove duplicate bookmarks.
        
        Args:
            cursor: SQLite cursor
            duplicate_sets: List of duplicate bookmark sets
            preserve_newest: Whether to preserve the newest bookmark
            preserve_tags: Whether to preserve tags from removed bookmarks
            
        Returns:
            Number of bookmarks removed
        """
        removed_count = 0
        
        for duplicate_set in duplicate_sets:
            # Sort by date (newest first) if preserving newest
            if preserve_newest:
                duplicate_set.sort(key=lambda x: x['date_added'], reverse=True)
            
            # Keep the first bookmark, remove the rest
            keep_bookmark = duplicate_set[0]
            remove_bookmarks = duplicate_set[1:]
            
            # Collect tags from bookmarks to be removed
            all_tags = set(keep_bookmark['tags'])
            for bookmark in remove_bookmarks:
                all_tags.update(bookmark['tags'])
            
            # Remove duplicate bookmarks
            for bookmark in remove_bookmarks:
                self._remove_bookmark(cursor, bookmark['id'])
                removed_count += 1
            
            # Update tags on kept bookmark if preserving tags
            if preserve_tags and len(all_tags) > len(keep_bookmark['tags']):
                self._update_bookmark_tags(cursor, keep_bookmark['id'], list(all_tags))
        
        return removed_count
    
    def _remove_bookmark(self, cursor: sqlite3.Cursor, bookmark_id: int) -> None:
        """
        Remove a bookmark.
        
        Args:
            cursor: SQLite cursor
            bookmark_id: Bookmark ID
        """
        query = "DELETE FROM moz_bookmarks WHERE id = ?"
        cursor.execute(query, (bookmark_id,))
    
    def _update_bookmark_tags(self, cursor: sqlite3.Cursor, bookmark_id: int, tags: List[str]) -> None:
        """
        Update tags for a bookmark.
        
        Args:
            cursor: SQLite cursor
            bookmark_id: Bookmark ID
            tags: List of tags
        """
        # First, remove existing tags
        query = """
        DELETE FROM moz_bookmarks
        WHERE type = 1 AND parent IN (
            SELECT id FROM moz_bookmarks WHERE parent = 4
        ) AND fk = (
            SELECT fk FROM moz_bookmarks WHERE id = ?
        )
        """
        cursor.execute(query, (bookmark_id,))
        
        # Then, add new tags
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
                INSERT INTO moz_bookmarks (type, parent, title, dateAdded, lastModified)
                VALUES (2, 4, ?, strftime('%s', 'now') * 1000000, strftime('%s', 'now') * 1000000)
                """
                cursor.execute(query, (tag,))
                tag_folder_id = cursor.lastrowid
            
            # Add bookmark to tag folder
            query = """
            INSERT INTO moz_bookmarks (type, fk, parent, dateAdded, lastModified)
            SELECT 1, fk, ?, strftime('%s', 'now') * 1000000, strftime('%s', 'now') * 1000000
            FROM moz_bookmarks WHERE id = ?
            """
            cursor.execute(query, (tag_folder_id, bookmark_id))
