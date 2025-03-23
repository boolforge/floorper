"""
Configuration settings for Floorpizer.
Contains all constants, paths, and configuration values.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class BrowserConfig:
    name: str
    app_id: str
    profiles_dir: str
    profiles_ini: str
    executable: str
    registry_path: str

@dataclass
class FloorpConfig:
    name: str
    app_id: str
    profiles_dir: str
    profiles_ini: str
    executable: str
    registry_path: str
    dirs: List[str]
    files: List[str]
    version: str

# Version information
VERSION = "2.0.0"
AUTHOR = "Your Name"
LICENSE = "MIT"

# Browser configurations
BROWSERS: Dict[str, BrowserConfig] = {
    "firefox": BrowserConfig(
        name="Firefox",
        app_id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
        profiles_dir="Mozilla\\Firefox\\Profiles",
        profiles_ini="Mozilla\\Firefox\\profiles.ini",
        executable="firefox.exe",
        registry_path=r"SOFTWARE\Mozilla\Mozilla Firefox"
    ),
    "chrome": BrowserConfig(
        name="Google Chrome",
        app_id="{8A69D345-D564-463c-AFF1-A69D9E530F96}",
        profiles_dir="Google\\Chrome\\User Data",
        profiles_ini="",
        executable="chrome.exe",
        registry_path=r"SOFTWARE\Google\Chrome"
    ),
    "edge": BrowserConfig(
        name="Microsoft Edge",
        app_id="{B2A7FD52-51F8-4D47-A8F1-7B1D4F8F8F7F}",
        profiles_dir="Microsoft\\Edge\\User Data",
        profiles_ini="",
        executable="msedge.exe",
        registry_path=r"SOFTWARE\Microsoft\Edge"
    ),
    "opera": BrowserConfig(
        name="Opera",
        app_id="{8B5F1F82-A8E3-4B8A-8D1F-7F8B8F8F8F8F}",
        profiles_dir="Opera Software\\Opera Stable",
        profiles_ini="",
        executable="opera.exe",
        registry_path=r"SOFTWARE\Opera Software\Opera Stable"
    ),
    "brave": BrowserConfig(
        name="Brave",
        app_id="{AFE6A462-C574-4B8A-AF43-4CC60DF4563B}",
        profiles_dir="BraveSoftware\\Brave-Browser\\User Data",
        profiles_ini="",
        executable="brave.exe",
        registry_path=r"SOFTWARE\BraveSoftware\Brave-Browser"
    ),
    "vivaldi": BrowserConfig(
        name="Vivaldi",
        app_id="{50EC71FB-D6A3-4A2E-8946-B6F5F6F6F6F6}",
        profiles_dir="Vivaldi\\User Data",
        profiles_ini="",
        executable="vivaldi.exe",
        registry_path=r"SOFTWARE\Vivaldi"
    ),
    "librewolf": BrowserConfig(
        name="LibreWolf",
        app_id="{EC8030F7-C20A-464F-9B0E-13A3A9E97384}",
        profiles_dir="LibreWolf\\Profiles",
        profiles_ini="LibreWolf\\profiles.ini",
        executable="librewolf.exe",
        registry_path=r"SOFTWARE\LibreWolf"
    ),
    "waterfox": BrowserConfig(
        name="Waterfox",
        app_id="{EC8030F7-C20A-464F-9B0E-13A3A9E97384}",
        profiles_dir="Waterfox\\Profiles",
        profiles_ini="Waterfox\\profiles.ini",
        executable="waterfox.exe",
        registry_path=r"SOFTWARE\Waterfox"
    ),
    "pale_moon": BrowserConfig(
        name="Pale Moon",
        app_id="{8DE7FCBB-C55C-4FCD-8D6A-6B6F6F6F6F6F}",
        profiles_dir="Moonchild Productions\\Pale Moon\\Profiles",
        profiles_ini="Moonchild Productions\\Pale Moon\\profiles.ini",
        executable="palemoon.exe",
        registry_path=r"SOFTWARE\Moonchild Productions\Pale Moon"
    ),
    "basilisk": BrowserConfig(
        name="Basilisk",
        app_id="{EC8030F7-C20A-464F-9B0E-13A3A9E97384}",
        profiles_dir="Basilisk\\Profiles",
        profiles_ini="Basilisk\\profiles.ini",
        executable="basilisk.exe",
        registry_path=r"SOFTWARE\Basilisk"
    ),
    "chromium": BrowserConfig(
        name="Chromium",
        app_id="{5AECBD6F-4C9A-4A0F-A3D6-C7F4F0FD4669}",
        profiles_dir="Chromium\\User Data",
        profiles_ini="",
        executable="chromium.exe",
        registry_path=r"SOFTWARE\Chromium"
    ),
    "opera_gx": BrowserConfig(
        name="Opera GX",
        app_id="{8B5F1F82-A8E3-4B8A-8D1F-7F8B8F8F8F8F}",
        profiles_dir="Opera Software\\Opera GX Stable",
        profiles_ini="",
        executable="opera_gx.exe",
        registry_path=r"SOFTWARE\Opera Software\Opera GX Stable"
    ),
    "tor_browser": BrowserConfig(
        name="Tor Browser",
        app_id="{EC8030F7-C20A-464F-9B0E-13A3A9E97384}",
        profiles_dir="TorBrowser\\Data\\Browser\\profile.default",
        profiles_ini="",
        executable="firefox.exe",
        registry_path=r"SOFTWARE\Tor Browser"
    ),
    "yandex": BrowserConfig(
        name="Yandex Browser",
        app_id="{36FCA03C-6DAA-43BB-A46F-11D8DFD11F4C}",
        profiles_dir="Yandex\\YandexBrowser\\User Data",
        profiles_ini="",
        executable="browser.exe",
        registry_path=r"SOFTWARE\Yandex\YandexBrowser"
    ),
    "slimjet": BrowserConfig(
        name="Slimjet",
        app_id="{99A13B39-1B22-4169-80BC-36936CE0B59C}",
        profiles_dir="Slimjet\\User Data",
        profiles_ini="",
        executable="slimjet.exe",
        registry_path=r"SOFTWARE\Slimjet"
    ),
    "seamonkey": BrowserConfig(
        name="SeaMonkey",
        app_id="{92650c4d-4b8e-4d2a-b7eb-24ecf4f6b63a}",
        profiles_dir="Mozilla\\SeaMonkey\\Profiles",
        profiles_ini="Mozilla\\SeaMonkey\\profiles.ini",
        executable="seamonkey.exe",
        registry_path=r"SOFTWARE\Mozilla\SeaMonkey"
    )
}

# Floorp configuration
FLOORP = FloorpConfig(
    name="Floorp",
    app_id="{9D8B75F0-9623-4689-9C78-DCEA9FF97F57}",
    profiles_dir="Floorp\\Profiles",
    profiles_ini="Floorp\\profiles.ini",
    executable="floorp.exe",
    registry_path=r"SOFTWARE\Floorp",
    dirs=[
        "Workspaces",
        "newtabImages",
        "ssb",
        "chrome",
        "extension-store",
        "extension-store-menus"
    ],
    files=[
        "floorp_notes_backup.json",
        "extension-preferences.json",
        "search.json.mozlz4"
    ],
    version=VERSION
)

# File patterns
EXCLUDE_PATTERNS: List[str] = [
    "saved-telemetry-pings",
    "Telemetry.ShutdownTime.txt",
    "datareporting",
    "ExperimentStoreData.json",
    "memory-report.json.gz",
    "enumerate_devices.txt",
    "minidumps",
    "crashes",
    "mediacapabilities",
    "shader-cache",
    "security_state",
    "bookmarkbackups",
    "gmp",
    "gmp-gmpopenh264",
    "gmp-widevinecdm"
]

CRITICAL_FILES: List[str] = [
    "logins.json",
    "logins-backup.json",
    "key4.db",
    "cert9.db",
    "places.sqlite",
    "cookies.sqlite",
    "formhistory.sqlite",
    "permissions.sqlite",
    "content-prefs.sqlite",
    "storage.sqlite",
    "webappsstore.sqlite",
    "sessionstore.jsonlz4",
    "prefs.js",
    "extensions.json",
    "addonStartup.json.lz4",
    "containers.json",
    "handlers.json",
    "xulstore.json",
    "downloads.json",
    "search.json.mozlz4"
]

# Profile items to migrate
PROFILE_ITEMS = [
    "bookmarks",
    "history",
    "passwords",
    "cookies",
    "extensions",
    "preferences",
    "sessions",
    "forms",
    "permissions",
    "certificates"
]

# Migration rules
MIGRATION_RULES = {
    "firefox": {
        "bookmarks": ["places.sqlite"],
        "history": ["places.sqlite"],
        "passwords": ["logins.json", "key4.db"],
        "cookies": ["cookies.sqlite"],
        "extensions": ["extensions.json", "addonStartup.json.lz4"],
        "preferences": ["prefs.js"],
        "sessions": ["sessionstore.jsonlz4"],
        "forms": ["formhistory.sqlite"],
        "permissions": ["permissions.sqlite"],
        "certificates": ["cert9.db"]
    }
}

# Backup settings
BACKUP_SUFFIX = "_backup"

# Path configurations
def get_appdata_path() -> Path:
    """Get the AppData path based on the operating system."""
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"])
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    else:
        return Path.home() / ".config"

def get_browser_path(browser: str) -> Path:
    """Get the browser profile path."""
    return get_appdata_path() / BROWSERS[browser].profiles_dir

def get_floorp_path() -> Path:
    """Get the Floorp profile path."""
    return get_appdata_path() / FLOORP.profiles_dir

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = "floorpizer.log"
LOG_LEVEL = logging.INFO

# Performance settings
CHUNK_SIZE = 8192  # For file operations
MAX_WORKERS = os.cpu_count() or 4  # For parallel operations
BUFFER_SIZE = 1024 * 1024  # 1MB buffer for large files

# Security settings
ENCRYPTION_KEY_SIZE = 32  # 256 bits
HASH_ALGORITHM = "sha256"
SALT_SIZE = 16

# Error handling
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
TIMEOUT = 30  # seconds for file operations