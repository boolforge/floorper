# Floorper

Floorper is a comprehensive browser profile management tool that combines the functionality of Floorpizer and BrowserMigration. It provides robust capabilities for detecting, migrating, and managing browser profiles with a special focus on Firefox-based browsers, particularly Floorp.

## Features

- **Multi-browser Support**: Detects and manages profiles from various browsers, with specialized support for Firefox-based browsers including Floorp, Waterfox, LibreWolf, Pale Moon, and Basilisk.
- **Profile Migration**: Migrate profiles between different browsers, preserving bookmarks, history, passwords, cookies, extensions, and preferences.
- **Backup & Restore**: Create and restore backups of browser profiles to protect your data.
- **Multiple Interfaces**: Choose between GUI, TUI, or CLI based on your preferences and environment.
- **Cross-platform**: Works on Windows, macOS, and Linux.

## Installation

```bash
# Clone the repository
git clone https://github.com/boolforge/floorper.git
cd floorper

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m floorper
```

## Usage

### Graphical User Interface (GUI)

The GUI provides an intuitive way to interact with Floorper. Simply run the application without any arguments to launch the GUI (if available):

```bash
python -m floorper
```

### Text User Interface (TUI)

The TUI provides a terminal-based interface with rich visual elements:

```bash
python -m floorper --tui
```

### Command Line Interface (CLI)

The CLI provides powerful command-line options for scripting and automation:

```bash
# Show help
python -m floorper --help

# Detect installed browsers
python -m floorper --detect

# List profiles for a specific browser
python -m floorper --list-profiles firefox

# Migrate from one profile to another
python -m floorper --migrate firefox:default floorp:imported

# Create a backup of a profile
python -m floorper --backup firefox:default

# Restore a backup
python -m floorper --restore backup_file.zip floorp:restored
```

## Project Structure

```
floorper/
├── browsers/              # Browser-specific modules
│   ├── handlers/          # Handlers for specific browsers
│   │   └── firefox_handler.py
│   └── firefox_based.py   # Handler for Firefox-based browsers
├── core/                  # Core functionality
│   ├── browser_detector.py
│   ├── profile_migrator.py
│   └── backup_manager.py
├── interfaces/            # User interfaces
│   ├── cli.py             # Command Line Interface
│   ├── gui.py             # Graphical User Interface
│   └── tui.py             # Text User Interface
├── utils/                 # Utility modules
│   ├── platform/          # Platform-specific utilities
│   └── app_info/          # Application information
├── __main__.py            # Entry point
└── requirements.txt       # Dependencies
```

## Dependencies

- **PyQt6**: For the graphical user interface
- **Textual**: For the text user interface
- **Rich**: For enhanced terminal output
- **pathlib**: For cross-platform path handling
- **sqlite3**: For browser database access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
