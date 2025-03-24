#!/usr/bin/env python3
"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This script runs comprehensive tests to ensure Floorper works correctly
across different platforms and with various browsers.
"""

import os
import sys
import platform
import logging
import unittest
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import floorper modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import floorper modules
from floorper.core import BrowserDetector, ProfileMigrator
from floorper.utils import get_platform, get_app_info, get_floorp_profiles
from floorper.backup import BackupManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('floorper.tests')

class TestBrowserDetector(unittest.TestCase):
    """Test the BrowserDetector class."""
    
    def setUp(self):
        """Set up the test case."""
        self.detector = BrowserDetector()
    
    def test_detect_browsers(self):
        """Test browser detection."""
        browsers = self.detector.detect_browsers()
        
        # We should at least detect some browsers
        logger.info(f"Detected browsers: {list(browsers.keys())}")
        
        # Platform-specific checks
        platform_type = get_platform()
        
        if platform_type == 'windows':
            # On Windows, we should detect at least Chrome or Firefox
            self.assertTrue(
                any(b in browsers for b in ['chrome', 'firefox', 'edge']),
                "Failed to detect any common browsers on Windows"
            )
        elif platform_type == 'macos':
            # On macOS, we should detect at least Safari or Firefox
            self.assertTrue(
                any(b in browsers for b in ['safari', 'firefox', 'chrome']),
                "Failed to detect any common browsers on macOS"
            )
        elif platform_type == 'linux':
            # On Linux, we should detect at least Firefox or Chrome
            self.assertTrue(
                any(b in browsers for b in ['firefox', 'chrome', 'chromium']),
                "Failed to detect any common browsers on Linux"
            )
    
    def test_get_profiles(self):
        """Test profile detection."""
        # Get detected browsers
        browsers = self.detector.detect_browsers()
        
        for browser_id in browsers:
            profiles = self.detector.get_profiles(browser_id)
            logger.info(f"Detected {len(profiles)} profiles for {browser_id}")
            
            # Each profile should have at least a name and path
            for profile in profiles:
                self.assertIn('name', profile, f"Profile for {browser_id} missing 'name'")
                self.assertIn('path', profile, f"Profile for {browser_id} missing 'path'")

class TestProfileMigrator(unittest.TestCase):
    """Test the ProfileMigrator class."""
    
    def setUp(self):
        """Set up the test case."""
        self.migrator = ProfileMigrator()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock source profile
        self.source_profile = os.path.join(self.temp_dir, 'source_profile')
        os.makedirs(self.source_profile, exist_ok=True)
        
        # Create mock target profile
        self.target_profile = os.path.join(self.temp_dir, 'target_profile')
        os.makedirs(self.target_profile, exist_ok=True)
        
        # Create mock files in source profile
        with open(os.path.join(self.source_profile, 'prefs.js'), 'w') as f:
            f.write('// Test preferences\n')
        
        with open(os.path.join(self.source_profile, 'bookmarks.html'), 'w') as f:
            f.write('<html><body><h1>Test Bookmarks</h1></body></html>\n')
        
        # Create bookmarks directory
        os.makedirs(os.path.join(self.source_profile, 'bookmarkbackups'), exist_ok=True)
        
        # Create mock bookmark backup
        with open(os.path.join(self.source_profile, 'bookmarkbackups', 'bookmarks.json'), 'w') as f:
            f.write('{"bookmarks": []}\n')
    
    def tearDown(self):
        """Clean up after the test case."""
        shutil.rmtree(self.temp_dir)
    
    def test_migrate_profile(self):
        """Test profile migration."""
        # Migrate profile
        result = self.migrator.migrate_profile(
            browser_id='firefox',
            source_profile=self.source_profile,
            target_profile=self.target_profile
        )
        
        # Check result
        self.assertTrue(result.get('success', False), f"Migration failed: {result.get('error', 'Unknown error')}")
        
        # Check that files were copied
        self.assertTrue(os.path.exists(os.path.join(self.target_profile, 'prefs.js')))
        self.assertTrue(os.path.exists(os.path.join(self.target_profile, 'bookmarks.html')))
        self.assertTrue(os.path.exists(os.path.join(self.target_profile, 'bookmarkbackups')))
        self.assertTrue(os.path.exists(os.path.join(self.target_profile, 'bookmarkbackups', 'bookmarks.json')))

class TestBackupManager(unittest.TestCase):
    """Test the BackupManager class."""
    
    def setUp(self):
        """Set up the test case."""
        self.backup_manager = BackupManager()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock profile
        self.profile_dir = os.path.join(self.temp_dir, 'profile')
        os.makedirs(self.profile_dir, exist_ok=True)
        
        # Create mock files in profile
        with open(os.path.join(self.profile_dir, 'prefs.js'), 'w') as f:
            f.write('// Test preferences\n')
        
        with open(os.path.join(self.profile_dir, 'bookmarks.html'), 'w') as f:
            f.write('<html><body><h1>Test Bookmarks</h1></body></html>\n')
    
    def tearDown(self):
        """Clean up after the test case."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_backup(self):
        """Test backup creation."""
        # Create backup
        backup_path = self.backup_manager.create_backup(self.profile_dir)
        
        # Check that backup was created
        self.assertIsNotNone(backup_path, "Backup creation failed")
        self.assertTrue(os.path.exists(backup_path), f"Backup path does not exist: {backup_path}")
        
        # Check that backup contains the expected files
        self.assertTrue(os.path.exists(os.path.join(backup_path, 'prefs.js')))
        self.assertTrue(os.path.exists(os.path.join(backup_path, 'bookmarks.html')))
    
    def test_restore_backup(self):
        """Test backup restoration."""
        # Create backup
        backup_path = self.backup_manager.create_backup(self.profile_dir)
        
        # Delete original files
        os.remove(os.path.join(self.profile_dir, 'prefs.js'))
        os.remove(os.path.join(self.profile_dir, 'bookmarks.html'))
        
        # Restore backup
        result = self.backup_manager.restore_backup(backup_path, self.profile_dir)
        
        # Check result
        self.assertTrue(result, "Backup restoration failed")
        
        # Check that files were restored
        self.assertTrue(os.path.exists(os.path.join(self.profile_dir, 'prefs.js')))
        self.assertTrue(os.path.exists(os.path.join(self.profile_dir, 'bookmarks.html')))

class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test cross-platform compatibility."""
    
    def test_platform_detection(self):
        """Test platform detection."""
        platform_type = get_platform()
        system = platform.system().lower()
        
        logger.info(f"Detected platform: {platform_type}")
        logger.info(f"System: {system}")
        
        if system == 'windows' or system.startswith('win'):
            self.assertEqual(platform_type, 'windows')
        elif system == 'darwin':
            self.assertEqual(platform_type, 'macos')
        elif system == 'linux':
            self.assertEqual(platform_type, 'linux')
        elif system == 'haiku':
            self.assertEqual(platform_type, 'haiku')
        elif system == 'os/2' or system == 'os2':
            self.assertEqual(platform_type, 'os2')
    
    def test_app_info(self):
        """Test app info."""
        app_info = get_app_info()
        
        logger.info(f"App info: {app_info}")
        
        self.assertEqual(app_info['name'], 'Floorper')
        self.assertIn('version', app_info)
        self.assertIn('platform', app_info)
        self.assertEqual(app_info['platform'], get_platform())

def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestBrowserDetector))
    suite.addTest(unittest.makeSuite(TestProfileMigrator))
    suite.addTest(unittest.makeSuite(TestBackupManager))
    suite.addTest(unittest.makeSuite(TestCrossPlatformCompatibility))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
