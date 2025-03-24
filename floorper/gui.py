"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides the GUI interface for the Floorper application,
implemented using PyQt6 for a modern, responsive user experience.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any, Tuple

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QCheckBox, QProgressBar,
    QTabWidget, QScrollArea, QFrame, QSplitter, QMessageBox,
    QFileDialog, QGroupBox, QRadioButton, QButtonGroup, QToolBar,
    QStatusBar, QDialog, QListWidget, QListWidgetItem, QTextEdit,
    QLineEdit, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QIcon, QPixmap, QFont, QAction, QColor, QPalette

from floorper.core import FloorperCore

# Setup logging
logger = logging.getLogger('floorper.gui')

class FloorperGUI(QMainWindow):
    """
    Main GUI window for the Floorper application.
    
    This class provides a modern, responsive user interface for
    browser profile migration using PyQt6.
    """
    
    def __init__(self, controller: Optional[FloorperCore] = None):
        """
        Initialize the GUI.
        
        Args:
            controller: Optional FloorperCore controller instance
        """
        super().__init__()
        
        self.controller = controller or FloorperCore()
        self.settings = QSettings("Floorper", "FloorperApp")
        
        self._init_ui()
        self._load_settings()
        self._connect_signals()
        
        logger.info("GUI initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Floorper - Universal Browser Profile Migration Tool for Floorp")
        self.setMinimumSize(900, 600)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Add toolbar actions
        self.action_detect = QAction("Detect Browsers", self)
        self.action_settings = QAction("Settings", self)
        self.action_about = QAction("About", self)
        
        self.toolbar.addAction(self.action_detect)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.action_settings)
        self.toolbar.addAction(self.action_about)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.main_splitter)
        
        # Create browser panel
        self.browser_panel = BrowserPanel(self.controller)
        self.main_splitter.addWidget(self.browser_panel)
        
        # Create options panel
        self.options_panel = OptionsPanel()
        self.main_splitter.addWidget(self.options_panel)
        
        # Set splitter sizes
        self.main_splitter.setSizes([400, 500])
        
        # Create bottom panel
        self.bottom_panel = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_panel)
        self.main_layout.addWidget(self.bottom_panel)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.bottom_layout.addWidget(self.progress_bar)
        
        # Create action buttons
        self.button_layout = QHBoxLayout()
        self.bottom_layout.addLayout(self.button_layout)
        
        self.button_layout.addStretch()
        
        self.button_migrate = QPushButton("Migrate Profiles")
        self.button_migrate.setEnabled(False)
        self.button_layout.addWidget(self.button_migrate)
        
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.setVisible(False)
        self.button_layout.addWidget(self.button_cancel)
    
    def _load_settings(self):
        """Load application settings."""
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Restore window state
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def _save_settings(self):
        """Save application settings."""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Save window state
        self.settings.setValue("windowState", self.saveState())
    
    def _connect_signals(self):
        """Connect signals to slots."""
        # Toolbar actions
        self.action_detect.triggered.connect(self.detect_browsers)
        self.action_settings.triggered.connect(self.show_settings_dialog)
        self.action_about.triggered.connect(self.show_about_dialog)
        
        # Browser panel signals
        self.browser_panel.source_selected.connect(self.update_migrate_button)
        self.browser_panel.target_selected.connect(self.update_migrate_button)
        
        # Action buttons
        self.button_migrate.clicked.connect(self.start_migration)
        self.button_cancel.clicked.connect(self.cancel_migration)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self._save_settings()
        event.accept()
    
    def detect_browsers(self):
        """Detect installed browsers."""
        self.status_bar.showMessage("Detecting browsers...")
        
        # Start detection in a separate thread
        self.detection_thread = BrowserDetectionThread(self.controller)
        self.detection_thread.detection_complete.connect(self.on_detection_complete)
        self.detection_thread.start()
    
    def on_detection_complete(self, browsers):
        """
        Handle browser detection completion.
        
        Args:
            browsers: List of detected browsers
        """
        self.browser_panel.update_browsers(browsers)
        self.status_bar.showMessage(f"Detected {len(browsers)} browsers")
    
    def update_migrate_button(self):
        """Update the migrate button state."""
        source_profile = self.browser_panel.get_selected_source_profile()
        target_profile = self.browser_panel.get_selected_target_profile()
        
        self.button_migrate.setEnabled(source_profile is not None and target_profile is not None)
    
    def start_migration(self):
        """Start the migration process."""
        source_profile = self.browser_panel.get_selected_source_profile()
        target_profile = self.browser_panel.get_selected_target_profile()
        data_types = self.options_panel.get_selected_data_types()
        options = self.options_panel.get_options()
        
        if not source_profile or not target_profile:
            QMessageBox.warning(
                self,
                "Migration Error",
                "Please select both source and target profiles."
            )
            return
        
        # Update UI for migration
        self.button_migrate.setEnabled(False)
        self.button_cancel.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Migration in progress...")
        
        # Start migration in a separate thread
        self.migration_thread = MigrationThread(
            self.controller,
            source_profile,
            target_profile,
            data_types,
            options
        )
        self.migration_thread.progress_update.connect(self.update_progress)
        self.migration_thread.migration_complete.connect(self.on_migration_complete)
        self.migration_thread.start()
    
    def cancel_migration(self):
        """Cancel the migration process."""
        if hasattr(self, 'migration_thread') and self.migration_thread.isRunning():
            # Implement cancellation logic
            self.migration_thread.requestInterruption()
            self.status_bar.showMessage("Cancelling migration...")
    
    def update_progress(self, progress, message):
        """
        Update the progress bar and status message.
        
        Args:
            progress: Progress percentage (0-100)
            message: Status message
        """
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(message)
    
    def on_migration_complete(self, result):
        """
        Handle migration completion.
        
        Args:
            result: Migration result
        """
        # Reset UI after migration
        self.button_migrate.setEnabled(True)
        self.button_cancel.setVisible(False)
        self.progress_bar.setVisible(False)
        
        # Show result message
        if result.get("success", False):
            self.status_bar.showMessage("Migration completed successfully")
            QMessageBox.information(
                self,
                "Migration Complete",
                "Profile migration completed successfully."
            )
        else:
            self.status_bar.showMessage("Migration completed with errors")
            QMessageBox.warning(
                self,
                "Migration Issues",
                f"Profile migration completed with issues: {result.get('message', '')}"
            )
        
        # Show detailed results dialog
        self.show_results_dialog(result)
    
    def show_settings_dialog(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Floorper",
            "Floorper - Universal Browser Profile Migration Tool for Floorp\n\n"
            "Version: 1.0.0\n\n"
            "A tool for migrating browser profiles to Floorp."
        )
    
    def show_results_dialog(self, result):
        """
        Show the migration results dialog.
        
        Args:
            result: Migration result
        """
        dialog = ResultsDialog(result, self)
        dialog.exec()


class BrowserPanel(QWidget):
    """
    Panel for browser and profile selection.
    
    This panel allows users to select source and target browsers
    and profiles for migration.
    """
    
    # Custom signals
    source_selected = pyqtSignal()
    target_selected = pyqtSignal()
    
    def __init__(self, controller):
        """
        Initialize the browser panel.
        
        Args:
            controller: FloorperCore controller instance
        """
        super().__init__()
        
        self.controller = controller
        self.source_browsers = []
        self.target_browsers = []
        self.source_profiles = {}
        self.target_profiles = {}
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create source group
        self.source_group = QGroupBox("Source Browser")
        self.source_layout = QVBoxLayout(self.source_group)
        
        self.source_browser_combo = QComboBox()
        self.source_layout.addWidget(QLabel("Select Browser:"))
        self.source_layout.addWidget(self.source_browser_combo)
        
        self.source_profile_list = QListWidget()
        self.source_layout.addWidget(QLabel("Select Profile:"))
        self.source_layout.addWidget(self.source_profile_list)
        
        self.layout.addWidget(self.source_group)
        
        # Create target group
        self.target_group = QGroupBox("Target Browser (Floorp)")
        self.target_layout = QVBoxLayout(self.target_group)
        
        self.target_profile_list = QListWidget()
        self.target_layout.addWidget(QLabel("Select Floorp Profile:"))
        self.target_layout.addWidget(self.target_profile_list)
        
        self.layout.addWidget(self.target_group)
        
        # Connect signals
        self.source_browser_combo.currentIndexChanged.connect(self.on_source_browser_changed)
        self.source_profile_list.itemSelectionChanged.connect(self.on_source_profile_changed)
        self.target_profile_list.itemSelectionChanged.connect(self.on_target_profile_changed)
    
    def update_browsers(self, browsers):
        """
        Update the browser lists.
        
        Args:
            browsers: List of detected browsers
        """
        self.source_browsers = browsers
        
        # Update source browser combo
        self.source_browser_combo.clear()
        for browser in browsers:
            if browser.get("id") != "floorp":  # Exclude Floorp from source
                self.source_browser_combo.addItem(browser.get("name"), browser.get("id"))
        
        # Find Floorp browser
        floorp_browser = next((b for b in browsers if b.get("id") == "floorp"), None)
        if floorp_browser:
            self.update_target_profiles(floorp_browser.get("id"))
    
    def on_source_browser_changed(self, index):
        """
        Handle source browser selection change.
        
        Args:
            index: Selected index
        """
        if index < 0:
            return
        
        browser_id = self.source_browser_combo.currentData()
        self.update_source_profiles(browser_id)
    
    def update_source_profiles(self, browser_id):
        """
        Update the source profile list.
        
        Args:
            browser_id: Browser identifier
        """
        self.source_profile_list.clear()
        
        # Get profiles for the selected browser
        profiles = self.controller.get_browser_profiles(browser_id)
        self.source_profiles[browser_id] = profiles
        
        # Update profile list
        for profile in profiles:
            item = QListWidgetItem(profile.get("name", "Unknown Profile"))
            item.setData(Qt.ItemDataRole.UserRole, profile)
            self.source_profile_list.addItem(item)
    
    def update_target_profiles(self, browser_id):
        """
        Update the target profile list.
        
        Args:
            browser_id: Browser identifier (should be "floorp")
        """
        self.target_profile_list.clear()
        
        # Get profiles for Floorp
        profiles = self.controller.get_browser_profiles(browser_id)
        self.target_profiles[browser_id] = profiles
        
        # Update profile list
        for profile in profiles:
            item = QListWidgetItem(profile.get("name", "Unknown Profile"))
            item.setData(Qt.ItemDataRole.UserRole, profile)
            self.target_profile_list.addItem(item)
    
    def on_source_profile_changed(self):
        """Handle source profile selection change."""
        self.source_selected.emit()
    
    def on_target_profile_changed(self):
        """Handle target profile selection change."""
        self.target_selected.emit()
    
    def get_selected_source_profile(self):
        """
        Get the selected source profile.
        
        Returns:
            Selected source profile or None
        """
        items = self.source_profile_list.selectedItems()
        if not items:
            return None
        
        return items[0].data(Qt.ItemDataRole.UserRole)
    
    def get_selected_target_profile(self):
        """
        Get the selected target profile.
        
        Returns:
            Selected target profile or None
        """
        items = self.target_profile_list.selectedItems()
        if not items:
            return None
        
        return items[0].data(Qt.ItemDataRole.UserRole)


class OptionsPanel(QWidget):
    """
    Panel for migration options.
    
    This panel allows users to configure migration options
    such as data types and merge strategies.
    """
    
    def __init__(self):
        """Initialize the options panel."""
        super().__init__()
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create data types group
        self.data_types_group = QGroupBox("Data Types to Migrate")
        self.data_types_layout = QVBoxLayout(self.data_types_group)
        
        # Add data type checkboxes
        self.checkbox_bookmarks = QCheckBox("Bookmarks")
        self.checkbox_bookmarks.setChecked(True)
        self.data_types_layout.addWidget(self.checkbox_bookmarks)
        
        self.checkbox_history = QCheckBox("History")
        self.checkbox_history.setChecked(True)
        self.data_types_layout.addWidget(self.checkbox_history)
        
        self.checkbox_passwords = QCheckBox("Passwords")
        self.checkbox_passwords.setChecked(True)
        self.data_types_layout.addWidget(self.checkbox_passwords)
        
        self.checkbox_cookies = QCheckBox("Cookies")
        self.checkbox_cookies.setChecked(True)
        self.data_types_layout.addWidget(self.checkbox_cookies)
        
        self.checkbox_extensions = QCheckBox("Extensions")
        self.checkbox_extensions.setChecked(True)
        self.data_types_layout.addWidget(self.checkbox_extensions)
        
        self.checkbox_preferences = QCheckBox("Preferences")
        self.checkbox_preferences.setChecked(True)
        self.data_types_layout.addWidget(self.checkbox_preferences)
        
        self.checkbox_sessions = QCheckBox("Sessions")
        self.checkbox_sessions.setChecked(True)
        self.data_types_layout.addWidget(self.checkbox_sessions)
        
        self.layout.addWidget(self.data_types_group)
        
        # Create merge strategy group
        self.merge_group = QGroupBox("Merge Strategy")
        self.merge_layout = QVBoxLayout(self.merge_group)
        
        self.merge_button_group = QButtonGroup(self)
        
        self.radio_smart = QRadioButton("Smart Merge (Recommended)")
        self.radio_smart.setChecked(True)
        self.merge_button_group.addButton(self.radio_smart)
        self.merge_layout.addWidget(self.radio_smart)
        
        self.radio_append = QRadioButton("Append Only")
        self.merge_button_group.addButton(self.radio_append)
        self.merge_layout.addWidget(self.radio_append)
        
        self.radio_overwrite = QRadioButton("Overwrite Existing")
        self.merge_button_group.addButton(self.radio_overwrite)
        self.merge_layout.addWidget(self.radio_overwrite)
        
        self.layout.addWidget(self.merge_group)
        
        # Create options group
        self.options_group = QGroupBox("Additional Options")
        self.options_layout = QVBoxLayout(self.options_group)
        
        self.checkbox_backup = QCheckBox("Create Backup Before Migration")
        self.checkbox_backup.setChecked(True)
        self.options_layout.addWidget(self.checkbox_backup)
        
        self.checkbox_deduplicate = QCheckBox("Deduplicate Items")
        self.checkbox_deduplicate.setChecked(True)
        self.options_layout.addWidget(self.checkbox_deduplicate)
        
        self.layout.addWidget(self.options_group)
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
    
    def get_selected_data_types(self):
        """
        Get the selected data types.
        
        Returns:
            List of selected data types
        """
        data_types = []
        
        if self.checkbox_bookmarks.isChecked():
            data_types.append("bookmarks")
        
        if self.checkbox_history.isChecked():
            data_types.append("history")
        
        if self.checkbox_passwords.isChecked():
            data_types.append("passwords")
        
        if self.checkbox_cookies.isChecked():
            data_types.append("cookies")
        
        if self.checkbox_extensions.isChecked():
            data_types.append("extensions")
        
        if self.checkbox_preferences.isChecked():
            data_types.append("preferences")
        
        if self.checkbox_sessions.isChecked():
            data_types.append("sessions")
        
        return data_types
    
    def get_options(self):
        """
        Get the selected options.
        
        Returns:
            Dictionary of options
        """
        options = {
            "backup": self.checkbox_backup.isChecked(),
            "deduplicate": self.checkbox_deduplicate.isChecked()
        }
        
        # Add merge strategy
        if self.radio_smart.isChecked():
            options["merge_strategy"] = "smart"
        elif self.radio_append.isChecked():
            options["merge_strategy"] = "append"
        elif self.radio_overwrite.isChecked():
            options["merge_strategy"] = "overwrite"
        
        return options


class SettingsDialog(QDialog):
    """
    Dialog for application settings.
    
    This dialog allows users to configure application settings
    such as logging and appearance.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the settings dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create general tab
        self.general_tab = QWidget()
        self.general_layout = QVBoxLayout(self.general_tab)
        self.tabs.addTab(self.general_tab, "General")
        
        # Add general settings
        self.checkbox_confirm = QCheckBox("Confirm before migration")
        self.checkbox_confirm.setChecked(True)
        self.general_layout.addWidget(self.checkbox_confirm)
        
        self.checkbox_auto_detect = QCheckBox("Auto-detect browsers on startup")
        self.checkbox_auto_detect.setChecked(True)
        self.general_layout.addWidget(self.checkbox_auto_detect)
        
        # Create appearance tab
        self.appearance_tab = QWidget()
        self.appearance_layout = QVBoxLayout(self.appearance_tab)
        self.tabs.addTab(self.appearance_tab, "Appearance")
        
        # Add appearance settings
        self.appearance_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.appearance_layout.addWidget(self.theme_combo)
        
        # Create advanced tab
        self.advanced_tab = QWidget()
        self.advanced_layout = QVBoxLayout(self.advanced_tab)
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        # Add advanced settings
        self.advanced_layout.addWidget(QLabel("Log Level:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Debug", "Info", "Warning", "Error"])
        self.log_level_combo.setCurrentIndex(1)  # Info
        self.advanced_layout.addWidget(self.log_level_combo)
        
        # Add buttons
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)
        
        self.button_layout.addStretch()
        
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.clicked.connect(self.reject)
        self.button_layout.addWidget(self.button_cancel)
        
        self.button_save = QPushButton("Save")
        self.button_save.clicked.connect(self.accept)
        self.button_layout.addWidget(self.button_save)


class ResultsDialog(QDialog):
    """
    Dialog for migration results.
    
    This dialog shows detailed results of a migration operation.
    """
    
    def __init__(self, result, parent=None):
        """
        Initialize the results dialog.
        
        Args:
            result: Migration result
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.result = result
        
        self.setWindowTitle("Migration Results")
        self.setMinimumSize(600, 400)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create summary label
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.layout.addWidget(self.summary_label)
        
        # Set summary text
        if self.result.get("success", False):
            self.summary_label.setText("Migration completed successfully.")
        else:
            self.summary_label.setText(f"Migration completed with issues: {self.result.get('message', '')}")
        
        # Create details group
        self.details_group = QGroupBox("Details")
        self.details_layout = QVBoxLayout(self.details_group)
        self.layout.addWidget(self.details_group)
        
        # Create details text
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_layout.addWidget(self.details_text)
        
        # Format and set details text
        details_html = "<table width='100%' border='1' cellspacing='0' cellpadding='4'>"
        details_html += "<tr><th>Data Type</th><th>Status</th><th>Message</th><th>Statistics</th></tr>"
        
        for data_type, data_result in self.result.get("details", {}).items():
            success = data_result.get("success", False)
            message = data_result.get("message", "")
            stats = data_result.get("stats", {})
            
            status_color = "green" if success else "red"
            status_text = "Success" if success else "Failed"
            
            stats_text = ""
            for stat_name, stat_value in stats.items():
                stats_text += f"{stat_name}: {stat_value}<br>"
            
            details_html += f"<tr>"
            details_html += f"<td>{data_type}</td>"
            details_html += f"<td style='color: {status_color};'>{status_text}</td>"
            details_html += f"<td>{message}</td>"
            details_html += f"<td>{stats_text}</td>"
            details_html += f"</tr>"
        
        details_html += "</table>"
        
        self.details_text.setHtml(details_html)
        
        # Add close button
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)
        
        self.button_layout.addStretch()
        
        self.button_close = QPushButton("Close")
        self.button_close.clicked.connect(self.accept)
        self.button_layout.addWidget(self.button_close)


class BrowserDetectionThread(QThread):
    """
    Thread for browser detection.
    
    This thread performs browser detection in the background
    to keep the UI responsive.
    """
    
    # Custom signals
    detection_complete = pyqtSignal(list)
    
    def __init__(self, controller):
        """
        Initialize the detection thread.
        
        Args:
            controller: FloorperCore controller instance
        """
        super().__init__()
        
        self.controller = controller
    
    def run(self):
        """Run the thread."""
        try:
            browsers = self.controller.detect_browsers()
            self.detection_complete.emit(browsers)
        except Exception as e:
            logger.error(f"Error in browser detection thread: {str(e)}")
            self.detection_complete.emit([])


class MigrationThread(QThread):
    """
    Thread for profile migration.
    
    This thread performs profile migration in the background
    to keep the UI responsive.
    """
    
    # Custom signals
    progress_update = pyqtSignal(int, str)
    migration_complete = pyqtSignal(dict)
    
    def __init__(self, controller, source_profile, target_profile, data_types, options):
        """
        Initialize the migration thread.
        
        Args:
            controller: FloorperCore controller instance
            source_profile: Source profile information
            target_profile: Target profile information
            data_types: Data types to migrate
            options: Migration options
        """
        super().__init__()
        
        self.controller = controller
        self.source_profile = source_profile
        self.target_profile = target_profile
        self.data_types = data_types
        self.options = options
    
    def run(self):
        """Run the thread."""
        try:
            # Simulate progress updates
            # In a real implementation, this would be based on actual progress
            total_steps = len(self.data_types)
            for i, data_type in enumerate(self.data_types):
                if self.isInterruptionRequested():
                    break
                
                progress = int((i / total_steps) * 100)
                self.progress_update.emit(progress, f"Migrating {data_type}...")
                
                # Simulate work
                QThread.msleep(500)
            
            # Perform actual migration
            result = self.controller.migrate_profile(
                self.source_profile,
                self.target_profile,
                self.data_types,
                self.options
            )
            
            self.progress_update.emit(100, "Migration complete")
            self.migration_complete.emit(result)
        except Exception as e:
            logger.error(f"Error in migration thread: {str(e)}")
            self.progress_update.emit(0, f"Error: {str(e)}")
            self.migration_complete.emit({
                "success": False,
                "message": f"Error: {str(e)}",
                "details": {}
            })


def main():
    """Main entry point for the GUI."""
    app = QApplication(sys.argv)
    
    # Create controller
    controller = FloorperCore()
    
    # Create and show main window
    window = FloorperGUI(controller)
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
