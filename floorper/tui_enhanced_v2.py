"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides an enhanced TUI (Text-based User Interface) using Textual.
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
from floorper.core import BrowserDetector, ProfileMigrator
from floorper.utils import get_platform, get_app_info, get_floorp_profiles, get_theme_colors
from floorper.backup import BackupManager
from floorper.retro import RetroProfileHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('floorper.tui')

# Theme definitions
THEMES = {
    "dark": {
        "background": "#121212",
        "surface": "#1E1E1E",
        "primary": "#BB86FC",
        "secondary": "#03DAC6",
        "error": "#CF6679",
        "success": "#4CAF50",
        "warning": "#FFAB00",
        "text": "#FFFFFF",
        "text-muted": "#BBBBBB",
        "border": "#333333",
    },
    "light": {
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "primary": "#6200EE",
        "secondary": "#03DAC6",
        "error": "#B00020",
        "success": "#4CAF50",
        "warning": "#FF6D00",
        "text": "#000000",
        "text-muted": "#666666",
        "border": "#DDDDDD",
    },
    "floorp": {
        "background": "#1A1B26",
        "surface": "#24283B",
        "primary": "#7AA2F7",
        "secondary": "#BB9AF7",
        "error": "#F7768E",
        "success": "#9ECE6A",
        "warning": "#E0AF68",
        "text": "#C0CAF5",
        "text-muted": "#565F89",
        "border": "#414868",
    },
    "retro": {
        "background": "#000000",
        "surface": "#0A0A0A",
        "primary": "#00FF00",
        "secondary": "#00FFFF",
        "error": "#FF0000",
        "success": "#00FF00",
        "warning": "#FFFF00",
        "text": "#00FF00",
        "text-muted": "#008800",
        "border": "#00FF00",
    },
    "sunset": {
        "background": "#282C34",
        "surface": "#3E4451",
        "primary": "#E06C75",
        "secondary": "#56B6C2",
        "error": "#BE5046",
        "success": "#98C379",
        "warning": "#E5C07B",
        "text": "#ABB2BF",
        "text-muted": "#636D83",
        "border": "#4B5263",
    }
}

class AnimatedLogo(Static):
    """An animated Floorper logo widget."""
    
    DEFAULT_CSS = """
    AnimatedLogo {
        width: 100%;
        height: 5;
        content-align: center middle;
        text-style: bold;
        color: $primary;
    }
    """
    
    def __init__(self):
        """Initialize the animated logo."""
        super().__init__()
        self.frame = 0
        self.frames = [
            "╔═╗╦  ╔═╗╔═╗╦═╗╔═╗╔═╗╦═╗",
            "╠╣ ║  ║ ║║ ║╠╦╝╠═╝║╣ ╠╦╝",
            "╚  ╩═╝╚═╝╚═╝╩╚═╩  ╚═╝╩╚═"
        ]
        self.animation_speed = 0.5  # seconds per frame
        self.last_update = time.time()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.set_interval(0.1, self.animate)
    
    def animate(self) -> None:
        """Animate the logo."""
        current_time = time.time()
        if current_time - self.last_update >= self.animation_speed:
            self.frame = (self.frame + 1) % len(self.frames)
            self.update(self.frames[self.frame])
            self.last_update = current_time

class ThemeSelector(Widget):
    """A theme selector widget."""
    
    DEFAULT_CSS = """
    ThemeSelector {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface;
        border: solid $border;
        margin: 1 0;
    }
    
    ThemeSelector > Label {
        width: 100%;
        height: 1;
        margin-bottom: 1;
    }
    
    ThemeSelector > Horizontal {
        width: 100%;
        height: auto;
    }
    
    .theme-option {
        width: 1fr;
        height: 3;
        margin: 0 1;
        border: solid $border;
        content-align: center middle;
    }
    
    .theme-option:hover {
        border: solid $primary;
    }
    
    .theme-option-selected {
        border: solid $primary 2;
    }
    
    .theme-dark {
        background: #121212;
        color: #FFFFFF;
    }
    
    .theme-light {
        background: #FAFAFA;
        color: #000000;
    }
    
    .theme-floorp {
        background: #1A1B26;
        color: #7AA2F7;
    }
    
    .theme-retro {
        background: #000000;
        color: #00FF00;
    }
    
    .theme-sunset {
        background: #282C34;
        color: #E06C75;
    }
    """
    
    def __init__(self, current_theme: str = "floorp"):
        """Initialize the theme selector.
        
        Args:
            current_theme: The current theme name
        """
        super().__init__()
        self.current_theme = current_theme
    
    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label("Select Theme:")
        
        with Horizontal():
            for theme in THEMES:
                classes = ["theme-option", f"theme-{theme}"]
                if theme == self.current_theme:
                    classes.append("theme-option-selected")
                
                yield Static(theme.capitalize(), id=f"theme-{theme}", classes=classes)
    
    def on_static_click(self, event: Static.Clicked) -> None:
        """Handle static click events."""
        if event.static.id and event.static.id.startswith("theme-"):
            theme = event.static.id.replace("theme-", "")
            
            # Update selected theme
            self.current_theme = theme
            
            # Update classes
            for static in self.query(".theme-option"):
                if static.id == f"theme-{theme}":
                    static.add_class("theme-option-selected")
                else:
                    static.remove_class("theme-option-selected")
            
            # Post theme changed message
            self.post_message(self.ThemeChanged(theme))
    
    class ThemeChanged(events.Message):
        """Message sent when the theme is changed."""
        
        def __init__(self, theme: str) -> None:
            """Initialize the message.
            
            Args:
                theme: The new theme name
            """
            super().__init__()
            self.theme = theme

class BrowserCard(Static):
    """A card widget representing a detected browser."""
    
    DEFAULT_CSS = """
    BrowserCard {
        width: 100%;
        height: auto;
        min-height: 3;
        padding: 1;
        background: $surface;
        border: solid $border;
        margin-bottom: 1;
    }
    
    BrowserCard:hover {
        border: solid $primary;
    }
    
    BrowserCard > Horizontal {
        width: 100%;
        height: auto;
    }
    
    BrowserCard Label.browser-name {
        width: 30%;
        text-style: bold;
        color: $primary;
    }
    
    BrowserCard Label.browser-path {
        width: 60%;
        color: $text-muted;
    }
    
    BrowserCard Checkbox {
        width: 10%;
        content-align: center middle;
    }
    """
    
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
        with Horizontal():
            yield Checkbox(value=self.browser_selected, id=f"checkbox_{self.browser_id}")
            yield Label(self.browser_name, id=f"name_{self.browser_id}", classes="browser-name")
            yield Label(self.browser_path, id=f"path_{self.browser_id}", classes="browser-path")
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox change events."""
        self.browser_selected = event.value
        self.post_message(self.BrowserSelected(self.browser_id, event.value))
    
    class BrowserSelected(events.Message):
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
    
    DEFAULT_CSS = """
    ProfileCard {
        width: 100%;
        height: auto;
        min-height: 3;
        padding: 1;
        background: $surface;
        border: solid $border;
        margin-bottom: 1;
    }
    
    ProfileCard:hover {
        border: solid $primary;
    }
    
    ProfileCard > Horizontal {
        width: 100%;
        height: auto;
    }
    
    ProfileCard Label.profile-name {
        width: 30%;
        text-style: bold;
        color: $secondary;
    }
    
    ProfileCard Label.profile-path {
        width: 60%;
        color: $text-muted;
    }
    
    ProfileCard Checkbox {
        width: 10%;
        content-align: center middle;
    }
    """
    
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
        with Horizontal():
            yield Checkbox(value=self.profile_selected, id=f"checkbox_{self.profile_id}")
            yield Label(self.profile_name, id=f"name_{self.profile_id}", classes="profile-name")
            yield Label(self.profile_path, id=f"path_{self.profile_id}", classes="profile-path")
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox change events."""
        self.profile_selected = event.value
        self.post_message(self.ProfileSelected(self.profile_id, event.value))
    
    class ProfileSelected(events.Message):
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

class WelcomeScreen(Screen):
    """Welcome screen for the application."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "start", "Start"),
        Binding("t", "toggle_theme", "Toggle Theme"),
    ]
    
    DEFAULT_CSS = """
    WelcomeScreen {
        background: $background;
        color: $text;
    }
    
    #welcome-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    #welcome-panel {
        width: 80%;
        height: auto;
        background: $surface;
        border: solid $primary;
        padding: 2;
    }
    
    #welcome-title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #welcome-subtitle {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        margin-bottom: 2;
    }
    
    #welcome-description {
        width: 100%;
        height: auto;
        margin-bottom: 2;
    }
    
    #welcome-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="welcome-container"):
            with Container(id="welcome-panel"):
                yield AnimatedLogo()
                yield Static("Universal Browser Profile Migration Tool for Floorp", id="welcome-title")
                yield Static("TUI Edition", id="welcome-subtitle")
                
                yield Static(
                    "Welcome to Floorper, a powerful tool for migrating browser profiles to Floorp. "
                    "This application allows you to seamlessly transfer your bookmarks, history, "
                    "passwords, and other data from various browsers to Floorp.",
                    id="welcome-description"
                )
                
                yield ThemeSelector(current_theme="floorp")
                
                with Horizontal(id="welcome-buttons"):
                    yield Button("Start Migration", id="start", variant="primary")
                    yield Button("Quit", id="quit", variant="error")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start":
            self.action_start()
        elif event.button.id == "quit":
            self.action_quit()
    
    def on_theme_selector_theme_changed(self, message: ThemeSelector.ThemeChanged) -> None:
        """Handle theme changed events."""
        self.app.change_theme(message.theme)
    
    def action_start(self) -> None:
        """Start the migration process."""
        self.app.push_screen(BrowserDetectionScreen())
    
    def action_toggle_theme(self) -> None:
        """Toggle between available themes."""
        current_theme = self.app.current_theme
        themes = list(THEMES.keys())
        current_index = themes.index(current_theme) if current_theme in themes else 0
        next_index = (current_index + 1) % len(themes)
        next_theme = themes[next_index]
        self.app.change_theme(next_theme)
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class BrowserDetectionScreen(Screen):
    """Screen for detecting browsers."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
        Binding("n", "next", "Next"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "select_all", "Select All"),
        Binding("c", "clear_all", "Clear All"),
    ]
    
    DEFAULT_CSS = """
    BrowserDetectionScreen {
        background: $background;
        color: $text;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #subtitle {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        margin-bottom: 2;
    }
    
    #browser-list {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        margin-bottom: 2;
    }
    
    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .empty-message {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
        margin: 2 0;
    }
    
    #loading-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    """
    
    def __init__(self):
        """Initialize the screen."""
        super().__init__()
        self.detector = BrowserDetector()
        self.selected_browsers = {}
        self.is_loading = True
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            yield Static("Browser Detection", id="title")
            yield Static("Select browsers to migrate profiles from:", id="subtitle")
            
            with Container(id="browser-list"):
                with Container(id="loading-container"):
                    yield LoadingIndicator()
                    yield Static("Detecting browsers...", classes="empty-message")
            
            with Horizontal(id="button-row"):
                yield Button("Back", id="back", variant="primary")
                yield Button("Refresh", id="refresh", variant="primary")
                yield Button("Select All", id="select-all", variant="default")
                yield Button("Clear All", id="clear-all", variant="default")
                yield Button("Next", id="next", variant="success")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.detect_browsers()
    
    @work(thread=True)
    async def detect_browsers(self) -> None:
        """Detect installed browsers in a worker thread."""
        self.is_loading = True
        
        # Show loading indicator
        try:
            browser_list = self.query_one("#browser-list")
            loading_container = self.query_one("#loading-container")
        except NoMatches:
            return
        
        # Detect browsers
        browsers = self.detector.detect_browsers()
        
        # Update UI in main thread
        def update_ui():
            # Remove loading container
            loading_container.remove()
            
            # Clear existing browser cards
            for child in browser_list.children:
                if isinstance(child, BrowserCard):
                    child.remove()
            
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
            
            self.is_loading = False
        
        # Schedule UI update on main thread
        self.call_from_thread(update_ui)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "refresh":
            self.action_refresh()
        elif event.button.id == "select-all":
            self.action_select_all()
        elif event.button.id == "clear-all":
            self.action_clear_all()
        elif event.button.id == "next":
            self.action_next()
    
    def on_browser_card_browser_selected(self, message: BrowserCard.BrowserSelected) -> None:
        """Handle browser selection events."""
        if message.selected:
            self.selected_browsers[message.browser_id] = True
        else:
            self.selected_browsers.pop(message.browser_id, None)
    
    def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh the browser list."""
        if not self.is_loading:
            self.detect_browsers()
    
    def action_select_all(self) -> None:
        """Select all browsers."""
        if self.is_loading:
            return
        
        for card in self.query(BrowserCard):
            checkbox = card.query_one(Checkbox)
            checkbox.value = True
    
    def action_clear_all(self) -> None:
        """Clear all browser selections."""
        if self.is_loading:
            return
        
        for card in self.query(BrowserCard):
            checkbox = card.query_one(Checkbox)
            checkbox.value = False
    
    def action_next(self) -> None:
        """Proceed to the next screen."""
        if self.is_loading:
            return
        
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
        Binding("a", "select_all", "Select All"),
        Binding("c", "clear_all", "Clear All"),
    ]
    
    DEFAULT_CSS = """
    ProfileSelectionScreen {
        background: $background;
        color: $text;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #subtitle {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        margin-bottom: 2;
    }
    
    #profile-list {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        margin-bottom: 2;
    }
    
    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .empty-message {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
        margin: 2 0;
    }
    
    #loading-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    """
    
    def __init__(self, selected_browsers: List[str]):
        """Initialize the screen.
        
        Args:
            selected_browsers: List of selected browser identifiers
        """
        super().__init__()
        self.selected_browsers = selected_browsers
        self.detector = BrowserDetector()
        self.selected_profiles = {}
        self.is_loading = True
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            yield Static("Profile Selection", id="title")
            yield Static("Select profiles to migrate to Floorp:", id="subtitle")
            
            with Container(id="profile-list"):
                with Container(id="loading-container"):
                    yield LoadingIndicator()
                    yield Static("Detecting profiles...", classes="empty-message")
            
            with Horizontal(id="button-row"):
                yield Button("Back", id="back", variant="primary")
                yield Button("Refresh", id="refresh", variant="primary")
                yield Button("Select All", id="select-all", variant="default")
                yield Button("Clear All", id="clear-all", variant="default")
                yield Button("Next", id="next", variant="success")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.detect_profiles()
    
    @work(thread=True)
    async def detect_profiles(self) -> None:
        """Detect browser profiles in a worker thread."""
        self.is_loading = True
        
        # Show loading indicator
        try:
            profile_list = self.query_one("#profile-list")
            loading_container = self.query_one("#loading-container")
        except NoMatches:
            return
        
        # Detect profiles for selected browsers
        all_profiles = []
        
        for browser_id in self.selected_browsers:
            profiles = self.detector.get_profiles(browser_id)
            
            for profile in profiles:
                profile['browser_id'] = browser_id
                all_profiles.append(profile)
        
        # Update UI in main thread
        def update_ui():
            # Remove loading container
            loading_container.remove()
            
            # Clear existing profile cards
            for child in profile_list.children:
                if isinstance(child, ProfileCard):
                    child.remove()
            
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
            
            self.is_loading = False
        
        # Schedule UI update on main thread
        self.call_from_thread(update_ui)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "refresh":
            self.action_refresh()
        elif event.button.id == "select-all":
            self.action_select_all()
        elif event.button.id == "clear-all":
            self.action_clear_all()
        elif event.button.id == "next":
            self.action_next()
    
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
        if not self.is_loading:
            self.detect_profiles()
    
    def action_select_all(self) -> None:
        """Select all profiles."""
        if self.is_loading:
            return
        
        for card in self.query(ProfileCard):
            checkbox = card.query_one(Checkbox)
            checkbox.value = True
    
    def action_clear_all(self) -> None:
        """Clear all profile selections."""
        if self.is_loading:
            return
        
        for card in self.query(ProfileCard):
            checkbox = card.query_one(Checkbox)
            checkbox.value = False
    
    def action_next(self) -> None:
        """Proceed to the next screen."""
        if self.is_loading:
            return
        
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
    
    DEFAULT_CSS = """
    FloorpProfileSelectionScreen {
        background: $background;
        color: $text;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #subtitle {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        margin-bottom: 2;
    }
    
    #floorp-profile-list {
        width: 100%;
        height: auto;
        margin-bottom: 2;
    }
    
    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .profile-option {
        width: 100%;
        height: auto;
        min-height: 3;
        padding: 1;
        background: $surface;
        border: solid $border;
        margin-bottom: 1;
    }
    
    .profile-option:hover {
        border: solid $primary;
    }
    
    .profile-option-selected {
        border: solid $primary 2;
    }
    
    .profile-name {
        text-style: bold;
        color: $primary;
    }
    
    .profile-path {
        color: $text-muted;
    }
    """
    
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
        
        with Container(id="main-container"):
            yield Static("Floorp Profile Selection", id="title")
            yield Static("Select a Floorp profile to migrate to:", id="subtitle")
            
            with Container(id="floorp-profile-list"):
                # Floorp profile options will be added here
                pass
            
            with Horizontal(id="button-row"):
                yield Button("Back", id="back", variant="primary")
                yield Button("Next", id="next", variant="success")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        self.show_floorp_profiles()
    
    def show_floorp_profiles(self) -> None:
        """Show Floorp profiles."""
        # Clear existing profile options
        profile_list = self.query_one("#floorp-profile-list")
        profile_list.remove_children()
        
        # Add profile options
        for i, profile in enumerate(self.floorp_profiles):
            with Container(classes="profile-option", id=f"profile-{i}"):
                yield Static(f"Name: {profile['name']}", classes="profile-name")
                yield Static(f"Path: {profile['path']}", classes="profile-path")
    
    def on_container_click(self, event: Container.Clicked) -> None:
        """Handle container click events."""
        if isinstance(event.container, Container) and event.container.id and event.container.id.startswith("profile-"):
            # Get profile index
            profile_index = int(event.container.id.split("-")[1])
            
            # Update selected profile
            self.selected_floorp_profile = self.floorp_profiles[profile_index]['path']
            
            # Update UI
            for container in self.query(".profile-option"):
                if container.id == event.container.id:
                    container.add_class("profile-option-selected")
                else:
                    container.remove_class("profile-option-selected")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "next":
            self.action_next()
    
    def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()
    
    def action_next(self) -> None:
        """Proceed to the next screen."""
        if not self.selected_floorp_profile:
            self.notify("Please select a Floorp profile.", severity="error")
            return
        
        # Pass selected profiles and Floorp profile to the next screen
        self.app.push_screen(MigrationOptionsScreen(
            self.selected_profiles,
            self.selected_floorp_profile
        ))
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class MigrationOptionsScreen(Screen):
    """Screen for configuring migration options."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "back", "Back"),
        Binding("n", "next", "Next"),
    ]
    
    DEFAULT_CSS = """
    MigrationOptionsScreen {
        background: $background;
        color: $text;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #subtitle {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        margin-bottom: 2;
    }
    
    #options-container {
        width: 100%;
        height: auto;
        background: $surface;
        border: solid $border;
        padding: 1;
        margin-bottom: 2;
    }
    
    .option-group {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding-bottom: 1;
        border-bottom: solid $border;
    }
    
    .option-group-title {
        width: 100%;
        height: auto;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    .option-row {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }
    
    .option-label {
        width: 70%;
        height: auto;
    }
    
    .option-control {
        width: 30%;
        height: auto;
        content-align: right middle;
    }
    
    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(self, selected_profiles: List[str], floorp_profile: str):
        """Initialize the screen.
        
        Args:
            selected_profiles: List of selected profile identifiers
            floorp_profile: Path to the selected Floorp profile
        """
        super().__init__()
        self.selected_profiles = selected_profiles
        self.floorp_profile = floorp_profile
        self.options = {
            'backup_before_migration': True,
            'migrate_bookmarks': True,
            'migrate_history': True,
            'migrate_passwords': True,
            'migrate_cookies': True,
            'migrate_extensions': True,
            'migrate_preferences': True,
            'deduplicate_bookmarks': True,
            'deduplicate_history': True,
            'merge_sessions': True,
        }
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            yield Static("Migration Options", id="title")
            yield Static("Configure migration settings:", id="subtitle")
            
            with Container(id="options-container"):
                with Container(classes="option-group"):
                    yield Static("General Options", classes="option-group-title")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Create backup before migration", classes="option-label")
                        yield Switch(value=self.options['backup_before_migration'], id="backup_before_migration", classes="option-control")
                
                with Container(classes="option-group"):
                    yield Static("Data to Migrate", classes="option-group-title")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Bookmarks", classes="option-label")
                        yield Switch(value=self.options['migrate_bookmarks'], id="migrate_bookmarks", classes="option-control")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("History", classes="option-label")
                        yield Switch(value=self.options['migrate_history'], id="migrate_history", classes="option-control")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Passwords", classes="option-label")
                        yield Switch(value=self.options['migrate_passwords'], id="migrate_passwords", classes="option-control")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Cookies", classes="option-label")
                        yield Switch(value=self.options['migrate_cookies'], id="migrate_cookies", classes="option-control")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Extensions", classes="option-label")
                        yield Switch(value=self.options['migrate_extensions'], id="migrate_extensions", classes="option-control")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Preferences", classes="option-label")
                        yield Switch(value=self.options['migrate_preferences'], id="migrate_preferences", classes="option-control")
                
                with Container(classes="option-group"):
                    yield Static("Advanced Options", classes="option-group-title")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Deduplicate bookmarks", classes="option-label")
                        yield Switch(value=self.options['deduplicate_bookmarks'], id="deduplicate_bookmarks", classes="option-control")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Deduplicate history", classes="option-label")
                        yield Switch(value=self.options['deduplicate_history'], id="deduplicate_history", classes="option-control")
                    
                    with Horizontal(classes="option-row"):
                        yield Static("Merge sessions", classes="option-label")
                        yield Switch(value=self.options['merge_sessions'], id="merge_sessions", classes="option-control")
            
            with Horizontal(id="button-row"):
                yield Button("Back", id="back", variant="primary")
                yield Button("Start Migration", id="next", variant="success")
        
        yield Footer()
    
    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch change events."""
        if event.switch.id in self.options:
            self.options[event.switch.id] = event.value
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "back":
            self.action_back()
        elif event.button.id == "next":
            self.action_next()
    
    def action_back(self) -> None:
        """Go back to the previous screen."""
        self.app.pop_screen()
    
    def action_next(self) -> None:
        """Proceed to the next screen."""
        # Pass selected profiles, Floorp profile, and options to the next screen
        self.app.push_screen(MigrationScreen(
            self.selected_profiles,
            self.floorp_profile,
            self.options
        ))
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class MigrationScreen(Screen):
    """Screen for migrating profiles."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    DEFAULT_CSS = """
    MigrationScreen {
        background: $background;
        color: $text;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #subtitle {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        margin-bottom: 2;
    }
    
    #migration-status {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }
    
    #status-text {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }
    
    #progress-container {
        width: 100%;
        height: auto;
        margin-bottom: 2;
    }
    
    #migration-log {
        width: 100%;
        height: 1fr;
        background: $surface;
        border: solid $border;
        padding: 1;
        overflow-y: auto;
        margin-bottom: 2;
    }
    
    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    .success {
        color: $success;
    }
    
    .error {
        color: $error;
    }
    
    .warning {
        color: $warning;
    }
    
    .info {
        color: $secondary;
    }
    """
    
    def __init__(self, selected_profiles: List[str], floorp_profile: str, options: Dict[str, bool]):
        """Initialize the screen.
        
        Args:
            selected_profiles: List of selected profile identifiers
            floorp_profile: Path to the selected Floorp profile
            options: Migration options
        """
        super().__init__()
        self.selected_profiles = selected_profiles
        self.floorp_profile = floorp_profile
        self.options = options
        self.migrator = ProfileMigrator()
        self.backup_manager = BackupManager()
        self.current_profile_index = 0
        self.migration_successful = False
        self.total_profiles = len(selected_profiles)
        self.current_step = "preparing"
        self.steps = ["preparing", "backup", "migration", "cleanup", "complete"]
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            yield Static("Migration", id="title")
            yield Static("Migrating profiles to Floorp...", id="subtitle")
            
            with Container(id="migration-status"):
                yield Static("Preparing migration...", id="status-text")
                
                with Container(id="progress-container"):
                    yield ProgressBar(total=100, id="progress-bar")
            
            with ScrollableContainer(id="migration-log"):
                # Migration log will be added here
                pass
            
            with Horizontal(id="button-row"):
                yield Button("Cancel", id="cancel", variant="error")
                yield Button("Finish", id="finish", variant="success", disabled=True)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle the mount event."""
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
        self.run_worker(self.migrate_profiles, thread=True)
    
    @work(thread=True)
    async def migrate_profiles(self) -> None:
        """Migrate profiles in a worker thread."""
        log_container = self.query_one("#migration-log")
        progress_bar = self.query_one("#progress-bar")
        
        # Calculate total steps
        total_steps = len(self.steps) + self.total_profiles - 1
        progress_bar.total = total_steps
        current_step = 0
        
        # Log migration start
        self.log_message(log_container, "Starting migration process...", "info")
        
        # Create backup if requested
        if self.options.get('backup_before_migration', True):
            self.current_step = "backup"
            current_step += 1
            progress_bar.progress = current_step
            
            self.call_from_thread(self.query_one("#status-text").update, "Creating backup...")
            self.log_message(log_container, "Creating backup of Floorp profile...", "info")
            
            try:
                backup_path = self.backup_manager.create_backup(self.floorp_profile)
                self.log_message(log_container, f"Backup created successfully at: {backup_path}", "success")
            except Exception as e:
                self.log_message(log_container, f"Failed to create backup: {str(e)}", "error")
                self.log_message(log_container, "Continuing without backup...", "warning")
        
        # Process each profile
        self.current_step = "migration"
        for i, profile_id in enumerate(self.selected_profiles):
            # Update status
            self.current_profile_index = i
            current_step += 1
            progress_bar.progress = current_step
            
            # Parse profile ID
            browser_id, profile_path = profile_id.split(':', 1)
            
            # Update status text
            status_text = f"Migrating profile {i+1}/{self.total_profiles}: {profile_path}"
            self.call_from_thread(self.query_one("#status-text").update, status_text)
            
            # Log migration start
            self.log_message(log_container, f"Migrating {browser_id} profile: {profile_path}", "info")
            
            try:
                # Perform migration
                result = self.migrator.migrate_profile(
                    browser_id=browser_id,
                    source_profile=profile_path,
                    target_profile=self.floorp_profile,
                    options=self.options
                )
                
                # Log migration result
                if result.get('success', False):
                    self.log_message(log_container, f"✓ Successfully migrated {browser_id} profile", "success")
                    
                    # Log details
                    if 'details' in result:
                        for detail in result['details']:
                            self.log_message(log_container, f"  - {detail}", "info")
                else:
                    self.log_message(log_container, f"✗ Failed to migrate {browser_id} profile: {result.get('error', 'Unknown error')}", "error")
            except Exception as e:
                # Log migration error
                self.log_message(log_container, f"✗ Error migrating {browser_id} profile: {str(e)}", "error")
        
        # Cleanup
        self.current_step = "cleanup"
        current_step += 1
        progress_bar.progress = current_step
        
        self.call_from_thread(self.query_one("#status-text").update, "Cleaning up...")
        self.log_message(log_container, "Performing cleanup...", "info")
        
        # Complete
        self.current_step = "complete"
        current_step += 1
        progress_bar.progress = current_step
        
        self.call_from_thread(self.query_one("#status-text").update, "Migration completed")
        self.log_message(log_container, "Migration process completed successfully!", "success")
        
        # Enable finish button
        self.call_from_thread(self.query_one("#finish").disabled, False)
        
        # Set migration as successful
        self.migration_successful = True
    
    def log_message(self, container: Widget, message: str, level: str = "info") -> None:
        """Log a message to the migration log.
        
        Args:
            container: Container widget to add the message to
            message: Message text
            level: Message level (info, success, warning, error)
        """
        self.call_from_thread(container.mount, Static(message, classes=level))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "cancel":
            self.action_quit()
        elif event.button.id == "finish":
            self.action_finish()
    
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
        Binding("n", "new", "New Migration"),
    ]
    
    DEFAULT_CSS = """
    SummaryScreen {
        background: $background;
        color: $text;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #title {
        width: 100%;
        height: auto;
        content-align: center middle;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    
    #subtitle {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        margin-bottom: 2;
    }
    
    #summary-container {
        width: 100%;
        height: auto;
        background: $surface;
        border: solid $success;
        padding: 2;
        margin-bottom: 2;
    }
    
    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            yield Static("Migration Summary", id="title")
            yield Static("Profile migration completed successfully!", id="subtitle")
            
            with Container(id="summary-container"):
                yield Static("Your browser profiles have been migrated to Floorp.")
                yield Static("You can now launch Floorp to access your migrated data.")
                yield Static("")
                yield Static("Thank you for using Floorper!")
            
            with Horizontal(id="button-row"):
                yield Button("Launch Floorp", id="launch", variant="primary")
                yield Button("New Migration", id="new", variant="success")
                yield Button("Quit", id="quit", variant="error")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "launch":
            self.launch_floorp()
        elif event.button.id == "new":
            self.action_new()
        elif event.button.id == "quit":
            self.action_quit()
    
    def launch_floorp(self) -> None:
        """Launch Floorp."""
        from floorper.utils import launch_browser
        launch_browser('floorp')
        self.notify("Launching Floorp...")
    
    def action_new(self) -> None:
        """Start a new migration."""
        self.app.push_screen(BrowserDetectionScreen())
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

class FloorperTUI(App):
    """Main Floorper TUI application."""
    
    TITLE = "Floorper - Universal Browser Profile Migration Tool for Floorp"
    SUB_TITLE = "TUI Edition"
    
    DEFAULT_CSS = """
    * {
        transition: background 500ms in_out_cubic, color 500ms in_out_cubic;
    }
    
    Screen {
        background: $background;
        color: $text;
    }
    
    LoadingIndicator {
        color: $primary;
    }
    
    ProgressBar {
        width: 100%;
        height: 1;
    }
    
    ProgressBar > .bar {
        color: $primary 60%;
    }
    
    ProgressBar > .complete {
        color: $success 60%;
    }
    
    Select {
        width: 100%;
        height: auto;
        background: $surface;
        border: solid $border;
        padding: 1;
    }
    
    Select:focus {
        border: solid $primary;
    }
    
    Button {
        background: $surface;
        color: $text;
        border: solid $border;
    }
    
    Button:hover {
        background: $surface 80%;
        border: solid $primary;
    }
    
    Button.primary {
        background: $primary 30%;
        color: $primary;
        border: solid $primary 60%;
    }
    
    Button.primary:hover {
        background: $primary 40%;
    }
    
    Button.success {
        background: $success 30%;
        color: $success;
        border: solid $success 60%;
    }
    
    Button.success:hover {
        background: $success 40%;
    }
    
    Button.error {
        background: $error 30%;
        color: $error;
        border: solid $error 60%;
    }
    
    Button.error:hover {
        background: $error 40%;
    }
    
    Button:disabled {
        background: $surface 20%;
        color: $text-muted;
        border: solid $border;
    }
    
    Checkbox {
        background: $surface;
        color: $primary;
    }
    
    Switch {
        background: $surface;
        color: $primary;
    }
    
    Header {
        background: $surface;
        color: $text;
        border-bottom: solid $border;
    }
    
    Footer {
        background: $surface;
        color: $text;
        border-top: solid $border;
    }
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.current_theme = "floorp"
    
    def on_mount(self) -> None:
        """Handle the mount event."""
        # Set theme colors
        self.change_theme(self.current_theme)
    
    def compose(self) -> ComposeResult:
        """Compose the application."""
        # Start with the welcome screen
        yield WelcomeScreen()
    
    def change_theme(self, theme_name: str) -> None:
        """Change the application theme.
        
        Args:
            theme_name: Name of the theme to apply
        """
        if theme_name not in THEMES:
            theme_name = "floorp"
        
        self.current_theme = theme_name
        theme = THEMES[theme_name]
        
        # Apply theme colors
        self.app.styles.background = theme["background"]
        self.app.styles.color = theme["text"]
        
        # Set CSS variables
        for name, color in theme.items():
            self.app.styles.set_rule(f"$", f"{name}", color)
        
        # Notify user
        self.notify(f"Theme changed to {theme_name.capitalize()}")

def main():
    """Main entry point for the TUI application."""
    app = FloorperTUI()
    app.run()

if __name__ == "__main__":
    main()
