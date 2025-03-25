# Technical Documentation

## Architecture Overview

Floorper is designed with a modular architecture that separates core functionality from user interfaces. This document provides technical details about the internal structure and implementation of Floorper.

## Project Structure

```
floorper/
├── floorper/
│   ├── __init__.py
│   ├── __main__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── browser_detector.py
│   │   ├── profile_migrator.py
│   │   └── backup_manager.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── tui.py
│   │   └── gui.py
│   ├── browsers/
│   │   ├── __init__.py
│   │   ├── firefox.py
│   │   ├── chrome.py
│   │   └── ...
│   └── utils/
│       ├── __init__.py
│       └── performance.py
├── tests/
│   ├── __init__.py
│   ├── browser_compatibility_test.py
│   └── ...
├── README.md
├── USER_GUIDE.md
└── TECHNICAL_DOCS.md
```

## Core Modules

### Browser Detector (`core/browser_detector.py`)

The Browser Detector module is responsible for detecting browser installations and profiles on the system. It uses a combination of techniques:

1. **Path-based detection**: Checks common installation paths for browsers
2. **Registry-based detection** (Windows): Checks Windows registry for browser installations
3. **Profile structure analysis**: Analyzes directory structures to identify browser profiles

Key methods:
- `detect_all_profiles()`: Detects all browser profiles on the system
- `detect_profiles(browser_id)`: Detects profiles for a specific browser
- `detect_browser_from_path(path)`: Identifies which browser a profile belongs to

### Profile Migrator (`core/profile_migrator.py`)

The Profile Migrator handles the migration of data between browser profiles. It supports various data types:

1. **Bookmarks**: Browser bookmarks and favorites
2. **History**: Browsing history
3. **Cookies**: Website cookies
4. **Passwords**: Saved passwords
5. **Form Data**: Autofill information
6. **Extensions**: Browser extensions and add-ons
7. **Settings**: Browser settings and preferences

Key methods:
- `migrate_profile(source_profile, target_profile, data_types, options)`: Migrates data from source to target
- `_migrate_data_type(data_type, source_profile, target_profile, source_family, target_family, options)`: Handles migration of a specific data type

### Backup Manager (`core/backup_manager.py`)

The Backup Manager handles creating, listing, verifying, and restoring backups of browser profiles.

Key methods:
- `create_backup(profile_path, browser_id, profile_name)`: Creates a backup of a profile
- `list_backups(browser_id=None)`: Lists available backups
- `verify_backup(backup_path)`: Verifies the integrity of a backup
- `restore_backup(backup_path, target_path, merge)`: Restores a backup to a target location

## Interface Modules

### Command Line Interface (`interfaces/cli.py`)

The CLI provides a command-line interface for Floorper, suitable for scripting and automation. It uses Python's `argparse` module to parse command-line arguments.

Key commands:
- `list`: Lists detected browser profiles
- `migrate`: Migrates data between profiles
- `backup`: Manages profile backups (create, list, restore, verify)
- `version`: Shows version information

### Text User Interface (`interfaces/tui.py`)

The TUI provides a modern terminal-based interface using the Textual library. It offers a user-friendly way to interact with Floorper in terminal environments.

Key components:
- `ProfileScreen`: Displays detected profiles
- `MigrationScreen`: Handles profile migration
- `ProgressScreen`: Shows migration progress

### Graphical User Interface (`interfaces/gui.py`)

The GUI provides a graphical interface using PyQt6. It offers the most user-friendly way to interact with Floorper.

Key components:
- `FloorperMainWindow`: Main application window
- `ProfileListItem`: Custom list widget item for browser profiles
- `BackupRestoreDialog`: Dialog for restoring backups
- `ProfileDetectionThread`: Thread for detecting browser profiles
- `MigrationThread`: Thread for migrating browser profiles

## Performance Optimizations

Floorper includes several performance optimizations:

### Caching

The `@cached` decorator in `utils/performance.py` provides function-level caching to avoid redundant operations. This is particularly useful for browser detection, which can be time-consuming.

### Parallel Processing

The `parallel_map` function in `utils/performance.py` enables parallel execution of operations using Python's `concurrent.futures` module. This is used for:

1. Detecting profiles from multiple browsers simultaneously
2. Migrating multiple data types in parallel

### Execution Time Measurement

The `@timed` decorator in `utils/performance.py` measures and logs the execution time of functions, helping identify performance bottlenecks.

## Browser Support

Floorper supports a wide range of browsers through the `BROWSERS` dictionary in `core/constants.py`. Each browser entry includes:

- **Name**: Human-readable name
- **Family**: Browser family (e.g., "firefox", "chromium")
- **Paths**: Common installation paths by platform
- **Executables**: Executable names
- **Profile Paths**: Common profile paths by platform
- **Profile Pattern**: Regex pattern to identify profile directories
- **Data Locations**: Paths to various data types within profiles

## Data Migration Process

The data migration process follows these steps:

1. **Validation**: Validate source and target profiles
2. **Backup**: Create a backup of the target profile (if enabled)
3. **Data Extraction**: Extract data from the source profile
4. **Data Conversion**: Convert data to a format compatible with the target browser
5. **Data Insertion**: Insert converted data into the target profile
6. **Verification**: Verify the migration was successful

Different migration strategies are used depending on the source and target browser families:

- **Same Family**: Direct file copying with format adjustments
- **Different Families**: Data extraction, conversion, and insertion

## Error Handling

Floorper uses Python's exception handling mechanism to catch and handle errors. Key error handling strategies:

1. **Graceful Degradation**: If a specific data type fails to migrate, continue with others
2. **Detailed Logging**: Log detailed error information for debugging
3. **User Feedback**: Provide clear error messages to users

## Extending Floorper

### Adding Support for New Browsers

To add support for a new browser:

1. Add browser information to `BROWSERS` in `core/constants.py`
2. Implement browser-specific detection logic if needed
3. Implement browser-specific data extraction and insertion methods

### Adding Support for New Data Types

To add support for a new data type:

1. Add data type information to `DATA_TYPES` in `core/constants.py`
2. Implement data type-specific migration methods in `ProfileMigrator`
3. Update interfaces to include the new data type

## Testing

Floorper includes tests for browser compatibility in `tests/browser_compatibility_test.py`. This script:

1. Tests detection of standard, exotic, and retro browsers
2. Measures detection time
3. Verifies profile detection works correctly
4. Generates a detailed report of results

## Performance Considerations

- **Memory Usage**: Large profiles can consume significant memory during migration
- **Disk I/O**: Backup and restore operations are disk I/O intensive
- **CPU Usage**: Parallel processing can utilize multiple CPU cores

## Security Considerations

- **Sensitive Data**: Floorper handles sensitive data like passwords and cookies
- **Backup Security**: Backups are not encrypted by default
- **File Permissions**: Proper file permissions should be maintained

## Future Improvements

Potential areas for future improvement:

1. **Encrypted Backups**: Add support for encrypted profile backups
2. **Cloud Sync**: Add support for syncing profiles to cloud storage
3. **Plugin System**: Implement a plugin system for extending functionality
4. **Remote Migration**: Support migrating profiles between different machines
5. **Browser Extension**: Create browser extensions for easier profile management
