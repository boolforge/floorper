"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides an enhanced TUI (Text-based User Interface) using Textual.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static, Label, Select, ProgressBar, Checkbox
from textual.screen import Screen
from textual.binding import Binding
from textual.reactive import reactive

# Import local modules
from floorper.core import BrowserDetector, ProfileMigrator
from floorper.utils import get_platform, get_app_info, get_floorp_profiles, get_theme_colors

# Setup logging
logger = logging.getLogger('floorper.tui')

class BrowserCard(Static):
    """A card widget representing a detected browser."""
    
    browser_id = reactive("")
    browser_name = reactive("")
    browser_path = reactive("")
    browser_icon = reactive("")
    browser_selected = reactive(False)
    
    def __init__(self, browser_id: str, browser_name: str, browser_path: str, browser_icon: str = ""):
        """Initialize the browser card.
        
        Args:
            browser_id: Browser identifier
            browser_name: Browser display name
            browser_path: Path to the browser executable or profile
            browser_icon: Path to the browser icon (optional)
        """
        super().__init__()
        self.browser_id = browser_id
        self.browser_name = browser_name
        self.browser_path = browser_path
        self.browser_icon = browser_icon
        self.browser_selected = False
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Horizontal(
            Checkbox(value=self.browser_selected, id=f"checkbox_{self.browser_id}"),
            Label(self.browser_name, id=f"name_{self.browser_id}"),
            Label(self.browser_path, id=f"path_{self.browser_id}"),
            classes="browser-card"
        )
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox change events."""
        self.browser_selected = event.value
        self.app.post_message(self.BrowserSelected(self.browser_id, event.value))
    
    class BrowserSelected(Static.Message):
        """Message sent when a browser is selected or deselected."""
        
        def __init__(self, browser_id: str, selected: bool) -> None:
            """Initialize the message.
            
            Args:
                browser_id: Browser identifier
                selected: Whether the browser is selected
            """
            super().__init__()
            self.browser_id = browser_id
            self.selected = selected

class ProfileCard(Static):
    """A card widget representing a browser profile."""
    
    profile_id = reactive("")
    profile_name = reactive("")
    profile_path = reactive("")
    profile_selected = reactive(False)
    
    def __init__(self, profile_id: str, profile_name: str, profile_path: str):
        """Initialize the profile card.
        
        Args:
            profile_id: Profile identifier
            profile_name: Profile display name
            profile_path: Path to the profile
        """
        super().__init__()
        self.profile_id = profile_id
        self.profile_name = profile_name
        self.profile_path = profile_path
        self.profile_selected = False
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Horizontal(
            Checkbox(value=self.profile_selected, id=f"checkbox_{self.profile_id}"),
            Label(self.profile_name, id=f"name_{self.profile_id}"),
            Label(self.profile_path, id=f"path_{self.profile_id}"),
            classes="profile-card"
        )
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox change events."""
        self.profile_selected = event.value
        self.app.post_message(self.ProfileSelected(self.profile_id, event.value))
    
    class ProfileSelected(Static.Message):
        """Message sent when a profile is selected or deselected."""
        
        def __init__(self, profile_id: str, selected: bool) -> None:
            """Initialize the message.
            
            Args:
                profile_id: Profile identifier
                selected: Whether the profile is selected
            """
            super().__init__()
            self.profile_id = profile_id
            self.selected = selected

class BrowserDetectionScreen(Screen):
    """Screen for detecting browsers."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "next", "Next"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        """Initialize the screen."""
        super().__init__()
        self.detector = BrowserDetector()
        self.selected_browsers = {}
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Static("# Browser Detection", classes="title")
            yield Static("Select browsers to migrate profiles from:", classes="subtitle")
            
            with Container(id="browser-list"):
                # Browser cards will be added here
                pass
            
            with Horizontal(classes="button-row"):
                yield Button("Refresh", id="refresh", variant="primary")
                yield Button("Next", id="next", variant="success")
                yield Button("Quit", id="quit", variant="error")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.detect_browsers()
    
    def detect_browsers(self) -> None:
        """Detect installed browsers."""
        # Clear existing browser cards
        browser_list = self.query_one("#browser-list")
        browser_list.remove_children()
        
        # Detect browsers
        browsers = self.detector.detect_browsers()
        
        if not browsers:
            browser_list.mount(Static("No browsers detected.", classes="empty-message"))
            return
        
        # Add browser cards
        for browser_id, browser_info in browsers.items():
            card = BrowserCard(
                browser_id=browser_id,
                browser_name=browser_info.get('name', browser_id),
                browser_path=browser_info.get('path', ''),
                browser_icon=browser_info.get('icon', '')
            )
            browser_list.mount(card)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "refresh":
            self.detect_browsers()
        elif event.button.id == "next":
            self.action_next()
        elif event.button.id == "quit":
            self.action_quit()
    
    def on_browser_card_browser_selected(self, message: BrowserCard.BrowserSelected) -> None:
        """Handle browser selection events."""
        if message.selected:
            self.selected_browsers[message.browser_id] = True
        else:
            self.selected_browsers.pop(message.browser_id, None)
    
    def action_refresh(self) -> None:
        """Refresh the browser list."""
        self.detect_browsers()
    
    def action_next(self) -> None:
        """Proceed to the next screen."""
        if not self.selected_browsers:
            self.notify("Please select at least one browser.", severity="error")
            return
        
        # Pass selected browsers to the next screen
        self.app.push_screen(ProfileSelectionScreen(list(self.selected_browsers.keys())))
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class ProfileSelectionScreen(Screen):
    """Screen for selecting profiles."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
        Binding("n", "next", "Next"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, selected_browsers: List[str]):
        """Initialize the screen.
        
        Args:
            selected_browsers: List of selected browser identifiers
        """
        super().__init__()
        self.selected_browsers = selected_browsers
        self.detector = BrowserDetector()
        self.selected_profiles = {}
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Static("# Profile Selection", classes="title")
            yield Static("Select profiles to migrate to Floorp:", classes="subtitle")
            
            with Container(id="profile-list"):
                # Profile cards will be added here
                pass
            
            with Horizontal(classes="button-row"):
                yield Button("Back", id="back", variant="primary")
                yield Button("Refresh", id="refresh", variant="primary")
                yield Button("Next", id="next", variant="success")
                yield Button("Quit", id="quit", variant="error")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.detect_profiles()
    
    def detect_profiles(self) -> None:
        """Detect browser profiles."""
        # Clear existing profile cards
        profile_list = self.query_one("#profile-list")
        profile_list.remove_children()
        
        # Detect profiles for selected browsers
        all_profiles = []
        
        for browser_id in self.selected_browsers:
            profiles = self.detector.get_profiles(browser_id)
            
            for profile in profiles:
                profile['browser_id'] = browser_id
                all_profiles.append(profile)
        
        if not all_profiles:
            profile_list.mount(Static("No profiles detected.", classes="empty-message"))
            return
        
        # Add profile cards
        for profile in all_profiles:
            profile_id = f"{profile['browser_id']}:{profile.get('id', '')}"
            card = ProfileCard(
                profile_id=profile_id,
                profile_name=f"{profile.get('name', '')} ({profile['browser_id']})",
                profile_path=profile.get('path', '')
            )
            profile_list.mount(card)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "refresh":
            self.detect_profiles()
        elif event.button.id == "next":
            self.action_next()
        elif event.button.id == "quit":
            self.action_quit()
    
    def on_profile_card_profile_selected(self, message: ProfileCard.ProfileSelected) -> None:
        """Handle profile selection events."""
        if message.selected:
            self.selected_profiles[message.profile_id] = True
        else:
            self.selected_profiles.pop(message.profile_id, None)
    
    def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh the profile list."""
        self.detect_profiles()
    
    def action_next(self) -> None:
        """Proceed to the next screen."""
        if not self.selected_profiles:
            self.notify("Please select at least one profile.", severity="error")
            return
        
        # Get Floorp profiles
        floorp_profiles = get_floorp_profiles()
        
        if not floorp_profiles:
            self.notify("No Floorp profiles detected. Please install Floorp first.", severity="error")
            return
        
        # Pass selected profiles to the next screen
        self.app.push_screen(FloorpProfileSelectionScreen(
            list(self.selected_profiles.keys()),
            floorp_profiles
        ))
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class FloorpProfileSelectionScreen(Screen):
    """Screen for selecting Floorp profiles."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
        Binding("n", "next", "Next"),
    ]
    
    def __init__(self, selected_profiles: List[str], floorp_profiles: List[Dict[str, Any]]):
        """Initialize the screen.
        
        Args:
            selected_profiles: List of selected profile identifiers
            floorp_profiles: List of Floorp profiles
        """
        super().__init__()
        self.selected_profiles = selected_profiles
        self.floorp_profiles = floorp_profiles
        self.selected_floorp_profile = None
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Static("# Floorp Profile Selection", classes="title")
            yield Static("Select a Floorp profile to migrate to:", classes="subtitle")
            
            with Container(id="floorp-profile-list"):
                # Floorp profile options will be added here
                pass
            
            with Horizontal(classes="button-row"):
                yield Button("Back", id="back", variant="primary")
                yield Button("Next", id="next", variant="success")
                yield Button("Quit", id="quit", variant="error")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.show_floorp_profiles()
    
    def show_floorp_profiles(self) -> None:
        """Show Floorp profiles."""
        # Clear existing profile options
        profile_list = self.query_one("#floorp-profile-list")
        profile_list.remove_children()
        
        # Create profile options
        options = [(profile['path'], profile['name']) for profile in self.floorp_profiles]
        
        # Add profile selector
        profile_list.mount(
            Select(
                options=options,
                prompt="Select Floorp profile",
                id="floorp-profile-select"
            )
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "next":
            self.action_next()
        elif event.button.id == "quit":
            self.action_quit()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select change events."""
        if event.select.id == "floorp-profile-select":
            self.selected_floorp_profile = event.value
    
    def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()
    
    def action_next(self) -> None:
        """Proceed to the next screen."""
        if not self.selected_floorp_profile:
            self.notify("Please select a Floorp profile.", severity="error")
            return
        
        # Pass selected profiles and Floorp profile to the next screen
        self.app.push_screen(MigrationScreen(
            self.selected_profiles,
            self.selected_floorp_profile
        ))
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class MigrationScreen(Screen):
    """Screen for migrating profiles."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
    ]
    
    def __init__(self, selected_profiles: List[str], floorp_profile: str):
        """Initialize the screen.
        
        Args:
            selected_profiles: List of selected profile identifiers
            floorp_profile: Path to the selected Floorp profile
        """
        super().__init__()
        self.selected_profiles = selected_profiles
        self.floorp_profile = floorp_profile
        self.migrator = ProfileMigrator()
        self.current_profile_index = 0
        self.migration_successful = False
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Static("# Migration", classes="title")
            yield Static("Migrating profiles to Floorp...", classes="subtitle")
            
            with Container(id="migration-status"):
                yield Static("Preparing migration...", id="status-text")
                yield ProgressBar(total=100, id="progress-bar")
            
            with Container(id="migration-log"):
                # Migration log will be added here
                pass
            
            with Horizontal(classes="button-row"):
                yield Button("Back", id="back", variant="primary")
                yield Button("Finish", id="finish", variant="success")
                yield Button("Quit", id="quit", variant="error")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        # Disable back button during migration
        self.query_one("#back").disabled = True
        
        # Start migration
        self.start_migration()
    
    def start_migration(self) -> None:
        """Start the migration process."""
        # Update status
        self.query_one("#status-text").update("Starting migration...")
        
        # Set progress bar
        progress_bar = self.query_one("#progress-bar")
        progress_bar.progress = 0
        
        # Start migration in a worker thread
        self.app.run_worker(self.migrate_profiles, thread=True)
    
    async def migrate_profiles(self) -> None:
        """Migrate profiles in a worker thread."""
        # Get total number of profiles
        total_profiles = len(self.selected_profiles)
        
        # Update progress bar
        progress_bar = self.query_one("#progress-bar")
        progress_bar.total = total_profiles
        
        # Create migration log container
        log_container = self.query_one("#migration-log")
        
        # Process each profile
        for i, profile_id in enumerate(self.selected_profiles):
            # Update status
            self.current_profile_index = i
            progress_bar.progress = i
            
            # Parse profile ID
            browser_id, profile_path = profile_id.split(':', 1)
            
            # Update status text
            status_text = f"Migrating profile {i+1}/{total_profiles}: {profile_path}"
            self.call_from_thread(self.query_one("#status-text").update, status_text)
            
            # Log migration start
            log_message = f"Migrating {browser_id} profile: {profile_path}"
            self.call_from_thread(log_container.mount, Static(log_message))
            
            try:
                # Perform migration
                result = self.migrator.migrate_profile(
                    browser_id=browser_id,
                    source_profile=profile_path,
                    target_profile=self.floorp_profile
                )
                
                # Log migration result
                if result.get('success', False):
                    log_message = f"✓ Successfully migrated {browser_id} profile"
                    self.call_from_thread(log_container.mount, Static(log_message, classes="success"))
                else:
                    log_message = f"✗ Failed to migrate {browser_id} profile: {result.get('error', 'Unknown error')}"
                    self.call_from_thread(log_container.mount, Static(log_message, classes="error"))
            except Exception as e:
                # Log migration error
                log_message = f"✗ Error migrating {browser_id} profile: {str(e)}"
                self.call_from_thread(log_container.mount, Static(log_message, classes="error"))
        
        # Update progress bar to completion
        self.call_from_thread(progress_bar.update, total_profiles)
        
        # Update status
        self.call_from_thread(self.query_one("#status-text").update, "Migration completed")
        
        # Enable back button
        self.call_from_thread(self.query_one("#back").enable)
        
        # Set migration as successful
        self.migration_successful = True
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "finish":
            self.action_finish()
        elif event.button.id == "quit":
            self.action_quit()
    
    def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()
    
    def action_finish(self) -> None:
        """Finish the migration process."""
        if self.migration_successful:
            self.app.push_screen(SummaryScreen())
        else:
            self.notify("Migration is still in progress or has failed.", severity="error")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class SummaryScreen(Screen):
    """Screen for showing migration summary."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main"):
            yield Static("# Migration Summary", classes="title")
            yield Static("Profile migration completed successfully!", classes="subtitle")
            
            with Container(id="summary-content"):
                yield Static("Your browser profiles have been migrated to Floorp.")
                yield Static("You can now launch Floorp to access your migrated data.")
            
            with Horizontal(classes="button-row"):
                yield Button("Launch Floorp", id="launch", variant="primary")
                yield Button("New Migration", id="new", variant="success")
                yield Button("Quit", id="quit", variant="error")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "launch":
            self.launch_floorp()
        elif event.button.id == "new":
            self.new_migration()
        elif event.button.id == "quit":
            self.action_quit()
    
    def launch_floorp(self) -> None:
        """Launch Floorp."""
        from floorper.utils import launch_browser
        launch_browser('floorp')
        self.notify("Launching Floorp...")
    
    def new_migration(self) -> None:
        """Start a new migration."""
        self.app.push_screen(BrowserDetectionScreen())
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class FloorperTUI(App):
    """Main Floorper TUI application."""
    
    TITLE = "Floorper - Universal Browser Profile Migration Tool for Floorp"
    SUB_TITLE = "TUI Edition"
    
    CSS = """
    Screen {
        background: $background;
    }
    
    .title {
        text-style: bold;
        content-align: center;
        width: 100%;
        margin: 1 0;
    }
    
    .subtitle {
        text-style: italic;
        content-align: center;
        width: 100%;
        margin: 1 0 2 0;
    }
    
    #main {
        width: 100%;
        height: auto;
        margin: 1 2;
    }
    
    .browser-card, .profile-card {
        width: 100%;
        height: 3;
        margin: 0 0 1 0;
        padding: 0 1;
        border: solid $primary;
    }
    
    .button-row {
        width: 100%;
        height: 3;
        margin: 2 0 0 0;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    
    #migration-status {
        width: 100%;
        height: auto;
        margin: 1 0;
    }
    
    #migration-log {
        width: 100%;
        height: auto;
        margin: 1 0;
        border: solid $primary;
        padding: 1;
        max-height: 20;
        overflow-y: scroll;
    }
    
    .success {
        color: $success;
    }
    
    .error {
        color: $error;
    }
    
    .empty-message {
        text-style: italic;
        color: $text-muted;
    }
    
    #summary-content {
        width: 100%;
        height: auto;
        margin: 2 0;
        padding: 1;
        border: solid $success;
    }
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.theme = get_default_theme()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        # Set theme colors
        theme_colors = get_theme_colors(self.theme)
        
        for name, color in theme_colors.items():
            self.screen.styles.background = theme_colors['background']
            self.screen.styles.color = theme_colors['text']
    
    def compose(self) -> ComposeResult:
        """Compose the application."""
        # Start with the browser detection screen
        yield BrowserDetectionScreen()

def main():
    """Main entry point for the TUI application."""
    app = FloorperTUI()
    app.run()

if __name__ == "__main__":
    main()
