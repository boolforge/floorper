#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorpizer - Universal Browser Profile Migration Tool
===================================================

A powerful tool to migrate profiles from various browsers to Floorp.
Supports Firefox, Chrome, Edge, Opera, Brave, Vivaldi, LibreWolf,
Waterfox, Pale Moon, and Basilisk.

Author: Your Name
Version: 2.0.0
License: MIT
"""

import os
import sys
import argparse
import logging
import colorama
from colorama import Fore, Style
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image

# Import local modules
from .utils import decompress_lz4, safe_db_connection
from .browser_detection import BrowserDetector, Profile
from .profile_migration import ProfileMigrator
from .gui import FloorpizerGUI
from .config import (
    BROWSERS,
    FLOORP,
    VERSION
)

# Setup logging
logger = logging.getLogger("Floorpizer")

def print_banner():
    """Print the application banner."""
    banner = f"""
{Fore.CYAN}
    FLOORPIZER
    ==========
{Style.RESET_ALL}
{Fore.YELLOW}Universal Browser Profile Migration Tool v{VERSION}{Style.RESET_ALL}
"""
    print(banner)

def print_profile_summary(profile: Profile) -> None:
    """Print a summary of profile contents."""
    print(f"\n{Fore.CYAN}Profile: {profile.name}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Browser: {BROWSERS[profile.browser_type].name}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Version: {profile.version}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Default: {'Yes' if profile.is_default else 'No'}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Contents:{Style.RESET_ALL}")
    for key, value in profile.stats.items():
        print(f"{Fore.GREEN}  {key.title()}: {value}{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Total items: {sum(profile.stats.values())}{Style.RESET_ALL}")

def handle_interactive_mode():
    """Handle interactive menu mode."""
    print(f"\n{Fore.CYAN}Select an option:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Migrate Firefox profile to Floorp")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Migrate Chrome profile to Floorp")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Migrate Edge profile to Floorp")
    print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Migrate Opera profile to Floorp")
    print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Migrate Brave profile to Floorp")
    print(f"{Fore.YELLOW}6.{Style.RESET_ALL} Migrate Vivaldi profile to Floorp")
    print(f"{Fore.YELLOW}7.{Style.RESET_ALL} Migrate LibreWolf profile to Floorp")
    print(f"{Fore.YELLOW}8.{Style.RESET_ALL} Migrate Waterfox profile to Floorp")
    print(f"{Fore.YELLOW}9.{Style.RESET_ALL} Migrate Pale Moon profile to Floorp")
    print(f"{Fore.YELLOW}10.{Style.RESET_ALL} Migrate Basilisk profile to Floorp")
    print(f"{Fore.YELLOW}11.{Style.RESET_ALL} Migrate ALL detected profiles to Floorp")
    print(f"{Fore.YELLOW}12.{Style.RESET_ALL} Exit")
    
    try:
        option = int(input(f"\n{Fore.GREEN}Enter the number of the desired option: {Style.RESET_ALL}"))
        
        if option == 12:
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
            return
        
        if option == 11:  # Migrate ALL profiles
            handle_migrate_all()
            return
            
        if 1 <= option <= 10:
            browser_map = {
                1: "firefox", 2: "chrome", 3: "edge", 4: "opera",
                5: "brave", 6: "vivaldi", 7: "librewolf", 8: "waterfox",
                9: "pale_moon", 10: "basilisk"
            }
            browser = browser_map[option]
            handle_single_browser_migration(browser)
        else:
            print(f"\n{Fore.RED}Invalid option{Style.RESET_ALL}")
            
    except ValueError:
        print(f"\n{Fore.RED}Please enter a valid number{Style.RESET_ALL}")

def handle_single_browser_migration(browser_type: str):
    """Handle migration for a single browser type."""
    detector = BrowserDetector()
    profiles = detector.detect_profiles(browser_type)
    
    if not profiles:
        print(f"\n{Fore.RED}No profiles found for {BROWSERS[browser_type].name}{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Detected profiles for {BROWSERS[browser_type].name}:{Style.RESET_ALL}")
    for i, profile in enumerate(profiles, 1):
        print(f"\n{Fore.YELLOW}{i}. {profile.name} {'(Default)' if profile.is_default else ''}{Style.RESET_ALL}")
        print(f"   Path: {profile.path}")
        print_profile_summary(profile)
    
    if len(profiles) > 1:
        print(f"\n{Fore.CYAN}Multiple profiles detected. Choose an option:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Migrate a specific profile")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Merge all profiles into one")
        
        try:
            merge_option = int(input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}"))
            
            if merge_option == 2:
                handle_merge_profiles(profiles)
                return
                
            if merge_option != 1:
                print(f"\n{Fore.RED}Invalid option{Style.RESET_ALL}")
                return
        except ValueError:
            print(f"\n{Fore.RED}Please enter a valid number{Style.RESET_ALL}")
            return
    
    try:
        profile_index = int(input(f"\n{Fore.GREEN}Select the number of the profile to migrate: {Style.RESET_ALL}")) - 1
        if 0 <= profile_index < len(profiles):
            selected_profile = profiles[profile_index]
            handle_profile_migration(selected_profile)
        else:
            print(f"\n{Fore.RED}Invalid profile selection{Style.RESET_ALL}")
    except ValueError:
        print(f"\n{Fore.RED}Please enter a valid number{Style.RESET_ALL}")

def handle_migrate_all():
    """Handle migration of all detected profiles."""
    detector = BrowserDetector()
    all_profiles = detector.detect_all_browsers()
    
    if not all_profiles:
        print(f"\n{Fore.RED}No profiles detected in any browser!{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Detected profiles:{Style.RESET_ALL}")
    for browser_type, profiles in all_profiles.items():
        print(f"\n{Fore.YELLOW}{BROWSERS[browser_type].name}:{Style.RESET_ALL}")
        for profile in profiles:
            print(f"  - {profile.name} {'(Default)' if profile.is_default else ''}")
            print_profile_summary(profile)
    
    print(f"\n{Fore.CYAN}Choose an option:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Migrate each profile separately")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Merge all profiles into one")
    
    try:
        merge_option = int(input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}"))
        
        if merge_option == 2:
            handle_merge_all_profiles(all_profiles)
        elif merge_option == 1:
            for browser_type, profiles in all_profiles.items():
                for profile in profiles:
                    handle_profile_migration(profile)
        else:
            print(f"\n{Fore.RED}Invalid option{Style.RESET_ALL}")
    except ValueError:
        print(f"\n{Fore.RED}Please enter a valid number{Style.RESET_ALL}")

def handle_profile_migration(profile: Profile):
    """Handle migration of a single profile."""
    migrator = ProfileMigrator()
    
    # Create target profile path
    target_profile = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / FLOORP.profiles_dir / f"{profile.name}_floorp"
    
    print(f"\n{Fore.CYAN}Migrating {profile.name} from {BROWSERS[profile.browser_type].name}...{Style.RESET_ALL}")
    if migrator.migrate_profile(profile.path, target_profile):
        print(f"{Fore.GREEN}Migration successful!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Migration failed!{Style.RESET_ALL}")

def handle_merge_profiles(profiles: List[Profile]):
    """Handle merging multiple profiles into one."""
    migrator = ProfileMigrator()
    
    # Create target profile path
    target_profile = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / FLOORP.profiles_dir / "merged_profile"
    
    print(f"\n{Fore.CYAN}Merging {len(profiles)} profiles...{Style.RESET_ALL}")
    if migrator.migrate_profile(profiles[0].path, target_profile, merge=True):
        print(f"{Fore.GREEN}Merge successful!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Merge failed!{Style.RESET_ALL}")

def handle_merge_all_profiles(all_profiles: Dict[str, List[Profile]]):
    """Handle merging all detected profiles into one."""
    migrator = ProfileMigrator()
    
    # Create target profile path
    target_profile = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / FLOORP.profiles_dir / "integrated_profile"
    
    print(f"\n{Fore.CYAN}Merging all profiles...{Style.RESET_ALL}")
    success = True
    
    for browser_type, profiles in all_profiles.items():
        for profile in profiles:
            print(f"\n{Fore.CYAN}Processing {profile.name} from {BROWSERS[browser_type].name}...{Style.RESET_ALL}")
            if not migrator.migrate_profile(profile.path, target_profile, merge=True):
                success = False
                print(f"{Fore.RED}Failed to process {profile.name}{Style.RESET_ALL}")
    
    if success:
        print(f"\n{Fore.GREEN}All profiles merged successfully!{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}Some profiles failed to merge.{Style.RESET_ALL}")

def generate_floorplan(room_width, room_length, furniture):
    """Generate a floorplan with furniture placement"""
    # Create a new figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Draw room outline
    ax.add_patch(plt.Rectangle((0, 0), room_width, room_length, fill=False, color='black', linewidth=2))
    
    # Draw furniture
    for item in furniture:
        x, y = item['position']
        width, length = item['dimensions']
        color = item['color']
        
        # Draw furniture rectangle
        ax.add_patch(plt.Rectangle((x, y), width, length, fill=True, color=color, alpha=0.5))
        
        # Add furniture label
        ax.text(x + width/2, y + length/2, item['name'], 
                horizontalalignment='center', verticalalignment='center')
    
    # Set plot properties
    ax.set_xlim(-1, room_width + 1)
    ax.set_ylim(-1, room_length + 1)
    ax.set_aspect('equal')
    ax.grid(True)
    
    # Save the plot
    plt.savefig('floorplan.png')
    plt.close()
    
    return 'floorplan.png'

def main():
    """Process command line arguments and GUI."""
    
    # Initialize colorama for colored output
    colorama.init()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Universal Browser Profile Migration Tool")
    parser.add_argument("--source", help="Source profile path")
    parser.add_argument("--target", help="Target profile path")
    parser.add_argument("--browser", help="Source browser type")
    parser.add_argument("--auto", action="store_true", help="Auto-detect and migrate profiles")
    parser.add_argument("--merge", action="store_true", help="Merge multiple profiles into one")
    parser.add_argument("--no-gui", action="store_true", help="Force command line mode")
    
    args = parser.parse_args()
    
    # ASCII art logo
    banner = f"""
{Fore.CYAN}
    FLOORPIZER
    ==========
{Style.RESET_ALL}
{Fore.YELLOW}Universal Browser Profile Migration Tool v{VERSION}{Style.RESET_ALL}
"""
    
    # If no arguments are provided, try to use GUI
    if len(sys.argv) == 1 and not args.no_gui:
        try:
            # Try with our simplified GUI first
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            print(banner)
            
            # Create a simple window
            root = tk.Tk()
            root.title("Floorpizer")
            root.geometry("800x600")
            
            # Main frame
            main_frame = ttk.Frame(root, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=10)
            
            header_label = ttk.Label(
                header_frame,
                text=f"Floorpizer {VERSION}",
                font=("Helvetica", 16, "bold")
            )
            header_label.pack()
            
            subtitle_label = ttk.Label(
                header_frame,
                text="Universal Browser Profile Migration Tool",
                font=("Helvetica", 10)
            )
            subtitle_label.pack()
            
            # Browser selection
            browser_frame = ttk.LabelFrame(main_frame, text="Select Browsers", padding=10)
            browser_frame.pack(fill=tk.X, pady=10)
            
            # Create checkboxes for each browser
            browser_vars = {}
            for i, (browser_id, browser_info) in enumerate(BROWSERS.items()):
                var = tk.BooleanVar()
                checkbox = ttk.Checkbutton(
                    browser_frame,
                    text=browser_info.name,
                    variable=var
                )
                checkbox.grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=2)
                browser_vars[browser_id] = var
            
            # Action buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            def detect_profiles():
                selected_browsers = [
                    browser_id for browser_id, var in browser_vars.items()
                    if var.get()
                ]
                
                if not selected_browsers:
                    messagebox.showerror("Error", "Please select at least one browser")
                    return
                
                log_text.insert(tk.END, "Starting profile detection...\n")
                
                detector = BrowserDetector()
                all_profiles = []
                
                for browser_id in selected_browsers:
                    browser_name = BROWSERS[browser_id].name
                    log_text.insert(tk.END, f"Detecting profiles for {browser_name}...\n")
                    profiles = detector.detect_profiles(browser_id)
                    
                    if profiles:
                        log_text.insert(tk.END, f"Found {len(profiles)} profiles for {browser_name}\n")
                        all_profiles.extend(profiles)
                        for profile in profiles:
                            log_text.insert(tk.END, f"  - {profile.name} ({profile.path})\n")
                    else:
                        log_text.insert(tk.END, f"No profiles found for {browser_name}\n")
                
                if all_profiles:
                    messagebox.showinfo("Success", f"Found {len(all_profiles)} profiles")
                else:
                    messagebox.showinfo("Info", "No profiles found")
                
                log_text.see(tk.END)
            
            def migrate_profiles():
                selected_browsers = [
                    browser_id for browser_id, var in browser_vars.items()
                    if var.get()
                ]
                
                if not selected_browsers:
                    messagebox.showerror("Error", "Please select at least one browser")
                    return
                
                detector = BrowserDetector()
                migrator = ProfileMigrator()
                all_profiles = []
                
                for browser_id in selected_browsers:
                    profiles = detector.detect_profiles(browser_id)
                    all_profiles.extend(profiles)
                
                if not all_profiles:
                    messagebox.showerror("Error", "No profiles found to migrate")
                    return
                
                result = messagebox.askquestion("Confirm", f"Migrate {len(all_profiles)} profiles to Floorp?")
                if result != "yes":
                    return
                
                log_text.insert(tk.END, "Starting profile migration...\n")
                
                for profile in all_profiles:
                    log_text.insert(tk.END, f"Migrating {profile.name} from {BROWSERS[profile.browser_type].name}...\n")
                    try:
                        migrator.migrate_profile(profile, FLOORP.path)
                        log_text.insert(tk.END, f"Successfully migrated {profile.name}\n")
                    except Exception as e:
                        log_text.insert(tk.END, f"Error migrating {profile.name}: {e}\n")
                
                messagebox.showinfo("Complete", "Migration completed")
                log_text.see(tk.END)
            
            detect_button = ttk.Button(
                button_frame,
                text="Detect Profiles",
                command=detect_profiles
            )
            detect_button.pack(side=tk.LEFT, padx=5)
            
            migrate_button = ttk.Button(
                button_frame,
                text="Migrate to Floorp",
                command=migrate_profiles
            )
            migrate_button.pack(side=tk.LEFT, padx=5)
            
            # Log area
            log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
            log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            log_text = tk.Text(log_frame, height=10, width=80)
            log_text.pack(fill=tk.BOTH, expand=True)
            log_text.insert(tk.END, f"Floorpizer {VERSION} started\n")
            log_text.insert(tk.END, "Simple mode activated due to compatibility issues\n")
            log_text.insert(tk.END, "Please select browsers and click 'Detect Profiles'\n")
            
            # Status bar
            status_var = tk.StringVar(value="Ready")
            status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Start the application
            root.mainloop()
            return
            
        except Exception as e:
            print(f"{Fore.RED}Error starting GUI: {e}{Style.RESET_ALL}")
            print("Falling back to command line mode...")
    
    # Display logo and version
    print(banner)
    print(f"Universal Browser Profile Migration Tool v{VERSION}")
    
    # Handle command line arguments
    if args.auto:
        handle_migrate_all()
        return
    
    if args.source and args.target:
        migrator = ProfileMigrator()
        if migrator.migrate_profile(args.source, args.target, merge=args.merge):
            print(f"{Fore.GREEN}Migration completed successfully!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Migration failed!{Style.RESET_ALL}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()