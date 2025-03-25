#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - PyQt6 GUI Interface
=============================

A modern graphical user interface for Floorper using PyQt6.
Provides a user-friendly interface for browser profile detection and migration.
"""

import os
import sys
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Union, Set

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QListWidget, QListWidgetItem, QCheckBox,
    QComboBox, QProgressBar, QMessageBox, QTabWidget, QSplitter,
    QFrame, QScrollArea, QGroupBox, QGridLayout, QFileDialog,
    QDialog, QDialogButtonBox, QLineEdit, QTextEdit, QSpacerItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QPalette

from ..core.constants import BROWSERS, DATA_TYPES
from ..core.browser_detector import BrowserDetector
from ..core.profile_migrator import ProfileMigrator
from ..core.backup_manager import BackupManager

logger = logging.getLogger(__name__)

class ProfileDetectionThread(QThread):
    """Thread for detecting browser profiles."""
    
    finished = pyqtSignal(list)
    
    def run(self):
        """Run the thread."""
        try:
            detector = BrowserDetector()
            profiles = detector.detect_all_profiles()
            self.finished.emit(profiles)
        except Exception as e:
            logger.error(f"Error detecting profiles: {str(e)}")
            self.finished.emit([])


class MigrationThread(QThread):
    """Thread for migrating browser profiles."""
    
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list)
    
    def __init__(self, source_profiles, target_profile, data_types, options=None):
        super().__init__()
        self.source_profiles = source_profiles
        self.target_profile = target_profile
        self.data_types = data_types
        self.options = options or {}
        self.migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
    
    def run(self):
        """Run the thread."""
        try:
            results = []
            
            # Create backup of target profile
            self.progress.emit("Creating backup of target profile...", 0)
            backup_path = self.backup_manager.create_backup(
                self.target_profile["path"],
                self.target_profile["browser_id"],
                self.target_profile["name"]
            )
            
            if not backup_path:
                self.progress.emit("Warning: Failed to create backup, continuing without backup", 5)
            else:
                self.progress.emit(f"Backup created: {backup_path}", 10)
            
            # Calculate progress steps
            total_profiles = len(self.source_profiles)
            progress_per_profile = 90 / total_profiles if total_profiles > 0 else 90
            
            # Migrate each source profile
            for i, source_profile in enumerate(self.source_profiles):
                source_browser = BROWSERS.get(source_profile["browser_id"], {}).get("name", "Unknown Browser")
                target_browser = BROWSERS.get(self.target_profile["browser_id"], {}).get("name", "Unknown Browser")
                
                self.progress.emit(
                    f"Migrating from {source_browser} to {target_browser} ({i+1}/{total_profiles})",
                    10 + int(i * progress_per_profile)
                )
                
                # Perform migration
                result = self.migrator.migrate_profile(
                    source_profile,
                    self.target_profile,
                    self.data_types,
                    {"backup": False}  # We already created a backup
                )
                
                results.append(result)
                
                # Update progress
                if result["success"]:
                    migrated_items = sum(
                        result["migrated_data"].get(dt, {}).get("migrated_items", 0)
                        for dt in self.data_types
                    )
                    self.progress.emit(
                        f"Successfully migrated {migrated_items} items",
                        10 + int((i + 1) * progress_per_profile)
                    )
                else:
                    errors = result.get("errors", [])
                    error_msg = errors[0] if errors else "Unknown error"
                    self.progress.emit(
                        f"Migration completed with errors: {error_msg}",
                        10 + int((i + 1) * progress_per_profile)
                    )
            
            self.progress.emit("Migration complete!", 100)
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            self.progress.emit(f"Error: {str(e)}", 100)
            self.finished.emit([])


class ProfileListItem(QListWidgetItem):
    """Custom list widget item for browser profiles."""
    
    def __init__(self, profile):
        browser_name = BROWSERS.get(profile["browser_id"], {}).get("name", "Unknown Browser")
        super().__init__(f"{browser_name} - {profile['name']}")
        self.profile = profile
        self.setToolTip(f"Path: {profile['path']}")


class BackupRestoreDialog(QDialog):
    """Dialog for restoring backups."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Restore Backup")
        self.setMinimumWidth(500)
        self.backup_manager = BackupManager()
        self.backups = []
        self.selected_backup = None
        
        self.init_ui()
        self.load_backups()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Backup list
        self.backup_list = QListWidget()
        self.backup_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.backup_list.itemSelectionChanged.connect(self.on_backup_selected)
        layout.addWidget(QLabel("Available Backups:"))
        layout.addWidget(self.backup_list)
        
        # Backup details
        self.details_group = QGroupBox("Backup Details")
        details_layout = QGridLayout()
        
        self.browser_label = QLabel("Browser: ")
        self.profile_label = QLabel("Profile: ")
        self.date_label = QLabel("Date: ")
        self.files_label = QLabel("Files: ")
        self.size_label = QLabel("Size: ")
        
        details_layout.addWidget(QLabel("Browser:"), 0, 0)
        details_layout.addWidget(self.browser_label, 0, 1)
        details_layout.addWidget(QLabel("Profile:"), 1, 0)
        details_layout.addWidget(self.profile_label, 1, 1)
        details_layout.addWidget(QLabel("Date:"), 2, 0)
        details_layout.addWidget(self.date_label, 2, 1)
        details_layout.addWidget(QLabel("Files:"), 3, 0)
        details_layout.addWidget(self.files_label, 3, 1)
        details_layout.addWidget(QLabel("Size:"), 4, 0)
        details_layout.addWidget(self.size_label, 4, 1)
        
        self.details_group.setLayout(details_layout)
        layout.addWidget(self.details_group)
        
        # Target directory
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Restore to:"))
        self.target_path = QLineEdit()
        target_layout.addWidget(self.target_path)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_target)
        target_layout.addWidget(self.browse_button)
        layout.addLayout(target_layout)
        
        # Options
        self.merge_checkbox = QCheckBox("Merge with existing files")
        layout.addWidget(self.merge_checkbox)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_backups(self):
        """Load available backups."""
        self.backups = self.backup_manager.list_backups()
        self.backup_list.clear()
        
        for backup in self.backups:
            browser_id = backup.get("browser_id", "")
            browser_name = BROWSERS.get(browser_id, {}).get("name", "Unknown Browser")
            profile_name = backup.get("profile_name", "")
            created_at = backup.get("created_at", "")
            
            item = QListWidgetItem(f"{browser_name} - {profile_name} ({created_at})")
            item.setData(Qt.ItemDataRole.UserRole, backup)
            self.backup_list.addItem(item)
    
    def on_backup_selected(self):
        """Handle backup selection."""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return
        
        backup = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.selected_backup = backup
        
        # Update details
        browser_id = backup.get("browser_id", "")
        browser_name = BROWSERS.get(browser_id, {}).get("name", "Unknown Browser")
        self.browser_label.setText(browser_name)
        self.profile_label.setText(backup.get("profile_name", ""))
        self.date_label.setText(backup.get("created_at", ""))
        
        summary = backup.get("summary", {})
        self.files_label.setText(str(summary.get("file_count", 0)))
        
        size = summary.get("total_size", 0)
        size_str = f"{size / 1024 / 1024:.2f} MB" if size else "Unknown"
        self.size_label.setText(size_str)
        
        # Set default target path
        self.target_path.setText(backup.get("source_path", ""))
    
    def browse_target(self):
        """Browse for target directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Target Directory", self.target_path.text()
        )
        if directory:
            self.target_path.setText(directory)
    
    def get_restore_options(self):
        """Get the restore options."""
        if not self.selected_backup:
            return None
        
        return {
            "backup_path": self.selected_backup.get("path", ""),
            "target_path": self.target_path.text(),
            "merge": self.merge_checkbox.isChecked()
        }


class FloorperMainWindow(QMainWindow):
    """Main window for the Floorper GUI application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Floorper - Browser Profile Migration Tool")
        self.setMinimumSize(800, 600)
        
        self.detector = BrowserDetector()
        self.migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
        
        self.profiles = []
        self.selected_source_profiles = []
        self.selected_target_profile = None
        self.selected_data_types = set(DATA_TYPES.keys())
        
        self.init_ui()
        self.detect_profiles()
    
    def init_ui(self):
        """Initialize the UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Profiles tab
        profiles_tab = QWidget()
        profiles_layout = QVBoxLayout(profiles_tab)
        
        # Status label
        self.status_label = QLabel("Detecting browser profiles...")
        profiles_layout.addWidget(self.status_label)
        
        # Profiles list
        profiles_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Source profiles
        source_widget = QWidget()
        source_layout = QVBoxLayout(source_widget)
        source_layout.addWidget(QLabel("Available Profiles (select source):"))
        
        self.profiles_list = QListWidget()
        self.profiles_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.profiles_list.itemSelectionChanged.connect(self.on_source_selection_changed)
        source_layout.addWidget(self.profiles_list)
        
        refresh_button = QPushButton("Refresh Profiles")
        refresh_button.clicked.connect(self.detect_profiles)
        source_layout.addWidget(refresh_button)
        
        profiles_splitter.addWidget(source_widget)
        
        # Target profile
        target_widget = QWidget()
        target_layout = QVBoxLayout(target_widget)
        target_layout.addWidget(QLabel("Target Profile:"))
        
        self.target_combo = QComboBox()
        self.target_combo.currentIndexChanged.connect(self.on_target_selection_changed)
        target_layout.addWidget(self.target_combo)
        
        # Data types
        data_types_group = QGroupBox("Data Types to Migrate:")
        data_types_layout = QVBoxLayout()
        
        self.data_type_checkboxes = {}
        for data_type, info in DATA_TYPES.items():
            checkbox = QCheckBox(info.get("name", data_type))
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_data_type_changed)
            self.data_type_checkboxes[data_type] = checkbox
            data_types_layout.addWidget(checkbox)
        
        data_types_group.setLayout(data_types_layout)
        target_layout.addWidget(data_types_group)
        
        # Migration options
        options_group = QGroupBox("Migration Options:")
        options_layout = QVBoxLayout()
        
        self.backup_checkbox = QCheckBox("Create backup before migration")
        self.backup_checkbox.setChecked(True)
        options_layout.addWidget(self.backup_checkbox)
        
        self.deduplicate_checkbox = QCheckBox("Deduplicate items")
        self.deduplicate_checkbox.setChecked(True)
        options_layout.addWidget(self.deduplicate_checkbox)
        
        options_group.setLayout(options_layout)
        target_layout.addWidget(options_group)
        
        # Migrate button
        self.migrate_button = QPushButton("Migrate Profiles")
        self.migrate_button.clicked.connect(self.start_migration)
        self.migrate_button.setEnabled(False)
        target_layout.addWidget(self.migrate_button)
        
        profiles_splitter.addWidget(target_widget)
        profiles_layout.addWidget(profiles_splitter)
        
        self.tab_widget.addTab(profiles_tab, "Profile Migration")
        
        # Backup tab
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        
        backup_label = QLabel("Manage browser profile backups")
        backup_layout.addWidget(backup_label)
        
        backup_buttons_layout = QHBoxLayout()
        
        create_backup_button = QPushButton("Create Backup")
        create_backup_button.clicked.connect(self.create_backup)
        backup_buttons_layout.addWidget(create_backup_button)
        
        restore_backup_button = QPushButton("Restore Backup")
        restore_backup_button.clicked.connect(self.restore_backup)
        backup_buttons_layout.addWidget(restore_backup_button)
        
        backup_layout.addLayout(backup_buttons_layout)
        
        # Backup list
        backup_layout.addWidget(QLabel("Available Backups:"))
        self.backup_list = QListWidget()
        backup_layout.addWidget(self.backup_list)
        
        refresh_backups_button = QPushButton("Refresh Backups")
        refresh_backups_button.clicked.connect(self.refresh_backups)
        backup_layout.addWidget(refresh_backups_button)
        
        self.tab_widget.addTab(backup_tab, "Backups")
        
        # Progress tab (initially hidden)
        self.progress_tab = QWidget()
        progress_layout = QVBoxLayout(self.progress_tab)
        
        self.progress_label = QLabel("Migration in progress...")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_details = QTextEdit()
        self.progress_details.setReadOnly(True)
        progress_layout.addWidget(self.progress_details)
        
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.on_migration_done)
        self.done_button.setEnabled(False)
        progress_layout.addWidget(self.done_button)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def detect_profiles(self):
        """Detect browser profiles."""
        self.status_label.setText("Detecting browser profiles...")
        self.statusBar().showMessage("Detecting browser profiles...")
        self.profiles_list.clear()
        self.target_combo.clear()
        
        # Start detection thread
        self.detection_thread = ProfileDetectionThread()
        self.detection_thread.finished.connect(self.on_profiles_detected)
        self.detection_thread.start()
    
    def on_profiles_detected(self, profiles):
        """Handle detected profiles."""
        self.profiles = profiles
        
        if not profiles:
            self.status_label.setText("No browser profiles found.")
            self.statusBar().showMessage("No browser profiles found.")
            return
        
        # Add profiles to list
        for profile in profiles:
            self.profiles_list.addItem(ProfileListItem(profile))
        
        # Add profiles to target combo
        for i, profile in enumerate(profiles):
            browser_name = BROWSERS.get(profile["browser_id"], {}).get("name", "Unknown Browser")
            self.target_combo.addItem(f"{browser_name} - {profile['name']}", i)
        
        self.status_label.setText(f"Found {len(profiles)} browser profiles.")
        self.statusBar().showMessage(f"Found {len(profiles)} browser profiles.")
    
    def on_source_selection_changed(self):
        """Handle source profile selection changes."""
        self.selected_source_profiles = []
        
        for item in self.profiles_list.selectedItems():
            if isinstance(item, ProfileListItem):
                self.selected_source_profiles.append(item.profile)
        
        # Update target combo by removing selected source profiles
        self.update_target_combo()
        
        # Update migrate button state
        self.update_migrate_button()
    
    def update_target_combo(self):
        """Update target combo box to exclude selected source profiles."""
        current_index = self.target_combo.currentIndex()
        current_data = self.target_combo.currentData() if current_index >= 0 else None
        
        self.target_combo.clear()
        
        source_paths = [p["path"] for p in self.selected_source_profiles]
        
        for i, profile in enumerate(self.profiles):
            if profile["path"] not in source_paths:
                browser_name = BROWSERS.get(profile["browser_id"], {}).get("name", "Unknown Browser")
                self.target_combo.addItem(f"{browser_name} - {profile['name']}", i)
        
        # Try to restore previous selection
        if current_data is not None:
            index = self.target_combo.findData(current_data)
            if index >= 0:
                self.target_combo.setCurrentIndex(index)
    
    def on_target_selection_changed(self, index):
        """Handle target profile selection changes."""
        if index < 0:
            self.selected_target_profile = None
        else:
            profile_index = self.target_combo.currentData()
            if profile_index is not None and 0 <= profile_index < len(self.profiles):
                self.selected_target_profile = self.profiles[profile_index]
            else:
                self.selected_target_profile = None
        
        # Update migrate button state
        self.update_migrate_button()
    
    def on_data_type_changed(self, state):
        """Handle data type checkbox changes."""
        sender = self.sender()
        
        for data_type, checkbox in self.data_type_checkboxes.items():
            if checkbox == sender:
                if state == Qt.CheckState.Checked.value:
                    self.selected_data_types.add(data_type)
                else:
                    self.selected_data_types.discard(data_type)
                break
        
        # Update migrate button state
        self.update_migrate_button()
    
    def update_migrate_button(self):
        """Update the state of the migrate button."""
        enabled = (
            len(self.selected_source_profiles) > 0 and
            self.selected_target_profile is not None and
            len(self.selected_data_types) > 0
        )
        self.migrate_button.setEnabled(enabled)
    
    def start_migration(self):
        """Start the migration process."""
        # Show progress tab
        if self.tab_widget.count() <= 2:
            self.tab_widget.addTab(self.progress_tab, "Progress")
        self.tab_widget.setCurrentWidget(self.progress_tab)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_details.clear()
        self.done_button.setEnabled(False)
        
        # Get migration options
        options = {
            "backup": self.backup_checkbox.isChecked(),
            "deduplicate": self.deduplicate_checkbox.isChecked(),
            "merge_strategy": "smart"
        }
        
        # Start migration thread
        self.migration_thread = MigrationThread(
            self.selected_source_profiles,
            self.selected_target_profile,
            list(self.selected_data_types),
            options
        )
        self.migration_thread.progress.connect(self.update_migration_progress)
        self.migration_thread.finished.connect(self.on_migration_finished)
        self.migration_thread.start()
    
    def update_migration_progress(self, message, progress):
        """Update migration progress."""
        self.progress_label.setText(message)
        self.progress_bar.setValue(progress)
        self.progress_details.append(message)
        self.statusBar().showMessage(message)
    
    def on_migration_finished(self, results):
        """Handle migration completion."""
        self.progress_label.setText("Migration complete!")
        self.done_button.setEnabled(True)
        
        # Analyze results
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)
        
        if success_count == total_count:
            self.progress_details.append("\nAll migrations completed successfully!")
        else:
            self.progress_details.append(f"\n{success_count} of {total_count} migrations completed successfully.")
            
            # Show errors
            self.progress_details.append("\nErrors:")
            for i, result in enumerate(results):
                if not result.get("success", False):
                    errors = result.get("errors", [])
                    source_profile = result.get("source_profile", {})
                    browser_name = BROWSERS.get(source_profile.get("browser_id", ""), {}).get("name", "Unknown Browser")
                    profile_name = source_profile.get("name", "")
                    
                    for error in errors:
                        self.progress_details.append(f"- {browser_name} - {profile_name}: {error}")
        
        self.statusBar().showMessage("Migration complete!")
    
    def on_migration_done(self):
        """Handle done button click after migration."""
        # Switch back to profiles tab
        self.tab_widget.setCurrentIndex(0)
        
        # Remove progress tab
        self.tab_widget.removeTab(self.tab_widget.indexOf(self.progress_tab))
    
    def refresh_backups(self):
        """Refresh the backup list."""
        self.backup_list.clear()
        
        backups = self.backup_manager.list_backups()
        
        for backup in backups:
            browser_id = backup.get("browser_id", "")
            browser_name = BROWSERS.get(browser_id, {}).get("name", "Unknown Browser")
            profile_name = backup.get("profile_name", "")
            created_at = backup.get("created_at", "")
            
            item = QListWidgetItem(f"{browser_name} - {profile_name} ({created_at})")
            item.setData(Qt.ItemDataRole.UserRole, backup)
            self.backup_list.addItem(item)
        
        self.statusBar().showMessage(f"Found {len(backups)} backups.")
    
    def create_backup(self):
        """Create a backup of a browser profile."""
        # Show profile selection dialog
        if not self.profiles:
            QMessageBox.warning(
                self, "No Profiles", "No browser profiles found to backup."
            )
            return
        
        profile_index, ok = QInputDialog.getItem(
            self, "Select Profile", "Profile to backup:",
            [f"{BROWSERS.get(p['browser_id'], {}).get('name', 'Unknown')} - {p['name']}" for p in self.profiles],
            0, False
        )
        
        if not ok:
            return
        
        # Find selected profile
        selected_index = -1
        for i, profile in enumerate(self.profiles):
            browser_name = BROWSERS.get(profile["browser_id"], {}).get("name", "Unknown Browser")
            if f"{browser_name} - {profile['name']}" == profile_index:
                selected_index = i
                break
        
        if selected_index < 0:
            return
        
        profile = self.profiles[selected_index]
        
        # Create backup
        self.statusBar().showMessage(f"Creating backup of {profile['name']}...")
        
        backup_path = self.backup_manager.create_backup(
            profile["path"],
            profile["browser_id"],
            profile["name"]
        )
        
        if backup_path:
            QMessageBox.information(
                self, "Backup Created", f"Backup created successfully at:\n{backup_path}"
            )
            self.refresh_backups()
        else:
            QMessageBox.warning(
                self, "Backup Failed", "Failed to create backup."
            )
    
    def restore_backup(self):
        """Restore a backup."""
        dialog = BackupRestoreDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            options = dialog.get_restore_options()
            if not options:
                return
            
            # Verify options
            if not options["backup_path"] or not options["target_path"]:
                QMessageBox.warning(
                    self, "Invalid Options", "Backup path and target path are required."
                )
                return
            
            # Restore backup
            self.statusBar().showMessage("Restoring backup...")
            
            success = self.backup_manager.restore_backup(
                options["backup_path"],
                options["target_path"],
                options["merge"]
            )
            
            if success:
                QMessageBox.information(
                    self, "Restore Complete", "Backup restored successfully."
                )
            else:
                QMessageBox.warning(
                    self, "Restore Failed", "Failed to restore backup."
                )


class FloorperGUI:
    """Main Floorper GUI application."""
    
    def __init__(self):
        """Initialize the GUI application."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("floorper.log")
            ]
        )
    
    def run(self):
        """Run the GUI application."""
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle("Fusion")
        
        # Create and show main window
        window = FloorperMainWindow()
        window.show()
        
        return app.exec()


def main():
    """Run the Floorper GUI application."""
    gui = FloorperGUI()
    return gui.run()


if __name__ == "__main__":
    sys.exit(main())
