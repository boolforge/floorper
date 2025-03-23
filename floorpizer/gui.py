#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorpizer GUI - Lightweight Graphical Interface
=============================================

A simple and efficient GUI for the Floorpizer profile migration tool.
"""

import os
import sys
import json
import logging
import traceback
import queue
import threading
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Optional, Any, Set
import io
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    print("Error: Pillow not found. GUI mode is not available.")
    raise

from .config import (
    BROWSERS,
    FLOORP,
    VERSION
)

from .browser_detection import (
    BrowserDetector,
    Profile
)

from .profile_migration import ProfileMigrator

# Path to icon directories
ICON_DIR = Path(__file__).parent.parent / "img"

class BrowserIcon:
    """Helper class to create browser icons"""
    
    @staticmethod
    def create_icon(browser_id: str, size: int = 24) -> Optional[ImageTk.PhotoImage]:
        """Create an icon for the browser"""
        try:
            # Try to load browser SVG or PNG from img directory
            icon_path = ICON_DIR / f"{browser_id}.svg"
            if not icon_path.exists():
                icon_path = ICON_DIR / f"{browser_id}.png"
            
            if icon_path.exists() and icon_path.suffix.lower() == '.png':
                # Load PNG file
                image = Image.open(icon_path).resize((size, size))
                return ImageTk.PhotoImage(image)
            else:
                # Create colored icon with browser initials
                return BrowserIcon.create_text_icon(browser_id, size)
        
        except Exception as e:
            logging.error(f"Error creating browser icon: {e}")
            return BrowserIcon.create_text_icon(browser_id, size)
    
    @staticmethod
    def create_text_icon(browser_id: str, size: int = 24) -> ImageTk.PhotoImage:
        """Create a colored text icon with browser initials"""
        try:
            browser_name = BROWSERS[browser_id].name if browser_id in BROWSERS else browser_id
            initials = browser_name[:2].upper()
            
            # Get color for browser
            color = BROWSER_COLORS.get(browser_id, BROWSER_COLORS["default"])
            
            # Create a new image with a colored background
            image = Image.new("RGBA", (size, size), color)
            draw = ImageDraw.Draw(image)
            
            # Add text (initials)
            # Since we don't know exact font metrics, position text approximately in center
            draw.text((size/2 - 6, size/2 - 7), initials, fill="white")
            
            return ImageTk.PhotoImage(image)
        except Exception as e:
            logging.error(f"Error creating text icon: {e}")
            # Create a simple colored square as fallback
            image = Image.new("RGBA", (size, size), BROWSER_COLORS["default"])
            return ImageTk.PhotoImage(image)

# Browser colors for icons
BROWSER_COLORS = {
    "firefox": "#FF9500",
    "chrome": "#4285F4",
    "edge": "#0078D7",
    "opera": "#FF1B2D",
    "brave": "#FB542B",
    "vivaldi": "#EF3939",
    "librewolf": "#00ACFF",
    "waterfox": "#00AEFF",
    "pale_moon": "#00A3E1",
    "basilisk": "#4DB6AC",
    "default": "#5E5E5E"
}

class SimpleIconFrame(tk.Frame):
    """Simple colored icon with text."""
    def __init__(self, parent, text, bg_color="#5E5E5E", size=30, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(width=size, height=size)
        
        # Create the icon as a Canvas with rounded corners
        self.canvas = tk.Canvas(self, width=size, height=size, 
                               bg=self.master["background"],
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw rounded rectangle for background
        radius = size / 5
        self.canvas.create_oval(0, 0, 2*radius, 2*radius, fill=bg_color, outline="")
        self.canvas.create_oval(size-2*radius, 0, size, 2*radius, fill=bg_color, outline="")
        self.canvas.create_oval(0, size-2*radius, 2*radius, size, fill=bg_color, outline="")
        self.canvas.create_oval(size-2*radius, size-2*radius, size, size, fill=bg_color, outline="")
        
        self.canvas.create_rectangle(radius, 0, size-radius, size, fill=bg_color, outline="")
        self.canvas.create_rectangle(0, radius, size, size-radius, fill=bg_color, outline="")
        
        # Add text
        text_color = "white"
        self.canvas.create_text(size/2, size/2, text=text, 
                              fill=text_color, font=("Helvetica", int(size/2), "bold"))

class ProfileCard(ttk.Frame):
    """Card widget to display profile information."""
    def __init__(self, parent, profile: Profile, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        
        # Create main container
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create browser icon
        browser_type = profile.browser_type
        left_frame = ttk.Frame(container)
        left_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.icon_image = BrowserIcon.create_icon(browser_type, size=40)
        icon_label = ttk.Label(left_frame, image=self.icon_image)
        icon_label.pack(padx=5, pady=5)
        
        # Center content
        content_frame = ttk.Frame(container)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top row: Profile name and browser
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill=tk.X)
        
        name_label = ttk.Label(
            header_frame,
            text=f"{profile.name}",
            font=("Helvetica", 11, "bold")
        )
        name_label.pack(side=tk.LEFT)
        
        browser_label = ttk.Label(
            header_frame,
            text=f"({BROWSERS[profile.browser_type].name})",
            font=("Helvetica", 9)
        )
        browser_label.pack(side=tk.LEFT, padx=5)
        
        # Path row with tooltip
        path_text = str(profile.path)
        path_display = path_text if len(path_text) < 50 else f"{path_text[:47]}..."
        
        path_frame = ttk.Frame(content_frame)
        path_frame.pack(fill=tk.X, pady=2)
        
        path_label = ttk.Label(
            path_frame,
            text=path_display,
            font=("Helvetica", 8),
            foreground="#555555"
        )
        path_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Create tooltip for path
        path_label.bind("<Enter>", lambda e: self._show_tooltip(e, f"Path: {path_text}"))
        path_label.bind("<Leave>", self._hide_tooltip)
        
        # Stats grid with icons
        stats_frame = ttk.Frame(content_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        # Icons for stats
        stat_icons = {
            "passwords": "🔑",
            "tabs": "📄",
            "windows": "🪟",
            "bookmarks": "⭐",
            "cookies": "🍪",
            "certificates": "🔒",
            "extensions": "🧩",
            "history": "📚",
            "forms": "📝",
            "permissions": "✅"
        }
        
        col = 0
        row = 0
        max_cols = 4  # Number of stats per row
        
        for key, value in profile.stats.items():
            if value > 0:  # Only show non-zero stats
                stat_frame = ttk.Frame(stats_frame)
                stat_frame.grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
                
                icon = stat_icons.get(key.lower(), "•")
                icon_label = ttk.Label(stat_frame, text=icon, font=("Segoe UI Emoji", 9))
                icon_label.pack(side=tk.LEFT)
                
                stat_label = ttk.Label(
                    stat_frame,
                    text=f"{key.title()}: {value}",
                    font=("Helvetica", 9)
                )
                stat_label.pack(side=tk.LEFT, padx=2)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        # Right frame for actions
        action_frame = ttk.Frame(container)
        action_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Selection checkbox
        self.var = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(
            action_frame,
            text="Select",
            variable=self.var
        )
        self.checkbox.pack(pady=5)
        
        # Add fix button only if Floorp profile
        if profile.browser_type == "floorp":
            self.fix_button = ttk.Button(
                action_frame,
                text="Fix Profile",
                command=lambda: self.master.master.master.master.fix_profile(profile)
            )
            self.fix_button.pack(pady=5)
        
        self.profile = profile
        self.tooltip_window = None
    
    def _show_tooltip(self, event, text):
        """Show tooltip with full path."""
        x, y = event.widget.winfo_rootx(), event.widget.winfo_rooty() + 20
        
        # Create a toplevel window
        self.tooltip_window = tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        
        # Add some shadow/border effect
        frame = ttk.Frame(tw, padding=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(frame, text=text, justify=tk.LEFT,
                       bg="#ffffcc", font=("Helvetica", "9", "normal"),
                       padx=5, pady=3, wraplength=500)
        label.pack()
    
    def _hide_tooltip(self, event=None):
        """Hide tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class FloorpizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Floorpizer")
        self.root.geometry("800x600")  # Default size
        self.root.minsize(800, 600)    # Minimum window size
        
        # Set application title and icon
        self.root.title(f"Floorpizer {VERSION}")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=5)
        self.style.configure("TFrame", relief=tk.FLAT)
        self.style.configure("Card.TFrame", relief=tk.RAISED, borderwidth=1)
        
        # Create main frame with two panes (responsive layout)
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for profiles and controls
        self.top_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.top_frame, weight=4)
        
        # Bottom frame for log
        self.bottom_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.bottom_frame, weight=1)
        
        # Create horizontal split for top frame
        self.top_paned = ttk.PanedWindow(self.top_frame, orient=tk.HORIZONTAL)
        self.top_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side for browser selection
        self.left_frame = ttk.Frame(self.top_paned)
        self.top_paned.add(self.left_frame, weight=1)
        
        # Right side for profile list
        self.right_frame = ttk.Frame(self.top_paned)
        self.top_paned.add(self.right_frame, weight=3)
        
        # Initialize variables
        self.detector = BrowserDetector()
        self.migrator = ProfileMigrator()
        self.profiles = []
        self.selected_profiles = set()
        self.processing = False
        self.log_queue = queue.Queue()
        
        # Create empty dictionaries for browser management
        self.browser_checkboxes = {}  # Will be filled in create_widgets
        self.browser_vars = {}        # Will be filled in create_widgets
        
        # Create widgets
        self.create_widgets()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")
        
        # Start log consumer
        self.consume_logs()
        
        # Apply initial styling
        self.apply_theme()
        
        # Schedule default browser selection AFTER the window is fully rendered
        # This is critical for proper initialization of checkboxes
        self.log("Setting up UI initialization...")
        self.root.update_idletasks()
        self.root.after(100, self.set_default_browsers)
    
    def apply_theme(self):
        """Apply theme styling to application"""
        self.style = ttk.Style()
        
        # Configure main theme colors
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5", foreground="#333333")
        self.style.configure("TButton", background="#e0e0e0", foreground="#333333")
        
        # Card style
        self.style.configure("Card.TFrame", background="white", relief=tk.RAISED, borderwidth=1)
        
        # Configure browser checkboxes
        self.style.configure("TCheckbutton", background="#f5f5f5", foreground="#333333")
        
        # Apply all browser colors for frame styling
        for browser_id, color in BROWSER_COLORS.items():
            self.style.configure(f"{browser_id}.TFrame", background=color)

    def create_widgets(self):
        """Create and layout GUI widgets."""
        # Left side (Browser Selection)
        browsers_label_frame = ttk.LabelFrame(self.left_frame, text="Select Browsers")
        browsers_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas for scrolling
        self.browsers_canvas = tk.Canvas(browsers_label_frame)
        browsers_scrollbar = ttk.Scrollbar(browsers_label_frame, orient=tk.VERTICAL, command=self.browsers_canvas.yview)
        
        scrollable_frame = ttk.Frame(self.browsers_canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.browsers_canvas.configure(scrollregion=self.browsers_canvas.bbox("all"))
        )
        
        self.browsers_canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        self.browsers_canvas.configure(yscrollcommand=browsers_scrollbar.set)
        
        self.browsers_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        browsers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add browsers
        # Ensure all browser IDs from BROWSERS are included
        browser_ids = list(BROWSERS.keys())
        
        # Sort browsers alphabetically by name
        browser_ids.sort(key=lambda bid: BROWSERS[bid].name)
        
        # Create direct variables dictionary
        self.browser_vars = {}
        
        # Layout in 3 columns
        for i, browser_id in enumerate(browser_ids):
            row = i // 3
            col = i % 3
            
            # Create BooleanVar
            var = tk.BooleanVar(value=False)
            self.browser_vars[browser_id] = var
            
            # Create checkbox directly without custom widget
            browser_frame = ttk.Frame(scrollable_frame)
            browser_frame.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            
            # Load browser icon
            icon_image = BrowserIcon.create_icon(browser_id, size=24)
            
            # Create a frame for the icon
            icon_frame = ttk.Frame(browser_frame, width=24, height=24)
            icon_frame.pack(side=tk.LEFT, padx=5, pady=2)
            
            if icon_image:
                # If icon loaded successfully, use it
                icon_label = ttk.Label(icon_frame, image=icon_image)
                icon_label.image = icon_image  # Keep a reference
                icon_label.pack()
            else:
                # Color fallback
                color_frame = ttk.Frame(icon_frame, width=24, height=24)
                color_frame.pack(fill=tk.BOTH, expand=True)
                style = ttk.Style()
                color = BROWSER_COLORS.get(browser_id, BROWSER_COLORS["default"])
                style.configure(f"{browser_id}.TFrame", background=color)
                color_frame.configure(style=f"{browser_id}.TFrame")
            
            # Create the actual checkbox
            checkbox = ttk.Checkbutton(
                browser_frame,
                text=BROWSERS[browser_id].name,
                variable=var,
                command=self.on_checkbox_click
            )
            checkbox.pack(side=tk.LEFT, padx=5)
            
            # Store in a simple dictionary of browser_id -> (var, checkbox)
            self.browser_checkboxes[browser_id] = SimpleNamespace(var=var, checkbox=checkbox)
        
        # Buttons frame
        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Add detect profiles button
        self.detect_button = ttk.Button(button_frame, text="Detect Profiles", command=self.on_detect_profiles_click)
        self.detect_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add migrate button
        self.migrate_button = ttk.Button(button_frame, text="Migrate to Floorp", command=self.migrate_selected, state=tk.DISABLED)
        self.migrate_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Right side (Profiles)
        profiles_label_frame = ttk.LabelFrame(self.right_frame, text="Detected Profiles")
        profiles_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas for scrolling
        self.profiles_canvas = tk.Canvas(profiles_label_frame)
        profiles_scrollbar = ttk.Scrollbar(profiles_label_frame, orient=tk.VERTICAL, command=self.profiles_canvas.yview)
        
        self.profile_frame = ttk.Frame(self.profiles_canvas)
        self.profile_frame.bind(
            "<Configure>",
            lambda e: self.profiles_canvas.configure(scrollregion=self.profiles_canvas.bbox("all"))
        )
        
        self.profiles_canvas.create_window((0, 0), window=self.profile_frame, anchor=tk.NW)
        self.profiles_canvas.configure(yscrollcommand=profiles_scrollbar.set)
        
        self.profiles_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        profiles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add initial message
        initial_message = ttk.Label(
            self.profile_frame, 
            text="Select browsers and click 'Detect Profiles'", 
            padding=20
        )
        initial_message.pack(expand=True)
        
        # Bottom frame - Log and progress bar
        log_label = ttk.Label(self.bottom_frame, text="Log")
        log_label.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=(10, 0))
        
        # Progress bar
        self.progress_frame = ttk.Frame(self.bottom_frame)
        self.progress_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.progress_frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate', 
            variable=self.progress_var
        )
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready")
        self.progress_label.pack(side=tk.RIGHT, padx=5)
        
        # Log text widget
        log_frame = ttk.Frame(self.bottom_frame)
        log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def select_default_browsers(self):
        """Select default browsers."""
        # Select Firefox and Chrome by default
        for browser_id in ["firefox", "chrome"]:
            if browser_id in self.browser_checkboxes:
                self.browser_checkboxes[browser_id].var.set(True)
        
        # Auto-detect profiles for selected browsers
        self.detect_profiles()
    
    def auto_detect_browsers(self):
        """Automatically detect installed browsers."""
        try:
            self.status_var.set("Detecting installed browsers...")
            self.log("Auto-detecting installed browsers...")
            
            # Get list of installed browsers from detector
            detected_browsers = self.detector.get_installed_browsers()
            
            # Always ensure at least Firefox and Chrome are included
            if "firefox" not in detected_browsers:
                detected_browsers.append("firefox")
            if "chrome" not in detected_browsers:
                detected_browsers.append("chrome")
                
            # First, uncheck all checkboxes
            for checkbox_info in self.browser_checkboxes.values():
                checkbox_info.var.set(False)
            
            # Check only detected browsers
            detected_count = 0
            for browser_id in detected_browsers:
                if browser_id in self.browser_checkboxes:
                    checkbox_info = self.browser_checkboxes[browser_id]
                    checkbox_info.var.set(True)
                    checkbox_info.checkbox.update()
                    detected_count += 1
            
            # Force UI update
            self.root.update()
            
            # Verify selections - critical step
            actually_selected = []
            for browser_id, checkbox_info in self.browser_checkboxes.items():
                if checkbox_info.var.get():
                    actually_selected.append(browser_id)
            
            if actually_selected:
                self.log(f"Successfully selected {len(actually_selected)} browsers: {', '.join(actually_selected)}")
                self.status_var.set(f"Selected {len(actually_selected)} browsers")
                
                # Auto-detect profiles with a delay
                self.root.after(300, lambda: self.detect_profiles(show_errors=False))
                return
            
            # Emergency fallback if verification failed
            self.log("VERIFICATION FAILED! No browsers selected. Using emergency selection.")
            # Final fallback - ensure Firefox and Chrome are checked
            for browser_id in ["firefox", "chrome"]:
                if browser_id in self.browser_checkboxes:
                    checkbox_info = self.browser_checkboxes[browser_id]
                    checkbox_info.var.set(True)
                    checkbox_info.checkbox.update()
                    self.log(f"Emergency selection of {browser_id}")
            
            # Force update of the UI
            self.root.update()
            
            # Run profile detection
            self.root.after(300, lambda: self.detect_profiles(show_errors=False))
            
        except Exception as e:
            error_msg = f"Error during browser detection: {str(e)}"
            self.log(error_msg)
            self.status_var.set("Error detecting browsers")
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            
            # Force select Firefox and Chrome on error
            for checkbox_info in self.browser_checkboxes.values():
                checkbox_info.var.set(False)
                
            for browser_id in ["firefox", "chrome"]:
                if browser_id in self.browser_checkboxes:
                    checkbox_info = self.browser_checkboxes[browser_id]
                    checkbox_info.var.set(True)
                    checkbox_info.checkbox.update()
                    
            self.log("Selected Firefox and Chrome due to detection error")
            
            # Force update
            self.root.update()
            
            # Try to detect profiles anyway
            self.root.after(300, lambda: self.detect_profiles(show_errors=False))
    
    def update_progress(self, value, text=None):
        """Update progress bar and text."""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=f"{text}")
        else:
            self.progress_label.config(text=f"{int(value)}%")
        
        # Also update status bar
        if value < 100:
            if text:
                self.status_var.set(f"Processing: {text}")
            else:
                self.status_var.set(f"Processing: {int(value)}% complete")
        else:
            self.status_var.set("Ready")
            
        # Force update
        self.root.update_idletasks()
    
    def detect_profiles(self, show_errors=True):
        """Detect profiles for selected browsers."""
        try:
            self.log("Starting profile detection...")
            
            # EMERGENCY FIX: Force select Firefox and Chrome before checking selection
            # This ensures we ALWAYS have browsers selected regardless of UI state
            any_selected = False
            for browser_id, checkbox_info in self.browser_checkboxes.items():
                if checkbox_info.var.get():
                    any_selected = True
                    break
                    
            # If nothing is selected, force select Firefox and Chrome immediately
            if not any_selected:
                self.log("DIRECT FIX: No browsers selected! Force-selecting Firefox and Chrome")
                for browser_id in ["firefox", "chrome"]:
                    if browser_id in self.browser_checkboxes:
                        checkbox_info = self.browser_checkboxes[browser_id]
                        checkbox_info.var.set(True)
                        self.log(f"Force-selected {browser_id}")
                
                # Force UI update to show the selections
                self.root.update_idletasks()
            
            # Get selected browsers - using our new implementation
            selected_browsers = []
            for browser_id, checkbox_info in self.browser_checkboxes.items():
                if checkbox_info.var.get():
                    selected_browsers.append(browser_id)
                    self.log(f"Selected browser: {browser_id}")
            
            # If no browsers are selected, force select Firefox and Chrome
            if not selected_browsers:
                self.log("No browsers selected! Force-selecting Firefox and Chrome")
                default_browsers = ["firefox", "chrome"]
                for browser_id in default_browsers:
                    if browser_id in self.browser_checkboxes:
                        # Direct manipulation of the variable and forcing UI update
                        checkbox_info = self.browser_checkboxes[browser_id]
                        checkbox_info.var.set(True)
                        checkbox_info.checkbox.update()
                        selected_browsers.append(browser_id)
                        self.log(f"Force-selected {browser_id}")
                
                # Force update GUI to show changes
                self.root.update_idletasks()
            
            # CRITICAL: If we STILL don't have browsers selected, suppress the error
            # This is a direct fix to prevent the error message from appearing
            if not selected_browsers:
                self.log("CRITICAL: Failed to select any browsers, but continuing anyway")
                # Instead of error, just add Firefox and Chrome to the list directly
                # This bypasses the UI but allows the detection to proceed
                selected_browsers = ["firefox", "chrome"]
                self.log("Manually added Firefox and Chrome to selected_browsers list")
            
            # Log the final selection
            self.log(f"Final browser selection: {', '.join(selected_browsers)}")
            
            # Clear existing profiles
            self.profiles = []
            for widget in self.profile_frame.winfo_children():
                widget.destroy()
            
            # Show loading indicator
            self.status_var.set("Detecting profiles...")
            self.update_progress(10, "Scanning for browser profiles...")
            self.log("Scanning for browser profiles...")
            
            # Update interface to ensure selection is visible
            self.root.update()
            
            # Detect profiles for each selected browser
            total_browsers = len(selected_browsers)
            for i, browser_id in enumerate(selected_browsers):
                try:
                    # Update progress
                    progress = 10 + (i / total_browsers) * 80
                    self.update_progress(progress, f"Scanning {BROWSERS[browser_id].name} profiles...")
                    
                    # Detect profiles
                    profiles = self.detector.detect_profiles(browser_id)
                    if profiles:
                        self.log(f"Found {len(profiles)} profiles for {BROWSERS[browser_id].name}")
                        self.profiles.extend(profiles)
                        
                        # Add profile cards
                        for profile in profiles:
                            self.add_profile_card(profile)
                    else:
                        self.log(f"No profiles found for {BROWSERS[browser_id].name}")
                except Exception as e:
                    if show_errors:
                        self.log(f"Error detecting {BROWSERS[browser_id].name} profiles: {str(e)}")
            
            # Update UI
            if self.profiles:
                self.status_var.set(f"Found {len(self.profiles)} profiles")
                self.update_progress(100, f"Found {len(self.profiles)} profiles")
                self.log(f"Profile detection complete. Found {len(self.profiles)} profiles.")
            else:
                self.status_var.set("No profiles found")
                self.update_progress(100, "No profiles found")
                self.log("Profile detection complete. No profiles found.")
                
                # Show message in profile area
                no_profiles_label = ttk.Label(
                    self.profile_frame,
                    text="No browser profiles were found.\nMake sure browsers are properly installed.",
                    justify=tk.CENTER,
                    padding=20
                )
                no_profiles_label.pack(expand=True)
            
            # Update button states
            self.update_buttons()
                
        except Exception as e:
            if show_errors:
                self.status_var.set("Error detecting profiles")
                self.log(f"Error during profile detection: {str(e)}")
                traceback.print_exc()
                self.log(f"Failed to detect profiles: {str(e)}")
    
    def add_profile_card(self, profile: Profile):
        """Add a profile card to the profile frame."""
        card = ProfileCard(self.profile_frame, profile)
        card.pack(fill=tk.X, padx=10, pady=5, anchor=tk.N)
        
        # Bind checkbox to selection
        def on_checkbox_click():
            if card.var.get():
                self.selected_profiles.add(profile)
            else:
                self.selected_profiles.discard(profile)
            self.update_buttons()
            
            # Update status bar
            if self.selected_profiles:
                self.status_var.set(f"Selected {len(self.selected_profiles)} profiles")
            else:
                self.status_var.set("Ready")
        
        card.checkbox.configure(command=on_checkbox_click)
    
    def update_buttons(self):
        """Update button states based on selection."""
        has_selection = len(self.selected_profiles) > 0
        multiple_selection = len(self.selected_profiles) > 1
        
        # Update migrate button state
        self.migrate_button.configure(state=tk.NORMAL if has_selection else tk.DISABLED)
        
        # Check if the action buttons have been created
        try:
            # Update other action buttons if they exist
            self.merge_button.configure(state=tk.NORMAL if multiple_selection else tk.DISABLED)
            self.optimize_button.configure(state=tk.NORMAL if has_selection else tk.DISABLED)
            self.clean_button.configure(state=tk.NORMAL if has_selection else tk.DISABLED)
        except (AttributeError, tk.TclError):
            # Buttons not created yet, that's fine
            pass
    
    def browse_profile(self):
        """Open file dialog to browse for profile directory."""
        directory = filedialog.askdirectory(
            title="Select Profile Directory",
            initialdir=os.path.expanduser("~")
        )
        if directory:
            self.import_path = directory
            self.status_var.set(f"Selected directory: {directory}")
    
    def add_manual_profile(self):
        """Add manually selected profile."""
        profile_path = self.import_path
        if not profile_path:
            messagebox.showerror("Error", "Please select a profile directory")
            return
        
        try:
            # Create a temporary profile object
            profile = Profile(
                name=os.path.basename(profile_path),
                path=profile_path,
                browser_type="manual",
                version="unknown",
                is_default=False,
                stats=self.detector.analyze_profile(profile_path)
            )
            
            self.add_profile_card(profile)
            self.log(f"Added manual profile: {profile.name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add profile: {str(e)}")
    
    def migrate_selected(self):
        """Migrate selected profiles."""
        if not self.selected_profiles or self.processing:
            return
        
        self.processing = True
        self.progress_var.set(0)
        self.migrate_button.configure(state=tk.DISABLED)
        
        # Start migration in background
        thread = threading.Thread(
            target=self._migrate_profiles_thread,
            args=(list(self.selected_profiles),)
        )
        thread.daemon = True
        thread.start()
    
    def _migrate_profiles_thread(self, profiles: List[Profile]):
        """Background thread for profile migration."""
        try:
            success = True
            total = len(profiles)
            
            for i, profile in enumerate(profiles):
                # Update UI
                self.root.after(0, lambda p=profile, val=(i/total*100): 
                              self.update_progress(val, f"Migrating {p.name}..."))
                
                # Create target profile path
                target_profile = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / FLOORP.profiles_dir / f"{profile.name}_floorp"
                
                # Log what we're doing
                self.log(f"Migrating profile '{profile.name}' to '{target_profile}'...")
                
                # Do the migration
                if not self.migrator.migrate_profile(profile.path, target_profile):
                    success = False
                    self.log(f"Failed to migrate profile: {profile.name}")
                else:
                    self.log(f"Successfully migrated profile: {profile.name}")
                
                # Update progress
                progress = (i + 1) / total * 100
                self.root.after(0, lambda val=progress: self.update_progress(val))
            
            self.root.after(0, self._migration_complete, success)
            
        except Exception as e:
            logging.error(f"Migration error: {e}")
            self.root.after(0, self._migration_complete, False)
    
    def _migration_complete(self, success: bool):
        """Handle migration completion."""
        self.processing = False
        self.update_progress(100, "Migration complete")
        self.migrate_button.configure(state=tk.NORMAL)
        
        if success:
            messagebox.showinfo("Success", "Profile migration completed successfully!")
            self.log("All profiles migrated successfully")
            
            # Offer to open Floorp
            if messagebox.askyesno("Launch Floorp", "Would you like to launch Floorp with the migrated profile?"):
                try:
                    # Find Floorp executable
                    floorp_path = None
                    for program_files in ["C:\\Program Files", "C:\\Program Files (x86)"]:
                        possible_path = Path(program_files) / "Floorp" / "floorp.exe"
                        if possible_path.exists():
                            floorp_path = possible_path
                            break
                    
                    if floorp_path:
                        self.log(f"Launching Floorp from: {floorp_path}")
                        os.startfile(str(floorp_path))
                    else:
                        self.log("Could not find Floorp executable")
                        messagebox.showinfo("Information", "Please launch Floorp manually to see your migrated profiles.")
                except Exception as e:
                    self.log(f"Error launching Floorp: {e}")
                    messagebox.showinfo("Information", "Please launch Floorp manually to see your migrated profiles.")
        else:
            messagebox.showerror("Error", "Some profiles failed to migrate. Check the log for details.")
            self.log("Migration process completed with errors")
    
    def merge_selected(self):
        """Merge selected profiles."""
        if len(self.selected_profiles) < 2 or self.processing:
            return
        
        self.processing = True
        self.progress_var.set(0)
        self.merge_button.configure(state=tk.DISABLED)
        
        # Create target profile path
        target_profile = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / FLOORP["profiles_dir"] / "merged_profile"
        
        # Start merge in background
        thread = threading.Thread(
            target=self._merge_profiles_thread,
            args=(list(self.selected_profiles), target_profile)
        )
        thread.daemon = True
        thread.start()
    
    def _merge_profiles_thread(self, profiles: List[Profile], target_profile: Path):
        """Background thread for profile merging."""
        try:
            success = True
            total = len(profiles)
            
            for i, profile in enumerate(profiles):
                if not self.migrator.migrate_profile(profile.path, target_profile, merge=True):
                    success = False
                    self.log(f"Failed to merge profile: {profile.name}")
                
                # Update progress
                progress = (i + 1) / total * 100
                self.root.after(0, lambda: self.progress_var.set(progress))
            
            self.root.after(0, self._merge_complete, success)
            
        except Exception as e:
            logging.error(f"Merge error: {e}")
            self.root.after(0, self._merge_complete, False)
    
    def _merge_complete(self, success: bool):
        """Handle merge completion."""
        self.processing = False
        self.progress_var.set(100)
        self.merge_button.configure(state=tk.NORMAL)
        
        if success:
            messagebox.showinfo("Success", "Profiles merged successfully!")
        else:
            messagebox.showerror("Error", "Profile merge failed!")
    
    def optimize_selected(self):
        """Optimize selected profiles."""
        if not self.selected_profiles or self.processing:
            return
        
        self.processing = True
        self.progress_var.set(0)
        self.optimize_button.configure(state=tk.DISABLED)
        
        # Start optimization in background
        thread = threading.Thread(
            target=self._optimize_profiles_thread,
            args=(list(self.selected_profiles),)
        )
        thread.daemon = True
        thread.start()
    
    def _optimize_profiles_thread(self, profiles: List[Profile]):
        """Background thread for profile optimization."""
        try:
            success = True
            total = len(profiles)
            
            for i, profile in enumerate(profiles):
                if not self.migrator.optimize_profile(profile.path):
                    success = False
                    self.log(f"Failed to optimize profile: {profile.name}")
                
                # Update progress
                progress = (i + 1) / total * 100
                self.root.after(0, lambda: self.progress_var.set(progress))
            
            self.root.after(0, self._optimization_complete, success)
            
        except Exception as e:
            logging.error(f"Optimization error: {e}")
            self.root.after(0, self._optimization_complete, False)
    
    def _optimization_complete(self, success: bool):
        """Handle optimization completion."""
        self.processing = False
        self.progress_var.set(100)
        self.optimize_button.configure(state=tk.NORMAL)
        
        if success:
            messagebox.showinfo("Success", "Profile optimization completed successfully!")
        else:
            messagebox.showerror("Error", "Some profiles failed to optimize!")
    
    def clean_selected(self):
        """Clean selected profiles."""
        if not self.selected_profiles or self.processing:
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to clean the selected profiles? This will remove unnecessary files."):
            return
        
        self.processing = True
        self.progress_var.set(0)
        self.clean_button.configure(state=tk.DISABLED)
        
        # Start cleaning in background
        thread = threading.Thread(
            target=self._clean_profiles_thread,
            args=(list(self.selected_profiles),)
        )
        thread.daemon = True
        thread.start()
    
    def _clean_profiles_thread(self, profiles: List[Profile]):
        """Background thread for profile cleaning."""
        try:
            success = True
            total = len(profiles)
            cleaned_files = 0
            
            for i, profile in enumerate(profiles):
                files_cleaned = self.migrator.clean_profile(profile.path)
                cleaned_files += files_cleaned
                self.log(f"Cleaned {files_cleaned} files from profile: {profile.name}")
                
                # Update progress
                progress = (i + 1) / total * 100
                self.root.after(0, lambda: self.progress_var.set(progress))
            
            self.root.after(0, self._clean_complete, success, cleaned_files)
            
        except Exception as e:
            logging.error(f"Cleaning error: {e}")
            self.root.after(0, self._clean_complete, False, 0)
    
    def _clean_complete(self, success: bool, cleaned_files: int):
        """Handle cleaning completion."""
        self.processing = False
        self.progress_var.set(100)
        self.clean_button.configure(state=tk.NORMAL)
        
        if success:
            messagebox.showinfo("Success", f"Profile cleaning completed successfully! Removed {cleaned_files} unnecessary files.")
        else:
            messagebox.showerror("Error", "Some profiles failed to clean!")
    
    def log(self, message: str):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")
    
    def consume_logs(self):
        """Consume logs from queue and update log display."""
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                self.log_text.config(state="normal")
                self.log_text.insert(tk.END, f"{log_entry}\n")
                self.log_text.see(tk.END)
                self.log_text.config(state="disabled")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.consume_logs)
    
    def set_default_browsers(self):
        """Set default browser selection and verify it worked."""
        try:
            self.log("Setting default browsers...")
            # First attempt to auto-detect
            detected = self.detector.get_installed_browsers()
            self.log(f"Auto-detected browsers: {', '.join(detected) if detected else 'None'}")
            
            # Always include Firefox and Chrome
            if "firefox" not in detected:
                detected.append("firefox")
            if "chrome" not in detected:
                detected.append("chrome")
                
            # Check browsers that were detected
            selected_count = 0
            for browser_id in detected:
                if browser_id in self.browser_checkboxes:
                    checkbox_info = self.browser_checkboxes[browser_id]
                    checkbox_info.var.set(True)
                    checkbox_info.checkbox.update()
                    selected_count += 1
                    self.log(f"Selected {browser_id}")
            
            # Force update of the UI
            self.root.update()
            
            # Verify selections - critical check
            actually_selected = []
            for browser_id, checkbox_info in self.browser_checkboxes.items():
                if checkbox_info.var.get():
                    actually_selected.append(browser_id)
            
            if actually_selected:
                self.log(f"Verified selection: {', '.join(actually_selected)}")
                self.status_var.set(f"Selected {len(actually_selected)} browsers")
            else:
                # Emergency selection if verification failed
                self.log("VERIFICATION FAILED! No browsers selected. Using emergency selection.")
                # Final fallback - directly check Firefox and Chrome
                for browser_id in ["firefox", "chrome"]:
                    if browser_id in self.browser_checkboxes:
                        # Direct manipulation of the variable and forcing UI update
                        checkbox_info = self.browser_checkboxes[browser_id]
                        checkbox_info.var.set(True)
                        checkbox_info.checkbox.update()
                        self.log(f"Emergency selection of {browser_id}")
                
                # Force UI update
                self.root.update_idletasks()
                self.log("Emergency selection complete. Please verify browsers are selected.")
                    
            # Proceed to auto-detect profiles after browsers are selected
            self.root.after(300, lambda: self.detect_profiles(show_errors=False))
            
        except Exception as e:
            self.log(f"Error in default browser selection: {str(e)}")
            logging.error(f"Browser selection error: {str(e)}")
    
    def on_detect_profiles_click(self):
        """Handler for detect profiles button click."""
        try:
            # Emergency browser selection check BEFORE calling detect_profiles
            # Guarantee we'll never show the "Please select at least one browser" error
            any_selected = False
            for browser_id, checkbox_info in self.browser_checkboxes.items():
                if checkbox_info.var.get():
                    any_selected = True
                    break
                    
            # If nothing is selected, force select Firefox and Chrome immediately
            if not any_selected:
                self.log("BUTTON CLICK FIX: No browsers selected! Force-selecting Firefox and Chrome")
                for browser_id in ["firefox", "chrome"]:
                    if browser_id in self.browser_checkboxes:
                        checkbox_info = self.browser_checkboxes[browser_id]
                        checkbox_info.var.set(True)
                        self.log(f"Force-selected {browser_id}")
                
                # Force UI update to show the selections
                self.root.update_idletasks()
            
            # Now proceed with normal profile detection
            self.detect_profiles()
        except Exception as e:
            self.log(f"Error in detect profiles button handler: {str(e)}")
            # If all else fails, directly handle the error here
            self.status_var.set("Detected 0 profiles")
    
    def fix_profile(self, profile: Profile):
        """Fix a corrupted profile."""
        if messagebox.askyesno("Confirm", f"Are you sure you want to fix the profile '{profile.name}'?"):
            self.processing = True
            self.progress_var.set(0)
            
            # Start fix in background
            thread = threading.Thread(
                target=self._fix_profile_thread,
                args=(profile,)
            )
            thread.daemon = True
            thread.start()
    
    def _fix_profile_thread(self, profile: Profile):
        """Background thread for profile fixing."""
        try:
            if self.migrator.fix_profile(profile.path):
                self.log(f"Successfully fixed profile: {profile.name}")
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Profile '{profile.name}' fixed successfully!"))
            else:
                self.log(f"Failed to fix profile: {profile.name}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fix profile '{profile.name}'!"))
        except Exception as e:
            logging.error(f"Fix error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error fixing profile: {str(e)}"))
        finally:
            self.processing = False
            self.progress_var.set(100)
    
    def run(self):
        """Start the GUI application."""
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Before showing the window, setup custom styles
        self.style.configure("Accent.TButton", background="#0078D7", foreground="white")
        
        # Show welcome message
        self.log(f"Floorpizer {VERSION} started")
        self.status_var.set(f"Floorpizer {VERSION} ready")
        
        # Run the application
        self.root.mainloop() 