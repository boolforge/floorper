#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main window for the Floorper application.
"""

import os
import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QCheckBox, QSplitter,
    QApplication, QTextEdit, QProgressBar, QGridLayout, QFileDialog
)
from PyQt6.QtCore import Qt, QSize, QRect, QRectF, QTimer
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QPainterPath, 
    QBrush, QPen, QIcon
)
from .browser_detector import BrowserDetector
from .profile_card import ProfileCard
from .profile_migrator import ProfileMigrator
from .constants import BROWSERS, BROWSER_COLORS

class FloorperWindow(QMainWindow):
    """
    Main window for the Floorper application. This class is responsible for
    creating and managing the UI components and handling user interactions.
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize browser detector and profile migrator
        self.browser_detector = BrowserDetector()
        self.profile_migrator = ProfileMigrator()
        
        # Initialize UI state
        self.selected_browsers = {}
        self.detected_profiles = {}
        self.selected_profiles = {}
        
        # Set up the UI
        self.setup_ui()
        
        # Automatically detect browsers when starting
        QTimer.singleShot(100, self.refresh_browsers)
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Set window properties
        self.setWindowTitle("Floorper 3.0.0 - Migrate profiles TO Floorp")
        self.setMinimumSize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Add header with logo and title
        header_layout = QHBoxLayout()
        
        # Create logo
        logo_size = 40
        pixmap = QPixmap(logo_size, logo_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw rounded rectangle logo
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#0078D7")))
        painter.setPen(Qt.PenStyle.NoPen)
        
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(logo_size), float(logo_size), 10.0, 10.0)
        painter.drawPath(path)
        
        # Add "BM" text to logo
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            QRect(0, 0, logo_size, logo_size),
            Qt.AlignmentFlag.AlignCenter,
            "FP"
        )
        painter.end()
        
        # Add logo to header
        logo_label = QLabel()
        logo_label.setPixmap(pixmap)
        header_layout.addWidget(logo_label)
        
        # Add app title to header
        title_label = QLabel("Floorper 3.0.0")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Add spacer to push everything to the left
        header_layout.addStretch()
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Add subtitle
        subtitle = QLabel("Floorp Profile Migration Tool - Migrate profiles FROM other browsers TO Floorp seamlessly")
        subtitle_font = QFont("Arial", 10)
        subtitle.setFont(subtitle_font)
        main_layout.addWidget(subtitle)
        
        # Create splitter for browser selection and profile display
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create browser selection panel
        browser_panel = QFrame()
        browser_panel.setFrameShape(QFrame.Shape.StyledPanel)
        browser_panel.setMinimumWidth(250)
        browser_panel.setMaximumWidth(350)
        
        browser_layout = QVBoxLayout(browser_panel)
        browser_layout.setContentsMargins(10, 10, 10, 10)
        browser_layout.setSpacing(5)
        
        # Add browser selection label
        browser_select_label = QLabel("Select Source Browsers")
        browser_select_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        browser_layout.addWidget(browser_select_label)
        
        # Create scroll area for browser checkboxes
        browser_scroll = QScrollArea()
        browser_scroll.setWidgetResizable(True)
        browser_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        browser_scroll_content = QWidget()
        browser_scroll_layout = QVBoxLayout(browser_scroll_content)
        browser_scroll_layout.setContentsMargins(0, 0, 0, 0)
        browser_scroll_layout.setSpacing(5)
        browser_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Add browser checkboxes
        self.browser_checkboxes = {}
        for browser_id, browser_info in BROWSERS.items():
            if browser_id == "floorp":  # Skip Floorp since it's the target
                continue
                
            checkbox = QCheckBox(f" {browser_info['name']}")
            checkbox.setObjectName(browser_id)
            checkbox.stateChanged.connect(self.on_browser_selection_changed)
            
            # Set Firefox, Chrome, and Edge checked by default
            if browser_id in ["firefox", "chrome", "edge"]:
                checkbox.setChecked(True)
            
            self.browser_checkboxes[browser_id] = checkbox
            browser_scroll_layout.addWidget(checkbox)
        
        browser_scroll_layout.addStretch()
        browser_scroll.setWidget(browser_scroll_content)
        browser_layout.addWidget(browser_scroll)
        
        # Add browser refresh button
        refresh_button = QPushButton("Refresh Browsers")
        refresh_button.clicked.connect(self.refresh_browsers)
        browser_layout.addWidget(refresh_button)
        
        # Add detect profiles button
        detect_button = QPushButton("Detect Profiles")
        detect_button.clicked.connect(self.on_detect_profiles_click)
        browser_layout.addWidget(detect_button)
        
        # Add browser panel to splitter
        splitter.addWidget(browser_panel)
        
        # Create profile display panel
        profile_panel = QFrame()
        profile_panel.setFrameShape(QFrame.Shape.StyledPanel)
        
        profile_layout = QVBoxLayout(profile_panel)
        profile_layout.setContentsMargins(10, 10, 10, 10)
        profile_layout.setSpacing(10)
        
        # Add profile display label
        profile_label = QLabel("Detected Profiles")
        profile_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        profile_layout.addWidget(profile_label)
        
        # Create scroll area for profile cards
        self.profile_scroll = QScrollArea()
        self.profile_scroll.setWidgetResizable(True)
        self.profile_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.profile_scroll_content = QWidget()
        self.profile_scroll_layout = QVBoxLayout(self.profile_scroll_content)
        self.profile_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.profile_scroll_layout.setSpacing(10)
        self.profile_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.profile_scroll.setWidget(self.profile_scroll_content)
        profile_layout.addWidget(self.profile_scroll)
        
        # Add migration button
        self.migrate_button = QPushButton("Migrate Selected Profiles TO Floorp")
        self.migrate_button.clicked.connect(self.on_migrate_click)
        self.migrate_button.setEnabled(False)
        profile_layout.addWidget(self.migrate_button)
        
        # Add select all button
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.on_select_all_click)
        self.select_all_button.setEnabled(False)
        profile_layout.addWidget(self.select_all_button)
        
        # Add open folder button
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.on_open_folder_click)
        profile_layout.addWidget(self.open_folder_button)
        
        # Add profile panel to splitter
        splitter.addWidget(profile_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([1, 3])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter, 1)
        
        # Add activity log
        log_label = QLabel("Activity Log")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(self.log_text)
        
        # Add status bar with profile count
        self.status_label = QLabel("Found 0 profiles")
        self.statusBar().addPermanentWidget(self.status_label)
        
        # Log initialization
        self.log("Welcome to Floorper 3.0.0 - Ready to detect browser profiles.")
    
    def log(self, message):
        """Add a message to the activity log."""
        self.log_text.append(message)
        self.logger.info(message)
    
    def on_browser_selection_changed(self):
        """Handle browser selection changes."""
        selected = []
        for browser_id, checkbox in self.browser_checkboxes.items():
            if checkbox.isChecked():
                selected.append(browser_id)
        
        # Ensure Firefox and Chrome are selected by default
        if "firefox" not in selected:
            self.browser_checkboxes["firefox"].setChecked(True)
            selected.append("firefox")
        
        if "chrome" not in selected:
            self.browser_checkboxes["chrome"].setChecked(True)
            selected.append("chrome")
        
        # Update selected browsers
        self.selected_browsers = {browser_id: BROWSERS[browser_id] for browser_id in selected}
    
    def refresh_browsers(self):
        """Refresh the browser list and check availability."""
        self.log("Refreshing browser detection...")
        detected = self.browser_detector.detect_browsers()
        
        # Update checkboxes based on detected browsers
        for browser_id, checkbox in self.browser_checkboxes.items():
            if browser_id in detected:
                checkbox.setEnabled(True)
                # Auto-select detected major browsers
                if browser_id in ["firefox", "chrome", "edge", "brave", "opera", "vivaldi"]:
                    checkbox.setChecked(True)
            else:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
        
        # Ensure Firefox and Chrome are always checked
        self.browser_checkboxes["firefox"].setChecked(True)
        self.browser_checkboxes["chrome"].setChecked(True)
        
        # Update selected browsers
        self.on_browser_selection_changed()
        
        # Log results
        self.log(f"Browser detection completed. Found {len(detected)} browsers.")
    
    def on_detect_profiles_click(self):
        """Handle detect profiles button click."""
        # Clear previous profiles
        self.clear_profile_display()
        
        # Ensure at least some browsers are selected
        any_selected = False
        for checkbox in self.browser_checkboxes.values():
            if checkbox.isChecked():
                any_selected = True
                break
        
        if not any_selected:
            self.log("BUTTON CLICK FIX: No browsers selected! Force-selecting Firefox and Chrome")
            self.browser_checkboxes["firefox"].setChecked(True)
            self.browser_checkboxes["chrome"].setChecked(True)
            self.on_browser_selection_changed()
        
        # Detect profiles for selected browsers
        self.detect_profiles()
    
    def detect_profiles(self, show_errors=True):
        """Detect profiles for selected browsers."""
        self.log("Starting profile detection...")
        selected_browsers = {browser_id: browser for browser_id, browser in self.selected_browsers.items()}
        
        # Ensure we always include Firefox and Chrome
        if not selected_browsers:
            self.log("No browsers selected! Force-selecting Firefox and Chrome.")
            selected_browsers = {
                "firefox": BROWSERS["firefox"],
                "chrome": BROWSERS["chrome"]
            }
        
        profiles_by_browser = {}
        total_profiles = 0
        
        for browser_id, browser_info in selected_browsers.items():
            try:
                # Special grouping for Opera GX/Opera to avoid too many cards
                if browser_id in ["opera", "opera_gx"]:
                    # Combine Opera profiles to avoid fragmentation
                    if "opera_combined" not in profiles_by_browser:
                        profiles_by_browser["opera_combined"] = []
                    
                    profiles = self.browser_detector.detect_profiles(browser_id)
                    if profiles:
                        # Group by base directory to create fewer cards
                        base_dirs = {}
                        for profile in profiles:
                            base_dir = os.path.dirname(profile["path"])
                            if base_dir not in base_dirs:
                                base_dirs[base_dir] = []
                            base_dirs[base_dir].append(profile)
                        
                        # Create one profile per base directory
                        for base_dir, dir_profiles in base_dirs.items():
                            combined_profile = {
                                "name": f"{browser_info['name']} ({len(dir_profiles)} profiles)",
                                "browser_id": browser_id,
                                "browser_name": browser_info["name"],
                                "path": base_dir,
                                "is_group": True,
                                "profiles": dir_profiles,
                                "stats": self.combine_profile_stats(dir_profiles)
                            }
                            profiles_by_browser["opera_combined"].append(combined_profile)
                            total_profiles += 1
                        
                        self.log(f"Found {len(profiles)} profiles for {browser_info['name']}")
                else:
                    # Regular browser profile detection
                    profiles = self.browser_detector.detect_profiles(browser_id)
                    if profiles:
                        profiles_by_browser[browser_id] = profiles
                        total_profiles += len(profiles)
                        self.log(f"Found {len(profiles)} profiles for {browser_info['name']}")
                    else:
                        if show_errors:
                            self.log(f"No profiles found for {browser_info['name']}")
            except Exception as e:
                if show_errors:
                    self.log(f"Error detecting profiles for {browser_info['name']}: {str(e)}")
        
        # Update the profile display
        self.detected_profiles = profiles_by_browser
        self.display_detected_profiles()
        
        # Update status
        self.status_label.setText(f"Found {total_profiles} profiles")
        self.log(f"Profile detection complete. Found {total_profiles} profiles.")
        
        # Enable migration if profiles were found
        self.migrate_button.setEnabled(total_profiles > 0)
        self.select_all_button.setEnabled(total_profiles > 0)
    
    def combine_profile_stats(self, profiles):
        """Combine stats from multiple profiles into one summary."""
        combined = {
            "bookmarks": 0,
            "passwords": 0,
            "cookies": 0,
            "history": 0,
            "extensions": 0
        }
        
        for profile in profiles:
            if "stats" in profile:
                for key, value in profile["stats"].items():
                    if key in combined and value:
                        combined[key] += value
        
        return combined
    
    def clear_profile_display(self):
        """Clear the profile display area."""
        # Clear the layout
        for i in reversed(range(self.profile_scroll_layout.count())): 
            item = self.profile_scroll_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Reset selected profiles
        self.selected_profiles = {}
    
    def display_detected_profiles(self):
        """Display detected profiles in the UI."""
        # Clear the current display
        self.clear_profile_display()
        
        # Display profiles for each browser
        for browser_id, profiles in self.detected_profiles.items():
            # Skip empty profile lists
            if not profiles:
                continue
            
            # Get browser information
            if browser_id == "opera_combined":
                browser_name = "Opera/Opera GX"
                browser_color = BROWSER_COLORS.get("opera", "#FF0000")
            else:
                browser_info = BROWSERS.get(browser_id, {"name": browser_id})
                browser_name = browser_info.get("name", browser_id)
                browser_color = BROWSER_COLORS.get(browser_id, "#808080")
            
            # Add profiles for this browser
            for profile in profiles:
                profile_card = ProfileCard(
                    profile,
                    browser_color,
                    self.on_profile_selected,
                    self.on_profile_fix
                )
                self.profile_scroll_layout.addWidget(profile_card)
        
        # Add stretch at the end to push all cards to the top
        self.profile_scroll_layout.addStretch()
    
    def on_profile_selected(self, profile, selected):
        """Handle profile selection."""
        profile_key = f"{profile['browser_id']}:{profile['path']}"
        
        if selected:
            self.selected_profiles[profile_key] = profile
        elif profile_key in self.selected_profiles:
            del self.selected_profiles[profile_key]
    
    def on_profile_fix(self, profile):
        """Handle profile fix button click."""
        # Open the profile directory
        try:
            path = profile["path"]
            if os.path.exists(path):
                # Use different methods based on OS
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    import subprocess
                    subprocess.call(["open", path])
                else:
                    import subprocess
                    subprocess.call(["xdg-open", path])
                
                self.log(f"Opened directory: {path}")
            else:
                self.log(f"Directory does not exist: {path}")
        except Exception as e:
            self.log(f"Error opening profile directory: {str(e)}")
    
    def on_select_all_click(self):
        """Handle select all button click."""
        # Find all profile cards
        for i in range(self.profile_scroll_layout.count()):
            item = self.profile_scroll_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ProfileCard):
                item.widget().select_checkbox.setChecked(True)
    
    def on_migrate_click(self):
        """Handle migrate button click."""
        if not self.selected_profiles:
            self.log("No profiles selected for migration.")
            return
        
        self.log(f"Starting migration of {len(self.selected_profiles)} profiles to Floorp...")
        
        # Create progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(len(self.selected_profiles))
        progress_bar.setValue(0)
        self.profile_scroll_layout.insertWidget(0, progress_bar)
        
        # Migrate each selected profile
        successful = 0
        failed = 0
        
        for i, (profile_key, profile) in enumerate(self.selected_profiles.items()):
            self.log(f"Migrating profile: {profile['name']} from {profile['browser_name']}...")
            
            try:
                # Perform the migration
                result = self.profile_migrator.migrate_to_floorp(profile)
                
                if result["success"]:
                    self.log(f"Successfully migrated {profile['name']} to Floorp at {result['target_path']}")
                    successful += 1
                else:
                    self.log(f"Failed to migrate {profile['name']}: {result['error']}")
                    failed += 1
            except Exception as e:
                self.log(f"Error migrating {profile['name']}: {str(e)}")
                failed += 1
            
            # Update progress
            progress_bar.setValue(i + 1)
            QApplication.processEvents()
        
        # Show migration summary
        self.log(f"Migration complete: {successful} successful, {failed} failed.")
        
        # Remove progress bar
        progress_bar.deleteLater()
    
    def on_open_folder_click(self):
        """Handle open folder button click."""
        # Open the selected profile directory
        try:
            if self.selected_profiles:
                profile = list(self.selected_profiles.values())[0]
                path = profile["path"]
                if os.path.exists(path):
                    # Use different methods based on OS
                    if sys.platform == "win32":
                        os.startfile(path)
                    elif sys.platform == "darwin":
                        import subprocess
                        subprocess.call(["open", path])
                    else:
                        import subprocess
                        subprocess.call(["xdg-open", path])
                    
                    self.log(f"Opened directory: {path}")
                else:
                    self.log(f"Directory does not exist: {path}")
            else:
                self.log("No profiles selected.")
        except Exception as e:
            self.log(f"Error opening profile directory: {str(e)}")


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = FloorperWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
