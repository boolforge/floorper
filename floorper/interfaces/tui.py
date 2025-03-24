#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Modern TUI Interface
==============================

A modern Text User Interface for Floorper using Textual library.
Provides a rich terminal interface for browser profile detection and migration.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union, Set

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Label, Select, Input, Checkbox
from textual.screen import Screen
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget

from ..core.constants import BROWSERS, DATA_TYPES
from ..core.browser_detector import BrowserDetector
from ..core.profile_migrator import ProfileMigrator
from ..core.backup_manager import BackupManager

logger = logging.getLogger(__name__)

class BrowserProfileCard(Static):
    """A card widget displaying browser profile information."""
    
    DEFAULT_CSS = """
    BrowserProfileCard {
        width: 100%;
        height: auto;
        border: solid $accent;
        padding: 1 2;
        margin: 1 0;
        background: $surface;
    }
    
    BrowserProfileCard:focus {
        border: double $accent;
    }
    
    BrowserProfileCard > .title {
        text-style: bold;
        color: $accent;
    }
    
    BrowserProfileCard > .path {
        color: $text-muted;
    }
    """
    
    def __init__(self, profile: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = profile
        self.selected = False
    
    def compose(self) -> ComposeResult:
        browser_name = BROWSERS.get(self.profile["browser_id"], {}).get("name", "Unknown Browser")
        yield Label(f"{browser_name} - {self.profile['name']}", classes="title")
        yield Label(f"Path: {self.profile['path']}", classes="path")
    
    def toggle_selected(self) -> None:
        """Toggle the selected state of this card."""
        self.selected = not self.selected
        if self.selected:
            self.add_class("selected")
        else:
            self.remove_class("selected")


class BrowserDetectionScreen(Screen):
    """Screen for detecting browser profiles."""
    
    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detector = BrowserDetector()
        self.profiles = []
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Label("Detecting browser profiles...", id="status")
            
            with Vertical(id="profiles_container"):
                # Will be populated with profile cards
                pass
            
            with Horizontal(id="actions"):
                yield Button("Refresh", id="refresh")
                yield Button("Next", id="next")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Event handler called when the screen is mounted."""
        self.detect_profiles()
    
    def detect_profiles(self) -> None:
        """Detect browser profiles and update the UI."""
        self.query_one("#status").update("Detecting browser profiles...")
        
        # Clear existing profiles
        profiles_container = self.query_one("#profiles_container")
        profiles_container.remove_children()
        
        # Detect profiles
        self.profiles = self.detector.detect_all_profiles()
        
        if not self.profiles:
            self.query_one("#status").update("No browser profiles found.")
            return
        
        # Add profile cards
        for profile in self.profiles:
            profiles_container.mount(BrowserProfileCard(profile))
        
        self.query_one("#status").update(f"Found {len(self.profiles)} browser profiles.")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler for button presses."""
        if event.button.id == "refresh":
            self.detect_profiles()
        elif event.button.id == "next":
            # Get selected profiles
            selected_profiles = []
            for index, card in enumerate(self.query(BrowserProfileCard)):
                if card.selected:
                    selected_profiles.append(self.profiles[index])
            
            if not selected_profiles:
                self.query_one("#status").update("Please select at least one profile.")
                return
            
            # Switch to migration screen
            self.app.push_screen(MigrationScreen(selected_profiles))
    
    def on_browser_profile_card_click(self, event: BrowserProfileCard.Click) -> None:
        """Event handler for profile card clicks."""
        event.widget.toggle_selected()
    
    def action_refresh(self) -> None:
        """Action to refresh the profile list."""
        self.detect_profiles()
    
    def action_quit(self) -> None:
        """Action to quit the application."""
        self.app.exit()


class MigrationScreen(Screen):
    """Screen for migrating browser profiles."""
    
    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self, source_profiles: List[Dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_profiles = source_profiles
        self.detector = BrowserDetector()
        self.migrator = ProfileMigrator()
        self.target_profiles = []
        self.selected_data_types = set(DATA_TYPES.keys())
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Label("Select target profile and data types to migrate", id="status")
            
            with Horizontal(id="migration_options"):
                with Vertical(id="source_profiles", classes="panel"):
                    yield Label("Source Profiles:", classes="panel-title")
                    for profile in self.source_profiles:
                        browser_name = BROWSERS.get(profile["browser_id"], {}).get("name", "Unknown Browser")
                        yield Label(f"{browser_name} - {profile['name']}")
                
                with Vertical(id="target_profiles", classes="panel"):
                    yield Label("Target Profile:", classes="panel-title")
                    yield Select(id="target_profile_select", options=[])
                
                with Vertical(id="data_types", classes="panel"):
                    yield Label("Data Types to Migrate:", classes="panel-title")
                    for data_type, info in DATA_TYPES.items():
                        yield Checkbox(info.get("name", data_type), id=f"dt_{data_type}", value=True)
            
            with Horizontal(id="actions"):
                yield Button("Back", id="back")
                yield Button("Migrate", id="migrate")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Event handler called when the screen is mounted."""
        self.detect_target_profiles()
    
    def detect_target_profiles(self) -> None:
        """Detect target browser profiles and update the UI."""
        # Detect all profiles
        all_profiles = self.detector.detect_all_profiles()
        
        # Filter out source profiles
        source_paths = [p["path"] for p in self.source_profiles]
        self.target_profiles = [p for p in all_profiles if p["path"] not in source_paths]
        
        # Update target profile select
        target_select = self.query_one("#target_profile_select")
        options = []
        
        for i, profile in enumerate(self.target_profiles):
            browser_name = BROWSERS.get(profile["browser_id"], {}).get("name", "Unknown Browser")
            options.append((str(i), f"{browser_name} - {profile['name']}"))
        
        target_select.set_options(options)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler for button presses."""
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "migrate":
            self.start_migration()
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Event handler for checkbox changes."""
        checkbox_id = event.checkbox.id
        if checkbox_id.startswith("dt_"):
            data_type = checkbox_id[3:]
            if event.value:
                self.selected_data_types.add(data_type)
            else:
                self.selected_data_types.discard(data_type)
    
    def start_migration(self) -> None:
        """Start the migration process."""
        # Get selected target profile
        target_select = self.query_one("#target_profile_select")
        if not target_select.value:
            self.query_one("#status").update("Please select a target profile.")
            return
        
        target_index = int(target_select.value)
        target_profile = self.target_profiles[target_index]
        
        # Get selected data types
        data_types = list(self.selected_data_types)
        
        if not data_types:
            self.query_one("#status").update("Please select at least one data type to migrate.")
            return
        
        # Switch to progress screen
        self.app.push_screen(MigrationProgressScreen(
            self.source_profiles,
            target_profile,
            data_types
        ))
    
    def action_back(self) -> None:
        """Action to go back to the previous screen."""
        self.app.pop_screen()
    
    def action_quit(self) -> None:
        """Action to quit the application."""
        self.app.exit()


class MigrationProgressScreen(Screen):
    """Screen for showing migration progress."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(
        self,
        source_profiles: List[Dict[str, Any]],
        target_profile: Dict[str, Any],
        data_types: List[str],
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.source_profiles = source_profiles
        self.target_profile = target_profile
        self.data_types = data_types
        self.migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
        self.current_profile_index = 0
        self.migration_results = []
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Label("Migration in progress...", id="status")
            
            with Vertical(id="progress_container"):
                yield Label("Preparing migration...", id="current_operation")
                yield Label("", id="progress_details")
            
            with Horizontal(id="actions"):
                yield Button("Done", id="done", disabled=True)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Event handler called when the screen is mounted."""
        # Start migration in a separate task
        asyncio.create_task(self.run_migration())
    
    async def run_migration(self) -> None:
        """Run the migration process asynchronously."""
        status = self.query_one("#status")
        current_operation = self.query_one("#current_operation")
        progress_details = self.query_one("#progress_details")
        
        # Create backup of target profile
        status.update("Creating backup of target profile...")
        backup_path = self.backup_manager.create_backup(
            self.target_profile["path"],
            self.target_profile["browser_id"],
            self.target_profile["name"]
        )
        
        if backup_path:
            progress_details.update(f"Backup created: {backup_path}")
        else:
            progress_details.update("Warning: Failed to create backup, continuing without backup")
        
        # Migrate each source profile
        for i, source_profile in enumerate(self.source_profiles):
            self.current_profile_index = i
            
            source_browser = BROWSERS.get(source_profile["browser_id"], {}).get("name", "Unknown Browser")
            target_browser = BROWSERS.get(self.target_profile["browser_id"], {}).get("name", "Unknown Browser")
            
            status.update(f"Migrating profile {i+1} of {len(self.source_profiles)}")
            current_operation.update(f"Migrating from {source_browser} to {target_browser}")
            
            # Perform migration
            result = self.migrator.migrate_profile(
                source_profile,
                self.target_profile,
                self.data_types,
                {"backup": False}  # We already created a backup
            )
            
            self.migration_results.append(result)
            
            # Update progress details
            if result["success"]:
                migrated_items = sum(
                    result["migrated_data"].get(dt, {}).get("migrated_items", 0)
                    for dt in self.data_types
                )
                progress_details.update(f"Successfully migrated {migrated_items} items")
            else:
                errors = result.get("errors", [])
                error_msg = errors[0] if errors else "Unknown error"
                progress_details.update(f"Migration completed with errors: {error_msg}")
            
            # Yield to allow UI updates
            await asyncio.sleep(0.1)
        
        # Migration complete
        status.update("Migration complete!")
        current_operation.update("All profiles migrated successfully")
        
        # Enable done button
        self.query_one("#done").disabled = False
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler for button presses."""
        if event.button.id == "done":
            # Return to main screen
            while len(self.app.screen_stack) > 1:
                self.app.pop_screen()
    
    def action_quit(self) -> None:
        """Action to quit the application."""
        self.app.exit()


class FloorperTUI(App):
    """Main Floorper TUI application."""
    
    TITLE = "Floorper - Browser Profile Migration Tool"
    SUB_TITLE = "Migrate profiles between browsers"
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    
    #status {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    #profiles_container {
        width: 100%;
        height: auto;
        margin: 1 0;
    }
    
    #actions {
        width: 100%;
        height: auto;
        align: right middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .panel {
        width: 1fr;
        height: auto;
        border: solid $accent;
        padding: 1;
        margin: 0 1;
    }
    
    .panel-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    .selected {
        background: $accent-darken-2;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("floorper.log")
            ]
        )
    
    def on_mount(self) -> None:
        """Event handler called when the app is mounted."""
        # Start with the browser detection screen
        self.push_screen(BrowserDetectionScreen())
    
    def action_quit(self) -> None:
        """Action to quit the application."""
        self.exit()


def main():
    """Run the Floorper TUI application."""
    app = FloorperTUI()
    app.run()


if __name__ == "__main__":
    main()
