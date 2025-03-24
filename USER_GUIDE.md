# User Guide

## Introduction

Welcome to Floorper, a comprehensive browser profile migration and management tool. This guide will help you understand how to use Floorper effectively to detect, backup, restore, and migrate profiles between different browsers.

## Getting Started

Floorper offers three different interfaces to accommodate various user preferences:

1. **Graphical User Interface (GUI)** - A user-friendly interface built with PyQt6
2. **Text User Interface (TUI)** - A modern terminal interface built with Textual
3. **Command Line Interface (CLI)** - A powerful command-line tool for scripting and automation

### Starting Floorper

To start Floorper with the default TUI:
```bash
floorper
```

To use the GUI:
```bash
floorper --gui
```

To use the CLI:
```bash
floorper --cli [command] [options]
```

## Browser Profile Detection

Floorper automatically detects browser profiles installed on your system. This includes profiles from standard browsers like Firefox, Chrome, and Edge, as well as exotic and retro browsers.

### Using the GUI

1. Launch the GUI interface
2. The main screen will display all detected browser profiles
3. You can refresh the profile list using the "Refresh Profiles" button

### Using the TUI

1. Launch the TUI interface
2. The main screen will display all detected browser profiles
3. You can refresh the profile list by pressing the "r" key or clicking the "Refresh" button

### Using the CLI

To list all detected profiles:
```bash
floorper --cli list
```

To list profiles for a specific browser:
```bash
floorper --cli list --browser firefox
```

To output the list in JSON format:
```bash
floorper --cli list --json
```

## Profile Migration

Floorper allows you to migrate data between browser profiles, including bookmarks, history, cookies, passwords, and more.

### Using the GUI

1. Select one or more source profiles from the list
2. Select a target profile from the dropdown
3. Choose which data types to migrate using the checkboxes
4. Click the "Migrate Profiles" button
5. Monitor the progress in the Progress tab

### Using the TUI

1. Select one or more source profiles by clicking on them
2. Click the "Next" button
3. Select a target profile from the dropdown
4. Choose which data types to migrate using the checkboxes
5. Click the "Migrate" button
6. Monitor the progress on the migration progress screen

### Using the CLI

To migrate from one profile to another:
```bash
floorper --cli migrate --source "/path/to/source/profile" --target "/path/to/target/profile"
```

To specify which data types to migrate:
```bash
floorper --cli migrate --source "/path/to/source/profile" --target "/path/to/target/profile" --data bookmarks,history,cookies
```

To skip creating a backup before migration:
```bash
floorper --cli migrate --source "/path/to/source/profile" --target "/path/to/target/profile" --no-backup
```

## Backup and Restore

Floorper provides functionality to create and restore backups of browser profiles.

### Using the GUI

#### Creating a Backup
1. Go to the "Backups" tab
2. Click the "Create Backup" button
3. Select the profile you want to backup
4. The backup will be created and added to the list

#### Restoring a Backup
1. Go to the "Backups" tab
2. Click the "Restore Backup" button
3. Select the backup you want to restore
4. Choose the target directory
5. Choose whether to merge with existing files
6. Click "OK" to restore the backup

### Using the TUI

Backup and restore functionality is integrated into the migration workflow in the TUI.

### Using the CLI

#### Creating a Backup
```bash
floorper --cli backup create --profile "/path/to/profile" --browser firefox --name "My Profile"
```

#### Listing Backups
```bash
floorper --cli backup list
```

#### Restoring a Backup
```bash
floorper --cli backup restore --backup "/path/to/backup.zip" --target "/path/to/restore/directory"
```

#### Verifying a Backup
```bash
floorper --cli backup verify --backup "/path/to/backup.zip"
```

## Advanced Features

### Performance Optimization

Floorper includes performance optimizations that can be enabled or disabled:

- **Caching**: Speeds up repeated operations by caching results
- **Parallel Processing**: Uses multiple CPU cores for faster processing

These optimizations are enabled by default but can be controlled through the CLI:

```bash
floorper --cli migrate --source "/path/to/source" --target "/path/to/target" --no-parallel
```

### Exotic and Retro Browser Support

Floorper supports a wide range of exotic and retro browsers. When migrating from these browsers, Floorper uses specialized techniques to extract and convert the data to a format compatible with modern browsers.

## Troubleshooting

### Common Issues

#### Profile Detection Fails
- Ensure the browser is installed correctly
- Check if the profile directory exists and is accessible
- Try running Floorper with administrator/root privileges

#### Migration Fails
- Check the log file (floorper.log) for detailed error messages
- Ensure both source and target profiles are valid
- Try creating a backup of the target profile before migration

#### Backup/Restore Fails
- Ensure you have write permissions to the backup directory
- Check if there's enough disk space
- Verify the backup file is not corrupted using the verify command

### Logs

Floorper creates log files that can help diagnose issues:

- **floorper.log**: Main application log
- **browser_compatibility_test.log**: Log for browser compatibility tests
- **performance_optimization.log**: Log for performance optimization tests

## Getting Help

If you encounter any issues or have questions, please:

1. Check the documentation
2. Look for similar issues in the GitHub repository
3. Open a new issue if your problem is not already addressed

## Contributing

We welcome contributions to Floorper! Please see the README.md file for information on how to contribute.
