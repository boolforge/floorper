"""
History Merger Module

This module provides functionality to merge browsing history from multiple Firefox profiles.
Based on techniques from Firefox History Merger (https://github.com/crazy-max/firefox-history-merger)
"""

import os
import sys
import sqlite3
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple

# Setup logging
logger = logging.getLogger('floorper.core.history.merger')

class HistoryMerger:
    """Merges browsing history from multiple Firefox profiles."""
    
    def __init__(self):
        """Initialize the history merger."""
        pass
    
    def merge_history(
        self,
        source_profiles: List[Dict[str, Any]],
        target_profile: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Merge browsing history from multiple source profiles into a target profile.
        
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
        preserve_visits = options.get('preserve_visits', True)
        preserve_frecency = options.get('preserve_frecency', True)
        avoid_duplicates = options.get('avoid_duplicates', True)
        max_age_days = options.get('max_age_days', 0)  # 0 means no limit
        
        results = {
            'total_urls_imported': 0,
            'total_visits_imported': 0,
            'duplicate_urls_skipped': 0,
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
            
            # Get existing URLs in target
            existing_urls = self._get_existing_urls(target_cursor)
            
            # Calculate cutoff time for max age
            cutoff_time = 0
            if max_age_days > 0:
                current_time = int(time.time() * 1000000)  # Microseconds
                cutoff_time = current_time - (max_age_days * 24 * 60 * 60 * 1000000)
            
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
                
                # Get history entries from source
                history_entries = self._get_history_entries(source_cursor, cutoff_time)
                
                # Import history entries
                for entry in history_entries:
                    # Skip if avoiding duplicates and URL already exists
                    if avoid_duplicates and entry['url'] in existing_urls:
                        results['duplicate_urls_skipped'] += 1
                        continue
                    
                    # Import URL
                    place_id = self._import_url(
                        target_cursor, entry, preserve_frecency
                    )
                    
                    # Import visits if requested
                    if preserve_visits:
                        visits_imported = self._import_visits(
                            source_cursor, target_cursor, entry['id'], place_id
                        )
                        results['total_visits_imported'] += visits_imported
                    
                    # Add URL to existing URLs
                    existing_urls.add(entry['url'])
                    results['total_urls_imported'] += 1
                
                # Close source connection
                source_conn.close()
            
            # Update frecency values
            self._update_frecency(target_cursor)
            
            # Commit changes
            target_conn.commit()
            
            # Close target connection
            target_conn.close()
            
            return results
        except Exception as e:
            logger.error(f"Error merging history: {e}")
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
    
    def _get_existing_urls(self, cursor: sqlite3.Cursor) -> Set[str]:
        """
        Get existing URLs from the places database.
        
        Args:
            cursor: SQLite cursor
            
        Returns:
            Set of URLs
        """
        query = "SELECT url FROM moz_places"
        cursor.execute(query)
        
        urls = set()
        for row in cursor.fetchall():
            urls.add(row['url'])
        
        return urls
    
    def _get_history_entries(
        self,
        cursor: sqlite3.Cursor,
        cutoff_time: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get history entries from the places database.
        
        Args:
            cursor: SQLite cursor
            cutoff_time: Cutoff time for entries (microseconds since epoch)
            
        Returns:
            List of history entries
        """
        if cutoff_time > 0:
            query = """
            SELECT id, url, title, visit_count, last_visit_date, frecency
            FROM moz_places
            WHERE last_visit_date > ?
            """
            cursor.execute(query, (cutoff_time,))
        else:
            query = """
            SELECT id, url, title, visit_count, last_visit_date, frecency
            FROM moz_places
            """
            cursor.execute(query)
        
        entries = []
        for row in cursor.fetchall():
            entry = {
                'id': row['id'],
                'url': row['url'],
                'title': row['title'],
                'visit_count': row['visit_count'],
                'last_visit_date': row['last_visit_date'],
                'frecency': row['frecency']
            }
            entries.append(entry)
        
        return entries
    
    def _import_url(
        self,
        cursor: sqlite3.Cursor,
        entry: Dict[str, Any],
        preserve_frecency: bool
    ) -> int:
        """
        Import a URL into the places database.
        
        Args:
            cursor: SQLite cursor
            entry: History entry
            preserve_frecency: Whether to preserve frecency
            
        Returns:
            Place ID
        """
        # Check if URL already exists
        query = "SELECT id FROM moz_places WHERE url = ?"
        cursor.execute(query, (entry['url'],))
        result = cursor.fetchone()
        
        if result:
            place_id = result['id']
            
            # Update existing entry
            if preserve_frecency:
                query = """
                UPDATE moz_places
                SET title = COALESCE(?, title),
                    visit_count = visit_count + ?,
                    frecency = MAX(frecency, ?)
                WHERE id = ?
                """
                cursor.execute(
                    query,
                    (entry['title'], entry['visit_count'], entry['frecency'], place_id)
                )
            else:
                query = """
                UPDATE moz_places
                SET title = COALESCE(?, title),
                    visit_count = visit_count + ?
                WHERE id = ?
                """
                cursor.execute(
                    query,
                    (entry['title'], entry['visit_count'], place_id)
                )
        else:
            # Create new entry
            query = """
            INSERT INTO moz_places (url, title, visit_count, frecency, guid)
            VALUES (?, ?, ?, ?, ?)
            """
            guid = self._generate_guid()
            frecency = entry['frecency'] if preserve_frecency else 0
            cursor.execute(
                query,
                (entry['url'], entry['title'], entry['visit_count'], frecency, guid)
            )
            place_id = cursor.lastrowid
        
        return place_id
    
    def _import_visits(
        self,
        source_cursor: sqlite3.Cursor,
        target_cursor: sqlite3.Cursor,
        source_place_id: int,
        target_place_id: int
    ) -> int:
        """
        Import visits for a URL.
        
        Args:
            source_cursor: Source SQLite cursor
            target_cursor: Target SQLite cursor
            source_place_id: Source place ID
            target_place_id: Target place ID
            
        Returns:
            Number of visits imported
        """
        # Get visits from source
        query = """
        SELECT visit_date, visit_type, session
        FROM moz_historyvisits
        WHERE place_id = ?
        """
        source_cursor.execute(query, (source_place_id,))
        
        # Get existing visit dates in target
        query = """
        SELECT visit_date
        FROM moz_historyvisits
        WHERE place_id = ?
        """
        target_cursor.execute(query, (target_place_id,))
        existing_dates = {row['visit_date'] for row in target_cursor.fetchall()}
        
        # Import visits
        visits_imported = 0
        for row in source_cursor.fetchall():
            # Skip if visit date already exists
            if row['visit_date'] in existing_dates:
                continue
            
            # Import visit
            query = """
            INSERT INTO moz_historyvisits (place_id, visit_date, visit_type, session)
            VALUES (?, ?, ?, ?)
            """
            target_cursor.execute(
                query,
                (target_place_id, row['visit_date'], row['visit_type'], row['session'])
            )
            visits_imported += 1
            
            # Add visit date to existing dates
            existing_dates.add(row['visit_date'])
        
        return visits_imported
    
    def _update_frecency(self, cursor: sqlite3.Cursor) -> None:
        """
        Update frecency values for all places.
        
        Args:
            cursor: SQLite cursor
        """
        # This is a simplified version of Firefox's frecency calculation
        query = """
        UPDATE moz_places
        SET frecency = CASE
            WHEN visit_count = 0 THEN 0
            ELSE visit_count * 100 + (strftime('%s', 'now') - last_visit_date / 1000000) / 86400
        END
        """
        cursor.execute(query)
    
    def _generate_guid(self) -> str:
        """
        Generate a GUID for Firefox database entries.
        
        Returns:
            GUID string
        """
        import uuid
        return str(uuid.uuid4()).replace('-', '').upper()
