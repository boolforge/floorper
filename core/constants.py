#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Constants
===================

Definitions of constants used throughout the Floorper application.
Includes information about browsers, profile paths, and configurations.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, List, Any

# Application version
VERSION = "2.0.0"

# Browser colors for UI
BROWSER_COLORS = {
    "firefox": "#FF9500",
    "chrome": "#4285F4",
    "edge": "#0078D7",
    "brave": "#FB542B",
    "opera": "#FF1B2D",
    "vivaldi": "#EF3939",
    "seamonkey": "#11A9F7",
    "librewolf": "#00ACFF",
    "waterfox": "#00AEF0",
    "pale_moon": "#2A2A2E",
    "basilisk": "#409A5C",
    "floorp": "#009EF7",
    "chromium": "#4587F3",
    "opera_gx": "#FF1B2D",
    "tor_browser": "#7D4698",
    "yandex": "#FFCC00",
    "slimjet": "#5E5E5E",
    "iron": "#4285F4",
    "epic": "#8C52FF",
    "gnome_web": "#4A86CF",
    "midori": "#4CAF50",
    "konqueror": "#1D99F3",
    "falkon": "#1D99F3",
    "otter": "#1D99F3",
    "qutebrowser": "#333333",
    "dillo": "#5E5E5E",
    "netsurf": "#5E5E5E",
    "elinks": "#333333",
    "links": "#333333",
    "lynx": "#333333",
    "w3m": "#333333",
    "default": "#5E5E5E"
}

# Information about supported browsers
BROWSERS = {
    # Firefox and derivatives
    "firefox": {
        "name": "Mozilla Firefox",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Mozilla/Firefox/Profiles",
            # Linux
            "~/.mozilla/firefox",
            # macOS
            "~/Library/Application Support/Firefox/Profiles",
            # Haiku
            "~/config/settings/mozilla/firefox",
            # OS/2
            "~/Mozilla/Firefox/Profiles"
        ],
        "registry_paths": [
            r"SOFTWARE\Mozilla\Mozilla Firefox"
        ],
        "executable_names": ["firefox", "firefox.exe", "firefox-bin"],
        "package_names": ["firefox", "mozilla-firefox"]
    },
    "floorp": {
        "name": "Floorp",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Floorp/Profiles",
            # Linux
            "~/.floorp",
            # macOS
            "~/Library/Application Support/Floorp/Profiles",
            # Haiku
            "~/config/settings/floorp",
            # OS/2
            "~/Floorp/Profiles"
        ],
        "registry_paths": [
            r"SOFTWARE\Floorp"
        ],
        "executable_names": ["floorp", "floorp.exe"],
        "package_names": ["floorp"]
    },
    "librewolf": {
        "name": "LibreWolf",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/LibreWolf/Profiles",
            # Linux
            "~/.librewolf",
            # macOS
            "~/Library/Application Support/LibreWolf/Profiles",
            # Haiku
            "~/config/settings/librewolf",
            # OS/2
            "~/LibreWolf/Profiles"
        ],
        "registry_paths": [],
        "executable_names": ["librewolf", "librewolf.exe"],
        "package_names": ["librewolf"]
    },
    "waterfox": {
        "name": "Waterfox",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Waterfox/Profiles",
            # Linux
            "~/.waterfox",
            # macOS
            "~/Library/Application Support/Waterfox/Profiles",
            # Haiku
            "~/config/settings/waterfox",
            # OS/2
            "~/Waterfox/Profiles"
        ],
        "registry_paths": [
            r"SOFTWARE\Waterfox"
        ],
        "executable_names": ["waterfox", "waterfox.exe"],
        "package_names": ["waterfox"]
    },
    "pale_moon": {
        "name": "Pale Moon",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Moonchild Productions/Pale Moon/Profiles",
            # Linux
            "~/.moonchild productions/pale moon",
            # macOS
            "~/Library/Application Support/Pale Moon/Profiles",
            # Haiku
            "~/config/settings/moonchild productions/pale moon",
            # OS/2
            "~/Moonchild Productions/Pale Moon/Profiles"
        ],
        "registry_paths": [
            r"SOFTWARE\Moonchild Productions\Pale Moon"
        ],
        "executable_names": ["palemoon", "palemoon.exe"],
        "package_names": ["palemoon"]
    },
    "basilisk": {
        "name": "Basilisk",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Moonchild Productions/Basilisk/Profiles",
            # Linux
            "~/.moonchild productions/basilisk",
            # macOS
            "~/Library/Application Support/Basilisk/Profiles",
            # Haiku
            "~/config/settings/moonchild productions/basilisk",
            # OS/2
            "~/Moonchild Productions/Basilisk/Profiles"
        ],
        "registry_paths": [
            r"SOFTWARE\Moonchild Productions\Basilisk"
        ],
        "executable_names": ["basilisk", "basilisk.exe"],
        "package_names": ["basilisk"]
    },
    "seamonkey": {
        "name": "SeaMonkey",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Mozilla/SeaMonkey/Profiles",
            # Linux
            "~/.mozilla/seamonkey",
            # macOS
            "~/Library/Application Support/SeaMonkey/Profiles",
            # Haiku
            "~/config/settings/mozilla/seamonkey",
            # OS/2
            "~/Mozilla/SeaMonkey/Profiles"
        ],
        "registry_paths": [
            r"SOFTWARE\Mozilla\SeaMonkey"
        ],
        "executable_names": ["seamonkey", "seamonkey.exe"],
        "package_names": ["seamonkey"]
    },
    "tor_browser": {
        "name": "Tor Browser",
        "family": "firefox",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Tor Browser/Browser/TorBrowser/Data/Browser/profile.default",
            # Linux
            "~/.tor-browser/Browser/TorBrowser/Data/Browser/profile.default",
            # macOS
            "~/Library/Application Support/TorBrowser-Data/Browser/profile.default",
            # Haiku
            "~/config/settings/tor-browser/Browser/TorBrowser/Data/Browser/profile.default",
            # OS/2
            "~/Tor Browser/Browser/TorBrowser/Data/Browser/profile.default"
        ],
        "registry_paths": [],
        "executable_names": ["tor-browser", "tor-browser.exe", "start-tor-browser"],
        "package_names": ["tor-browser", "torbrowser"]
    },
    
    # Chrome and derivatives
    "chrome": {
        "name": "Google Chrome",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Google/Chrome/User Data",
            # Linux
            "~/.config/google-chrome",
            # macOS
            "~/Library/Application Support/Google/Chrome",
            # Haiku
            "~/config/settings/Google/Chrome",
            # OS/2
            "~/Google/Chrome/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\Google\Chrome"
        ],
        "executable_names": ["chrome", "chrome.exe", "google-chrome", "google-chrome-stable"],
        "package_names": ["google-chrome", "google-chrome-stable"]
    },
    "chromium": {
        "name": "Chromium",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Chromium/User Data",
            # Linux
            "~/.config/chromium",
            # macOS
            "~/Library/Application Support/Chromium",
            # Haiku
            "~/config/settings/Chromium",
            # OS/2
            "~/Chromium/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\Chromium"
        ],
        "executable_names": ["chromium", "chromium.exe", "chromium-browser"],
        "package_names": ["chromium", "chromium-browser"]
    },
    "edge": {
        "name": "Microsoft Edge",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Microsoft/Edge/User Data",
            # Linux
            "~/.config/microsoft-edge",
            # macOS
            "~/Library/Application Support/Microsoft Edge",
            # Haiku
            "~/config/settings/Microsoft/Edge",
            # OS/2
            "~/Microsoft/Edge/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\Microsoft\Edge"
        ],
        "executable_names": ["msedge", "msedge.exe", "microsoft-edge"],
        "package_names": ["microsoft-edge", "microsoft-edge-stable"]
    },
    "brave": {
        "name": "Brave",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/BraveSoftware/Brave-Browser/User Data",
            # Linux
            "~/.config/BraveSoftware/Brave-Browser",
            # macOS
            "~/Library/Application Support/BraveSoftware/Brave-Browser",
            # Haiku
            "~/config/settings/BraveSoftware/Brave-Browser",
            # OS/2
            "~/BraveSoftware/Brave-Browser/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\BraveSoftware\Brave-Browser"
        ],
        "executable_names": ["brave", "brave.exe", "brave-browser"],
        "package_names": ["brave-browser"]
    },
    "opera": {
        "name": "Opera",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Opera Software/Opera Stable",
            # Linux
            "~/.config/opera",
            # macOS
            "~/Library/Application Support/com.operasoftware.Opera",
            # Haiku
            "~/config/settings/Opera Software/Opera Stable",
            # OS/2
            "~/Opera Software/Opera Stable"
        ],
        "registry_paths": [
            r"SOFTWARE\Opera Software"
        ],
        "executable_names": ["opera", "opera.exe"],
        "package_names": ["opera", "opera-stable"]
    },
    "vivaldi": {
        "name": "Vivaldi",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Vivaldi/User Data",
            # Linux
            "~/.config/vivaldi",
            # macOS
            "~/Library/Application Support/Vivaldi",
            # Haiku
            "~/config/settings/Vivaldi",
            # OS/2
            "~/Vivaldi/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\Vivaldi"
        ],
        "executable_names": ["vivaldi", "vivaldi.exe"],
        "package_names": ["vivaldi", "vivaldi-stable"]
    },
    "opera_gx": {
        "name": "Opera GX",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Opera Software/Opera GX Stable",
            # Linux
            "~/.config/opera-gx",
            # macOS
            "~/Library/Application Support/com.operasoftware.OperaGX",
            # Haiku
            "~/config/settings/Opera Software/Opera GX Stable",
            # OS/2
            "~/Opera Software/Opera GX Stable"
        ],
        "registry_paths": [
            r"SOFTWARE\Opera Software\Opera GX"
        ],
        "executable_names": ["opera-gx", "opera-gx.exe"],
        "package_names": ["opera-gx"]
    },
    
    # Other browsers
    "safari": {
        "name": "Safari",
        "family": "safari",
        "profile_paths": [
            # macOS
            "~/Library/Safari",
            "~/Library/Containers/com.apple.Safari/Data/Library/Safari"
        ],
        "registry_paths": [],
        "executable_names": ["safari"],
        "package_names": []
    },
    "gnome_web": {
        "name": "GNOME Web (Epiphany)",
        "family": "webkit",
        "profile_paths": [
            # Linux
            "~/.config/epiphany",
            "~/.local/share/epiphany"
        ],
        "registry_paths": [],
        "executable_names": ["epiphany", "epiphany-browser", "gnome-web"],
        "package_names": ["epiphany", "epiphany-browser", "gnome-web"]
    },
    "konqueror": {
        "name": "Konqueror",
        "family": "webkit",
        "profile_paths": [
            # Linux
            "~/.kde/share/apps/konqueror",
            "~/.kde4/share/apps/konqueror",
            "~/.local/share/konqueror"
        ],
        "registry_paths": [],
        "executable_names": ["konqueror"],
        "package_names": ["konqueror"]
    },
    "falkon": {
        "name": "Falkon",
        "family": "webkit",
        "profile_paths": [
            # Windows
            "~/AppData/Local/falkon",
            # Linux
            "~/.config/falkon",
            # macOS
            "~/Library/Application Support/falkon"
        ],
        "registry_paths": [],
        "executable_names": ["falkon", "falkon.exe"],
        "package_names": ["falkon"]
    },
    
    # Exotic browsers
    "qutebrowser": {
        "name": "qutebrowser",
        "family": "webkit",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/qutebrowser",
            # Linux
            "~/.config/qutebrowser",
            # macOS
            "~/Library/Application Support/qutebrowser"
        ],
        "registry_paths": [],
        "executable_names": ["qutebrowser", "qutebrowser.exe"],
        "package_names": ["qutebrowser"]
    },
    "dillo": {
        "name": "Dillo",
        "family": "other",
        "profile_paths": [
            # Linux
            "~/.dillo"
        ],
        "registry_paths": [],
        "executable_names": ["dillo"],
        "package_names": ["dillo"]
    },
    "netsurf": {
        "name": "NetSurf",
        "family": "other",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/NetSurf",
            # Linux
            "~/.config/netsurf",
            # macOS
            "~/Library/Application Support/NetSurf"
        ],
        "registry_paths": [],
        "executable_names": ["netsurf", "netsurf.exe"],
        "package_names": ["netsurf"]
    },
    
    # Text-based browsers
    "elinks": {
        "name": "ELinks",
        "family": "text",
        "profile_paths": [
            # Linux
            "~/.elinks"
        ],
        "registry_paths": [],
        "executable_names": ["elinks"],
        "package_names": ["elinks"]
    },
    "links": {
        "name": "Links",
        "family": "text",
        "profile_paths": [
            # Linux
            "~/.links",
            "~/.links2"
        ],
        "registry_paths": [],
        "executable_names": ["links", "links2"],
        "package_names": ["links", "links2"]
    },
    "lynx": {
        "name": "Lynx",
        "family": "text",
        "profile_paths": [
            # Linux
            "~/.lynx"
        ],
        "registry_paths": [],
        "executable_names": ["lynx"],
        "package_names": ["lynx"]
    },
    "w3m": {
        "name": "w3m",
        "family": "text",
        "profile_paths": [
            # Linux
            "~/.w3m"
        ],
        "registry_paths": [],
        "executable_names": ["w3m"],
        "package_names": ["w3m"]
    }
}

# Floorp specific information
FLOORP = {
    "name": "Floorp",
    "profiles_dir": "Floorp/Profiles",
    "default_profile": "default",
    "data_types": [
        "bookmarks",
        "history",
        "passwords",
        "cookies",
        "extensions",
        "preferences",
        "sessions"
    ]
}

# Data type descriptions
DATA_TYPES = {
    "bookmarks": {
        "name": "Bookmarks",
        "description": "Web page bookmarks and favorites",
        "firefox_files": ["places.sqlite", "bookmarks.html"],
        "chrome_files": ["Bookmarks"]
    },
    "history": {
        "name": "Browsing History",
        "description": "Visited websites history",
        "firefox_files": ["places.sqlite"],
        "chrome_files": ["History"]
    },
    "passwords": {
        "name": "Saved Passwords",
        "description": "Login credentials for websites",
        "firefox_files": ["logins.json", "key4.db", "signons.sqlite"],
        "chrome_files": ["Login Data"]
    },
    "cookies": {
        "name": "Cookies",
        "description": "Website cookies and storage",
        "firefox_files": ["cookies.sqlite"],
        "chrome_files": ["Cookies"]
    },
    "extensions": {
        "name": "Extensions",
        "description": "Browser extensions and add-ons",
        "firefox_files": ["extensions"],
        "chrome_files": ["Extensions"]
    },
    "preferences": {
        "name": "Preferences",
        "description": "Browser settings and preferences",
        "firefox_files": ["prefs.js", "user.js"],
        "chrome_files": ["Preferences"]
    },
    "sessions": {
        "name": "Sessions",
        "description": "Open tabs and session data",
        "firefox_files": ["sessionstore.jsonlz4", "sessionstore-backups"],
        "chrome_files": ["Current Session", "Current Tabs"]
    }
}

# Platform detection
def get_platform():
    """
    Detect the current platform.
    
    Returns:
        str: Platform identifier (windows, macos, linux, haiku, os2, other)
    """
    system = platform.system().lower()
    
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    elif system == "haiku":
        return "haiku"
    elif system == "os/2":
        return "os2"
    else:
        return "other"

# Current platform
PLATFORM = get_platform()
