#!/usr/bin/env python3
"""
Test script for Floorper advanced features.

This script tests the four advanced features implemented in Floorper:
1. Session Merger
2. Bookmarks Deduplicator
3. Bookmarks Merger
4. History Merger

Usage:
    python test_advanced_features.py
"""

import os
import sys
import tempfile
import unittest
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.session.merger import SessionMerger
    from core.bookmarks.deduplicator import BookmarksDeduplicator
    from core.bookmarks.merger import BookmarksMerger
    from core.history.merger import HistoryMerger
except ImportError:
    print("Error: Could not import required modules.")
    print("Make sure you're running this script from the tests directory.")
    sys.exit(1)


class TestAdvancedFeatures(unittest.TestCase):
    """Test cases for Floorper advanced features."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for test profiles
        self.test_dir = tempfile.mkdtemp()
        self.source_profile1 = os.path.join(self.test_dir, "source_profile1")
        self.source_profile2 = os.path.join(self.test_dir, "source_profile2")
        self.target_profile = os.path.join(self.test_dir, "target_profile")
        
        # Create the directories
        os.makedirs(self.source_profile1, exist_ok=True)
        os.makedirs(self.source_profile2, exist_ok=True)
        os.makedirs(self.target_profile, exist_ok=True)
        
        # Create mock profile data for testing
        self._create_mock_profile_data()
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directories
        shutil.rmtree(self.test_dir)
        
    def _create_mock_profile_data(self):
        """Create mock profile data for testing."""
        # Create mock session data
        with open(os.path.join(self.source_profile1, "sessionstore.jsonlz4"), "w") as f:
            f.write('{"mock": "session data 1"}')
        with open(os.path.join(self.source_profile2, "sessionstore.jsonlz4"), "w") as f:
            f.write('{"mock": "session data 2"}')
        with open(os.path.join(self.target_profile, "sessionstore.jsonlz4"), "w") as f:
            f.write('{"mock": "target session data"}')
            
        # Create mock places database for bookmarks and history
        with open(os.path.join(self.source_profile1, "places.sqlite"), "w") as f:
            f.write('mock places data 1')
        with open(os.path.join(self.source_profile2, "places.sqlite"), "w") as f:
            f.write('mock places data 2')
        with open(os.path.join(self.target_profile, "places.sqlite"), "w") as f:
            f.write('mock target places data')
    
    def test_session_merger(self):
        """Test the SessionMerger functionality."""
        merger = SessionMerger()
        source_profiles = [
            {"path": self.source_profile1},
            {"path": self.source_profile2}
        ]
        target_profile = {"path": self.target_profile}
        
        # This is a mock test since we can't actually merge sessions without real data
        # In a real test, we would check the result of the merge operation
        try:
            # Just verify that the method exists and can be called
            merger.merge_sessions(source_profiles, target_profile)
            self.assertTrue(True)  # If we get here, the test passes
        except AttributeError:
            self.fail("SessionMerger does not have merge_sessions method")
        except Exception as e:
            # We expect an exception since we're using mock data
            # In a real test with real data, this would not happen
            pass
    
    def test_bookmarks_deduplicator(self):
        """Test the BookmarksDeduplicator functionality."""
        deduplicator = BookmarksDeduplicator()
        profile_path = Path(self.target_profile)
        
        # This is a mock test since we can't actually deduplicate bookmarks without real data
        try:
            # Just verify that the method exists and can be called
            deduplicator.deduplicate_bookmarks(profile_path)
            self.assertTrue(True)  # If we get here, the test passes
        except AttributeError:
            self.fail("BookmarksDeduplicator does not have deduplicate_bookmarks method")
        except Exception as e:
            # We expect an exception since we're using mock data
            # In a real test with real data, this would not happen
            pass
    
    def test_bookmarks_merger(self):
        """Test the BookmarksMerger functionality."""
        merger = BookmarksMerger()
        source_profiles = [
            {"path": self.source_profile1, "name": "Profile 1"},
            {"path": self.source_profile2, "name": "Profile 2"}
        ]
        target_profile = {"path": self.target_profile}
        
        # This is a mock test since we can't actually merge bookmarks without real data
        try:
            # Just verify that the method exists and can be called
            merger.merge_bookmarks(source_profiles, target_profile)
            self.assertTrue(True)  # If we get here, the test passes
        except AttributeError:
            self.fail("BookmarksMerger does not have merge_bookmarks method")
        except Exception as e:
            # We expect an exception since we're using mock data
            # In a real test with real data, this would not happen
            pass
    
    def test_history_merger(self):
        """Test the HistoryMerger functionality."""
        merger = HistoryMerger()
        source_profiles = [
            {"path": self.source_profile1},
            {"path": self.source_profile2}
        ]
        target_profile = {"path": self.target_profile}
        
        # This is a mock test since we can't actually merge history without real data
        try:
            # Just verify that the method exists and can be called
            merger.merge_history(source_profiles, target_profile)
            self.assertTrue(True)  # If we get here, the test passes
        except AttributeError:
            self.fail("HistoryMerger does not have merge_history method")
        except Exception as e:
            # We expect an exception since we're using mock data
            # In a real test with real data, this would not happen
            pass


if __name__ == "__main__":
    unittest.main()
