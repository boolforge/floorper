#!/usr/bin/env python3
"""
Browser Profile Test Generator for Floorper

This script creates simulated browser profiles for testing Floorper's
compatibility with various browsers.
"""

import os
import json
import shutil
import random
import datetime
from pathlib import Path

# Base directory for test profiles
TEST_PROFILES_DIR = Path("test_profiles")

# Ensure the test profiles directory exists
TEST_PROFILES_DIR.mkdir(exist_ok=True)

# Define browser profile structures
BROWSER_PROFILES = {
    "firefox": {
        "path": TEST_PROFILES_DIR / "firefox",
        "structure": {
            "prefs.js": "// Firefox preferences\nuser_pref(\"browser.startup.homepage\", \"https://example.com\");\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "cookies.sqlite": b"SQLite format 3\0",
            "places.sqlite": b"SQLite format 3\0",
            "extensions": {
                "extension1@example.com": {
                    "manifest.json": json.dumps({
                        "name": "Test Extension",
                        "version": "1.0",
                        "manifest_version": 2
                    })
                }
            }
        }
    },
    "chrome": {
        "path": TEST_PROFILES_DIR / "chrome",
        "structure": {
            "Preferences": json.dumps({
                "homepage": "https://example.com",
                "extensions": {
                    "settings": {
                        "extension1": {
                            "manifest": {
                                "name": "Test Extension",
                                "version": "1.0"
                            }
                        }
                    }
                }
            }),
            "Bookmarks": json.dumps({
                "roots": {
                    "bookmark_bar": {
                        "children": [
                            {
                                "name": "Example",
                                "url": "https://example.com"
                            }
                        ]
                    }
                }
            }),
            "Cookies": b"SQLite format 3\0",
            "History": b"SQLite format 3\0",
            "Extensions": {
                "extension1": {
                    "manifest.json": json.dumps({
                        "name": "Test Extension",
                        "version": "1.0",
                        "manifest_version": 3
                    })
                }
            }
        }
    },
    "edge": {
        "path": TEST_PROFILES_DIR / "edge",
        "structure": {
            "Preferences": json.dumps({
                "homepage": "https://example.com",
                "extensions": {
                    "settings": {
                        "extension1": {
                            "manifest": {
                                "name": "Test Extension",
                                "version": "1.0"
                            }
                        }
                    }
                }
            }),
            "Bookmarks": json.dumps({
                "roots": {
                    "bookmark_bar": {
                        "children": [
                            {
                                "name": "Example",
                                "url": "https://example.com"
                            }
                        ]
                    }
                }
            }),
            "Cookies": b"SQLite format 3\0",
            "History": b"SQLite format 3\0"
        }
    },
    "opera": {
        "path": TEST_PROFILES_DIR / "opera",
        "structure": {
            "Preferences": json.dumps({
                "homepage": "https://example.com"
            }),
            "Bookmarks": json.dumps({
                "roots": {
                    "bookmark_bar": {
                        "children": [
                            {
                                "name": "Example",
                                "url": "https://example.com"
                            }
                        ]
                    }
                }
            }),
            "Cookies": b"SQLite format 3\0",
            "History": b"SQLite format 3\0"
        }
    },
    "safari": {
        "path": TEST_PROFILES_DIR / "safari",
        "structure": {
            "Bookmarks.plist": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n<plist version=\"1.0\">\n<dict>\n  <key>Children</key>\n  <array>\n    <dict>\n      <key>Title</key>\n      <string>Example</string>\n      <key>URL</key>\n      <string>https://example.com</string>\n    </dict>\n  </array>\n</dict>\n</plist>",
            "History.plist": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n<plist version=\"1.0\">\n<dict>\n  <key>WebHistoryDates</key>\n  <array>\n    <dict>\n      <key>title</key>\n      <string>Example</string>\n      <key>url</key>\n      <string>https://example.com</string>\n    </dict>\n  </array>\n</dict>\n</plist>",
            "Cookies.plist": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n<plist version=\"1.0\">\n<dict>\n  <key>Cookies</key>\n  <array>\n    <dict>\n      <key>Domain</key>\n      <string>example.com</string>\n      <key>Name</key>\n      <string>test</string>\n      <key>Value</key>\n      <string>test</string>\n    </dict>\n  </array>\n</dict>\n</plist>"
        }
    },
    "brave": {
        "path": TEST_PROFILES_DIR / "brave",
        "structure": {
            "Preferences": json.dumps({
                "homepage": "https://example.com",
                "brave": {
                    "shields": {
                        "ads_blocked": 1000,
                        "trackers_blocked": 2000
                    }
                }
            }),
            "Bookmarks": json.dumps({
                "roots": {
                    "bookmark_bar": {
                        "children": [
                            {
                                "name": "Example",
                                "url": "https://example.com"
                            }
                        ]
                    }
                }
            }),
            "Cookies": b"SQLite format 3\0",
            "History": b"SQLite format 3\0"
        }
    },
    "vivaldi": {
        "path": TEST_PROFILES_DIR / "vivaldi",
        "structure": {
            "Preferences": json.dumps({
                "homepage": "https://example.com",
                "vivaldi": {
                    "panels": {
                        "enabled": True
                    }
                }
            }),
            "Bookmarks": json.dumps({
                "roots": {
                    "bookmark_bar": {
                        "children": [
                            {
                                "name": "Example",
                                "url": "https://example.com"
                            }
                        ]
                    }
                }
            }),
            "Cookies": b"SQLite format 3\0",
            "History": b"SQLite format 3\0"
        }
    },
    "floorp": {
        "path": TEST_PROFILES_DIR / "floorp",
        "structure": {
            "prefs.js": "// Floorp preferences\nuser_pref(\"browser.startup.homepage\", \"https://example.com\");\nuser_pref(\"floorp.browser.tabs.style\", \"chrome\");\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "cookies.sqlite": b"SQLite format 3\0",
            "places.sqlite": b"SQLite format 3\0",
            "extensions": {
                "extension1@example.com": {
                    "manifest.json": json.dumps({
                        "name": "Test Extension",
                        "version": "1.0",
                        "manifest_version": 2
                    })
                }
            }
        }
    },
    "librewolf": {
        "path": TEST_PROFILES_DIR / "librewolf",
        "structure": {
            "prefs.js": "// LibreWolf preferences\nuser_pref(\"browser.startup.homepage\", \"https://example.com\");\nuser_pref(\"privacy.resistFingerprinting\", true);\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "cookies.sqlite": b"SQLite format 3\0",
            "places.sqlite": b"SQLite format 3\0"
        }
    },
    "waterfox": {
        "path": TEST_PROFILES_DIR / "waterfox",
        "structure": {
            "prefs.js": "// Waterfox preferences\nuser_pref(\"browser.startup.homepage\", \"https://example.com\");\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "cookies.sqlite": b"SQLite format 3\0",
            "places.sqlite": b"SQLite format 3\0"
        }
    },
    "palemoon": {
        "path": TEST_PROFILES_DIR / "palemoon",
        "structure": {
            "prefs.js": "// Pale Moon preferences\nuser_pref(\"browser.startup.homepage\", \"https://example.com\");\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "cookies.sqlite": b"SQLite format 3\0",
            "places.sqlite": b"SQLite format 3\0"
        }
    },
    "seamonkey": {
        "path": TEST_PROFILES_DIR / "seamonkey",
        "structure": {
            "prefs.js": "// SeaMonkey preferences\nuser_pref(\"browser.startup.homepage\", \"https://example.com\");\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "cookies.sqlite": b"SQLite format 3\0",
            "history.dat": b"SeaMonkey History File"
        }
    },
    "epiphany": {
        "path": TEST_PROFILES_DIR / "epiphany",
        "structure": {
            "bookmarks.gvdb": b"GVDB Bookmarks",
            "cookies.sqlite": b"SQLite format 3\0",
            "history.db": b"SQLite format 3\0"
        }
    },
    "falkon": {
        "path": TEST_PROFILES_DIR / "falkon",
        "structure": {
            "profiles.ini": "[General]\nstartProfile=default\n\n[Profiles]\n1\\Name=default\n",
            "profiles/default/bookmarks.json": json.dumps({
                "bookmarks": [
                    {
                        "name": "Example",
                        "url": "https://example.com"
                    }
                ]
            }),
            "profiles/default/cookies.db": b"SQLite format 3\0",
            "profiles/default/history.db": b"SQLite format 3\0"
        }
    },
    "lynx": {
        "path": TEST_PROFILES_DIR / "lynx",
        "structure": {
            "lynx.cfg": "# Lynx configuration\nSTARTFILE:https://example.com/\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "history": "https://example.com/\n"
        }
    },
    "links": {
        "path": TEST_PROFILES_DIR / "links",
        "structure": {
            "links.cfg": "# Links configuration\nhome https://example.com/\n",
            "bookmarks.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "history": "https://example.com/\n"
        }
    },
    "w3m": {
        "path": TEST_PROFILES_DIR / "w3m",
        "structure": {
            "config": "# w3m configuration\nhome_page https://example.com/\n",
            "bookmark.html": "<html><head><title>Bookmarks</title></head><body><h1>Bookmarks</h1><a href=\"https://example.com\">Example</a></body></html>",
            "history": "https://example.com/\n"
        }
    }
}

def create_file(path, content):
    """Create a file with the given content."""
    if isinstance(content, str):
        with open(path, 'w') as f:
            f.write(content)
    else:  # binary content
        with open(path, 'wb') as f:
            f.write(content)

def create_profile_structure(base_path, structure):
    """Recursively create the profile structure."""
    for name, content in structure.items():
        path = base_path / name
        
        if isinstance(content, dict):
            path.mkdir(exist_ok=True, parents=True)
            create_profile_structure(path, content)
        else:
            # Ensure parent directory exists
            path.parent.mkdir(exist_ok=True, parents=True)
            create_file(path, content)

def create_browser_profiles():
    """Create test profiles for all browsers."""
    print(f"Creating test profiles in {TEST_PROFILES_DIR}")
    
    for browser, profile_info in BROWSER_PROFILES.items():
        print(f"Creating profile for {browser}...")
        
        # Remove existing profile if it exists
        if profile_info["path"].exists():
            shutil.rmtree(profile_info["path"])
        
        # Create profile directory
        profile_info["path"].mkdir(exist_ok=True, parents=True)
        
        # Create profile structure
        create_profile_structure(profile_info["path"], profile_info["structure"])
        
        print(f"  Profile created at {profile_info['path']}")
    
    print("All browser profiles created successfully!")

if __name__ == "__main__":
    create_browser_profiles()
