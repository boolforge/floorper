"""
Floorper - Universal Browser Profile Migration Tool for Floorp

This module provides the TUI (Text User Interface) for the Floorper application,
implemented using Rich for a modern, feature-rich terminal interface.
"""

import os
import sys
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Callable

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.style import Style
from rich.live import Live
from rich.tree import Tree
from rich import print as rprint

from floorper.core import FloorperCore

# Setup logging
logger = logging.getLogger('floorper.tui')

class FloorperTUI:
    """
    Text-based user interface for the Floorper application.
    
    This class provides a feature-rich terminal interface for
    browser profile migration using the Rich library.
    """
    
    def __init__(self, controller: Optional[FloorperCore] = None):
        """
        Initialize the TUI.
        
        Args:
            controller: Optional FloorperCore controller instance
        """
        self.controller = controller or FloorperCore()
        self.console = Console()
        
        # State variables
        self.browsers = []
        self.source_browser = None
        self.source_profiles = []
        self.source_profile = None
        self.target_profiles = []
        self.target_profile = None
        self.data_types = ["bookmarks", "history", "passwords", "cookies", 
                          "extensions", "preferences", "sessions"]
        self.selected_data_types = self.data_types.copy()
        self.options = {
            "backup": True,
            "deduplicate": True,
            "merge_strategy": "smart"
        }
        
        logger.info("TUI initialized")
    
    def run(self):
        """Run the TUI application."""
        try:
            self._show_welcome_screen()
            self._detect_browsers()
            self._show_main_menu()
        except KeyboardInterrupt:
            self._exit_application("Operation cancelled by user")
        except Exception as e:
            logger.error(f"Error in TUI: {str(e)}")
            self._exit_application(f"Error: {str(e)}")
    
    def _show_welcome_screen(self):
        """Show the welcome screen."""
        self.console.clear()
        
        # Create welcome panel
        welcome_text = (
            "[bold blue]Floorper[/bold blue] - Universal Browser Profile Migration Tool for Floorp\n\n"
            "This tool helps you migrate profiles from various browsers to Floorp.\n"
            "It supports a wide range of browsers and can migrate bookmarks, history,\n"
            "passwords, cookies, extensions, preferences, and sessions."
        )
        
        welcome_panel = Panel(
            welcome_text,
            title="Welcome to Floorper",
            border_style="green",
            box=ROUNDED,
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
        self.console.print("\nInitializing...", style="italic")
        
        # Simulate initialization
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[green]Loading...", total=100)
            
            for i in range(101):
                progress.update(task, completed=i)
                time.sleep(0.01)
    
    def _detect_browsers(self):
        """Detect installed browsers."""
        self.console.print("\nDetecting browsers...", style="bold yellow")
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[green]Scanning system...", total=100)
            
            # Simulate detection progress
            for i in range(101):
                progress.update(task, completed=i)
                time.sleep(0.01)
            
            # Actual detection
            self.browsers = self.controller.detect_browsers()
        
        # Show detected browsers
        if self.browsers:
            self.console.print(f"\nDetected {len(self.browsers)} browsers:", style="bold green")
            
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("ID", style="dim")
            table.add_column("Name", style="bold")
            table.add_column("Version", style="cyan")
            table.add_column("Path", style="green")
            
            for i, browser in enumerate(self.browsers):
                table.add_row(
                    str(i + 1),
                    browser.get("name", "Unknown"),
                    browser.get("version", "Unknown"),
                    browser.get("path", "Unknown")
                )
            
            self.console.print(table)
        else:
            self.console.print("\nNo browsers detected.", style="bold red")
            self._exit_application("No browsers detected")
        
        # Wait for user input
        self.console.print("\nPress Enter to continue...", style="italic")
        input()
    
    def _show_main_menu(self):
        """Show the main menu."""
        while True:
            self.console.clear()
            
            # Create main menu panel
            menu_text = (
                "[bold]1.[/bold] Select Source Browser\n"
                f"   [{'green' if self.source_browser else 'red'}]"
                f"{self.source_browser.get('name', 'Not selected') if self.source_browser else 'Not selected'}[/]\n\n"
                
                "[bold]2.[/bold] Select Source Profile\n"
                f"   [{'green' if self.source_profile else 'red'}]"
                f"{self.source_profile.get('name', 'Not selected') if self.source_profile else 'Not selected'}[/]\n\n"
                
                "[bold]3.[/bold] Select Target Floorp Profile\n"
                f"   [{'green' if self.target_profile else 'red'}]"
                f"{self.target_profile.get('name', 'Not selected') if self.target_profile else 'Not selected'}[/]\n\n"
                
                "[bold]4.[/bold] Configure Data Types\n"
                f"   [{len(self.selected_data_types)} selected]\n\n"
                
                "[bold]5.[/bold] Configure Options\n\n"
                
                "[bold]6.[/bold] Start Migration\n\n"
                
                "[bold]7.[/bold] Help\n\n"
                
                "[bold]8.[/bold] Exit"
            )
            
            menu_panel = Panel(
                menu_text,
                title="Main Menu",
                border_style="blue",
                box=ROUNDED,
                padding=(1, 2)
            )
            
            self.console.print(menu_panel)
            
            # Get user choice
            choice = Prompt.ask(
                "Enter your choice",
                choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                default="1"
            )
            
            # Process choice
            if choice == "1":
                self._select_source_browser()
            elif choice == "2":
                if not self.source_browser:
                    self.console.print("Please select a source browser first.", style="bold red")
                    self._wait_for_input()
                else:
                    self._select_source_profile()
            elif choice == "3":
                self._select_target_profile()
            elif choice == "4":
                self._configure_data_types()
            elif choice == "5":
                self._configure_options()
            elif choice == "6":
                if self._validate_migration():
                    self._start_migration()
            elif choice == "7":
                self._show_help()
            elif choice == "8":
                self._exit_application("User requested exit")
    
    def _select_source_browser(self):
        """Select a source browser."""
        self.console.clear()
        
        # Create browser selection panel
        title = Panel(
            "Select a source browser",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Create browser table
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Version", style="cyan")
        
        # Filter out Floorp from source browsers
        source_browsers = [b for b in self.browsers if b.get("id") != "floorp"]
        
        for i, browser in enumerate(source_browsers):
            table.add_row(
                str(i + 1),
                browser.get("name", "Unknown"),
                browser.get("version", "Unknown")
            )
        
        self.console.print(table)
        
        # Get user choice
        choice = Prompt.ask(
            "Enter browser ID (or 'c' to cancel)",
            choices=[str(i + 1) for i in range(len(source_browsers))] + ["c"],
            default="c"
        )
        
        if choice == "c":
            return
        
        # Set selected browser
        self.source_browser = source_browsers[int(choice) - 1]
        self.source_profiles = []
        self.source_profile = None
        
        self.console.print(f"Selected browser: {self.source_browser.get('name')}", style="bold green")
        self._wait_for_input()
    
    def _select_source_profile(self):
        """Select a source profile."""
        self.console.clear()
        
        # Create profile selection panel
        title = Panel(
            f"Select a profile from {self.source_browser.get('name')}",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Get profiles
        self.console.print("Detecting profiles...", style="bold yellow")
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[green]Scanning profiles...", total=100)
            
            # Simulate progress
            for i in range(101):
                progress.update(task, completed=i)
                time.sleep(0.01)
            
            # Actual detection
            self.source_profiles = self.controller.get_browser_profiles(self.source_browser.get("id"))
        
        # Show detected profiles
        if self.source_profiles:
            self.console.print(f"\nDetected {len(self.source_profiles)} profiles:", style="bold green")
            
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("ID", style="dim")
            table.add_column("Name", style="bold")
            table.add_column("Path", style="green")
            
            for i, profile in enumerate(self.source_profiles):
                table.add_row(
                    str(i + 1),
                    profile.get("name", "Unknown"),
                    profile.get("path", "Unknown")
                )
            
            self.console.print(table)
            
            # Get user choice
            choice = Prompt.ask(
                "Enter profile ID (or 'c' to cancel)",
                choices=[str(i + 1) for i in range(len(self.source_profiles))] + ["c"],
                default="c"
            )
            
            if choice == "c":
                return
            
            # Set selected profile
            self.source_profile = self.source_profiles[int(choice) - 1]
            self.console.print(f"Selected profile: {self.source_profile.get('name')}", style="bold green")
        else:
            self.console.print("\nNo profiles detected.", style="bold red")
        
        self._wait_for_input()
    
    def _select_target_profile(self):
        """Select a target Floorp profile."""
        self.console.clear()
        
        # Create profile selection panel
        title = Panel(
            "Select a target Floorp profile",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Find Floorp browser
        floorp_browser = next((b for b in self.browsers if b.get("id") == "floorp"), None)
        
        if not floorp_browser:
            self.console.print("Floorp browser not detected.", style="bold red")
            self._wait_for_input()
            return
        
        # Get profiles
        self.console.print("Detecting Floorp profiles...", style="bold yellow")
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[green]Scanning profiles...", total=100)
            
            # Simulate progress
            for i in range(101):
                progress.update(task, completed=i)
                time.sleep(0.01)
            
            # Actual detection
            self.target_profiles = self.controller.get_browser_profiles(floorp_browser.get("id"))
        
        # Show detected profiles
        if self.target_profiles:
            self.console.print(f"\nDetected {len(self.target_profiles)} Floorp profiles:", style="bold green")
            
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("ID", style="dim")
            table.add_column("Name", style="bold")
            table.add_column("Path", style="green")
            
            for i, profile in enumerate(self.target_profiles):
                table.add_row(
                    str(i + 1),
                    profile.get("name", "Unknown"),
                    profile.get("path", "Unknown")
                )
            
            self.console.print(table)
            
            # Get user choice
            choice = Prompt.ask(
                "Enter profile ID (or 'c' to cancel)",
                choices=[str(i + 1) for i in range(len(self.target_profiles))] + ["c"],
                default="c"
            )
            
            if choice == "c":
                return
            
            # Set selected profile
            self.target_profile = self.target_profiles[int(choice) - 1]
            self.console.print(f"Selected profile: {self.target_profile.get('name')}", style="bold green")
        else:
            self.console.print("\nNo Floorp profiles detected.", style="bold red")
        
        self._wait_for_input()
    
    def _configure_data_types(self):
        """Configure data types to migrate."""
        self.console.clear()
        
        # Create data types panel
        title = Panel(
            "Select data types to migrate",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Show data types
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("ID", style="dim")
        table.add_column("Data Type", style="bold")
        table.add_column("Selected", style="green")
        
        for i, data_type in enumerate(self.data_types):
            selected = data_type in self.selected_data_types
            table.add_row(
                str(i + 1),
                data_type.capitalize(),
                "✓" if selected else "✗"
            )
        
        self.console.print(table)
        
        # Options
        self.console.print("\n[bold]Options:[/bold]")
        self.console.print("1-7: Toggle individual data types")
        self.console.print("a: Select all")
        self.console.print("n: Select none")
        self.console.print("s: Save and return")
        
        # Get user choice
        while True:
            choice = Prompt.ask(
                "Enter your choice",
                choices=["1", "2", "3", "4", "5", "6", "7", "a", "n", "s"],
                default="s"
            )
            
            if choice == "s":
                break
            elif choice == "a":
                self.selected_data_types = self.data_types.copy()
            elif choice == "n":
                self.selected_data_types = []
            elif choice in ["1", "2", "3", "4", "5", "6", "7"]:
                index = int(choice) - 1
                data_type = self.data_types[index]
                
                if data_type in self.selected_data_types:
                    self.selected_data_types.remove(data_type)
                else:
                    self.selected_data_types.append(data_type)
            
            # Update table
            self.console.clear()
            self.console.print(title)
            
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("ID", style="dim")
            table.add_column("Data Type", style="bold")
            table.add_column("Selected", style="green")
            
            for i, data_type in enumerate(self.data_types):
                selected = data_type in self.selected_data_types
                table.add_row(
                    str(i + 1),
                    data_type.capitalize(),
                    "✓" if selected else "✗"
                )
            
            self.console.print(table)
            
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("1-7: Toggle individual data types")
            self.console.print("a: Select all")
            self.console.print("n: Select none")
            self.console.print("s: Save and return")
    
    def _configure_options(self):
        """Configure migration options."""
        self.console.clear()
        
        # Create options panel
        title = Panel(
            "Configure Migration Options",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Show current options
        self._display_options()
        
        # Options menu
        self.console.print("\n[bold]Options:[/bold]")
        self.console.print("1: Toggle backup before migration")
        self.console.print("2: Toggle deduplication")
        self.console.print("3: Change merge strategy")
        self.console.print("s: Save and return")
        
        # Get user choice
        while True:
            choice = Prompt.ask(
                "Enter your choice",
                choices=["1", "2", "3", "s"],
                default="s"
            )
            
            if choice == "s":
                break
            elif choice == "1":
                self.options["backup"] = not self.options["backup"]
            elif choice == "2":
                self.options["deduplicate"] = not self.options["deduplicate"]
            elif choice == "3":
                self._change_merge_strategy()
            
            # Update display
            self.console.clear()
            self.console.print(title)
            self._display_options()
            
            self.console.print("\n[bold]Options:[/bold]")
            self.console.print("1: Toggle backup before migration")
            self.console.print("2: Toggle deduplication")
            self.console.print("3: Change merge strategy")
            self.console.print("s: Save and return")
    
    def _display_options(self):
        """Display current options."""
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("Option", style="bold")
        table.add_column("Value", style="green")
        
        table.add_row(
            "Backup before migration",
            "✓" if self.options["backup"] else "✗"
        )
        
        table.add_row(
            "Deduplicate items",
            "✓" if self.options["deduplicate"] else "✗"
        )
        
        strategy_display = {
            "smart": "Smart Merge (Recommended)",
            "append": "Append Only",
            "overwrite": "Overwrite Existing"
        }
        
        table.add_row(
            "Merge strategy",
            strategy_display.get(self.options["merge_strategy"], "Unknown")
        )
        
        self.console.print(table)
    
    def _change_merge_strategy(self):
        """Change the merge strategy."""
        self.console.clear()
        
        # Create strategy panel
        title = Panel(
            "Select Merge Strategy",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Show strategies
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("ID", style="dim")
        table.add_column("Strategy", style="bold")
        table.add_column("Description", style="green")
        
        strategies = [
            ("smart", "Smart Merge", "Intelligently merges data, avoiding duplicates"),
            ("append", "Append Only", "Adds new data without modifying existing data"),
            ("overwrite", "Overwrite", "Replaces existing data with new data")
        ]
        
        for i, (key, name, desc) in enumerate(strategies):
            selected = key == self.options["merge_strategy"]
            table.add_row(
                str(i + 1),
                f"{name} {'[bold green]✓[/bold green]' if selected else ''}",
                desc
            )
        
        self.console.print(table)
        
        # Get user choice
        choice = Prompt.ask(
            "Enter strategy ID (or 'c' to cancel)",
            choices=["1", "2", "3", "c"],
            default="c"
        )
        
        if choice == "c":
            return
        
        # Set selected strategy
        self.options["merge_strategy"] = strategies[int(choice) - 1][0]
    
    def _validate_migration(self):
        """Validate migration parameters."""
        if not self.source_browser:
            self.console.print("Please select a source browser.", style="bold red")
            self._wait_for_input()
            return False
        
        if not self.source_profile:
            self.console.print("Please select a source profile.", style="bold red")
            self._wait_for_input()
            return False
        
        if not self.target_profile:
            self.console.print("Please select a target Floorp profile.", style="bold red")
            self._wait_for_input()
            return False
        
        if not self.selected_data_types:
            self.console.print("Please select at least one data type to migrate.", style="bold red")
            self._wait_for_input()
            return False
        
        return True
    
    def _start_migration(self):
        """Start the migration process."""
        self.console.clear()
        
        # Create migration panel
        title = Panel(
            "Migration in Progress",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Show migration details
        self.console.print(f"Source: [bold]{self.source_browser.get('name')}[/bold] - {self.source_profile.get('name')}")
        self.console.print(f"Target: [bold]Floorp[/bold] - {self.target_profile.get('name')}")
        self.console.print(f"Data Types: [bold]{', '.join(dt.capitalize() for dt in self.selected_data_types)}[/bold]")
        
        # Confirm migration
        if not Confirm.ask("Start migration now?"):
            return
        
        # Start migration with progress tracking
        self.console.print("\nStarting migration...", style="bold yellow")
        
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            # Create tasks for each data type
            tasks = {}
            for data_type in self.selected_data_types:
                tasks[data_type] = progress.add_task(
                    f"[green]Migrating {data_type.capitalize()}...",
                    total=100
                )
            
            # Simulate progress for each task
            # In a real implementation, this would be based on actual progress
            for i in range(101):
                for data_type in self.selected_data_types:
                    progress.update(tasks[data_type], completed=i)
                time.sleep(0.05)
            
            # Perform actual migration
            result = self.controller.migrate_profile(
                self.source_profile,
                self.target_profile,
                self.selected_data_types,
                self.options
            )
        
        # Show migration results
        self._show_migration_results(result)
    
    def _show_migration_results(self, result):
        """
        Show migration results.
        
        Args:
            result: Migration result
        """
        self.console.clear()
        
        # Create results panel
        title_style = "bold green" if result.get("success", False) else "bold red"
        title_text = "Migration Completed Successfully" if result.get("success", False) else "Migration Completed with Issues"
        
        title = Panel(
            title_text,
            style=title_style,
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Show summary
        self.console.print(result.get("message", ""), style="bold")
        
        # Show details
        self.console.print("\n[bold]Details:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("Data Type", style="bold")
        table.add_column("Status", style="green")
        table.add_column("Message", style="cyan")
        table.add_column("Statistics", style="yellow")
        
        for data_type, data_result in result.get("details", {}).items():
            success = data_result.get("success", False)
            message = data_result.get("message", "")
            stats = data_result.get("stats", {})
            
            status_style = "green" if success else "red"
            status_text = "Success" if success else "Failed"
            
            stats_text = ", ".join(f"{k}: {v}" for k, v in stats.items())
            
            table.add_row(
                data_type.capitalize(),
                f"[{status_style}]{status_text}[/{status_style}]",
                message,
                stats_text
            )
        
        self.console.print(table)
        
        # Wait for user input
        self.console.print("\nPress Enter to return to main menu...", style="italic")
        input()
    
    def _show_help(self):
        """Show help information."""
        self.console.clear()
        
        # Create help panel
        title = Panel(
            "Floorper Help",
            style="bold blue",
            box=ROUNDED
        )
        
        self.console.print(title)
        
        # Show help content
        help_text = """
[bold]About Floorper[/bold]

Floorper is a universal browser profile migration tool for Floorp. It helps you migrate your profiles from various browsers to Floorp.

[bold]Migration Process[/bold]

1. Select a source browser
2. Select a source profile
3. Select a target Floorp profile
4. Configure which data types to migrate
5. Configure migration options
6. Start the migration

[bold]Data Types[/bold]

- [bold]Bookmarks[/bold]: Web page bookmarks and favorites
- [bold]History[/bold]: Browsing history
- [bold]Passwords[/bold]: Saved website credentials
- [bold]Cookies[/bold]: Website cookies and storage
- [bold]Extensions[/bold]: Browser extensions and add-ons
- [bold]Preferences[/bold]: Browser settings and preferences
- [bold]Sessions[/bold]: Open tabs and session state

[bold]Merge Strategies[/bold]

- [bold]Smart Merge[/bold]: Intelligently merges data, avoiding duplicates
- [bold]Append Only[/bold]: Adds new data without modifying existing data
- [bold]Overwrite[/bold]: Replaces existing data with new data

[bold]Tips[/bold]

- Always create a backup before migration (enabled by default)
- Close all browser instances before migration
- For best results, use the Smart Merge strategy
        """
        
        self.console.print(Panel(help_text, box=ROUNDED))
        
        # Wait for user input
        self.console.print("\nPress Enter to return to main menu...", style="italic")
        input()
    
    def _wait_for_input(self):
        """Wait for user input."""
        self.console.print("\nPress Enter to continue...", style="italic")
        input()
    
    def _exit_application(self, message=None):
        """
        Exit the application.
        
        Args:
            message: Optional exit message
        """
        self.console.clear()
        
        if message:
            self.console.print(message, style="bold yellow")
        
        self.console.print("\nThank you for using Floorper!", style="bold green")
        sys.exit(0)


def main():
    """Main entry point for the TUI."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create controller
    controller = FloorperCore()
    
    # Create and run TUI
    tui = FloorperTUI(controller)
    tui.run()


if __name__ == "__main__":
    main()
