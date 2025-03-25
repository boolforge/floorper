"""
Floorper - TUI Interface

This module provides a modern Text-based User Interface (TUI) for Floorper using Textual.
Features beautiful animations, themes, and a responsive design.
"""

import os
import sys
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid, ScrollableContainer
from textual.widgets import (
    Button, Header, Footer, Static, Label, Select, ProgressBar, Checkbox,
    Input, RadioSet, RadioButton, Switch, Tree, TabbedContent, TabPane,
    DataTable, Rule, LoadingIndicator, Markdown
)
from textual.screen import Screen
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget
from textual import events
from textual.css.query import NoMatches
from textual import work
from rich.text import Text
from rich.console import RenderableType
from rich.style import Style
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown as RichMarkdown

# Import local modules
from core.browser_detector import BrowserDetector
from core.profile_migrator import ProfileMigrator
from core.backup_manager import BackupManager
from utils.platform import get_platform
from utils.app_info import get_app_info, get_floorp_profiles, get_theme_colors
from browsers.retro import RetroProfileHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('floorper.tui')

# CSS for the TUI
CSS = """
Screen {
    background: $background;
}

Header {
    background: $primary;
    color: $text-on-primary;
}

Footer {
    background: $primary;
    color: $text-on-primary;
}

Button {
    background: $primary;
    color: $text-on-primary;
    min-width: 10;
    margin: 1 2;
    padding: 1 2;
}

Button:hover {
    background: $primary-hover;
}

Button:focus {
    background: $primary-focus;
}

#welcome {
    width: 100%;
    height: 100%;
    background: $background;
    color: $text;
    padding: 2 4;
}

#welcome-title {
    text-align: center;
    text-style: bold;
    color: $primary;
    margin-bottom: 1;
}

#welcome-description {
    text-align: center;
    margin-bottom: 2;
}

#welcome-buttons {
    align: center middle;
    margin-top: 2;
}

TabPane {
    padding: 1 2;
}

.tab-content {
    height: 100%;
    width: 100%;
    padding: 1;
}

.section-title {
    text-style: bold;
    color: $primary;
    margin-bottom: 1;
}

.section-description {
    margin-bottom: 1;
}

.browser-list {
    height: 10;
    border: solid $border;
    margin-bottom: 1;
}

.profile-list {
    height: 10;
    border: solid $border;
    margin-bottom: 1;
}

.form-grid {
    grid-size: 2;
    grid-gutter: 1;
    margin-bottom: 1;
}

.form-label {
    padding: 1 2;
    content-align: right middle;
}

.form-input {
    width: 100%;
}

.checkbox-container {
    margin: 1 0;
}

.progress-container {
    margin: 1 0;
}

.status-bar {
    background: $secondary;
    color: $text-on-secondary;
    height: 1;
    padding: 0 1;
}

.error-text {
    color: $error;
}

.success-text {
    color: $success;
}
"""

class FloorperTUI(App):
    """Main TUI application for Floorper."""
    
    CSS = CSS
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("f1", "help", "Help"),
        Binding("f5", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        """Initialize the TUI application."""
        super().__init__()
        
        # Initialize components
        self.browser_detector = BrowserDetector()
        self.profile_migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
        
        # Initialize state
        self.detected_browsers = []
        self.selected_browser = None
        self.browser_profiles = {}
        
        # Theme colors
        self.theme_colors = get_theme_colors()
        
        # Dark mode flag
        self.dark_mode = False
    
    def run(self) -> int:
        """
        Run the TUI application.
        
        Returns:
            Exit code
        """
        try:
            super().run()
            return 0
        except Exception as e:
            logger.error(f"Error running TUI: {e}")
            return 1
    
    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        # Create header and footer
        app_info = get_app_info()
        yield Header(show_clock=True)
        
        # Create main content
        with TabbedContent(id="main-tabs"):
            # Welcome tab
            with TabPane("Welcome", id="welcome-tab"):
                with Vertical(id="welcome"):
                    yield Label("Welcome to Floorper", id="welcome-title")
                    yield Label(
                        "Universal Browser Profile Migration Tool for Floorp",
                        id="welcome-description"
                    )
                    
                    # App info
                    with Vertical():
                        yield Label(f"Version: {app_info['version']}")
                        yield Label(f"Platform: {app_info['platform']}")
                        yield Label(f"Python: {app_info['python_version']}")
                    
                    # Welcome buttons
                    with Horizontal(id="welcome-buttons"):
                        yield Button("Detect Browsers", variant="primary", id="detect-button")
                        yield Button("Help", variant="default", id="help-button")
            
            # Detection tab
            with TabPane("Detection", id="detection-tab"):
                with Vertical(classes="tab-content"):
                    yield Label("Browser Detection", classes="section-title")
                    yield Label(
                        "Detect installed browsers and their profiles on your system.",
                        classes="section-description"
                    )
                    
                    # Detection button
                    yield Button("Detect Browsers", variant="primary", id="detect-browsers-button")
                    
                    # Results area
                    with Grid(classes="form-grid"):
                        yield Label("Detected Browsers:", classes="form-label")
                        yield DataTable(id="browsers-table", classes="browser-list")
                        
                        yield Label("Browser Profiles:", classes="form-label")
                        yield DataTable(id="profiles-table", classes="profile-list")
            
            # Migration tab
            with TabPane("Migration", id="migration-tab"):
                with Vertical(classes="tab-content"):
                    yield Label("Profile Migration", classes="section-title")
                    yield Label(
                        "Migrate profiles between browsers, including bookmarks, history, cookies, and more.",
                        classes="section-description"
                    )
                    
                    # Source and target selection
                    with Grid(classes="form-grid"):
                        yield Label("Source Browser:", classes="form-label")
                        yield Select(id="source-browser-select", classes="form-input")
                        
                        yield Label("Source Profile:", classes="form-label")
                        yield Select(id="source-profile-select", classes="form-input")
                        
                        yield Label("Target Browser:", classes="form-label")
                        yield Select(id="target-browser-select", classes="form-input")
                        
                        yield Label("Target Profile:", classes="form-label")
                        yield Select(id="target-profile-select", classes="form-input")
                    
                    # Data selection
                    yield Label("Data to Migrate:", classes="section-title")
                    
                    with Vertical(classes="checkbox-container"):
                        yield Checkbox("Bookmarks", id="bookmarks-checkbox", value=True)
                        yield Checkbox("History", id="history-checkbox", value=True)
                        yield Checkbox("Cookies", id="cookies-checkbox", value=True)
                        yield Checkbox("Passwords", id="passwords-checkbox", value=True)
                        yield Checkbox("Extensions", id="extensions-checkbox", value=True)
                        yield Checkbox("Preferences", id="preferences-checkbox", value=True)
                    
                    # Migration button
                    yield Button("Start Migration", variant="primary", id="migrate-button")
                    
                    # Progress bar
                    with Vertical(classes="progress-container"):
                        yield ProgressBar(id="migration-progress", visible=False)
                        yield Label("", id="migration-status")
            
            # Backup tab
            with TabPane("Backup", id="backup-tab"):
                with Vertical(classes="tab-content"):
                    yield Label("Backup & Restore", classes="section-title")
                    yield Label(
                        "Create backups of browser profiles and restore them when needed.",
                        classes="section-description"
                    )
                    
                    # Backup section
                    yield Label("Create Backup", classes="section-title")
                    
                    with Grid(classes="form-grid"):
                        yield Label("Browser:", classes="form-label")
                        yield Select(id="backup-browser-select", classes="form-input")
                        
                        yield Label("Profile:", classes="form-label")
                        yield Select(id="backup-profile-select", classes="form-input")
                        
                        yield Label("Backup Location:", classes="form-label")
                        with Horizontal():
                            yield Input(id="backup-location-input", classes="form-input")
                            yield Button("Browse", id="backup-browse-button")
                    
                    yield Button("Create Backup", variant="primary", id="create-backup-button")
                    
                    # Restore section
                    yield Label("Restore Backup", classes="section-title")
                    
                    with Grid(classes="form-grid"):
                        yield Label("Backup File:", classes="form-label")
                        with Horizontal():
                            yield Input(id="restore-file-input", classes="form-input")
                            yield Button("Browse", id="restore-browse-button")
                        
                        yield Label("Target Browser:", classes="form-label")
                        yield Select(id="restore-browser-select", classes="form-input")
                        
                        yield Label("Target Profile:", classes="form-label")
                        yield Select(id="restore-profile-select", classes="form-input")
                    
                    yield Button("Restore Backup", variant="primary", id="restore-backup-button")
            
            # Settings tab
            with TabPane("Settings", id="settings-tab"):
                with Vertical(classes="tab-content"):
                    yield Label("Settings", classes="section-title")
                    yield Label(
                        "Configure application settings and preferences.",
                        classes="section-description"
                    )
                    
                    # General settings
                    yield Label("General Settings", classes="section-title")
                    
                    with Vertical(classes="checkbox-container"):
                        yield Checkbox("Auto-detect browsers on startup", id="auto-detect-checkbox")
                        yield Checkbox("Create automatic backups before migration", id="auto-backup-checkbox", value=True)
                        yield Checkbox("Show welcome message on startup", id="show-welcome-checkbox", value=True)
                    
                    # Theme settings
                    yield Label("Theme Settings", classes="section-title")
                    
                    with Vertical(classes="checkbox-container"):
                        yield Checkbox("Dark Mode", id="dark-mode-checkbox", value=self.dark_mode)
                    
                    # Save button
                    yield Button("Save Settings", variant="primary", id="save-settings-button")
            
            # About tab
            with TabPane("About", id="about-tab"):
                with Vertical(classes="tab-content"):
                    yield Label("About Floorper", classes="section-title")
                    
                    # App info
                    with Vertical():
                        yield Label(f"Floorper {app_info['version']}")
                        yield Label(f"{app_info['description']}")
                        yield Label(f"Author: {app_info['author']}")
                        yield Label(f"License: {app_info['license']}")
                        yield Label(f"Platform: {app_info['platform']}")
                        yield Label(f"Python: {app_info['python_version']}")
                    
                    # Description
                    yield Markdown(
                        """
                        ## Features
                        
                        - **Multi-browser Support**: Detect and migrate profiles from various browsers, including exotic and retro browsers
                        - **Multiple Interfaces**: Choose between GUI (PyQt6), TUI (Textual), or CLI interfaces
                        - **Profile Migration**: Migrate bookmarks, history, cookies, passwords, and other data between browsers
                        - **Backup & Restore**: Create and manage backups of browser profiles
                        - **Performance Optimized**: Utilizes caching and parallel processing for efficient operations
                        - **Cross-platform**: Works on Windows, macOS, and Linux
                        """
                    )
        
        # Status bar
        yield Static("Ready", id="status-bar", classes="status-bar")
        
        # Footer
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        # Set up tables
        browsers_table = self.query_one("#browsers-table", DataTable)
        browsers_table.add_columns("Name", "Version", "Path")
        
        profiles_table = self.query_one("#profiles-table", DataTable)
        profiles_table.add_columns("Name", "Path")
        
        # Apply theme colors
        self._apply_theme_colors()
        
        # Auto-detect browsers if enabled
        # TODO: Implement settings loading
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button press events.
        
        Args:
            event: Button press event
        """
        button_id = event.button.id
        
        if button_id == "detect-button" or button_id == "detect-browsers-button":
            self._detect_browsers()
        elif button_id == "help-button":
            self.action_help()
        elif button_id == "migrate-button":
            self._migrate_profile()
        elif button_id == "create-backup-button":
            self._create_backup()
        elif button_id == "restore-backup-button":
            self._restore_backup()
        elif button_id == "backup-browse-button":
            self._browse_backup_location()
        elif button_id == "restore-browse-button":
            self._browse_restore_file()
        elif button_id == "save-settings-button":
            self._save_settings()
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Handle row selection in data tables.
        
        Args:
            event: Row selection event
        """
        table_id = event.data_table.id
        
        if table_id == "browsers-table":
            # Get selected browser
            row = event.data_table.get_row(event.row_key)
            browser_name = row[0]
            
            # Find browser in detected browsers
            for browser in self.detected_browsers:
                if browser["name"] == browser_name:
                    self.selected_browser = browser
                    self._show_browser_profiles(browser)
                    break
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """
        Handle select change events.
        
        Args:
            event: Select change event
        """
        select_id = event.select.id
        
        if select_id == "source-browser-select":
            self._update_profiles_select("source-browser-select", "source-profile-select")
        elif select_id == "target-browser-select":
            self._update_profiles_select("target-browser-select", "target-profile-select")
        elif select_id == "backup-browser-select":
            self._update_profiles_select("backup-browser-select", "backup-profile-select")
        elif select_id == "restore-browser-select":
            self._update_profiles_select("restore-browser-select", "restore-profile-select")
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """
        Handle checkbox change events.
        
        Args:
            event: Checkbox change event
        """
        checkbox_id = event.checkbox.id
        
        if checkbox_id == "dark-mode-checkbox":
            self.dark_mode = event.value
            self._apply_theme_colors()
    
    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark_mode = not self.dark_mode
        
        # Update checkbox
        try:
            dark_mode_checkbox = self.query_one("#dark-mode-checkbox", Checkbox)
            dark_mode_checkbox.value = self.dark_mode
        except NoMatches:
            pass
        
        # Apply theme colors
        self._apply_theme_colors()
    
    def action_help(self) -> None:
        """Show help information."""
        # TODO: Implement help screen
        self.notify("Help functionality not yet implemented", title="Help")
    
    def action_refresh(self) -> None:
        """Refresh the current view."""
        # Detect browsers again
        self._detect_browsers()
    
    @work
    async def _detect_browsers(self) -> None:
        """Detect installed browsers and their profiles."""
        # Update status
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update("Detecting browsers...")
        
        # Clear tables
        browsers_table = self.query_one("#browsers-table", DataTable)
        browsers_table.clear()
        
        profiles_table = self.query_one("#profiles-table", DataTable)
        profiles_table.clear()
        
        # Detect browsers
        try:
            self.detected_browsers = self.browser_detector.detect_browsers()
            
            # Add browsers to table
            for browser in self.detected_browsers:
                browsers_table.add_row(
                    browser["name"],
                    browser.get("version", ""),
                    browser.get("path", "")
                )
            
            # Update browser selects
            self._update_browser_selects()
            
            # Update status
            status_bar.update(f"Detected {len(self.detected_browsers)} browsers")
        except Exception as e:
            logger.error(f"Error detecting browsers: {e}")
            status_bar.update(f"Error detecting browsers: {e}")
    
    def _show_browser_profiles(self, browser: Dict[str, Any]) -> None:
        """
        Show profiles for the selected browser.
        
        Args:
            browser: Browser information
        """
        # Update status
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(f"Getting profiles for {browser['name']}...")
        
        # Clear profiles table
        profiles_table = self.query_one("#profiles-table", DataTable)
        profiles_table.clear()
        
        # Get profiles
        try:
            profiles = self.browser_detector.get_profiles(browser["id"])
            
            # Store profiles
            self.browser_profiles[browser["id"]] = profiles
            
            # Add profiles to table
            for profile in profiles:
                profiles_table.add_row(
                    profile["name"],
                    profile["path"]
                )
            
            # Update status
            status_bar.update(f"Found {len(profiles)} profiles for {browser['name']}")
        except Exception as e:
            logger.error(f"Error getting profiles: {e}")
            status_bar.update(f"Error getting profiles: {e}")
    
    def _update_browser_selects(self) -> None:
        """Update browser select widgets with detected browsers."""
        # Get select widgets
        selects = [
            self.query_one("#source-browser-select", Select),
            self.query_one("#target-browser-select", Select),
            self.query_one("#backup-browser-select", Select),
            self.query_one("#restore-browser-select", Select)
        ]
        
        # Update selects
        for select in selects:
            select.clear_options()
            
            for browser in self.detected_browsers:
                select.add_option(browser["name"], browser["id"])
    
    def _update_profiles_select(self, browser_select_id: str, profile_select_id: str) -> None:
        """
        Update profile select based on selected browser.
        
        Args:
            browser_select_id: ID of browser select widget
            profile_select_id: ID of profile select widget to update
        """
        # Get select widgets
        browser_select = self.query_one(f"#{browser_select_id}", Select)
        profile_select = self.query_one(f"#{profile_select_id}", Select)
        
        # Get selected browser
        browser_id = browser_select.value
        if not browser_id:
            return
        
        # Clear profile select
        profile_select.clear_options()
        
        # Get profiles
        if browser_id in self.browser_profiles:
            profiles = self.browser_profiles[browser_id]
        else:
            try:
                profiles = self.browser_detector.get_profiles(browser_id)
                self.browser_profiles[browser_id] = profiles
            except Exception as e:
                logger.error(f"Error getting profiles: {e}")
                profiles = []
        
        # Update profile select
        for profile in profiles:
            profile_select.add_option(profile["name"], profile["path"])
    
    @work
    async def _migrate_profile(self) -> None:
        """Migrate a browser profile."""
        # Get source and target profiles
        source_browser_select = self.query_one("#source-browser-select", Select)
        source_profile_select = self.query_one("#source-profile-select", Select)
        target_browser_select = self.query_one("#target-browser-select", Select)
        target_profile_select = self.query_one("#target-profile-select", Select)
        
        source_browser_id = source_browser_select.value
        source_profile_path = source_profile_select.value
        target_browser_id = target_browser_select.value
        target_profile_path = target_profile_select.value
        
        if not source_browser_id or not source_profile_path or not target_browser_id or not target_profile_path:
            self.notify("Please select source and target browsers and profiles", title="Migration Error")
            return
        
        # Get data types to migrate
        data_types = []
        if self.query_one("#bookmarks-checkbox", Checkbox).value:
            data_types.append("bookmarks")
        if self.query_one("#history-checkbox", Checkbox).value:
            data_types.append("history")
        if self.query_one("#cookies-checkbox", Checkbox).value:
            data_types.append("cookies")
        if self.query_one("#passwords-checkbox", Checkbox).value:
            data_types.append("passwords")
        if self.query_one("#extensions-checkbox", Checkbox).value:
            data_types.append("extensions")
        if self.query_one("#preferences-checkbox", Checkbox).value:
            data_types.append("preferences")
        
        # Show progress bar
        progress_bar = self.query_one("#migration-progress", ProgressBar)
        progress_bar.visible = True
        progress_bar.progress = 0
        
        status_label = self.query_one("#migration-status", Label)
        status_label.update("Migrating profile...")
        
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update("Migrating profile...")
        
        # Create source and target profile objects
        source_profile = {
            "browser_id": source_browser_id,
            "path": source_profile_path
        }
        
        target_profile = {
            "browser_id": target_browser_id,
            "path": target_profile_path
        }
        
        # Migrate profile
        try:
            def progress_callback(step: int, message: str) -> None:
                """
                Progress callback function.
                
                Args:
                    step: Current step (0-100)
                    message: Progress message
                """
                progress_bar.progress = step / 100
                status_label.update(message)
            
            result = await self.profile_migrator.migrate_profile_async(
                source_profile,
                target_profile,
                data_types,
                {"progress_callback": progress_callback}
            )
            
            # Hide progress bar
            progress_bar.visible = False
            
            if result.get("success", False):
                status_label.update("Migration completed successfully")
                status_bar.update("Migration completed successfully")
                self.notify("Profile migration completed successfully", title="Migration Complete")
            else:
                status_label.update(f"Migration failed: {result.get('error', 'Unknown error')}")
                status_bar.update("Migration failed")
                self.notify(f"Migration failed: {result.get('error', 'Unknown error')}", title="Migration Error")
        except Exception as e:
            logger.error(f"Error migrating profile: {e}")
            progress_bar.visible = False
            status_label.update(f"Migration failed: {e}")
            status_bar.update("Migration failed")
            self.notify(f"Migration failed: {e}", title="Migration Error")
    
    def _browse_backup_location(self) -> None:
        """Browse for backup location."""
        # TODO: Implement file browser
        self.notify("File browser not yet implemented", title="Browse")
    
    def _browse_restore_file(self) -> None:
        """Browse for backup file to restore."""
        # TODO: Implement file browser
        self.notify("File browser not yet implemented", title="Browse")
    
    def _create_backup(self) -> None:
        """Create a backup of a browser profile."""
        # Get browser and profile
        backup_browser_select = self.query_one("#backup-browser-select", Select)
        backup_profile_select = self.query_one("#backup-profile-select", Select)
        backup_location_input = self.query_one("#backup-location-input", Input)
        
        browser_id = backup_browser_select.value
        profile_path = backup_profile_select.value
        location = backup_location_input.value
        
        if not browser_id or not profile_path:
            self.notify("Please select a browser and profile to backup", title="Backup Error")
            return
        
        if not location:
            self.notify("Please enter a backup location", title="Backup Error")
            return
        
        # Create backup
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update("Creating backup...")
        
        try:
            backup_file = self.backup_manager.create_backup(
                profile_path,
                browser_id,
                location
            )
            
            status_bar.update(f"Backup created: {backup_file}")
            self.notify(f"Backup created successfully:\n{backup_file}", title="Backup Created")
        except Exception as e:
            logger.error(f"Backup error: {e}")
            status_bar.update("Backup creation failed")
            self.notify(f"Failed to create backup: {e}", title="Backup Error")
    
    def _restore_backup(self) -> None:
        """Restore a backup to a browser profile."""
        # Get backup file and target
        restore_file_input = self.query_one("#restore-file-input", Input)
        restore_browser_select = self.query_one("#restore-browser-select", Select)
        restore_profile_select = self.query_one("#restore-profile-select", Select)
        
        backup_file = restore_file_input.value
        browser_id = restore_browser_select.value
        profile_path = restore_profile_select.value
        
        if not backup_file:
            self.notify("Please enter a backup file to restore", title="Restore Error")
            return
        
        if not browser_id or not profile_path:
            self.notify("Please select a target browser and profile", title="Restore Error")
            return
        
        # Confirm restoration
        # TODO: Implement confirmation dialog
        
        # Restore backup
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update("Restoring backup...")
        
        try:
            self.backup_manager.restore_backup(
                backup_file,
                profile_path
            )
            
            status_bar.update("Backup restored successfully")
            self.notify("Backup restored successfully", title="Backup Restored")
        except Exception as e:
            logger.error(f"Restore error: {e}")
            status_bar.update("Backup restoration failed")
            self.notify(f"Failed to restore backup: {e}", title="Restore Error")
    
    def _save_settings(self) -> None:
        """Save application settings."""
        # Get settings
        auto_detect = self.query_one("#auto-detect-checkbox", Checkbox).value
        auto_backup = self.query_one("#auto-backup-checkbox", Checkbox).value
        show_welcome = self.query_one("#show-welcome-checkbox", Checkbox).value
        dark_mode = self.query_one("#dark-mode-checkbox", Checkbox).value
        
        # Save settings
        # TODO: Implement settings storage
        
        # Update status
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update("Settings saved")
        
        # Apply dark mode
        if dark_mode != self.dark_mode:
            self.dark_mode = dark_mode
            self._apply_theme_colors()
    
    def _apply_theme_colors(self) -> None:
        """Apply theme colors to the application."""
        # Get colors
        colors = self.theme_colors
        
        # Apply dark mode if enabled
        if self.dark_mode:
            colors = {
                "background": "#1e1e1e",
                "text": "#f8f8f8",
                "primary": "#4a6cf7",
                "primary-hover": "#3a5ce7",
                "primary-focus": "#2a4cd7",
                "secondary": "#6c757d",
                "success": "#28a745",
                "error": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                "light": "#343a40",
                "dark": "#f8f9fa",
                "border": "#495057",
                "highlight": "#2d3748",
                "text-on-primary": "#ffffff",
                "text-on-secondary": "#ffffff"
            }
        else:
            colors = {
                "background": "#ffffff",
                "text": "#212529",
                "primary": "#4a6cf7",
                "primary-hover": "#3a5ce7",
                "primary-focus": "#2a4cd7",
                "secondary": "#6c757d",
                "success": "#28a745",
                "error": "#dc3545",
                "warning": "#ffc107",
                "info": "#17a2b8",
                "light": "#f8f9fa",
                "dark": "#343a40",
                "border": "#dee2e6",
                "highlight": "#f8f9fa",
                "text-on-primary": "#ffffff",
                "text-on-secondary": "#ffffff"
            }
        
        # Apply colors
        self.app.stylesheet.set_variables(colors)
