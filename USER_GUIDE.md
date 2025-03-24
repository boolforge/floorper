# User Guide

This comprehensive guide will help you get the most out of Floorper, the Universal Browser Profile Migration Tool for Floorp.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the GUI](#using-the-gui)
4. [Using the TUI](#using-the-tui)
5. [Using the CLI](#using-the-cli)
6. [Migration Process](#migration-process)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Introduction

Floorper is designed to make migrating your browser profiles to Floorp as seamless as possible. Whether you're switching from Firefox, Chrome, Edge, or even text-based browsers like Lynx, Floorper can transfer your bookmarks, history, passwords, cookies, and more to Floorp without losing any data.

### Key Features

- **Universal Browser Support**: Migrate from virtually any browser to Floorp
- **Three Interface Options**: Choose between GUI, TUI, or CLI based on your preference
- **Smart Merging**: Preserves your existing Floorp data while adding new content
- **Cross-Platform**: Works on Windows, macOS, Linux, Haiku, and OS/2

## Getting Started

### System Requirements

- **Operating System**: Windows 7+, macOS 10.12+, Linux (most distributions), Haiku, or OS/2
- **Python**: Version 3.7 or higher
- **Disk Space**: At least 100MB free space
- **Memory**: Minimum 512MB RAM (2GB recommended for large profiles)

### Installation

#### From Package Manager

```bash
pip install floorper
```

#### From Source

```bash
git clone https://github.com/boolforge/floorper.git
cd floorper
pip install -e .
```

### First Run

After installation, you can launch Floorper in any of its three interface modes:

- **GUI**: `floorper-gui` or `python run_floorper_qt.py`
- **TUI**: `floorper-tui` or `python run_floorper_tui.py`
- **CLI**: `floorper --help` or `python run_floorper_cli.py --help`

## Using the GUI

The graphical user interface provides an intuitive way to migrate your browser profiles.

### Main Window

![Main Window](docs/images/main_window.png)

The main window consists of:
1. **Source Browser Selection**: Choose the browser to migrate from
2. **Source Profile Selection**: Select the specific profile to migrate
3. **Target Profile Selection**: Choose the Floorp profile to migrate to
4. **Data Type Selection**: Select which data to migrate (bookmarks, history, etc.)
5. **Options Panel**: Configure migration settings
6. **Start Migration Button**: Begin the migration process
7. **Log Viewer**: View progress and status messages

### Step-by-Step Process

1. **Select Source Browser**: From the dropdown menu, select the browser you want to migrate from
2. **Select Source Profile**: Choose the specific profile to migrate
3. **Select Target Profile**: Choose the Floorp profile to migrate to
4. **Select Data Types**: Check the boxes for the data you want to migrate:
   - Bookmarks
   - History
   - Passwords
   - Cookies
   - Extensions
   - Preferences
   - Other data types
5. **Configure Options**:
   - Merge Strategy: Choose how to handle duplicate data
   - Backup: Enable/disable automatic backup before migration
   - Advanced options
6. **Start Migration**: Click the "Start Migration" button
7. **Monitor Progress**: Watch the progress in the log viewer
8. **Review Results**: Once complete, review the migration summary

### Theme Settings

Floorper supports both light and dark themes. To change the theme:

1. Click on "Settings" in the menu bar
2. Select "Preferences"
3. Choose your preferred theme
4. Click "Apply"

## Using the TUI

The Text User Interface (TUI) provides a rich terminal-based experience for environments without graphical capabilities.

### Navigation

- Use **arrow keys** to navigate between options
- Press **Enter** to select
- Press **Tab** to move between panels
- Press **Esc** to go back or cancel
- Press **F1** for help

### Main Screen

The TUI main screen is divided into several panels:

1. **Browser Selection Panel**: List of detected browsers
2. **Profile Panel**: Profiles for the selected browser
3. **Options Panel**: Migration settings
4. **Log Panel**: Status and progress information

### Step-by-Step Process

1. Navigate to the Browser Selection Panel and select your source browser
2. Move to the Profile Panel and select the source profile
3. Select the target Floorp profile
4. Configure migration options
5. Press **F5** to start the migration
6. Monitor progress in the Log Panel

### Keyboard Shortcuts

| Key       | Action                    |
|-----------|---------------------------|
| F1        | Show help                 |
| F5        | Start migration           |
| F10       | Exit                      |
| Ctrl+S    | Save log                  |
| Ctrl+B    | Toggle browser panel      |
| Ctrl+P    | Toggle profile panel      |
| Ctrl+O    | Toggle options panel      |
| Ctrl+L    | Toggle log panel          |

## Using the CLI

The Command Line Interface is perfect for scripting, automation, and advanced users.

### Basic Usage

```bash
floorper --source <browser> --target <profile_path> --data-types <types>
```

### Examples

Migrate Firefox bookmarks and history to Floorp:
```bash
floorper --source firefox --target ~/.floorp/default --data-types bookmarks,history
```

List all detected browsers:
```bash
floorper --list-browsers
```

List all profiles for Chrome:
```bash
floorper --list-profiles --browser chrome
```

Migrate with a specific merge strategy:
```bash
floorper --source brave --target ~/.floorp/default --data-types all --merge-strategy smart
```

### Available Options

| Option            | Description                                      | Example                           |
|-------------------|--------------------------------------------------|-----------------------------------|
| --source          | Source browser name                              | --source firefox                  |
| --source-profile  | Source profile path (optional)                   | --source-profile ~/.mozilla/firefox/abc123.default |
| --target          | Target Floorp profile path                       | --target ~/.floorp/default        |
| --data-types      | Data types to migrate (comma-separated)          | --data-types bookmarks,history,passwords |
| --list-browsers   | List all detected browsers                       | --list-browsers                   |
| --list-profiles   | List all profiles for a browser                  | --list-profiles --browser chrome  |
| --merge-strategy  | How to handle duplicate data                     | --merge-strategy smart            |
| --backup          | Create backup before migration                   | --backup                          |
| --verbose         | Enable verbose output                            | --verbose                         |
| --quiet           | Suppress all output except errors                | --quiet                           |
| --log-file        | Save log to file                                 | --log-file migration.log          |
| --config-file     | Use configuration file                           | --config-file my_config.json      |

## Migration Process

Understanding the migration process can help you make the most of Floorper.

### What Gets Migrated

Depending on your selection, Floorper can migrate:

- **Bookmarks**: All bookmarks, including folder structure
- **History**: Browsing history with timestamps and titles
- **Passwords**: Securely stored login credentials
- **Cookies**: Website cookies for staying logged in
- **Extensions**: Browser extensions and their settings
- **Preferences**: Browser settings and configurations
- **Sessions**: Open tabs and windows
- **Certificates**: Security certificates
- **Form Data**: Saved form entries
- **Permissions**: Site-specific permissions

### Merge Strategies

Floorper offers three merge strategies:

1. **Smart** (default): Intelligently merges content, avoiding duplicates while preserving both existing and new data
2. **Overwrite**: Replaces existing data with imported data
3. **Append**: Adds imported data without attempting to remove duplicates

### Backup System

Before migration, Floorper can create a backup of your target profile. This is enabled by default and highly recommended. Backups are stored in the same directory as your profile with a timestamp suffix.

To restore a backup:
1. Close Floorp
2. Rename or delete the current profile directory
3. Rename the backup directory to the original profile name
4. Restart Floorp

## Troubleshooting

### Common Issues

#### Browser Not Detected

**Problem**: Floorper doesn't detect your browser.
**Solution**: 
- Ensure the browser is installed in a standard location
- Try specifying the profile path manually
- Check if you have sufficient permissions to access the browser files

#### Migration Fails

**Problem**: Migration process fails or freezes.
**Solution**:
- Check the log for specific error messages
- Ensure Floorp is closed during migration
- Try migrating fewer data types at once
- Verify you have sufficient disk space

#### Bookmarks Missing

**Problem**: Some bookmarks are missing after migration.
**Solution**:
- Try using a different merge strategy
- Check if bookmarks were placed in a different folder
- Verify the source browser's bookmarks are accessible

#### Passwords Not Migrated

**Problem**: Passwords aren't migrated.
**Solution**:
- Ensure you have permission to access the password database
- Some browsers require the master password to export passwords
- Check if your OS has additional security measures preventing access

### Log Files

Floorper creates detailed log files that can help diagnose issues:

- **GUI Mode**: Logs are saved in `~/.floorper/logs/`
- **TUI Mode**: Logs are displayed in the log panel and can be saved with Ctrl+S
- **CLI Mode**: Logs are output to the console or to a file specified with `--log-file`

## FAQ

### General Questions

**Q: Is Floorper safe to use?**
A: Yes, Floorper is designed to be non-destructive. It creates backups by default and never deletes your source browser data.

**Q: Can I migrate from multiple browsers at once?**
A: Currently, you need to perform separate migrations for each source browser. However, you can script this using the CLI.

**Q: Does Floorper work with portable browser installations?**
A: Yes, you can specify custom profile paths for portable installations.

**Q: Will my browser extensions work in Floorp?**
A: Most Firefox extensions will work in Floorp. Chrome extensions require conversion, which Floorper attempts to do automatically when possible.

### Technical Questions

**Q: How does Floorper handle encrypted passwords?**
A: Floorper uses the source browser's decryption mechanisms when available. For some browsers, you may need to provide a master password.

**Q: Can I use Floorper to migrate between non-Floorp browsers?**
A: Floorper is specifically designed for migrating to Floorp. While the underlying technology could support other targets, this isn't currently implemented.

**Q: Does Floorper support browser sync accounts?**
A: Floorper migrates local profile data only. After migration, you can sign in to your sync account in Floorp to sync with your cloud data.

**Q: How does Floorper handle duplicate bookmarks?**
A: With the "smart" merge strategy, Floorper identifies duplicates based on URL and avoids creating redundant entries.

### Support

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/boolforge/floorper/issues) for similar problems
2. Review the detailed logs for error messages
3. Open a new issue with:
   - Your operating system and version
   - Source and target browser details
   - Complete error logs
   - Steps to reproduce the issue
