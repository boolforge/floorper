"""
Floorper - GUI Interface

This module provides a modern graphical user interface for Floorper using PyQt6.
It allows users to detect, migrate, and manage browser profiles with a user-friendly interface.
"""

import os
import sys
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QCheckBox,
    QComboBox, QProgressBar, QMessageBox, QTabWidget, QSplitter,
    QFrame, QScrollArea, QGroupBox, QGridLayout, QFileDialog,
    QDialog, QDialogButtonBox, QLineEdit, QTextEdit, QSpacerItem,
    QSizePolicy, QStatusBar
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction, QColor, QPalette

from core.browser_detector import BrowserDetector
from core.profile_migrator import ProfileMigrator
from core.backup_manager import BackupManager
from utils.app_info import get_app_info, get_theme_colors

# Setup logging
logger = logging.getLogger('floorper.gui')

class FloorperGUI(QMainWindow):
    """Main GUI window for Floorper application."""
    
    def __init__(self):
        """Initialize the GUI."""
        super().__init__()
        
        # Initialize components
        self.browser_detector = BrowserDetector()
        self.profile_migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
        
        # Setup UI
        self.setWindowTitle("Floorper - Browser Profile Migration Tool")
        self.setMinimumSize(900, 600)
        
        # Apply theme
        self._apply_theme()
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_detection_tab()
        self._create_migration_tab()
        self._create_backup_tab()
        self._create_settings_tab()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Load settings
        self._load_settings()
        
        # Show welcome message
        self._show_welcome_message()
    
    def run(self) -> int:
        """
        Run the GUI application.
        
        Returns:
            Exit code
        """
        self.show()
        return QApplication(sys.argv).exec()
    
    def _apply_theme(self) -> None:
        """Apply theme colors to the application."""
        colors = get_theme_colors()
        
        # Create palette
        palette = QPalette()
        
        # Set colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["light"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["highlight"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["dark"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["light"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["background"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["link"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["light"]))
        
        # Apply palette
        self.setPalette(palette)
    
    def _create_detection_tab(self) -> None:
        """Create the browser detection tab."""
        detection_tab = QWidget()
        layout = QVBoxLayout(detection_tab)
        
        # Create header
        header_label = QLabel("Browser Detection")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Create description
        description_label = QLabel(
            "Detect installed browsers and their profiles on your system."
        )
        layout.addWidget(description_label)
        layout.addSpacing(10)
        
        # Create detection button
        detect_button = QPushButton("Detect Browsers")
        detect_button.clicked.connect(self._detect_browsers)
        layout.addWidget(detect_button)
        
        # Create results area
        results_group = QGroupBox("Detection Results")
        results_layout = QVBoxLayout(results_group)
        
        # Create browsers list
        self.browsers_list = QListWidget()
        results_layout.addWidget(QLabel("Detected Browsers:"))
        results_layout.addWidget(self.browsers_list)
        
        # Create profiles list
        self.profiles_list = QListWidget()
        results_layout.addWidget(QLabel("Browser Profiles:"))
        results_layout.addWidget(self.profiles_list)
        
        # Connect browser selection to profile display
        self.browsers_list.itemClicked.connect(self._show_browser_profiles)
        
        layout.addWidget(results_group)
        
        # Add tab
        self.tab_widget.addTab(detection_tab, "Detection")
    
    def _create_migration_tab(self) -> None:
        """Create the profile migration tab."""
        migration_tab = QWidget()
        layout = QVBoxLayout(migration_tab)
        
        # Create header
        header_label = QLabel("Profile Migration")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Create description
        description_label = QLabel(
            "Migrate profiles between browsers, including bookmarks, history, cookies, and more."
        )
        layout.addWidget(description_label)
        layout.addSpacing(10)
        
        # Create source and target selection
        selection_group = QGroupBox("Migration Settings")
        selection_layout = QGridLayout(selection_group)
        
        # Source browser
        selection_layout.addWidget(QLabel("Source Browser:"), 0, 0)
        self.source_browser_combo = QComboBox()
        selection_layout.addWidget(self.source_browser_combo, 0, 1)
        
        # Source profile
        selection_layout.addWidget(QLabel("Source Profile:"), 1, 0)
        self.source_profile_combo = QComboBox()
        selection_layout.addWidget(self.source_profile_combo, 1, 1)
        
        # Target browser
        selection_layout.addWidget(QLabel("Target Browser:"), 2, 0)
        self.target_browser_combo = QComboBox()
        selection_layout.addWidget(self.target_browser_combo, 2, 1)
        
        # Target profile
        selection_layout.addWidget(QLabel("Target Profile:"), 3, 0)
        self.target_profile_combo = QComboBox()
        selection_layout.addWidget(self.target_profile_combo, 3, 1)
        
        # Connect browser selection to profile display
        self.source_browser_combo.currentIndexChanged.connect(
            lambda: self._update_profiles(self.source_browser_combo, self.source_profile_combo)
        )
        self.target_browser_combo.currentIndexChanged.connect(
            lambda: self._update_profiles(self.target_browser_combo, self.target_profile_combo)
        )
        
        layout.addWidget(selection_group)
        
        # Create data selection
        data_group = QGroupBox("Data to Migrate")
        data_layout = QVBoxLayout(data_group)
        
        # Create checkboxes for data types
        self.bookmarks_checkbox = QCheckBox("Bookmarks")
        self.bookmarks_checkbox.setChecked(True)
        data_layout.addWidget(self.bookmarks_checkbox)
        
        self.history_checkbox = QCheckBox("History")
        self.history_checkbox.setChecked(True)
        data_layout.addWidget(self.history_checkbox)
        
        self.cookies_checkbox = QCheckBox("Cookies")
        self.cookies_checkbox.setChecked(True)
        data_layout.addWidget(self.cookies_checkbox)
        
        self.passwords_checkbox = QCheckBox("Passwords")
        self.passwords_checkbox.setChecked(True)
        data_layout.addWidget(self.passwords_checkbox)
        
        self.extensions_checkbox = QCheckBox("Extensions")
        self.extensions_checkbox.setChecked(True)
        data_layout.addWidget(self.extensions_checkbox)
        
        self.preferences_checkbox = QCheckBox("Preferences")
        self.preferences_checkbox.setChecked(True)
        data_layout.addWidget(self.preferences_checkbox)
        
        layout.addWidget(data_group)
        
        # Create migration button
        migrate_button = QPushButton("Start Migration")
        migrate_button.clicked.connect(self._migrate_profile)
        layout.addWidget(migrate_button)
        
        # Create progress bar
        self.migration_progress = QProgressBar()
        self.migration_progress.setVisible(False)
        layout.addWidget(self.migration_progress)
        
        # Add tab
        self.tab_widget.addTab(migration_tab, "Migration")
    
    def _create_backup_tab(self) -> None:
        """Create the backup and restore tab."""
        backup_tab = QWidget()
        layout = QVBoxLayout(backup_tab)
        
        # Create header
        header_label = QLabel("Backup & Restore")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Create description
        description_label = QLabel(
            "Create backups of browser profiles and restore them when needed."
        )
        layout.addWidget(description_label)
        layout.addSpacing(10)
        
        # Create backup section
        backup_group = QGroupBox("Create Backup")
        backup_layout = QGridLayout(backup_group)
        
        # Browser selection
        backup_layout.addWidget(QLabel("Browser:"), 0, 0)
        self.backup_browser_combo = QComboBox()
        backup_layout.addWidget(self.backup_browser_combo, 0, 1)
        
        # Profile selection
        backup_layout.addWidget(QLabel("Profile:"), 1, 0)
        self.backup_profile_combo = QComboBox()
        backup_layout.addWidget(self.backup_profile_combo, 1, 1)
        
        # Backup location
        backup_layout.addWidget(QLabel("Backup Location:"), 2, 0)
        backup_location_layout = QHBoxLayout()
        self.backup_location_edit = QLineEdit()
        backup_location_layout.addWidget(self.backup_location_edit)
        backup_browse_button = QPushButton("Browse...")
        backup_browse_button.clicked.connect(self._browse_backup_location)
        backup_location_layout.addWidget(backup_browse_button)
        backup_layout.addLayout(backup_location_layout, 2, 1)
        
        # Create backup button
        backup_button = QPushButton("Create Backup")
        backup_button.clicked.connect(self._create_backup)
        backup_layout.addWidget(backup_button, 3, 1)
        
        layout.addWidget(backup_group)
        
        # Create restore section
        restore_group = QGroupBox("Restore Backup")
        restore_layout = QGridLayout(restore_group)
        
        # Backup file
        restore_layout.addWidget(QLabel("Backup File:"), 0, 0)
        restore_file_layout = QHBoxLayout()
        self.restore_file_edit = QLineEdit()
        restore_file_layout.addWidget(self.restore_file_edit)
        restore_browse_button = QPushButton("Browse...")
        restore_browse_button.clicked.connect(self._browse_restore_file)
        restore_file_layout.addWidget(restore_browse_button)
        restore_layout.addLayout(restore_file_layout, 0, 1)
        
        # Target browser
        restore_layout.addWidget(QLabel("Target Browser:"), 1, 0)
        self.restore_browser_combo = QComboBox()
        restore_layout.addWidget(self.restore_browser_combo, 1, 1)
        
        # Target profile
        restore_layout.addWidget(QLabel("Target Profile:"), 2, 0)
        self.restore_profile_combo = QComboBox()
        restore_layout.addWidget(self.restore_profile_combo, 2, 1)
        
        # Create restore button
        restore_button = QPushButton("Restore Backup")
        restore_button.clicked.connect(self._restore_backup)
        restore_layout.addWidget(restore_button, 3, 1)
        
        layout.addWidget(restore_group)
        
        # Connect browser selection to profile display
        self.backup_browser_combo.currentIndexChanged.connect(
            lambda: self._update_profiles(self.backup_browser_combo, self.backup_profile_combo)
        )
        self.restore_browser_combo.currentIndexChanged.connect(
            lambda: self._update_profiles(self.restore_browser_combo, self.restore_profile_combo)
        )
        
        # Add tab
        self.tab_widget.addTab(backup_tab, "Backup & Restore")
    
    def _create_settings_tab(self) -> None:
        """Create the settings tab."""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # Create header
        header_label = QLabel("Settings")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Create description
        description_label = QLabel(
            "Configure application settings and preferences."
        )
        layout.addWidget(description_label)
        layout.addSpacing(10)
        
        # Create settings group
        settings_group = QGroupBox("General Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Create settings options
        self.auto_detect_checkbox = QCheckBox("Auto-detect browsers on startup")
        settings_layout.addWidget(self.auto_detect_checkbox)
        
        self.create_backups_checkbox = QCheckBox("Create automatic backups before migration")
        self.create_backups_checkbox.setChecked(True)
        settings_layout.addWidget(self.create_backups_checkbox)
        
        self.show_welcome_checkbox = QCheckBox("Show welcome message on startup")
        self.show_welcome_checkbox.setChecked(True)
        settings_layout.addWidget(self.show_welcome_checkbox)
        
        layout.addWidget(settings_group)
        
        # Create about group
        about_group = QGroupBox("About Floorper")
        about_layout = QVBoxLayout(about_group)
        
        # Get app info
        app_info = get_app_info()
        
        # Create about text
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml(f"""
            <h2>Floorper {app_info['version']}</h2>
            <p>{app_info['description']}</p>
            <p>Author: {app_info['author']}</p>
            <p>License: {app_info['license']}</p>
            <p>Running on {app_info['platform']} with Python {app_info['python_version']}</p>
            <p>Floorper is a comprehensive browser profile migration and management tool
            that allows users to detect, backup, restore, and migrate profiles between
            different browsers.</p>
        """)
        about_layout.addWidget(about_text)
        
        layout.addWidget(about_group)
        
        # Create save button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self._save_settings)
        layout.addWidget(save_button)
        
        # Add tab
        self.tab_widget.addTab(settings_tab, "Settings")
    
    def _detect_browsers(self) -> None:
        """Detect installed browsers and their profiles."""
        self.status_bar.showMessage("Detecting browsers...")
        
        # Clear lists
        self.browsers_list.clear()
        self.profiles_list.clear()
        
        # Create worker thread
        worker = DetectionWorker(self.browser_detector)
        
        # Connect signals
        worker.finished.connect(self._detection_finished)
        worker.browser_detected.connect(self._add_browser)
        
        # Start worker
        worker.start()
    
    def _detection_finished(self) -> None:
        """Handle browser detection completion."""
        self.status_bar.showMessage("Browser detection completed")
        
        # Update browser combos
        self._update_browser_combos()
    
    def _add_browser(self, browser: Dict[str, Any]) -> None:
        """
        Add a detected browser to the list.
        
        Args:
            browser: Browser information
        """
        item = QListWidgetItem(browser["name"])
        item.setData(Qt.ItemDataRole.UserRole, browser)
        self.browsers_list.addItem(item)
    
    def _show_browser_profiles(self, item: QListWidgetItem) -> None:
        """
        Show profiles for the selected browser.
        
        Args:
            item: Selected browser item
        """
        browser = item.data(Qt.ItemDataRole.UserRole)
        
        # Clear profiles list
        self.profiles_list.clear()
        
        # Get profiles
        profiles = self.browser_detector.get_profiles(browser["id"])
        
        # Add profiles to list
        for profile in profiles:
            profile_item = QListWidgetItem(profile["name"])
            profile_item.setData(Qt.ItemDataRole.UserRole, profile)
            self.profiles_list.addItem(profile_item)
    
    def _update_browser_combos(self) -> None:
        """Update browser combo boxes with detected browsers."""
        # Get browsers
        browsers = []
        for i in range(self.browsers_list.count()):
            browsers.append(self.browsers_list.item(i).data(Qt.ItemDataRole.UserRole))
        
        # Update source browser combo
        self.source_browser_combo.clear()
        for browser in browsers:
            self.source_browser_combo.addItem(browser["name"], browser)
        
        # Update target browser combo
        self.target_browser_combo.clear()
        for browser in browsers:
            self.target_browser_combo.addItem(browser["name"], browser)
        
        # Update backup browser combo
        self.backup_browser_combo.clear()
        for browser in browsers:
            self.backup_browser_combo.addItem(browser["name"], browser)
        
        # Update restore browser combo
        self.restore_browser_combo.clear()
        for browser in browsers:
            self.restore_browser_combo.addItem(browser["name"], browser)
    
    def _update_profiles(self, browser_combo: QComboBox, profile_combo: QComboBox) -> None:
        """
        Update profile combo box based on selected browser.
        
        Args:
            browser_combo: Browser combo box
            profile_combo: Profile combo box to update
        """
        # Get selected browser
        browser = browser_combo.currentData()
        if not browser:
            return
        
        # Clear profile combo
        profile_combo.clear()
        
        # Get profiles
        profiles = self.browser_detector.get_profiles(browser["id"])
        
        # Add profiles to combo
        for profile in profiles:
            profile_combo.addItem(profile["name"], profile)
    
    def _migrate_profile(self) -> None:
        """Migrate a browser profile."""
        # Get source and target profiles
        source_browser = self.source_browser_combo.currentData()
        source_profile = self.source_profile_combo.currentData()
        target_browser = self.target_browser_combo.currentData()
        target_profile = self.target_profile_combo.currentData()
        
        if not source_browser or not source_profile or not target_browser or not target_profile:
            QMessageBox.warning(
                self,
                "Migration Error",
                "Please select source and target browsers and profiles"
            )
            return
        
        # Get data types to migrate
        data_types = []
        if self.bookmarks_checkbox.isChecked():
            data_types.append("bookmarks")
        if self.history_checkbox.isChecked():
            data_types.append("history")
        if self.cookies_checkbox.isChecked():
            data_types.append("cookies")
        if self.passwords_checkbox.isChecked():
            data_types.append("passwords")
        if self.extensions_checkbox.isChecked():
            data_types.append("extensions")
        if self.preferences_checkbox.isChecked():
            data_types.append("preferences")
        
        # Show progress bar
        self.migration_progress.setVisible(True)
        self.migration_progress.setValue(0)
        
        # Create worker thread
        worker = MigrationWorker(
            self.profile_migrator,
            source_profile,
            target_profile,
            data_types
        )
        
        # Connect signals
        worker.progress.connect(self.migration_progress.setValue)
        worker.finished.connect(self._migration_finished)
        
        # Start worker
        self.status_bar.showMessage("Migrating profile...")
        worker.start()
    
    def _migration_finished(self, success: bool) -> None:
        """
        Handle profile migration completion.
        
        Args:
            success: Whether migration was successful
        """
        # Hide progress bar
        self.migration_progress.setVisible(False)
        
        if success:
            self.status_bar.showMessage("Profile migration completed successfully")
            QMessageBox.information(
                self,
                "Migration Complete",
                "Profile migration completed successfully"
            )
        else:
            self.status_bar.showMessage("Profile migration failed")
            QMessageBox.critical(
                self,
                "Migration Error",
                "Profile migration failed. Please check the logs for details."
            )
    
    def _browse_backup_location(self) -> None:
        """Browse for backup location."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Location",
            os.path.expanduser("~")
        )
        
        if directory:
            self.backup_location_edit.setText(directory)
    
    def _browse_restore_file(self) -> None:
        """Browse for backup file to restore."""
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            os.path.expanduser("~"),
            "Backup Files (*.zip);;All Files (*)"
        )
        
        if file:
            self.restore_file_edit.setText(file)
    
    def _create_backup(self) -> None:
        """Create a backup of a browser profile."""
        # Get browser and profile
        browser = self.backup_browser_combo.currentData()
        profile = self.backup_profile_combo.currentData()
        location = self.backup_location_edit.text()
        
        if not browser or not profile:
            QMessageBox.warning(
                self,
                "Backup Error",
                "Please select a browser and profile to backup"
            )
            return
        
        if not location:
            QMessageBox.warning(
                self,
                "Backup Error",
                "Please select a backup location"
            )
            return
        
        # Create backup
        try:
            backup_file = self.backup_manager.create_backup(
                profile["path"],
                browser["id"],
                location
            )
            
            self.status_bar.showMessage(f"Backup created: {backup_file}")
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup created successfully:\n{backup_file}"
            )
        except Exception as e:
            logger.error(f"Backup error: {e}")
            self.status_bar.showMessage("Backup creation failed")
            QMessageBox.critical(
                self,
                "Backup Error",
                f"Failed to create backup: {e}"
            )
    
    def _restore_backup(self) -> None:
        """Restore a backup to a browser profile."""
        # Get backup file and target
        backup_file = self.restore_file_edit.text()
        browser = self.restore_browser_combo.currentData()
        profile = self.restore_profile_combo.currentData()
        
        if not backup_file:
            QMessageBox.warning(
                self,
                "Restore Error",
                "Please select a backup file to restore"
            )
            return
        
        if not browser or not profile:
            QMessageBox.warning(
                self,
                "Restore Error",
                "Please select a target browser and profile"
            )
            return
        
        # Confirm restoration
        confirm = QMessageBox.question(
            self,
            "Confirm Restoration",
            f"Are you sure you want to restore this backup to {profile['name']}?\n"
            "This will overwrite the existing profile data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Restore backup
        try:
            self.backup_manager.restore_backup(
                backup_file,
                profile["path"]
            )
            
            self.status_bar.showMessage("Backup restored successfully")
            QMessageBox.information(
                self,
                "Backup Restored",
                "Backup restored successfully"
            )
        except Exception as e:
            logger.error(f"Restore error: {e}")
            self.status_bar.showMessage("Backup restoration failed")
            QMessageBox.critical(
                self,
                "Restore Error",
                f"Failed to restore backup: {e}"
            )
    
    def _load_settings(self) -> None:
        """Load application settings."""
        settings = QSettings("Floorper", "Floorper")
        
        # Load general settings
        self.auto_detect_checkbox.setChecked(
            settings.value("auto_detect", False, bool)
        )
        self.create_backups_checkbox.setChecked(
            settings.value("create_backups", True, bool)
        )
        self.show_welcome_checkbox.setChecked(
            settings.value("show_welcome", True, bool)
        )
        
        # Auto-detect browsers if enabled
        if self.auto_detect_checkbox.isChecked():
            self._detect_browsers()
    
    def _save_settings(self) -> None:
        """Save application settings."""
        settings = QSettings("Floorper", "Floorper")
        
        # Save general settings
        settings.setValue("auto_detect", self.auto_detect_checkbox.isChecked())
        settings.setValue("create_backups", self.create_backups_checkbox.isChecked())
        settings.setValue("show_welcome", self.show_welcome_checkbox.isChecked())
        
        # Show confirmation
        self.status_bar.showMessage("Settings saved")
    
    def _show_welcome_message(self) -> None:
        """Show welcome message if enabled."""
        settings = QSettings("Floorper", "Floorper")
        
        if settings.value("show_welcome", True, bool):
            QMessageBox.information(
                self,
                "Welcome to Floorper",
                "Welcome to Floorper, the Universal Browser Profile Migration Tool!\n\n"
                "This application allows you to detect, backup, restore, and migrate "
                "profiles between different browsers.\n\n"
                "To get started, go to the Detection tab and click 'Detect Browsers' "
                "to find installed browsers on your system."
            )


class DetectionWorker(QThread):
    """Worker thread for browser detection."""
    
    # Signals
    browser_detected = pyqtSignal(dict)
    finished = pyqtSignal()
    
    def __init__(self, detector: BrowserDetector):
        """
        Initialize the worker.
        
        Args:
            detector: Browser detector instance
        """
        super().__init__()
        self.detector = detector
    
    def run(self) -> None:
        """Run the worker."""
        try:
            # Detect browsers
            browsers = self.detector.detect_browsers()
            
            # Emit signals
            for browser in browsers:
                self.browser_detected.emit(browser)
            
            self.finished.emit()
        except Exception as e:
            logger.error(f"Detection error: {e}")
            self.finished.emit()


class MigrationWorker(QThread):
    """Worker thread for profile migration."""
    
    # Signals
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)
    
    def __init__(
        self,
        migrator: ProfileMigrator,
        source_profile: Dict[str, Any],
        target_profile: Dict[str, Any],
        data_types: List[str]
    ):
        """
        Initialize the worker.
        
        Args:
            migrator: Profile migrator instance
            source_profile: Source profile information
            target_profile: Target profile information
            data_types: Data types to migrate
        """
        super().__init__()
        self.migrator = migrator
        self.source_profile = source_profile
        self.target_profile = target_profile
        self.data_types = data_types
    
    def run(self) -> None:
        """Run the worker."""
        try:
            # Set up progress reporting
            total_steps = len(self.data_types)
            current_step = 0
            
            def progress_callback(step: int, message: str) -> None:
                """
                Progress callback function.
                
                Args:
                    step: Current step (0-100)
                    message: Progress message
                """
                nonlocal current_step
                progress = int((current_step * 100 + step) / total_steps)
                self.progress.emit(progress)
            
            # Migrate profile
            result = self.migrator.migrate_profile(
                self.source_profile,
                self.target_profile,
                self.data_types,
                {"progress_callback": progress_callback}
            )
            
            # Emit finished signal
            self.finished.emit(result.get("success", False))
        except Exception as e:
            logger.error(f"Migration error: {e}")
            self.finished.emit(False)
