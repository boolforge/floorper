#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants for the Floorper application.
"""

import os
import platform

# Application version
APP_VERSION = "3.0.0"

# Browser definitions with detection paths and other info
BROWSERS = {
    # Target browser (not shown in source browsers list)
    "floorp": {
        "name": "Floorp",
        "exe_names": ["floorp.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/floorp/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Floorp"
        ]
    },
    
    # Mozilla family
    "firefox": {
        "name": "Firefox",
        "exe_names": ["firefox.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Mozilla/Firefox/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Mozilla\Firefox"
        ]
    },
    "waterfox": {
        "name": "Waterfox",
        "exe_names": ["waterfox.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Waterfox/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Waterfox"
        ]
    },
    "pale_moon": {
        "name": "Pale Moon",
        "exe_names": ["palemoon.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Moonchild Productions/Pale Moon/Profiles"),
            os.path.expanduser("~/AppData/Roaming/Pale Moon/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Moonchild Productions\Pale Moon"
        ]
    },
    "basilisk": {
        "name": "Basilisk",
        "exe_names": ["basilisk.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Moonchild Productions/Basilisk/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Moonchild Productions\Basilisk"
        ]
    },
    "librewolf": {
        "name": "LibreWolf",
        "exe_names": ["librewolf.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/LibreWolf/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\LibreWolf"
        ]
    },
    "seamonkey": {
        "name": "SeaMonkey",
        "exe_names": ["seamonkey.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Mozilla/SeaMonkey/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Mozilla\SeaMonkey"
        ]
    },
    
    # Chromium family
    "chrome": {
        "name": "Google Chrome",
        "exe_names": ["chrome.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Google/Chrome/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Google\Chrome"
        ]
    },
    "chromium": {
        "name": "Chromium",
        "exe_names": ["chromium.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Chromium/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Chromium"
        ]
    },
    "edge": {
        "name": "Microsoft Edge",
        "exe_names": ["msedge.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Microsoft/Edge/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Microsoft\Edge"
        ]
    },
    "brave": {
        "name": "Brave",
        "exe_names": ["brave.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/BraveSoftware/Brave-Browser/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\BraveSoftware\Brave-Browser"
        ]
    },
    "opera": {
        "name": "Opera",
        "exe_names": ["opera.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Opera Software/Opera Stable"),
            os.path.expanduser("~/AppData/Roaming/Opera/Opera")
        ],
        "profile_registry": [
            r"SOFTWARE\Opera Software"
        ]
    },
    "opera_gx": {
        "name": "Opera GX",
        "exe_names": ["opera_gx.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Opera Software/Opera GX Stable")
        ],
        "profile_registry": [
            r"SOFTWARE\Opera Software\Opera GX Stable"
        ]
    },
    "vivaldi": {
        "name": "Vivaldi",
        "exe_names": ["vivaldi.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Vivaldi/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Vivaldi"
        ]
    },
    "tor_browser": {
        "name": "Tor Browser",
        "exe_names": ["firefox.exe", "tor-browser.exe", "start-tor-browser.exe"],
        "profile_paths": [
            os.path.expanduser("~/Desktop/Tor Browser/Browser/TorBrowser/Data/Browser/profile.default")
        ],
        "profile_registry": []
    },
    
    # Other browsers
    "maxthon": {
        "name": "Maxthon",
        "exe_names": ["maxthon.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Maxthon/Application/User Data"),
            os.path.expanduser("~/AppData/Roaming/Maxthon5")
        ],
        "profile_registry": [
            r"SOFTWARE\Maxthon5"
        ]
    },
    "slimjet": {
        "name": "Slimjet",
        "exe_names": ["slimjet.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Slimjet/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Slimjet"
        ]
    },
    "cent": {
        "name": "Cent Browser",
        "exe_names": ["cent-browser.exe", "chrome.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/CentBrowser/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Cent Browser"
        ]
    },
    "comodo": {
        "name": "Comodo Dragon",
        "exe_names": ["dragon.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Comodo/Dragon/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Comodo\Dragon"
        ]
    },
    "yandex": {
        "name": "Yandex Browser",
        "exe_names": ["browser.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Yandex/YandexBrowser/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\Yandex\YandexBrowser"
        ]
    },
    "360": {
        "name": "360 Browser",
        "exe_names": ["360chrome.exe", "360se.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/360Chrome/Chrome/User Data"),
            os.path.expanduser("~/AppData/Local/360se6/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\360Chrome",
            r"SOFTWARE\360se6"
        ]
    },
    "iron": {
        "name": "SRWare Iron",
        "exe_names": ["iron.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/Chromium/User Data"),
            os.path.expanduser("~/AppData/Local/SRWare Iron/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\SRWare"
        ]
    },
    "coc_coc": {
        "name": "Coc Coc",
        "exe_names": ["coccoc.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/CocCoc/Browser/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\CocCoc"
        ]
    },
    "netscape": {
        "name": "Netscape",
        "exe_names": ["netscape.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Netscape/NSB/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Netscape\Netscape Browser"
        ]
    },
    "avant": {
        "name": "Avant Browser",
        "exe_names": ["avant.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Roaming/Avant Browser/Profiles")
        ],
        "profile_registry": [
            r"SOFTWARE\Avant Browser"
        ]
    },
    "uc": {
        "name": "UC Browser",
        "exe_names": ["UCBrowser.exe"],
        "profile_paths": [
            os.path.expanduser("~/AppData/Local/UCBrowser/User Data")
        ],
        "profile_registry": [
            r"SOFTWARE\UCBrowser"
        ]
    }
}

# Browser colors for UI display
BROWSER_COLORS = {
    "floorp": "#0066CC",
    "firefox": "#FF9500",
    "chrome": "#4285F4",
    "edge": "#0078D7",
    "brave": "#FB542B",
    "opera": "#FF1B2D",
    "opera_gx": "#FF1B2D",
    "vivaldi": "#EF3939",
    "waterfox": "#00ACFF",
    "pale_moon": "#00B7E0",
    "librewolf": "#506CF0",
    "basilisk": "#45A1FF",
    "chromium": "#4587F3",
    "tor_browser": "#7D4698",
    "maxthon": "#2166BC",
    "slimjet": "#1A73E8",
    "cent": "#F48024",
    "comodo": "#00B050",
    "yandex": "#FFCC00",
    "360": "#32CD32",
    "iron": "#C0C0C0",
    "coc_coc": "#43A047",
    "netscape": "#00C1DE",
    "avant": "#0000FF",
    "uc": "#FF6A00",
    "seamonkey": "#4A6FBA",
    "default": "#808080"  # Default color for unknown browsers
}

# Icons for browsers (placeholder paths, will be implemented with actual icons)
BROWSER_ICONS = {
    "floorp": "icons/floorp.png",
    "firefox": "icons/firefox.png",
    "chrome": "icons/chrome.png",
    "edge": "icons/edge.png",
    "brave": "icons/brave.png",
    "opera": "icons/opera.png",
    "opera_gx": "icons/opera_gx.png",
    "vivaldi": "icons/vivaldi.png",
    "waterfox": "icons/waterfox.png",
    "pale_moon": "icons/pale_moon.png",
    "librewolf": "icons/librewolf.png",
    "basilisk": "icons/basilisk.png",
    "chromium": "icons/chromium.png",
    "tor_browser": "icons/tor_browser.png",
    "maxthon": "icons/maxthon.png",
    # Add more as needed
}
