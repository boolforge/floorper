# Advanced Features Documentation

This document provides detailed information about the advanced features implemented in Floorper, based on several reference projects.

## 1. Session Merger

The Session Merger functionality allows you to combine Firefox sessions from multiple profiles, preserving tabs and windows.

### Features
- Merges open tabs and windows from multiple profiles
- Preserves session history for each tab
- Avoids duplicate tabs by default (configurable)
- Handles Firefox's compressed session format (mozLz40)

### Usage
```python
from core.session.merger import SessionMerger

# Initialize the merger
merger = SessionMerger()

# Define profiles
source_profiles = [
    {"path": "/path/to/profile1"},
    {"path": "/path/to/profile2"}
]
target_profile = {"path": "/path/to/target_profile"}

# Optional configuration
options = {
    "allow_duplicates": False  # Skip duplicate URLs
}

# Merge sessions
result = merger.merge_sessions(source_profiles, target_profile, options)
```

## 2. Bookmarks Deduplicator

The Bookmarks Deduplicator identifies and removes duplicate bookmarks within a Firefox profile.

### Features
- Detects bookmarks with identical URLs
- Preserves the newest bookmark by default
- Combines tags from removed duplicates
- Supports dry run mode for testing

### Usage
```python
from core.bookmarks.deduplicator import BookmarksDeduplicator

# Initialize the deduplicator
deduplicator = BookmarksDeduplicator()

# Define profile path
profile_path = Path("/path/to/profile")

# Optional configuration
options = {
    "dry_run": False,           # Test without making changes
    "preserve_newest": True,     # Keep the most recently added bookmark
    "preserve_tags": True        # Combine tags from all duplicates
}

# Deduplicate bookmarks
results = deduplicator.deduplicate_bookmarks(profile_path, options)
print(f"Found {results['duplicate_sets']} sets of duplicates")
print(f"Removed {results['duplicates_removed']} duplicate bookmarks")
```

## 3. Bookmarks Merger

The Bookmarks Merger combines bookmarks from multiple Firefox profiles into a single profile.

### Features
- Imports bookmarks from multiple source profiles
- Preserves folder structure (optional)
- Avoids duplicate bookmarks (configurable)
- Imports tags associated with bookmarks

### Usage
```python
from core.bookmarks.merger import BookmarksMerger

# Initialize the merger
merger = BookmarksMerger()

# Define profiles
source_profiles = [
    {"path": "/path/to/profile1", "name": "Work Profile"},
    {"path": "/path/to/profile2", "name": "Personal Profile"}
]
target_profile = {"path": "/path/to/target_profile"}

# Optional configuration
options = {
    "preserve_structure": True,  # Maintain folder hierarchy
    "avoid_duplicates": True,    # Skip duplicate URLs
    "import_tags": True          # Import bookmark tags
}

# Merge bookmarks
results = merger.merge_bookmarks(source_profiles, target_profile, options)
print(f"Imported {results['total_bookmarks_imported']} bookmarks")
print(f"Created {results['folders_created']} folders")
```

## 4. History Merger

The History Merger combines browsing history from multiple Firefox profiles into a single profile.

### Features
- Imports history entries from multiple source profiles
- Preserves visit dates and types
- Maintains frecency values (configurable)
- Filters by age (optional)

### Usage
```python
from core.history.merger import HistoryMerger

# Initialize the merger
merger = HistoryMerger()

# Define profiles
source_profiles = [
    {"path": "/path/to/profile1"},
    {"path": "/path/to/profile2"}
]
target_profile = {"path": "/path/to/target_profile"}

# Optional configuration
options = {
    "preserve_visits": True,     # Import individual visit records
    "preserve_frecency": True,   # Maintain frecency values
    "avoid_duplicates": True,    # Skip duplicate URLs
    "max_age_days": 90           # Only import history from last 90 days
}

# Merge history
results = merger.merge_history(source_profiles, target_profile, options)
print(f"Imported {results['total_urls_imported']} URLs")
print(f"Imported {results['total_visits_imported']} visits")
```

## Integration with Floorper

These advanced features are integrated into Floorper's interfaces (GUI, TUI, CLI) and can be accessed through the appropriate menus or commands.

### CLI Examples
```bash
# Merge sessions
python -m floorper --merge-sessions firefox:profile1,firefox:profile2 floorp:target

# Deduplicate bookmarks
python -m floorper --deduplicate-bookmarks firefox:profile1

# Merge bookmarks
python -m floorper --merge-bookmarks firefox:profile1,firefox:profile2 floorp:target

# Merge history
python -m floorper --merge-history firefox:profile1,firefox:profile2 floorp:target
```

## Technical Implementation

These features are implemented using SQLite operations on Firefox's places.sqlite database and direct manipulation of the sessionstore.jsonlz4 files. The implementation is based on techniques from the following reference projects:

1. Firefox Session Merger (https://github.com/james-cube/firefox-session-merger)
2. Firefox Bookmarks Deduplicator (https://github.com/james-cube/firefox-bookmarks-deduplicator)
3. Firefox Bookmarks Merger (https://github.com/james-cube/firefox-bookmarks-merger)
4. Firefox History Merger (https://github.com/crazy-max/firefox-history-merger)

## Other projects to get inspiration from (to be clasified and described)

https://github.com/roylind/profile_firefox_manager
https://github.com/rafspiny/firefox-profiles-recovery
https://github.com/ggtd/ff_firefox_profiler
https://github.com/vagvalas/Firefox-Profile-Migrator
https://github.com/tarekziade/conditioned-profile
https://github.com/noroot/ff-profiles-recovery
https://github.com/sxyrxyy/Firefox_Decrypt_All_Profiles_Passwords_Dirty
https://github.com/mcomella/firefox_multi
https://github.com/ltndat/firefoxprofilemanager
https://github.com/mathisdt/firefox-userdata-analysis
https://github.com/rishabh-a7da6/firefox-password-decrypt
https://github.com/darsh12/alfred-chrome-switcher
https://github.com/Kerisa/BrowserPasswordDump
https://github.com/germanrg/pyrefox
https://github.com/haaag/PyBrowsers
https://github.com/sugashsm/webinspect
https://github.com/lacostej/sync_ff_chrome_profiles
https://github.com/luismsgomes/firefox-profile
https://hg-edge.mozilla.org/mozilla-central/file/tip/testing/mozbase/mozprofile
https://github.com/numirias/firefed
https://github.com/unode/firefox_decrypt
https://github.com/tokiclover/browser-home-profile
https://github.com/sugashsm/webinspect
https://github.com/HolyboiDCoder/convert_cookie
https://github.com/byjosh/tagged_bookmarks_export_tool
https://github.com/psiegman/bookmark-generator
https://github.com/obsidianforensics/hindsight
https://github.com/Busindre/dumpzilla
https://github.com/nqyy/browser-history-analyzer
https://github.com/globecyber/Infornito
https://github.com/vund9x/BrowserForensic
https://github.com/SSPRASATH/browser-forensics
https://github.com/Rodrigoo0m/Browsers_Forensics
https://github.com/jdmastermy/BrowserForensicsToolkit
https://github.com/kerbalette/browser-forensics
https://github.com/xern/browser-forensics
https://github.com/cameronwickes/foxhunter
https://github.com/kushalsai20/Web-browser-forensics
https://github.com/bocian67/WindowsBrowserForensics
https://github.com/f4ktu4l/browser_forensics
https://github.com/vicgc/barff
https://github.com/mart123p/tor-browser-forensics
https://github.com/jsipahio/WebForensics
https://github.com/moncj/browserdump
https://github.com/DarthBandicoot/Forensics-MultiTool
https://github.com/Dhurzo/BrowserForensics
https://github.com/radams15/BrowserForensics
https://github.com/jdjiko00/Web-browser-forensics
https://github.com/R0aDt0OSCP/BraveBrowserForensics
https://github.com/SecTraversl/python_browser-forensics_Tools
https://github.com/Prvvv/ChromeForensics
https://github.com/niftycode/firefox-forensics
https://github.com/13HJoe/Google-Chrome-Forensics
https://github.com/securycore/barff
https://github.com/AlejandroCanoMon/No-privacy
https://github.com/3ls3if/Forensics-Credential-Harvester
https://github.com/The-BrAVo-Team/BrowserHistory
https://github.com/SSPRASATH/Inforamtion-Gathering-script-for-Browser-artefacts
https://github.com/nathan-out/WBFAP
https://github.com/sugashsm/webinspect
https://github.com/LewisC22/ForensicTool
https://github.com/foreni-packages/dumpzilla
https://github.com/tehreemcodes/BraveTrace
https://github.com/atcreech/digital-forensics-project/blob/main/OneDrive/Desktop/Programming%20Projects/Python/main.py
https://github.com/yogsec/Web-History-Analysis
