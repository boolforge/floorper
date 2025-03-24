#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Constantes
=====================

Definiciones de constantes utilizadas en toda la aplicación Floorper.
Incluye información sobre navegadores, rutas de perfiles y configuraciones.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, List, Any

# Versión de la aplicación
APP_VERSION = "1.0.0"

# Colores para los navegadores
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

# Información de navegadores soportados
BROWSERS = {
    # Firefox y derivados
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
    
    # Chrome y derivados
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
        "package_names": ["brave-browser", "brave"]
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
    "yandex": {
        "name": "Yandex Browser",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Yandex/YandexBrowser/User Data",
            # Linux
            "~/.config/yandex-browser",
            # macOS
            "~/Library/Application Support/Yandex/YandexBrowser",
            # Haiku
            "~/config/settings/Yandex/YandexBrowser",
            # OS/2
            "~/Yandex/YandexBrowser/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\Yandex\YandexBrowser"
        ],
        "executable_names": ["yandex-browser", "yandex-browser.exe", "browser"],
        "package_names": ["yandex-browser", "yandex-browser-stable"]
    },
    "iron": {
        "name": "SRWare Iron",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Chromium/User Data",
            # Linux
            "~/.config/iron",
            # macOS
            "~/Library/Application Support/Iron",
            # Haiku
            "~/config/settings/Iron",
            # OS/2
            "~/Iron/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\SRWare\Iron"
        ],
        "executable_names": ["iron", "iron.exe", "srware-iron"],
        "package_names": ["iron", "srware-iron"]
    },
    "slimjet": {
        "name": "Slimjet",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Slimjet/User Data",
            # Linux
            "~/.config/slimjet",
            # macOS
            "~/Library/Application Support/Slimjet",
            # Haiku
            "~/config/settings/Slimjet",
            # OS/2
            "~/Slimjet/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\Slimjet"
        ],
        "executable_names": ["slimjet", "slimjet.exe"],
        "package_names": ["slimjet"]
    },
    "epic": {
        "name": "Epic Privacy Browser",
        "family": "chrome",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Epic Privacy Browser/User Data",
            # Linux
            "~/.config/epic",
            # macOS
            "~/Library/Application Support/Epic",
            # Haiku
            "~/config/settings/Epic",
            # OS/2
            "~/Epic Privacy Browser/User Data"
        ],
        "registry_paths": [
            r"SOFTWARE\Epic Privacy Browser"
        ],
        "executable_names": ["epic", "epic.exe", "epic-browser"],
        "package_names": ["epic", "epic-browser"]
    },
    
    # Otros navegadores
    "gnome_web": {
        "name": "GNOME Web (Epiphany)",
        "family": "webkit",
        "profile_paths": [
            # Linux
            "~/.local/share/epiphany",
            # macOS
            "~/Library/Application Support/Epiphany",
            # Haiku
            "~/config/settings/epiphany",
            # OS/2
            "~/Epiphany"
        ],
        "registry_paths": [],
        "executable_names": ["epiphany", "epiphany-browser", "gnome-web"],
        "package_names": ["epiphany", "epiphany-browser", "gnome-web"]
    },
    "midori": {
        "name": "Midori",
        "family": "webkit",
        "profile_paths": [
            # Windows
            "~/AppData/Local/Midori",
            # Linux
            "~/.config/midori",
            # macOS
            "~/Library/Application Support/Midori",
            # Haiku
            "~/config/settings/midori",
            # OS/2
            "~/Midori"
        ],
        "registry_paths": [],
        "executable_names": ["midori", "midori.exe"],
        "package_names": ["midori"]
    },
    "konqueror": {
        "name": "Konqueror",
        "family": "webkit",
        "profile_paths": [
            # Linux
            "~/.kde/share/apps/konqueror",
            "~/.kde4/share/apps/konqueror",
            "~/.local/share/konqueror",
            # Haiku
            "~/config/settings/konqueror",
            # OS/2
            "~/Konqueror"
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
            "~/Library/Application Support/falkon",
            # Haiku
            "~/config/settings/falkon",
            # OS/2
            "~/Falkon"
        ],
        "registry_paths": [],
        "executable_names": ["falkon", "falkon.exe"],
        "package_names": ["falkon"]
    },
    "otter": {
        "name": "Otter Browser",
        "family": "webkit",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/OtterBrowser",
            # Linux
            "~/.config/otter-browser",
            # macOS
            "~/Library/Application Support/Otter Browser",
            # Haiku
            "~/config/settings/otter-browser",
            # OS/2
            "~/OtterBrowser"
        ],
        "registry_paths": [],
        "executable_names": ["otter-browser", "otter-browser.exe"],
        "package_names": ["otter-browser"]
    },
    "qutebrowser": {
        "name": "qutebrowser",
        "family": "webkit",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/qutebrowser",
            # Linux
            "~/.config/qutebrowser",
            # macOS
            "~/Library/Application Support/qutebrowser",
            # Haiku
            "~/config/settings/qutebrowser",
            # OS/2
            "~/qutebrowser"
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
            "~/.dillo",
            # Haiku
            "~/config/settings/dillo",
            # OS/2
            "~/Dillo"
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
            "~/.netsurf",
            # macOS
            "~/Library/Application Support/NetSurf",
            # Haiku
            "~/config/settings/netsurf",
            # OS/2
            "~/NetSurf"
        ],
        "registry_paths": [],
        "executable_names": ["netsurf", "netsurf.exe"],
        "package_names": ["netsurf"]
    },
    
    # Navegadores de texto
    "elinks": {
        "name": "ELinks",
        "family": "text",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/ELinks",
            # Linux
            "~/.elinks",
            # macOS
            "~/Library/Application Support/ELinks",
            # Haiku
            "~/config/settings/elinks",
            # OS/2
            "~/ELinks"
        ],
        "registry_paths": [],
        "executable_names": ["elinks"],
        "package_names": ["elinks"]
    },
    "links": {
        "name": "Links",
        "family": "text",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Links",
            # Linux
            "~/.links",
            # macOS
            "~/Library/Application Support/Links",
            # Haiku
            "~/config/settings/links",
            # OS/2
            "~/Links"
        ],
        "registry_paths": [],
        "executable_names": ["links"],
        "package_names": ["links"]
    },
    "lynx": {
        "name": "Lynx",
        "family": "text",
        "profile_paths": [
            # Windows
            "~/AppData/Roaming/Lynx",
            # Linux
            "~/.lynx",
            # macOS
            "~/Library/Application Support/Lynx",
            # Haiku
            "~/config/settings/lynx",
            # OS/2
            "~/Lynx"
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
            "~/.w3m",
            # macOS
            "~/Library/Application Support/w3m",
            # Haiku
            "~/config/settings/w3m",
            # OS/2
            "~/w3m"
        ],
        "registry_paths": [],
        "executable_names": ["w3m"],
        "package_names": ["w3m"]
    }
}

# Tipos de datos a migrar
PROFILE_DATA_TYPES = [
    "bookmarks",
    "history",
    "passwords",
    "cookies",
    "extensions",
    "preferences",
    "certificates",
    "form_data",
    "permissions",
    "sessions"
]

# Obtener directorio de usuario
def get_user_home() -> Path:
    """
    Obtiene el directorio home del usuario de manera multiplataforma.
    
    Returns:
        Path: Ruta al directorio home del usuario
    """
    return Path.home()

# Expandir rutas de perfil
def expand_path(path: str) -> str:
    """
    Expande una ruta con ~ al directorio home del usuario.
    
    Args:
        path: Ruta con ~ para expandir
        
    Returns:
        str: Ruta expandida
    """
    return os.path.expanduser(path)

# Detectar plataforma
def get_platform() -> str:
    """
    Detecta la plataforma actual.
    
    Returns:
        str: Identificador de plataforma ('windows', 'linux', 'macos', 'haiku', 'os2', 'other')
    """
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "haiku1":
        return "haiku"
    elif sys.platform == "os2emx":
        return "os2"
    else:
        return "other"

# Obtener rutas de perfil para la plataforma actual
def get_platform_profile_paths(browser_id: str) -> List[str]:
    """
    Obtiene las rutas de perfil para un navegador en la plataforma actual.
    
    Args:
        browser_id: ID del navegador
        
    Returns:
        List[str]: Lista de rutas de perfil expandidas
    """
    if browser_id not in BROWSERS:
        return []
    
    platform = get_platform()
    paths = []
    
    for path in BROWSERS[browser_id].get("profile_paths", []):
        expanded_path = expand_path(path)
        # Filtrar rutas según la plataforma
        if platform == "windows" and "AppData" in expanded_path:
            paths.append(expanded_path)
        elif platform == "linux" and ("~/.config" in path or "~/.mozilla" in path or "~/.local" in path):
            paths.append(expanded_path)
        elif platform == "macos" and "Library/Application Support" in expanded_path:
            paths.append(expanded_path)
        elif platform == "haiku" and "config/settings" in expanded_path:
            paths.append(expanded_path)
        elif platform == "os2" and not any(p in path for p in ["AppData", "~/.config", "Library", "config/settings"]):
            paths.append(expanded_path)
    
    return paths
