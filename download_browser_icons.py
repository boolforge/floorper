#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Download missing browser icons in SVG format
"""

import os
import requests
import time

# Directory to save icons
ICONS_DIR = "browsers"

# List of browsers that need icons
MISSING_BROWSERS = [
    {
        "name": "seamonkey",
        "url": "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/seamonkey.svg"
    },
    {
        "name": "kmeleon",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9c/K-Meleon_logo.svg"
    },
    {
        "name": "otter",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Otter_Browser_logo.svg"
    },
    {
        "name": "dooble",
        "url": "https://raw.githubusercontent.com/textbrowser/dooble/master/Icons/Logo/dooble.svg"
    },
    {
        "name": "midori",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Midori_Logo.svg"
    },
    {
        "name": "falkon",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Falkon_icon.svg"
    },
    {
        "name": "qutebrowser",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Qutebrowser-icon.svg"
    },
    {
        "name": "netscape",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netscape_icon.svg"
    },
    {
        "name": "lynx",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Lynx_browser_logo.svg"
    },
    {
        "name": "links",
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Links_logo.svg"
    },
    {
        "name": "w3m",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/8e/W3m_logo.svg"
    },
    {
        "name": "chromium",
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Chromium_Material_Icon.svg"
    },
    {
        "name": "safari",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/52/Safari_browser_logo.svg"
    }
]

def download_icon(browser):
    """Download an icon for a browser"""
    name = browser["name"]
    url = browser["url"]
    filename = os.path.join(ICONS_DIR, f"{name}.svg")
    
    print(f"Downloading {name} icon from {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Successfully downloaded {name} icon to {filename}")
            return True
        else:
            print(f"Failed to download {name} icon: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {name} icon: {str(e)}")
        return False

def main():
    """Main function"""
    # Ensure the icons directory exists
    os.makedirs(ICONS_DIR, exist_ok=True)
    
    # Download each missing icon
    success_count = 0
    for browser in MISSING_BROWSERS:
        if download_icon(browser):
            success_count += 1
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    print(f"\nDownloaded {success_count} of {len(MISSING_BROWSERS)} browser icons")

if __name__ == "__main__":
    main()
